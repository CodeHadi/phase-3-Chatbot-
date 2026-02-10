from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Provide a convenient local fallback for development so the backend can run
# without requiring a remote DB. If you want production behavior, set
# `DATABASE_URL` in a `.env` file (e.g. Neon/Postgres). For quick runs we'll
# default to a local SQLite file.
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./dev.db"
    print("⚠️  DATABASE_URL not set — using local sqlite dev.db")

# Create engine with SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session