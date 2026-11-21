
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone
from bson import ObjectId
import re

from database.connection import db
from backend.utils.dependencies import require_roles
from backend.utils.audit import log_action

router = APIRouter()


def customer_access(customer_id, user):
    if not ObjectId.is_valid(customer_id):
        raise HTTPException(400, "Invalid customer ID")

    query = {"_id": ObjectId(customer_id)}

    if user["role"] == "SalesExecutive":
        query["assigned_to"] = user["username"]

    customer = db.customers.find_one(query)

    if not customer:
        raise HTTPException(404, "Customer not found")

    return customer


def format_customer(customer):
    customer["_id"] = str(customer["_id"])
    return customer


class CustomerCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str
    company_name: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    status: str = "Active"
    assigned_to: str


class CustomerUpdate(BaseModel):
    customer_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = None
    company_name: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    status: str | None = None
    assigned_to: str | None = None


@router.get("/")
def get_customers(
    user=Depends(require_roles("Admin", "Manager", "SalesExecutive"))
):
    query = {}

    if user["role"] == "SalesExecutive":
        query["assigned_to"] = user["username"]

    customers = [
        format_customer(c)
        for c in db.customers.find(query)
    ]

    return {"count": len(customers), "customers": customers}


@router.post("/", status_code=201)
def create_customer(
    data: CustomerCreate,
    user=Depends(require_roles("Admin", "Manager", "SalesExecutive"))
):
    if not re.fullmatch(r"[6-9]\d{9}", data.phone):
        raise HTTPException(400, "Enter a valid 10-digit Indian mobile number")

    email = str(data.email).lower()

    if db.customers.find_one({"email": email}):
        raise HTTPException(409, "Email already exists")

    if db.customers.find_one({"phone": data.phone}):
        raise HTTPException(409, "Phone already exists")

    if data.status not in ["Active", "Inactive"]:
        raise HTTPException(400, "Invalid customer status")

    assigned_to = (
        user["username"]
        if user["role"] == "SalesExecutive"
        else data.assigned_to
    )

    customer = data.model_dump()
    customer.update({
        "email": email,
        "assigned_to": assigned_to,
        "created_date": datetime.now(timezone.utc),
        "created_by": user["username"]
    })

    result = db.customers.insert_one(customer)

    log_action(
        user["username"],
        "CREATE",
        "Customer",
        result.inserted_id,
        new_value={
            "customer_name": customer["customer_name"],
            "email": customer["email"],
            "phone": customer["phone"]
        }
    )

    return {
        "message": "Customer created successfully",
        "customer_id": str(result.inserted_id)
    }


@router.get("/{customer_id}")
def get_customer(
    customer_id: str,
    user=Depends(require_roles("Admin", "Manager", "SalesExecutive"))
):
    return format_customer(customer_access(customer_id, user))


@router.put("/{customer_id}")
def update_customer(
    customer_id: str,
    data: CustomerUpdate,
    user=Depends(require_roles("Admin", "Manager", "SalesExecutive"))
):
    old_customer = customer_access(customer_id, user)

    updates = data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(400, "No update data provided")

    if user["role"] == "SalesExecutive":
        updates.pop("assigned_to", None)

    if "phone" in updates:
        if not re.fullmatch(r"[6-9]\d{9}", updates["phone"]):
            raise HTTPException(400, "Invalid phone number")

        if db.customers.find_one({
            "phone": updates["phone"],
            "_id": {"$ne": ObjectId(customer_id)}
        }):
            raise HTTPException(409, "Phone already exists")

    if "email" in updates:
        updates["email"] = str(updates["email"]).lower()

        if db.customers.find_one({
            "email": updates["email"],
            "_id": {"$ne": ObjectId(customer_id)}
        }):
            raise HTTPException(409, "Email already exists")

    if "status" in updates and updates["status"] not in ["Active", "Inactive"]:
        raise HTTPException(400, "Invalid customer status")

    old_value = {
        key: old_customer.get(key)
        for key in updates
    }

    updates["updated_at"] = datetime.now(timezone.utc)
    updates["updated_by"] = user["username"]

    db.customers.update_one(
        {"_id": ObjectId(customer_id)},
        {"$set": updates}
    )

    log_action(
        user["username"],
        "UPDATE",
        "Customer",
        customer_id,
        old_value=old_value,
        new_value=updates
    )

    return {"message": "Customer updated successfully"}


@router.delete("/{customer_id}")
def deactivate_customer(
    customer_id: str,
    user=Depends(require_roles("Admin", "Manager"))
):
    customer = customer_access(customer_id, user)

    db.customers.update_one(
        {"_id": ObjectId(customer_id)},
        {"$set": {
            "status": "Inactive",
            "updated_at": datetime.now(timezone.utc),
            "updated_by": user["username"]
        }}
    )

    log_action(
        user["username"],
        "DEACTIVATE",
        "Customer",
        customer_id,
        old_value={"status": customer.get("status")},
        new_value={"status": "Inactive"}
    )

    return {"message": "Customer deactivated successfully"}
