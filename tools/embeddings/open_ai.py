# Importing OpenAI Library.
from openai import OpenAI

from tools.key import open_ai_api_key


# Setting the OpenAI API Key.
client = OpenAI(api_key=open_ai_api_key)

# Generating the Embeddings.
def generate_embeddings(chunk, model):
    return client.embeddings.create(
                input = chunk,
                model = model
            )