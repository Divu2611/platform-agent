# Importing Python Libraries.
import os
import uuid
# Importing FastAPI Libraries.
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse,FileResponse


from .model import LoginRequest, Request
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import sign_jwt

from workflow import graph

# Loading the environment variables.
from config import load_env_vars
load_env_vars()

# Getting authorized username and password.
auth_user = os.getenv("auth_user")
auth_password = os.getenv("auth_password")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Serve ui files
app.mount("/ui", StaticFiles(directory="ui"), name="ui")


@app.get("/")
def read_root() -> dict:
    return RedirectResponse(url="/view/login")


@app.get("/view/login")
def login_page():
    return FileResponse("ui/login.html")


@app.get("/view/chat")
async def chat_page():
    return FileResponse("ui/chat.html")


def check_user(email: str, password: str):
    if email == auth_user and password == auth_password:
        return True
    return False

@app.post("/api/login")
def login(request: LoginRequest):
    email = request.email
    password = request.password

    if check_user(email, password):
        return sign_jwt(email)
    raise HTTPException(status_code=401, detail="User not authenticated.")


@app.post("/api/chat", dependencies=[Depends(JWTBearer())])
async def graph_stream(request: Request):
    body = request.body
    client_id = request.client_id

    config = {"configurable": {"thread_id": uuid.uuid4()}}

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