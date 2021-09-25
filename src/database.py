from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import constants

#if constants.debug:
#    SQLALCHEMY_DATABASE_URL = "sqlite:///./../data/database.db"  # For testing, real is later

SQLALCHEMY_DATABASE_URL = "sqlite:////var/royal-automation/database.db"  # Deployed URL

if constants.debug:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
    
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
