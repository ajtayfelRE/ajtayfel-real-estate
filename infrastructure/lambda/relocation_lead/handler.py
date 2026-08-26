import json
import os
import re
import uuid
from datetime import datetime, timezone

import boto3


TABLE_NAME = os.environ["TABLE_NAME"]
NOTIFY_EMAIL = os.environ["NOTIFY_EMAIL"]
FROM_EMAIL = os.environ.get("FROM_EMAIL", NOTIFY_EMAIL)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

ses = boto3.client("sesv2")

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

ALLOWED_INQUIRY_TYPES = {
    "buying",
    "selling",
    "relocation",
    "general",
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


def base_lead(payload, lead_type):
    now = datetime.now(timezone.utc).isoformat()

    return {
        "lead_id": str(uuid.uuid4()),
        "created_at": now,
        "updated_at": now,
        "status": "NEW",
        "lead_type": lead_type,

        "first_name": clean(payload.get("first_name"), 100),
        "last_name": clean(payload.get("last_name"), 100),
        "email": clean(payload.get("email"), 254).lower(),
        "phone": clean(payload.get("phone"), 50),

        "consent_contact": payload.get("consent_contact") is True
    }


def build_relocation_lead(payload):
    lead = base_lead(payload, "relocation")

    lead.update({
        "current_city": clean(payload.get("current_city"), 100),
        "current_state": clean(payload.get("current_state"), 50),

        "destination_city": clean(
            payload.get("destination_city"),
            100
        ),
        "destination_state": clean(
            payload.get("destination_state"),
            50
        ),

        "relocation_type": clean(
            payload.get("relocation_type"),
            50
        ).lower(),

        "timeframe": clean(payload.get("timeframe"), 100),
        "price_range": clean(payload.get("price_range"), 100),
        "has_agent": clean(payload.get("has_agent"), 50),

        "notes": clean(payload.get("notes"), 2000),

        "source": clean(
            payload.get("source") or "relocation-form",
            100
        )
    })

    errors = []

    if not lead["first_name"]:
        errors.append("First name is required.")

    if not lead["last_name"]:
        errors.append("Last name is required.")

    if not lead["email"] or not EMAIL_RE.match(lead["email"]):
        errors.append("A valid email address is required.")

    if not lead["current_state"]:
        errors.append("Current state is required.")

    if not lead["destination_state"]:
        errors.append("Destination state is required.")

    if lead["relocation_type"] not in ALLOWED_RELOCATION_TYPES:
        errors.append("A valid relocation type is required.")

    if not lead["timeframe"]:
        errors.append("Timeframe is required.")

    if not lead["consent_contact"]:
        errors.append("Contact consent is required.")

    return lead, errors


def build_contact_lead(payload):
    lead = base_lead(payload, "contact")

    lead.update({
        "inquiry_type": clean(
            payload.get("inquiry_type"),
            50
        ).lower(),

        "notes": clean(
            payload.get("message") or payload.get("notes"),
            2000
        ),

        "source": clean(
            payload.get("source") or "contact-page",
            100
        )
    })

    errors = []

    if not lead["first_name"]:
        errors.append("First name is required.")

    if not lead["last_name"]:
        errors.append("Last name is required.")

    if not lead["email"] or not EMAIL_RE.match(lead["email"]):
        errors.append("A valid email address is required.")

    if lead["inquiry_type"] not in ALLOWED_INQUIRY_TYPES:
        errors.append("A valid inquiry type is required.")

    if not lead["notes"]:
        errors.append("A message is required.")

    if not lead["consent_contact"]:
        errors.append("Contact consent is required.")

    return lead, errors


def send_notification(lead):
    if lead.get("lead_type") == "contact":
        subject = "New AJTayfel.com contact inquiry"

        body = f"""A new website contact inquiry was received.

Name: {lead.get("first_name", "")} {lead.get("last_name", "")}
Email: {lead.get("email", "")}
Phone: {lead.get("phone", "")}

Inquiry type: {lead.get("inquiry_type", "")}

Source: {lead.get("source", "")}
Lead ID: {lead.get("lead_id", "")}
Created: {lead.get("created_at", "")}

Message:
{lead.get("notes", "")}
"""

    else:
        subject = "New AJTayfel.com relocation lead"

        current_location = ", ".join(
            part for part in [
                lead.get("current_city"),
                lead.get("current_state")
            ]
            if part
        )

        destination = ", ".join(
            part for part in [
                lead.get("destination_city"),
                lead.get("destination_state")
            ]
            if part
        )

        body = f"""A new relocation lead was received.

Name: {lead.get("first_name", "")} {lead.get("last_name", "")}
Email: {lead.get("email", "")}
Phone: {lead.get("phone", "")}

Current location: {current_location}
Destination: {destination}

Relocation need: {lead.get("relocation_type", "")}
Timeframe: {lead.get("timeframe", "")}
Price range: {lead.get("price_range", "")}
Existing agent: {lead.get("has_agent", "")}

Source: {lead.get("source", "")}
Lead ID: {lead.get("lead_id", "")}
Created: {lead.get("created_at", "")}

Notes:
{lead.get("notes", "")}
"""

    ses.send_email(
        FromEmailAddress=FROM_EMAIL,
        Destination={
            "ToAddresses": [
                NOTIFY_EMAIL
            ]
        },
        Content={
            "Simple": {
                "Subject": {
                    "Data": subject
                },
                "Body": {
                    "Text": {
                        "Data": body
                    }
                }
            }
        }
    )


def lambda_handler(event, context):
    http = event.get("requestContext", {}).get("http", {})

    if http.get("method") != "POST":
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

    request_path = (
        event.get("rawPath")
        or http.get("path")
        or ""
    )

    if request_path == "/leads/relocation":
        lead, errors = build_relocation_lead(payload)

    elif request_path == "/leads/contact":
        lead, errors = build_contact_lead(payload)

    else:
        return response(404, {
            "error": "Lead endpoint not found."
        })

    if errors:
        return response(400, {
            "error": "Validation failed.",
            "details": errors
        })

    try:
        table.put_item(
            Item=lead,
            ConditionExpression="attribute_not_exists(lead_id)"
        )
    except Exception:
        print("Failed to store lead.")
        raise

    try:
        send_notification(lead)
    except Exception:
        # Lead storage remains the primary operation.
        print("Lead stored, but SES notification failed.")

    return response(201, {
        "success": True,
        "lead_id": lead["lead_id"]
    })
