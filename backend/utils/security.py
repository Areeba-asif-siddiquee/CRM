
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Password hashing
password_hasher = PasswordHash.recommended()


def hash_password(password: str):
    return password_hasher.hash(password)


def verify_password(password: str, hashed_password: str):
    return password_hasher.verify(password, hashed_password)


# Generate JWT token
def create_access_token(username: str, role: str):

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "role": role,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# Verify JWT token
def decode_access_token(token: str):
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except Exception as error:
        print("JWT VERIFICATION ERROR:", repr(error))
        raise