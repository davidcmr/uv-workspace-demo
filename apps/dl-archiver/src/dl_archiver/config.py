import os

from core import CloudProvider, ProviderConfig


class Config:
    def __init__(self) -> None:
        self.aws_region_name = os.getenv("AWS_REGION", "us-east-1")
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key_id = os.getenv("AWS_SECRET_KEY_ID")
        self.aws_session_token = os.getenv("AWS_SESSION_TOKEN")
        self.aws_profile_name = os.getenv("AWS_PROFILE_NAME")
        self._provider_name = os.getenv("CLOUD_PROVIDER")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///:memory:")
        self.readonly_database_url = os.getenv("READONLY_DATABASE_URL")

    @property
    def cloud_provider(self) -> CloudProvider:
        if not self._provider_name:
            raise ValueError("CLOUD_PROVIDER environment variable is not set")
        try:
            return CloudProvider(self._provider_name.lower())
        except ValueError as err:
            valid_providers = [p.value for p in CloudProvider]
            raise ValueError(
                f"Invalid cloud provider: {self._provider_name}. Valid providers: {valid_providers}"
            ) from err

    @property
    def provider_config(self) -> ProviderConfig:
        return ProviderConfig(
            aws_region_name=self.aws_region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_key_id=self.aws_secret_key_id,
            aws_session_token=self.aws_session_token,
            aws_profile_name=self.aws_profile_name,
        )
