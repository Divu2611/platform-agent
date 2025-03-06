# Importing LangChain Libraries.
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model

from tools.key import open_ai_api_key


# Defining OpenAI chat model.
def get_chat_model(model, temperature):
    params = {
        "model": model,
        "api_key": open_ai_api_key
    }

    if model not in ["o3-mini"]:
        params["temperature"] = temperature

    open_ai_chat_model = ChatOpenAI(**params)

    return open_ai_chat_model


# Defining OpenAI LLM model.
def get_llm(model):
    open_ai_llm = init_chat_model(model, model_provider="openai")
    return open_ai_llm