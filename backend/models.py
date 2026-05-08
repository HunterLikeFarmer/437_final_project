from utils import now_iso


# Builds a dictionary representing an active alert shown on the dashboard.
def make_alert(alert_id, severity, message, source="system", timestamp=None, alert_type="alert"):
    return {
        "id": alert_id,
        "severity": severity,
        "message": message,
        "source": source,
        "timestamp": timestamp or now_iso(),
        "alert_type": alert_type
    }


# Builds a dictionary representing one event row for logging and API responses.
def make_event(source, event_type, severity, message, raw_payload=None, timestamp=None):
    return {
        "timestamp": timestamp or now_iso(),
        "source": source,
        "event_type": event_type,
        "severity": severity,
        "message": message,
        "raw_payload": raw_payload
    }


# Creates the starting in-memory state used before MQTT messages arrive.
def default_system_state():
    return {
        "environment": {
            "node_id": None,
            "status": None,
            "temperature": None,
            "humidity": None,
            "light": None,
            "last_updated": None
        },
        "motion": {
            "detected": False,
            "last_updated": None
        },
        "sound": {
            "level": None,
            "cry_detected": False,
            "last_updated": None
        },
        "safety": {
            "node_id": None,
            "status": None,
            "kids_close": False,
            "boundary_alert": False,
            "lock_value": None,
            "lock_status": "unknown",
            "last_updated": None
        },
        "alerts": []
    }
