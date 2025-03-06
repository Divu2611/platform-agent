# Importing Libraries.
import os

# Loading the environment variables.
from config import load_env_vars
load_env_vars()


# Defining Tavily API key.
tavily_api_key = os.getenv("TAVILY_API_KEY")