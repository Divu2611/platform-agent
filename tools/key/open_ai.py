# Importing Libraries.
import os
from dotenv import load_dotenv

# Loading the environment variables.
load_dotenv()


# Defining OpenAI API key.
open_ai_api_key = os.getenv("open_ai_api_key")