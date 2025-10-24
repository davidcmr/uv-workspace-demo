import sqlalchemy as sa


class Base(sa.orm.DeclarativeBase):
    pass


class FileModel(Base):
    __tablename__ = "files"
    id = sa.Column(sa.Integer, primary_key=True)
    path = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False)
    updated_at = sa.Column(sa.DateTime, nullable=False)
