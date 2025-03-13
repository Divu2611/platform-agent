# Importing DB Libraries.
from pgvector.sqlalchemy import Vector 
from sqlalchemy import Column, Integer, String, DateTime

from tools.database import Base


# Defining the Embedding Class.
class Embedding(Base):
    __tablename__ = "embedding_doc_bkp"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    chunk = Column(String, nullable=False)
    embedding = Column(Vector, nullable=False)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)