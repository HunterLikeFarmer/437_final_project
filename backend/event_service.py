from database import get_recent_events as read_recent_events
from database import insert_event
from models import make_event


# Converts one MQTT message into a readable event and saves it to SQLite.
def process_mqtt_event(topic, payload):
    source = payload.get("node_id", payload.get("source", topic))
    status = payload.get("status", "ok")

    if topic.endswith("/alert") or "/system/alert" in topic:
        event = make_event(
            source=source,
            event_type="alert",
            severity=payload.get("severity", "high"),
            message=payload.get("message", "Alert received from device"),
            raw_payload=payload,
            timestamp=payload.get("timestamp")
        )
    elif payload.get("command") and status in ("received", "ack", "acknowledged"):
        event = make_event(
            source=source,
            event_type="command_ack",
            severity="low",
            message=f"Command acknowledged: {payload.get('command')}",
            raw_payload=payload,
            timestamp=payload.get("timestamp")
        )
    elif status not in ("ok", "online", "ready"):
        event = make_event(
            source=source,
            event_type="warning",
            severity=payload.get("severity", "medium"),
            message=payload.get("message", f"Device reported status: {status}"),
            raw_payload=payload,
            timestamp=payload.get("timestamp")
        )
    else:
        event = make_event(
            source=source,
            event_type="status_update",
            severity="low",
            message=payload.get("message", f"Status update from {source}"),
            raw_payload=payload,
            timestamp=payload.get("timestamp")
        )

    event_id = insert_event(event)
    event["id"] = event_id
    return event


# Creates and stores an event from backend code instead of an MQTT message.
def create_event(source, event_type, severity, message, raw_payload=None):
    event = make_event(source, event_type, severity, message, raw_payload)
    event_id = insert_event(event)
    event["id"] = event_id
    return event


# Returns recent event records for the API route.
def get_recent_events(limit=50):
    return read_recent_events(limit)
