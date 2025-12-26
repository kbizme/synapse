from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


Base = declarative_base()

DATABASE_URL = "sqlite:///./synapse.db"

engine = create_engine(url=DATABASE_URL,
                       connect_args={"check_same_thread": False}
                    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
   """
   Initialize database tables explicitly.
   This must be called intentionally (no side effects on import).
   """
   from app.core.persistence import models   # noqa: F401

   Base.metadata.create_all(bind=engine)