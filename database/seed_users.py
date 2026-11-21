
from datetime import datetime, timezone

from database.connection import db
from backend.utils.security import hash_password

# Create the three application roles
roles = ["Admin", "Manager", "SalesExecutive"]

for role_name in roles:
    db.roles.update_one(
        {"name": role_name},
        {"$setOnInsert": {"name": role_name}},
        upsert=True
    )

# Temporary demo accounts for AcxiomCRM
demo_users = [
    {
        "username": "admin",
        "password": "admin123",
        "role": "Admin"
    },
    {
        "username": "manager",
        "password": "manager123",
        "role": "Manager"
    },
    {
        "username": "sales",
        "password": "sales123",
        "role": "SalesExecutive"
    }
]

for user in demo_users:
    db.users.update_one(
        {"username": user["username"]},
        {
            "$setOnInsert": {
                "username": user["username"],
                "password_hash": hash_password(user["password"]),
                "role": user["role"],
                "is_active": True,
                "failed_login_count": 0,
                "created_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )

print("Roles and demo users initialized successfully!")
