# Importing DB Libraries.
from sqlalchemy import Column, Integer, String, DateTime

from tools.database import Base


# Defining the Agent Class.
class Agent(Base):
    __tablename__ = "agent"
    __table_args__ = {"schema": "public"}

    agent_id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, nullable=False)
    system_prompt = Column(String, nullable=False)
    platform_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)