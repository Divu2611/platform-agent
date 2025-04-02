# Importing DB Libraries.
from sqlalchemy import Column, Integer, String, DateTime
from pgvector.sqlalchemy import Vector 

from tools.database import Base


# Defining the Embedding Class.
class Embedding(Base):
    __tablename__ = "embedding"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String, nullable=False)
    chunk = Column(String, nullable=False)
    embedding = Column(Vector, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)