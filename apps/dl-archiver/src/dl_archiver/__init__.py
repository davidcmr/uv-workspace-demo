import sqlalchemy as sa
from core import CloudManager, Database

from .config import Config
from .models import FileModel

config = Config()
db = Database(config.database_url, config.readonly_database_url)


def main() -> None:
    with open("test.txt", "w") as f:
        f.write("Hello, world!")
    cm = CloudManager(config.cloud_provider, config.provider_config)
    cm.upload_object("test.txt", "test-bucket", "test.txt")
    with db.session(readonly=True) as session:
        update_stmt = (
            sa.update(FileModel)
            .where(FileModel.path == "test.txt")
            .values(path="new_path.txt")
        )
        session.execute(update_stmt)
