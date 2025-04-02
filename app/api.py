# Importing Python Libraries.
import json
import uuid
import asyncio
# Importing FastAPI Libraries.
from sse_starlette import EventSourceResponse
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware

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


@app.post("/api/v1/chat/{chat_id}")
async def graph_stream(chat_id: str, request: ConversationRequest):
    body = request.body
    client_id = request.client_id

    chat_id = chat_id if chat_id is not '1' else uuid.uuid4()
    config = {"configurable": {"thread_id": chat_id}}

    user_input = {
        "initial_question": body,
        "client_id": client_id
    }

    # add_message(thread_id=thread_id, source="user", message=body, type="text")

    # async def generate():
    #     output = graph.invoke(user_input, config=config)

    #     response = output["answer"]
    #     add_message(thread_id=thread_id, source="platform agent", message=response, type="text")

    #     words = response.split()
    #     for word in words:
    #         yield f"data:{word}\n"
    #         await asyncio.sleep(0.05)
    #     for update in graph.astream(
    #         user_input,
    #         config=config,
    #         stream_mode="updates",
    #     ):
    #         if "get_answer" in update:
    #             response = update['get_answer']['answer']
    #             add_message(thread_id=thread_id, source="platform agent", message=response, type="text")

    #             words = response.split()
    #             for word in words:
    #                 yield f"data:{word}\n"
    # return EventSourceResponse(generate())
    # return StreamingResponse(generate(), media_type="text/event-stream")

    for update in graph.stream(
        user_input,
        config=config,
        stream_mode="updates",
    ):
        if "get_answer" in update:
            response = update['get_answer']['answer']
            # add_message(thread_id=thread_id, source="platform agent", message=response, type="text")
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


def get_graph_state(config):
    return graph.get_state(config = config)

def get_next_runnable(config):
    return get_graph_state(config=config).next


# def add_message(thread_id: int, source: str, message: str, type: str):
    message = message.replace("'", "''").replace("\n", " ").replace(":", " - ")
    source = source.replace("'", "''")
    type = type.replace("'", "''")

    query = f"""
        INSERT INTO message (
            thread_id,
            source,
            content,
            type
        )
        VALUES ({thread_id}, '{source}', '{message}', '{type}')
    """

    try:
        create(insert_query = query)

        return {
            'status_code' : 200,
            'detail' : "Message added successfully!"
        }
    except HTTPException as exception:
        print(exception)
        return {
            'status_code' : 400,
            'detail' : f"Failed to add message: {exception}"
        }
    except Exception as exception:
        print(exception)
        return {
            'status_code' : 500,
            'detail' : f"Failed to add message: {exception}"
        }