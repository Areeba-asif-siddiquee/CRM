
from fastapi import APIRouter, Depends
from backend.utils.dependencies import require_roles
from database.connection import db

router = APIRouter()


@router.get("/stats")
def dashboard_stats(
    user=Depends(
        require_roles("Admin", "Manager", "SalesExecutive")
    )
):
    query = {}

    if user["role"] == "SalesExecutive":
        query["assigned_to"] = user["username"]

    total_customers = db.customers.count_documents(query)
    total_leads = db.leads.count_documents(query)

    opportunities = list(db.opportunities.find(query))

    open_opportunities = [
        x for x in opportunities
        if x.get("stage") not in ["Won", "Lost"]
    ]

    won_opportunities = [
        x for x in opportunities if x.get("stage") == "Won"
    ]

    lost_opportunities = [
        x for x in opportunities if x.get("stage") == "Lost"
    ]

    pipeline_value = sum(
        x.get("amount", 0) for x in open_opportunities
    )

    weighted_pipeline = sum(
        x.get("weighted_value", 0) for x in open_opportunities
    )

    pending_followups = db.followups.count_documents({
        **query,
        "status": "Planned"
    })

    return {
        "role": user["role"],
        "total_customers": total_customers,
        "total_leads": total_leads,
        "open_opportunities": len(open_opportunities),
        "won_opportunities": len(won_opportunities),
        "lost_opportunities": len(lost_opportunities),
        "pending_followups": pending_followups,
        "pipeline_value": pipeline_value,
        "weighted_pipeline": weighted_pipeline
    }
