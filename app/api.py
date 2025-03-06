# Importing FastAPI Libraries.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .model import Request

from workflow import graph


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


@app.post("/api/chat")
def graph_stream(request: Request):
    body = request.body
    thread_id = request.thread_id
    client_id = request.client_id

    config = {"configurable": {"thread_id": thread_id}}

    user_input = {
        "question": body,
        "client_id": client_id
    }

    for update in graph.stream(
        user_input,
        config=config,
        stream_mode="updates",
    ):
        return update['get_answer']['answer']


def get_graph_state(config):
    return graph.get_state(config = config)

def get_next_runnable(config):
    return get_graph_state(config=config).next