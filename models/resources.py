# Importing DB Libraries.
from sqlalchemy import Column, Integer, String, DateTime

from tools.database import Base


# Defining the Embedding Class.
class Resource(Base):
    __tablename__ = "resource"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, nullable=False)
    agent_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)