# Importing DB Libraries.
from sqlalchemy import Column, Integer, String, DateTime

from tools.database import Base


# Defining the User Class.
class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Integer, nullable=False, default=0)
    client_id = Column(Integer, nullable=False)
    client_name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    role = Column(String, nullable=False)