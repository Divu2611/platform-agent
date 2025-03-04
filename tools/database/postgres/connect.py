# Importing Libraries.
import os
from dotenv import load_dotenv
# Importing DB Libraries.
from sqlalchemy import create_engine, text, and_
from sqlalchemy.orm import sessionmaker, declarative_base

# Loading the environment variables.
load_dotenv()

# Define your PostgreSQL database URL
host = os.getenv("host").replace("/", "%2F")
database = os.getenv("database").replace("/", "%2F")
username = os.getenv("username").replace("/", "%2F")
password = os.getenv("password").replace("/", "%2F")
port = os.getenv("port")

__DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{database}"

# Create an engine
__engine = create_engine(__DATABASE_URL)

# Create a session
SessionLocal = sessionmaker(bind=__engine, autocommit=False, autoflush=False)

# Define a base class for models
Base = declarative_base()