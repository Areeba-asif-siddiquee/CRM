
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone
from bson import ObjectId

from database.connection import db
from backend.utils.dependencies import require_roles
from backend.utils.audit import log_action

router = APIRouter()

VALID_STATUSES = [
    "New", "Contacted", "Qualified",
    "Unqualified", "Converted", "Lost"
]


class LeadCreate(BaseModel):
    lead_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str
    company_name: str = ""
    source: str = "Other"
    status: str = "New"
    expected_value: float = Field(default=0, ge=0)
    assigned_to: str
    notes: str = ""


class LeadUpdate(BaseModel):
    lead_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    company_name: str | None = None
    source: str | None = None
    status: str | None = None
    expected_value: float | None = Field(default=None, ge=0)
    assigned_to: str | None = None
    notes: str | None = None


def get_lead(lead_id, user):
    if not ObjectId.is_valid(lead_id):
        raise HTTPException(400, "Invalid lead ID")

    query = {"_id": ObjectId(lead_id)}

    if user["role"] == "SalesExecutive":
        query["assigned_to"] = user["username"]

    lead = db.leads.find_one(query)

    if not lead:
        raise HTTPException(404, "Lead not found")

    return lead


def format_lead(lead):
    lead["_id"] = str(lead["_id"])
    return lead


@router.get("/")
def list_leads(user=Depends(
    require_roles("Admin", "Manager", "SalesExecutive")
)):
    query = {}

    if user["role"] == "SalesExecutive":
        query["assigned_to"] = user["username"]

    leads = [format_lead(x) for x in db.leads.find(query)]

    return {"count": len(leads), "leads": leads}


@router.post("/", status_code=201)
def create_lead(
    data: LeadCreate,
    user=Depends(require_roles("Admin", "Manager", "SalesExecutive"))
):
    if data.status not in VALID_STATUSES:
        raise HTTPException(400, "Invalid lead status")

    assigned_to = (
        user["username"]
        if user["role"] == "SalesExecutive"
        else data.assigned_to
    )

    lead = data.model_dump()
    lead.update({
        "email": str(data.email).lower(),
        "assigned_to": assigned_to,
        "created_by": user["username"],
        "created_date": datetime.now(timezone.utc)
    })

    result = db.leads.insert_one(lead)

    log_action(user["username"], "CREATE", "Lead", result.inserted_id)

    return {
        "message": "Lead created successfully",
        "lead_id": str(result.inserted_id)
    }


@router.get("/{lead_id}")
def lead_details(
    lead_id: str,
    user=Depends(require_roles("Admin", "Manager", "SalesExecutive"))
):
    return format_lead(get_lead(lead_id, user))


@router.put("/{lead_id}")
def update_lead(
    lead_id: str,
    data: LeadUpdate,
    user=Depends(require_roles("Admin", "Manager", "SalesExecutive"))
):
    get_lead(lead_id, user)

    updates = data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(400, "No update data provided")

    if "status" in updates and updates["status"] not in VALID_STATUSES:
        raise HTTPException(400, "Invalid lead status")

    if user["role"] == "SalesExecutive":
        updates.pop("assigned_to", None)

    if "email" in updates:
        updates["email"] = str(updates["email"]).lower()

    updates["updated_at"] = datetime.now(timezone.utc)
    updates["updated_by"] = user["username"]

    db.leads.update_one(
        {"_id": ObjectId(lead_id)},
        {"$set": updates}
    )

    log_action(user["username"], "UPDATE", "Lead", lead_id)

    return {"message": "Lead updated successfully"}


@router.delete("/{lead_id}")
def delete_lead(
    lead_id: str,
    user=Depends(require_roles("Admin", "Manager"))
):
    get_lead(lead_id, user)

    db.leads.update_one(
        {"_id": ObjectId(lead_id)},
        {"$set": {
            "status": "Lost",
            "updated_at": datetime.now(timezone.utc),
            "updated_by": user["username"]
        }}
    )

    log_action(user["username"], "MARK_LOST", "Lead", lead_id)

    return {"message": "Lead marked as Lost"}
