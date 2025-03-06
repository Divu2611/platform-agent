# Importing Python Libraries.
from pydantic import BaseModel


class Request(BaseModel):
    body: str
    thread_id: int
    client_id: int