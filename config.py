import os
from dotenv import dotenv_values
from io import StringIO

def load_env_vars():
    """
    Load environment variables from the APP_ENV_VARS environment variable.
    This function parses the string, sets environment variables, and makes them available globally.
    """
    # Fetch the environment variables and replace spaces with newlines
    app_env_vars = os.getenv("APP_ENV_VARS", "").replace(" ", "\n")

    # Parse the environment variables using dotenv
    parsed_env = dotenv_values(stream=StringIO(app_env_vars))
    
    # Set the parsed environment variables into the current environment
    for key, value in parsed_env.items():
        os.environ[key] = value