
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from database.connection import db
from backend.utils.security import (
    verify_password,
    create_access_token,
    decode_access_token
)

router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(data: LoginRequest):

    # Find the user in MongoDB
    user = db.users.find_one({"username": data.username})

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Check whether the account is active
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=403,
            detail="This account is inactive"
        )

    # Verify the password against its stored hash
    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Generate JWT token
    token = create_access_token(
        user["username"],
        user["role"]
    )

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "username": user["username"],
        "role": user["role"]
    }


@router.get("/me")
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        payload = decode_access_token(credentials.credentials)

        return {
            "username": payload["sub"],
            "role": payload["role"]
        }

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
