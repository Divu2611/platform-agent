# Importing Python Libraries.
import os
# Importing OpenAI library.
from openai import OpenAI

from dotenv import load_dotenv
# Load .env file
load_dotenv()

api_key = os.getenv("open_ai_api_key")

client = OpenAI(api_key=api_key)


def get_openai_embeddings(texts, model="text-embedding-ada-002"):
    try:
        response = client.embeddings.create(model=model,input=texts)
        embeddings = response.data[0].embedding

        return embeddings
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None
