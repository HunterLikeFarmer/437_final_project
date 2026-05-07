import json
from datetime import datetime, timezone

from flask import jsonify


# Returns the current UTC time as an ISO-formatted string.
def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# Converts a raw JSON string or bytes payload into a Python dictionary.
def safe_json_loads(raw):
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")

    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {}


# Builds a consistent JSON error response for Flask routes.
def make_error_response(message, status_code=400):
    response = jsonify({"status": "error", "message": message})
    response.status_code = status_code
    return response


# Checks whether a request dictionary contains all required fields.
def validate_required_fields(data, fields):
    missing = [field for field in fields if data.get(field) in (None, "")]
    if missing:
        return f"Missing required field(s): {', '.join(missing)}"
    return None
