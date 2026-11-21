
from database.connection import db

# Collections required for AcxiomCRM
COLLECTIONS = [
    "users",
    "roles",
    "customers",
    "leads",
    "opportunities",
    "followups",
    "activities",
    "audit_logs"
]

def initialize_database():
    existing = db.list_collection_names()

    for collection in COLLECTIONS:
        if collection not in existing:
            db.create_collection(collection)
            print(f"Created collection: {collection}")
        else:
            print(f"Already exists: {collection}")

    print("AcxiomCRM database initialized successfully!")
