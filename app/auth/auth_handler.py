# Importing Libraries.
import os
import time
from typing import Dict
# Importing JWT Libraries.
import jwt
from jwt.exceptions import ExpiredSignatureError

# Loading the environment variables.
from config import load_env_vars
load_env_vars()

# Defining the JWT secret and algorithm.
JWT_SECRET = os.getenv("jwt_secret")
ALGORITHM = os.getenv("jwt_algorithm")


# Signing the JWT token.
def sign_jwt(username: str) -> Dict[str, str]:
    payload = {
        "username": username,
        "expires": time.time() + 1800
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

    return {
        "access_token": token
    }


# Decoding the JWT token.
def decode_jwt(token: str) -> dict:
    token_review = dict()
    try:
        jwt_token = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])

        token_review["token_valid"] = True
        token_review["token"] = jwt_token

        return token_review
    except ExpiredSignatureError:
        token_review["token_valid"] = False
        token_review["token_expired"] = True

        return token_review
    except Exception:
        token_review["token_valid"] = False
        token_review["token_expired"] = False

        return token_review