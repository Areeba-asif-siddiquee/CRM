
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from database.connection import test_connection

from backend.routes import (
    auth,
    customers,
    leads,
    opportunities,
    followups,
    activities,
    dashboard,
    audit,
    users
)

app = FastAPI(
    title="AcxiomCRM API",
    description="Customer Relationship Management System",
    version="1.0.0"
)

# Frontend static files
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)

# ---------------- API ROUTERS ----------------

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    customers.router,
    prefix="/api/customers",
    tags=["Customers"]
)

app.include_router(
    leads.router,
    prefix="/api/leads",
    tags=["Leads"]
)

app.include_router(
    opportunities.router,
    prefix="/api/opportunities",
    tags=["Opportunities"]
)

app.include_router(
    followups.router,
    prefix="/api/followups",
    tags=["Follow-ups"]
)

app.include_router(
    activities.router,
    prefix="/api/activities",
    tags=["Activities"]
)

app.include_router(
    dashboard.router,
    prefix="/api/dashboard",
    tags=["Dashboard"]
)

app.include_router(
    audit.router,
    prefix="/api/audit",
    tags=["Audit Logs"]
)

# USER MANAGEMENT ROUTER
app.include_router(
    users.router,
    prefix="/api/users",
    tags=["Users"]
)

# ---------------- FRONTEND PAGES ----------------

@app.get("/")
def login_page():
    return FileResponse(FRONTEND_DIR / "pages" / "login.html")


@app.get("/dashboard")
def dashboard_page():
    return FileResponse(FRONTEND_DIR / "pages" / "dashboard.html")


@app.get("/customers")
def customers_page():
    return FileResponse(FRONTEND_DIR / "pages" / "customers.html")


@app.get("/leads")
def leads_page():
    return FileResponse(FRONTEND_DIR / "pages" / "leads.html")


@app.get("/opportunities")
def opportunities_page():
    return FileResponse(FRONTEND_DIR / "pages" / "opportunities.html")


@app.get("/followups")
def followups_page():
    return FileResponse(FRONTEND_DIR / "pages" / "followups.html")


@app.get("/activities")
def activities_page():
    return FileResponse(FRONTEND_DIR / "pages" / "activities.html")


@app.get("/audit")
def audit_page():
    return FileResponse(FRONTEND_DIR / "pages" / "audit.html")


@app.get("/reports")
def reports_page():
    return FileResponse(FRONTEND_DIR / "pages" / "reports.html")


@app.get("/users")
def users_page():
    return FileResponse(FRONTEND_DIR / "pages" / "users.html")


# ---------------- HOME / HEALTH CHECK ----------------

@app.get("/health")
def health_check():
    return {"status": "AcxiomCRM is running"}


@app.get("/test-db")
def test_database():
    return {"database_connected": test_connection()}
