
from datetime import datetime, timezone
from database.connection import db


def log_action(
    username,
    action,
    entity_name,
    record_id=None,
    old_value=None,
    new_value=None
):
    audit_record = {
        "username": username,
        "action": action,
        "entity_name": entity_name,
        "record_id": str(record_id) if record_id else None,
        "old_value": old_value,
        "new_value": new_value,
        "created_date": datetime.now(timezone.utc)
    }

    db.audit_logs.insert_one(audit_record)
