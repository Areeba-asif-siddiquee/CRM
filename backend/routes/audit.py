
from fastapi import APIRouter, Depends
from backend.utils.dependencies import require_roles
from database.connection import db

router = APIRouter()


@router.get("/")
def get_audit_logs(
    user=Depends(require_roles("Admin"))
):
    logs = []

    for item in db.audit_logs.find().sort("created_date", -1).limit(100):
        item["_id"] = str(item["_id"])
        logs.append(item)

    return {
        "count": len(logs),
        "audit_logs": logs
    }
