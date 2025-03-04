# Importing Libraries.
import os

# Loading the environment variables.
from config import load_env_vars
load_env_vars()


# Defining LangSmith API key.
langsmith_api_key = os.getenv("langsmith_api_key")