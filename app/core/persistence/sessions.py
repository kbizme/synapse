from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from app.core.persistence.db import SessionLocal


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Provide a transactional scope around a series of operations.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
