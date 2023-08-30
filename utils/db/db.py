from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from data.config import SQLALCHEMY_DATABASE_URL


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
MySession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def commit_and_refresh(session: Session, model: Base):
    """Commits and refreshes model instance and returns it."""
    session.commit()
    session.refresh(model)
    return model


def add_commit_and_refresh(model: Base):
    """Adds, commits and refreshes model instance and returns it."""
    session = MySession()
    try:
        session.add(model)
        return commit_and_refresh(session, model)
    except IntegrityError:
        pass
