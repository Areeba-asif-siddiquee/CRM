
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.utils.security import decode_access_token

security = HTTPBearer()


# Verify the user's JWT token
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


# Check whether the user has permission
def require_roles(*allowed_roles):

    def role_checker(
        current_user: dict = Depends(get_current_user)
    ):

        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource"
            )

        return current_user

    return role_checker
