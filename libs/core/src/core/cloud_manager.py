from abc import ABC, abstractmethod
from collections.abc import Iterator
from enum import Enum
from typing import NotRequired, TypedDict

import boto3
from mypy_boto3_s3.client import S3Client


class AWSConfig(TypedDict, total=False):
    """Configuration parameters for AWS cloud manager"""

    aws_region_name: str
    aws_access_key_id: NotRequired[str | None]
    aws_secret_key_id: NotRequired[str | None]
    aws_session_token: NotRequired[str | None]
    aws_profile_name: NotRequired[str | None]


ProviderConfig = AWSConfig


class CloudProvider(Enum):
    """Supported cloud providers"""

    AWS = "aws"
    # AZURE = "azure"
    # GCP = "gcp"


class AbstractCloudManager(ABC):
    """
    Abstract base class for cloud managers.
    This class provides a base for implementing cloud managers for different cloud providers.
    It provides a common interface for getting the provider configuration and the provider.
    """

    @abstractmethod
    def upload_object(self, file_path: str, bucket_name: str, object_key: str) -> None:
        """
        Upload a file to cloud storage.
        Args:
            file_path: The path to the file to upload.
            bucket_name: The name of the bucket to upload the object to.
            object_key: The key of the object to upload.
        """
        raise NotImplementedError()

    @abstractmethod
    def download_object(
        self, bucket_name: str, object_key: str, file_path: str
    ) -> None:
        """
        Download an object from cloud storage.
        Args:
            bucket_name: The name of the bucket to download the object from.
            object_key: The key of the object to download.
            file_path: The path of the local file to download the object to.
        """
        raise NotImplementedError()

    @abstractmethod
    def move_object(
        self,
        bucket_name: str,
        object_key: str,
        dest_object_key: str,
        delete_source: bool = True,
    ) -> None:
        """
        Move an object within the same bucket.
        Args:
            bucket_name: The name of the bucket to move the object from.
            object_key: The key of the object to move.
            dest_object_key: The key of the object to move the object to.
            delete_source: Whether to delete the source object after moving.
        """
        raise NotImplementedError()

    @abstractmethod
    def transfer_object(
        self,
        bucket_name: str,
        object_key: str,
        dest_bucket_name: str,
        dest_object_key: str,
        delete_source: bool = True,
    ) -> None:
        """
        Transfer an object to a new bucket.
        Args:
            bucket_name: The name of the bucket to transfer the object from.
            object_key: The key of the object to transfer.
            dest_bucket_name: The name of the bucket to transfer the object to.
            dest_object_key: The key of the object to transfer the object to.
            delete_source: Whether to delete the source object after transferring.
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_object(self, bucket_name: str, object_key: str) -> None:
        """
        Delete an object from cloud storage.
        Args:
            bucket_name: The name of the bucket to delete the object from.
            object_key: The key of the object to delete.
        """
        raise NotImplementedError()

    @abstractmethod
    def list_dir(self, bucket_name: str, prefix: str) -> Iterator[str]:
        """
        List the contents of a directory in cloud storage.
        Args:
            bucket_name: The name of the bucket to list the directory from.
            prefix: The prefix of the directory to list.
        """
        raise NotImplementedError()


class AWSCloudManager(AbstractCloudManager):
    """
    AWS implementation of the cloud manager.
    Provides unified access to AWS S3
    """

    def __init__(self, config: AWSConfig):
        self.region_name = config.get("aws_region_name", "us-east-1")
        self.profile_name = config.get("aws_profile_name")
        self.access_key_id = config.get("aws_access_key_id")
        self.secret_key_id = config.get("aws_secret_key_id")
        self.session_token = config.get("aws_session_token")
        self._s3_client: S3Client | None = None

    @property
    def s3_client(self) -> S3Client:
        if not self._s3_client:
            session = boto3.Session(profile_name=self.profile_name)
            self._s3_client = session.client("s3", region_name=self.region_name)
        return self._s3_client

    def upload_object(self, file_path: str, bucket_name: str, object_key: str) -> None:
        self.s3_client.upload_file(file_path, bucket_name, object_key)

    def download_object(
        self, bucket_name: str, object_key: str, file_path: str
    ) -> None:
        self.s3_client.download_file(bucket_name, object_key, file_path)

    def move_object(
        self,
        bucket_name: str,
        object_key: str,
        dest_object_key: str,
        delete_source: bool = True,
    ) -> None:
        self.upload_object(bucket_name, object_key, dest_object_key)
        if delete_source:
            self.delete_object(bucket_name, object_key)

    def transfer_object(
        self,
        bucket_name: str,
        object_key: str,
        dest_bucket_name: str,
        dest_object_key: str,
        delete_source: bool = True,
    ) -> None:
        copy_source = f"{bucket_name}/{object_key}"
        self.s3_client.copy_object(
            Bucket=dest_bucket_name, Key=dest_object_key, CopySource=copy_source
        )
        if delete_source:
            self.delete_object(bucket_name, object_key)

    def delete_object(self, bucket_name: str, object_key: str) -> None:
        self.s3_client.delete_object(Bucket=bucket_name, Key=object_key)

    def list_dir(self, bucket_name: str, prefix: str) -> Iterator[str]:
        paginator = self.s3_client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            for obj in page.get("Contents", []):
                yield obj["Key"]


class CloudManager(AbstractCloudManager):
    """
    Cloud manager for different cloud providers.
    This class provides a unified interface for the cloud manager.
    """

    def __init__(self, provider: CloudProvider, config: ProviderConfig):
        self._provider = provider
        self._config = config
        self._manager: AbstractCloudManager | None = None

    @property
    def manager(self) -> AbstractCloudManager:
        if not self._manager:
            match self._provider:
                case CloudProvider.AWS:
                    self._manager = AWSCloudManager(self._config)
        return self._manager

    def upload_object(self, file_path: str, bucket_name: str, object_key: str) -> None:
        self.manager.upload_object(file_path, bucket_name, object_key)

    def download_object(
        self, bucket_name: str, object_key: str, file_path: str
    ) -> None:
        self.manager.download_object(bucket_name, object_key, file_path)

    def move_object(
        self,
        bucket_name: str,
        object_key: str,
        dest_object_key: str,
        delete_source: bool = True,
    ) -> None:
        return self.manager.move_object(
            bucket_name, object_key, dest_object_key, delete_source
        )

    def transfer_object(
        self,
        bucket_name: str,
        object_key: str,
        dest_bucket_name: str,
        dest_object_key: str,
        delete_source: bool = True,
    ) -> None:
        return self.manager.transfer_object(
            bucket_name, object_key, dest_bucket_name, dest_object_key, delete_source
        )

    def delete_object(self, bucket_name: str, object_key: str) -> None:
        return self.manager.delete_object(bucket_name, object_key)

    def list_dir(self, bucket_name: str, prefix: str) -> Iterator[str]:
        return self.manager.list_dir(bucket_name, prefix)
