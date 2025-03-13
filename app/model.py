# Importing Python Libraries.
from pydantic import BaseModel


class Request(BaseModel):
    body: str
    client_id: int