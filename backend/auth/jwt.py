import os
import secrets
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Header
from typing import Optional

_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "")
if not _SECRET_KEY:
    _SECRET_KEY = secrets.token_hex(32)
    print("WARNING: JWT_SECRET_KEY not set. Using auto-generated key. "
          "Set the JWT_SECRET_KEY environment variable for production.")

SECRET_KEY = _SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {
            "exp": expire
        }
    )

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_optional_current_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not authorization:
        return None
    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            return None
        return decode_access_token(token)
    except Exception:
        return None