# Importing FastAPI Libraries.
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .auth_handler import decode_jwt


class JWTBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)


    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

            isTokenValid, isTokenExpired, payload = self.verify_jwt(credentials.credentials)
            if not isTokenValid:
                if isTokenExpired:
                    raise HTTPException(status_code=403, detail="Token has expired.")
                else:
                    raise HTTPException(status_code=403, detail="Invalid token.")
            return payload["token"]
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")


    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False
        isTokenExpired: bool = False

        try:
            payload = decode_jwt(jwtoken)

            if payload["token_valid"]:
                isTokenValid = True
            else:
                isTokenValid = False
                if payload["token_expired"]:
                    isTokenExpired = True
        except:
            isTokenValid = False

        return isTokenValid, isTokenExpired, payload