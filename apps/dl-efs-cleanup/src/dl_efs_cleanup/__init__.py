import sqlalchemy as sa
from database import Database

wdb = "sqlite:///:memory:"
rdb = None
db = Database(wdb, rdb)


def main() -> None:
    with db.session() as session:
        stmt = sa.text("SELECT 'hello world!' as greeting;")
        session.execute(stmt)
