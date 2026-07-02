from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

# Initialize SQLite engine
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} # Required for SQLite with FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency to yield a database session and ensure it closes automatically.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
