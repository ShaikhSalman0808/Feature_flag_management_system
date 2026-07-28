from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.config import DATABASE_URL

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=True  # Set to False in production
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)