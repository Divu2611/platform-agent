# Importing Libraries.
import os

# Loading the environment variables.
from config import load_env_vars
load_env_vars()


# Defining OpenAI API key.
open_ai_api_key = os.getenv("open_ai_api_key")