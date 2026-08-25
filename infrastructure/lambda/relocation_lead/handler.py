import json
import os
import re
import uuid
from datetime import datetime, timezone

import boto3


TABLE_NAME = os.environ["TABLE_NAME"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

EMAIL_RE = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)

ALLOWED_RELOCATION_TYPES = {
    "selling",
    "buying",
    "both",
    "researching",
}


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json"
        },
        "body": json.dumps(body)
    }


def clean(value, max_length=500):
    if value is None:
        return ""

    return str(value).strip()[:max_length]


def lambda_handler(event, context):
    if event.get("requestContext", {}).get("http", {}).get("method") != "POST":
        return response(405, {
            "error": "Method not allowed."
        })

    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return response(400, {
            "error": "Invalid JSON."
        })

    # Honeypot field. Real visitors should never fill this.
    if clean(payload.get("website"), 200):
        return response(200, {
            "success": True
        })

    first_name = clean(payload.get("first_name"), 100)
    last_name = clean(payload.get("last_name"), 100)
    email = clean(payload.get("email"), 254).lower()
    phone = clean(payload.get("phone"), 50)

    current_city = clean(payload.get("current_city"), 100)
    current_state = clean(payload.get("current_state"), 50)

    destination_city = clean(payload.get("destination_city"), 100)
    destination_state = clean(payload.get("destination_state"), 50)

    relocation_type = clean(
        payload.get("relocation_type"),
        50
    ).lower()

    timeframe = clean(payload.get("timeframe"), 100)
    price_range = clean(payload.get("price_range"), 100)

    has_agent = clean(payload.get("has_agent"), 50)
    notes = clean(payload.get("notes"), 2000)

    source = clean(
        payload.get("source") or "relocation-form",
        100
    )

    consent_contact = payload.get("consent_contact") is True

    errors = []

    if not first_name:
        errors.append("First name is required.")

    if not last_name:
        errors.append("Last name is required.")

    if not email or not EMAIL_RE.match(email):
        errors.append("A valid email address is required.")

    if not current_state:
        errors.append("Current state is required.")

    if not destination_state:
        errors.append("Destination state is required.")

    if relocation_type not in ALLOWED_RELOCATION_TYPES:
        errors.append("A valid relocation type is required.")

    if not timeframe:
        errors.append("Timeframe is required.")

    if not consent_contact:
        errors.append("Contact consent is required.")

    if errors:
        return response(400, {
            "error": "Validation failed.",
            "details": errors
        })

    now = datetime.now(timezone.utc).isoformat()

    lead = {
        "lead_id": str(uuid.uuid4()),
        "created_at": now,
        "updated_at": now,
        "status": "NEW",

        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,

        "current_city": current_city,
        "current_state": current_state,

        "destination_city": destination_city,
        "destination_state": destination_state,

        "relocation_type": relocation_type,
        "timeframe": timeframe,
        "price_range": price_range,

        "has_agent": has_agent,
        "notes": notes,

        "source": source,
        "consent_contact": consent_contact
    }

    try:
        table.put_item(
            Item=lead,
            ConditionExpression="attribute_not_exists(lead_id)"
        )
    except Exception:
        print("Failed to store relocation lead.")
        raise

    return response(201, {
        "success": True,
        "lead_id": lead["lead_id"]
    })
