
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

from database.connection import db
from backend.utils.dependencies import require_roles
from backend.utils.security import hash_password
from backend.utils.audit import log_action

router = APIRouter()

VALID_ROLES = ["Admin", "Manager", "SalesExecutive"]


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6)
    role: str
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    role: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/")
def get_users(current_user=Depends(require_roles("Admin"))):
    users = list(db.users.find({}, {"password": 0}))

    for user in users:
        user["_id"] = str(user["_id"])

    return users


@router.post("/")
def create_user(
    data: UserCreate,
    current_user=Depends(require_roles("Admin"))
):
    if data.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    if db.users.find_one({"username": data.username}):
        raise HTTPException(status_code=400, detail="Username already exists")

    user = {
        "username": data.username,
        "password": hash_password(data.password),
        "role": data.role,
        "full_name": data.full_name or data.username,
        "is_active": True
    }

    result = db.users.insert_one(user)

    log_action(
        username=current_user["username"],
        action="CREATE",
        entity_name="User",
        record_id=str(result.inserted_id)
    )

    return {
        "message": "User created successfully",
        "user_id": str(result.inserted_id)
    }


@router.put("/{user_id}")
def update_user(
    user_id: str,
    data: UserUpdate,
    current_user=Depends(require_roles("Admin"))
):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user = db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updates = data.model_dump(exclude_unset=True)

    if "role" in updates and updates["role"] not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    if user["username"] == current_user["username"]:
        if updates.get("is_active") is False:
            raise HTTPException(
                status_code=400,
                detail="You cannot deactivate your own account"
            )

        if updates.get("role") and updates["role"] != "Admin":
            raise HTTPException(
                status_code=400,
                detail="You cannot remove your own Admin role"
            )

    if updates.get("is_active") is False and user.get("role") == "Admin":
        other_admins = db.users.count_documents({
            "role": "Admin",
            "is_active": True,
            "_id": {"$ne": ObjectId(user_id)}
        })

        if other_admins == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one active Admin must remain"
            )

    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": updates}
    )

    log_action(
        username=current_user["username"],
        action="UPDATE",
        entity_name="User",
        record_id=user_id
    )

    return {"message": "User updated successfully"}


@router.delete("/{user_id}")
def deactivate_user(
    user_id: str,
    current_user=Depends(require_roles("Admin"))
):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user = db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["username"] == current_user["username"]:
        raise HTTPException(
            status_code=400,
            detail="You cannot deactivate your own account"
        )

    if user.get("role") == "Admin":
        other_admins = db.users.count_documents({
            "role": "Admin",
            "is_active": True,
            "_id": {"$ne": ObjectId(user_id)}
        })

        if other_admins == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one active Admin must remain"
            )

    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": False}}
    )

    log_action(
        username=current_user["username"],
        action="DEACTIVATE",
        entity_name="User",
        record_id=user_id
    )

    return {"message": "User deactivated successfully"}
