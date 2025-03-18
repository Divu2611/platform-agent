# Importing Python Libraries.
from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class Request(BaseModel):
    body: str
    client_id: int