# Importing Libraries.
import os
from dotenv import load_dotenv

from tools.key import open_ai_api_key, langsmith_api_key

# Loading the environment variables.
load_dotenv()

# LangSmith Integration.
def langsmith_integration():
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = os.getenv('endpoint')
    os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
    os.environ["LANGCHAIN_PROJECT"] = os.getenv('project')
    os.environ["OPENAI_API_KEY"] = open_ai_api_key