from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./call_quality.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Import models so SQLAlchemy registers table metadata before create_all.
    import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
