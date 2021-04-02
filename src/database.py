from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import constants

SQLALCHEMY_DATABASE_URL = ""
if constants.debug:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./../data/database.db"  # For testing, real is later
else:
    SQLALCHEMY_DATABASE_URL = ""  # Deployed URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
