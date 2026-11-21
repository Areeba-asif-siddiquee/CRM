
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timezone, date
from bson import ObjectId

from database.connection import db
from backend.utils.dependencies import require_roles
from backend.utils.audit import log_action

router = APIRouter()

STAGES = ["Qualification", "Proposal", "Negotiation", "Won", "Lost"]


class OpportunityCreate(BaseModel):
    opportunity_name: str = Field(min_length=1, max_length=100)
    customer_id: str
    amount: float = Field(gt=0)
    stage: str = "Qualification"
    probability: int = Field(ge=0, le=100)
    expected_close_date: date
    assigned_to: str
    notes: str = ""


class OpportunityUpdate(BaseModel):
    opportunity_name: str | None = None
    amount: float | None = Field(default=None, gt=0)
    stage: str | None = None
    probability: int | None = Field(default=None, ge=0, le=100)
    expected_close_date: date | None = None
    notes: str | None = None


def find_opportunity(opp_id, user):
    if not ObjectId.is_valid(opp_id):
        raise HTTPException(400, "Invalid opportunity ID")

    query = {"_id": ObjectId(opp_id)}

    if user["role"] == "SalesExecutive":
        query["assigned_to"] = user["username"]

    opp = db.opportunities.find_one(query)

    if not opp:
        raise HTTPException(404, "Opportunity not found")

    return opp


def format_opportunity(opp):
    opp["_id"] = str(opp["_id"])
    opp["customer_id"] = str(opp["customer_id"])
    return opp


@router.get("/")
def list_opportunities(user=Depends(
    require_roles("Admin", "Manager", "SalesExecutive")
)):
    query = {}

    if user["role"] == "SalesExecutive":
        query["assigned_to"] = user["username"]

    items = [
        format_opportunity(x)
        for x in db.opportunities.find(query)
    ]

    return {"count": len(items), "opportunities": items}


@router.post("/", status_code=201)
def create_opportunity(
    data: OpportunityCreate,
    user=Depends(require_roles("Admin", "Manager", "SalesExecutive"))
):
    if not ObjectId.is_valid(data.customer_id):
        raise HTTPException(400, "Invalid customer ID")

    customer_query = {"_id": ObjectId(data.customer_id)}

    if user["role"] == "SalesExecutive":
        customer_query["assigned_to"] = user["username"]

    if not db.customers.find_one(customer_query):
        raise HTTPException(404, "Customer not found or not assigned to you")

    if data.stage not in STAGES:
        raise HTTPException(400, "Invalid opportunity stage")

    if data.stage not in ["Won", "Lost"] and data.expected_close_date < date.today():
        raise HTTPException(400, "Expected close date cannot be in the past")

    assigned_to = (
        user["username"]
        if user["role"] == "SalesExecutive"
        else data.assigned_to
    )

    opp = data.model_dump()
    opp["customer_id"] = ObjectId(data.customer_id)
    opp["expected_close_date"] = data.expected_close_date.isoformat()

    opp.update({
        "assigned_to": assigned_to,
        "created_by": user["username"],
        "created_date": datetime.now(timezone.utc),
        "weighted_value": data.amount * data.probability / 100
    })

    result = db.opportunities.insert_one(opp)

    log_action(
        user["username"], "CREATE",
        "Opportunity", result.inserted_id
    )

    return {
        "message": "Opportunity created successfully",
        "opportunity_id": str(result.inserted_id)
    }


@router.get("/{opp_id}")
def opportunity_details(
    opp_id: str,
    user=Depends(require_roles("Admin", "Manager", "SalesExecutive"))
):
    return format_opportunity(find_opportunity(opp_id, user))


@router.put("/{opp_id}")
def update_opportunity(
    opp_id: str,
    data: OpportunityUpdate,
    user=Depends(require_roles("Admin", "Manager", "SalesExecutive"))
):
    find_opportunity(opp_id, user)

    updates = data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(400, "No update data provided")

    if "stage" in updates and updates["stage"] not in STAGES:
        raise HTTPException(400, "Invalid stage")

    if "expected_close_date" in updates:
        close_date = updates["expected_close_date"]

        if updates.get("stage", "Qualification") not in ["Won", "Lost"] and close_date < date.today():
            raise HTTPException(400, "Expected close date cannot be in the past")

        updates["expected_close_date"] = close_date.isoformat()

    old = db.opportunities.find_one({"_id": ObjectId(opp_id)})

    amount = updates.get("amount", old["amount"])
    probability = updates.get("probability", old["probability"])

    updates["weighted_value"] = amount * probability / 100
    updates["updated_at"] = datetime.now(timezone.utc)
    updates["updated_by"] = user["username"]

    db.opportunities.update_one(
        {"_id": ObjectId(opp_id)},
        {"$set": updates}
    )

    log_action(user["username"], "UPDATE", "Opportunity", opp_id)

    return {"message": "Opportunity updated successfully"}


@router.delete("/{opp_id}")
def delete_opportunity(
    opp_id: str,
    user=Depends(require_roles("Admin", "Manager"))
):
    find_opportunity(opp_id, user)

    db.opportunities.update_one(
        {"_id": ObjectId(opp_id)},
        {"$set": {
            "stage": "Lost",
            "updated_at": datetime.now(timezone.utc),
            "updated_by": user["username"]
        }}
    )

    log_action(user["username"], "MARK_LOST", "Opportunity", opp_id)

    return {"message": "Opportunity marked as Lost"}
