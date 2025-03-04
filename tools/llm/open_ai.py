# Importing LangChain Libraries.
from langchain_openai import ChatOpenAI

from tools.key import open_ai_api_key


# Defining OpenAI chat model.
def get_chat_model(model, temperature):
    params = {
        "model": model,
        "api_key": open_ai_api_key
    }

    if model not in ["o3-mini"]:
        params["temperature"] = temperature

    gpt_chat_model = ChatOpenAI(**params)

    return gpt_chat_model