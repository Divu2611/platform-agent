# Importing Python Libraries.
import os
import uvicorn
from dotenv import load_dotenv

# Loading the environment variables.
load_dotenv()

if __name__ == "__main__":
    host = os.getenv("host_api")
    port = int(os.getenv("port_api"))

    uvicorn.run("app.api:app", host=host, port=port, reload=True)