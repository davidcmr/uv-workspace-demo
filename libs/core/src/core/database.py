from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


class Database:
    """
    Database class that provides readonly and write sessions with autocommit.
    Can be instantiated and used globally in applications.
    """

    def __init__(self, write_url: str, readonly_url: str | None = None) -> None:
        self._db: Engine = create_engine(write_url, echo=False)
        self._db_ro: Engine | None = (
            create_engine(readonly_url, echo=False) if readonly_url else None
        )
        self._session = sessionmaker(bind=self._db, autocommit=False, autoflush=False)
        self._session_ro = (
            sessionmaker(bind=self._db_ro, autocommit=False, autoflush=False)
            if self._db_ro
            else None
        )

    @contextmanager
    def session(self, readonly: bool = False) -> Generator[Session]:
        if readonly and self._session_ro:
            _session = self._session_ro()
        elif not readonly:
            _session = self._session()
        else:
            raise RuntimeError(
                "Readonly connection not configured. Provide readonly_url when initializing the database."
            )
        try:
            yield _session
            _session.commit()
        except Exception:
            _session.rollback()
            raise
        finally:
            _session.close()
