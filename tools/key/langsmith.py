# Importing Libraries.
import os
from dotenv import load_dotenv

# Loading the environment variables.
load_dotenv()


# Defining LangSmith API key.
langsmith_api_key = os.getenv("langsmith_api_key")