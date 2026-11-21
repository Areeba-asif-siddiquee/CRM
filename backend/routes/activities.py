
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timezone, date
from bson import ObjectId

from database.connection import db
from backend.utils.dependencies import require_roles

router = APIRouter()

ACTIVITY_TYPES = ["Call", "Meeting", "Email", "Task"]
ACTIVITY_STATUSES = ["Planned", "Completed", "Cancelled"]


class ActivityCreate(BaseModel):
    activity_type: str
    subject: str = Field(min_length=1, max_length=150)
    description: str = ""
    activity_date: date
    customer_id: str | None = None
    lead_id: str | None = None
    assigned_to: str


class ActivityUpdate(BaseModel):
    subject: str | None = None
    description: str | None = None
    activity_date: date | None = None
    status: str | None = None


@router.get("/")
def list_activities(user=Depends(
    require_roles("Admin", "Manager", "SalesExecutive")
)):
    query = {}

    if user["role"] == "SalesExecutive":
        query["assigned_to"] = user["username"]

    activities = []

    for item in db.activities.find(query):
        item["_id"] = str(item["_id"])
        if item.get("customer_id"):
            item["customer_id"] = str(item["customer_id"])
        if item.get("lead_id"):
            item["lead_id"] = str(item["lead_id"])
        activities.append(item)

    return {"count": len(activities), "activities": activities}


@router.post("/", status_code=201)
def create_activity(
    data: ActivityCreate,
    user=Depends(require_roles("Admin", "Manager", "SalesExecutive"))
):
    if data.activity_type not in ACTIVITY_TYPES:
        raise HTTPException(400, "Invalid activity type")

    if data.activity_date < date.today():
        raise HTTPException(400, "Activity date cannot be in the past")

    if not data.customer_id and not data.lead_id:
        raise HTTPException(400, "Provide a customer ID or lead ID")

    record = data.model_dump()
    record["activity_date"] = data.activity_date.isoformat()

    for field in ["customer_id", "lead_id"]:
        value = record[field]
        if value:
            if not ObjectId.is_valid(value):
                raise HTTPException(400, f"Invalid {field}")
            record[field] = ObjectId(value)

    if user["role"] == "SalesExecutive":
        record["assigned_to"] = user["username"]

    record.update({
        "status": "Planned",
        "created_by": user["username"],
        "created_date": datetime.now(timezone.utc)
    })

    result = db.activities.insert_one(record)

    return {
        "message": "Activity created successfully",
        "activity_id": str(result.inserted_id)
    }


@router.put("/{activity_id}")
def update_activity(
    activity_id: str,
    data: ActivityUpdate,
    user=Depends(require_roles("Admin", "Manager", "SalesExecutive"))
):
    if not ObjectId.is_valid(activity_id):
        raise HTTPException(400, "Invalid activity ID")

    query = {"_id": ObjectId(activity_id)}

    if user["role"] == "SalesExecutive":
        query["assigned_to"] = user["username"]

    if not db.activities.find_one(query):
        raise HTTPException(404, "Activity not found")

    updates = data.model_dump(exclude_unset=True)

    if "status" in updates and updates["status"] not in ACTIVITY_STATUSES:
        raise HTTPException(400, "Invalid activity status")

    if "activity_date" in updates:
        if updates["activity_date"] < date.today():
            raise HTTPException(400, "Activity date cannot be in the past")
        updates["activity_date"] = updates["activity_date"].isoformat()

    updates["updated_at"] = datetime.now(timezone.utc)
    updates["updated_by"] = user["username"]

    db.activities.update_one(query, {"$set": updates})

    return {"message": "Activity updated successfully"}
