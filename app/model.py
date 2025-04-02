# Importing Python Libraries.
from typing import List
from pydantic import BaseModel


class NewChatRequest(BaseModel):
    chat_id: str
    user_id: int
    client_id: int

class NewChatResponse(BaseModel):
    status: str


class Message(BaseModel):
    message_id: str
    content: str

class NewMessage(BaseModel):
    message: Message
    response: Message

class NewMessageRequest(BaseModel):
    conversation: NewMessage
    chat_id: str

class NewMessageResponse(BaseModel):
    status: str


class ConversationRequest(BaseModel):
    body: str
    client_id: int


class MessageResponse(BaseModel):
    message_id: str
    content: str
    source: str

class MessagesResponse(BaseModel):
    messages: List[MessageResponse]