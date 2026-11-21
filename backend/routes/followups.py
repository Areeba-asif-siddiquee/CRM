
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timezone, date
from bson import ObjectId

from database.connection import db
from backend.utils.dependencies import require_roles
from backend.utils.audit import log_action

router = APIRouter()

FOLLOWUP_TYPES = ["Call", "Meeting", "Email", "Task"]
FOLLOWUP_STATUSES = ["Planned", "Completed", "Missed", "Cancelled"]


class FollowUpCreate(BaseModel):
    customer_id: str
    followup_date: date
    subject: str = Field(min_length=1, max_length=150)
    followup_type: str = "Call"
    remarks: str = ""
    assigned_to: str


class FollowUpUpdate(BaseModel):
    followup_date: date | None = None
    subject: str | None = None
    followup_type: str | None = None
    remarks: str | None = None
    status: str | None = None


def find_followup(followup_id, user):
    if not ObjectId.is_valid(followup_id):
        raise HTTPException(400, "Invalid follow-up ID")

    query = {"_id": ObjectId(followup_id)}

    if user["role"] == "SalesExecutive":
        query["assigned_to"] = user["username"]

    item = db.followups.find_one(query)

    if not item:
        raise HTTPException(404, "Follow-up not found")

    return item


def format_followup(item):
    item["_id"] = str(item["_id"])
    item["customer_id"] = str(item["customer_id"])
    return item


@router.get("/")
def list_followups(user=Depends(
    require_roles("Admin", "Manager", "SalesExecutive")
)):
    query = {}

    if user["role"] == "SalesExecutive":
        query["assigned_to"] = user["username"]

    items = [
        format_followup(x)
        for x in db.followups.find(query)
    ]

    return {"count": len(items), "followups": items}


@router.post("/", status_code=201)
def create_followup(
    data: FollowUpCreate,
    user=Depends(require_roles("Admin", "Manager", "SalesExecutive"))
):
    if not ObjectId.is_valid(data.customer_id):
        raise HTTPException(400, "Invalid customer ID")

    if data.followup_date < date.today():
        raise HTTPException(400, "Follow-up date cannot be in the past")

    if data.followup_type not in FOLLOWUP_TYPES:
        raise HTTPException(400, "Invalid follow-up type")

    customer_query = {"_id": ObjectId(data.customer_id)}

    if user["role"] == "SalesExecutive":
        customer_query["assigned_to"] = user["username"]

    if not db.customers.find_one(customer_query):
        raise HTTPException(404, "Customer not found or not assigned to you")

    assigned_to = (
        user["username"]
        if user["role"] == "SalesExecutive"
        else data.assigned_to
    )

    item = data.model_dump()
    item["customer_id"] = ObjectId(data.customer_id)
    item["followup_date"] = data.followup_date.isoformat()

    item.update({
        "assigned_to": assigned_to,
        "status": "Planned",
        "created_by": user["username"],
        "created_date": datetime.now(timezone.utc)
    })

    result = db.followups.insert_one(item)

    log_action(
        user["username"], "CREATE",
        "FollowUp", result.inserted_id
    )

    return {
        "message": "Follow-up scheduled successfully",
        "followup_id": str(result.inserted_id)
    }


@router.put("/{followup_id}")
def update_followup(
    followup_id: str,
    data: FollowUpUpdate,
    user=Depends(require_roles("Admin", "Manager", "SalesExecutive"))
):
    find_followup(followup_id, user)

    updates = data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(400, "No update data provided")

    if "followup_date" in updates:
        if updates["followup_date"] < date.today():
            raise HTTPException(400, "Follow-up date cannot be in the past")

        updates["followup_date"] = updates["followup_date"].isoformat()

    if "followup_type" in updates and updates["followup_type"] not in FOLLOWUP_TYPES:
        raise HTTPException(400, "Invalid follow-up type")

    if "status" in updates and updates["status"] not in FOLLOWUP_STATUSES:
        raise HTTPException(400, "Invalid follow-up status")

    updates["updated_at"] = datetime.now(timezone.utc)
    updates["updated_by"] = user["username"]

    db.followups.update_one(
        {"_id": ObjectId(followup_id)},
        {"$set": updates}
    )

    log_action(user["username"], "UPDATE", "FollowUp", followup_id)

    return {"message": "Follow-up updated successfully"}


@router.patch("/{followup_id}/complete")
def complete_followup(
    followup_id: str,
    user=Depends(require_roles("Admin", "Manager", "SalesExecutive"))
):
    find_followup(followup_id, user)

    db.followups.update_one(
        {"_id": ObjectId(followup_id)},
        {"$set": {
            "status": "Completed",
            "completed_at": datetime.now(timezone.utc),
            "updated_by": user["username"]
        }}
    )

    log_action(user["username"], "COMPLETE", "FollowUp", followup_id)

    return {"message": "Follow-up marked as completed"}
