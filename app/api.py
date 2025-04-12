# Importing Python Libraries.
import uuid
# Importing FastAPI Libraries.
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Body, Depends

from app.auth.auth_bearer import JWTBearer

from .model import NewChatRequest, NewChatResponse, NewMessageRequest, NewMessageResponse, ConversationRequest, MessagesResponse

from workflow import graph

from tools.database import create, retrieve


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def read_root() -> dict:
    return {"message": "Welcome to Platform!"}


@app.post("/api/v1/chat")
def create_new_chat(new_chat_request: NewChatRequest) -> NewChatResponse:
    try:
        chat_id = new_chat_request.chat_id
        user_id = new_chat_request.user_id
        client_id = new_chat_request.client_id

        # Insert a new chat record
        insert_chat_query = f'''
            INSERT INTO chat_aisdk (chat_id, user_id, client_id)
            VALUES ('{chat_id}', {user_id}, {client_id})
        '''

        create(insert_query = insert_chat_query)

        new_chat_response = NewChatResponse(
            status = "success"
        )

        return new_chat_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating new chat: {e}")


@app.post("/api/v1/message")
def create_new_message(new_message_request: NewMessageRequest) -> NewMessageResponse:
    try:
        conversation = new_message_request.conversation

        message = conversation.message
        message_id = message.message_id
        content = message.content

        response = conversation.response
        response_id = response.message_id
        response_content = response.content

        chat_id = new_message_request.chat_id

        # Insert a new message record
        insert_message_query = f'''
            INSERT INTO message_aisdk (message_id, content, source, chat_id)
            VALUES
                ('{message_id}', '{content}', 'user', '{chat_id}'),
                ('{response_id}', '{response_content}', 'assistant', '{chat_id}')
        '''

        create(insert_query = insert_message_query)

        new_message_response = NewMessageResponse(
            status = "success"
        )

        return new_message_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating new message: {e}")


@app.post("/api/v1/chat/{chat_id}", dependencies=[Depends(JWTBearer())])
async def graph_stream(chat_id: str, request: ConversationRequest):
    body = request.body
    client_id = request.client_id

    chat_id = chat_id if chat_id != '1' else uuid.uuid4()

    run_id = str(uuid.uuid4())
    config = {"run_id": run_id, "configurable": {"thread_id": chat_id}}

    trace(client_id = client_id, run_id = run_id, agent_id = 0)

    user_input = {
        "initial_question": body,
        "client_id": client_id
    }

    for update in graph.stream(
        user_input,
        config=config,
        stream_mode="updates",
    ):
        if "get_answer" in update:
            response = update['get_answer']['answer']
            return response


@app.get("/api/v1/chat/{chat_id}/messages")
def get_chat_messages(chat_id: str) -> MessagesResponse:
    try:
        # Retrieve messages for the chat
        retrieve_query = f'''
            SELECT message_id, content, source FROM message_aisdk
            WHERE chat_id = '{chat_id}'
        '''

        rows, columns = retrieve(retrieve_query = retrieve_query)

        messages = []
        for row in rows:
            message = {columns[i]: row[i] for i in range(len(columns))}
            messages.append(message)

        return MessagesResponse(messages=messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat messages: {e}")


def trace(client_id: int, run_id: str, agent_id: int):
    try:
        insert_query = f'''
            INSERT INTO public.agent_run_history(client_id, run_id, agent_id)
            VALUES ({client_id}, '{run_id}', {agent_id})
        '''

        create(insert_query = insert_query)
    except Exception as exception:
        print(f"Error inserting agent run history: {exception}")
        raise HTTPException(status_code=500, detail=f"Error inserting agent run history: {exception}")