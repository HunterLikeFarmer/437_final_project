from copy import deepcopy
from threading import Lock

from models import default_system_state, make_alert
from utils import now_iso


_state_lock = Lock()
_current_state = default_system_state()
_next_alert_id = 1
ENVIRONMENT_STATUS_TOPIC = "smart_toddler/environment/status"
SAFETY_STATUS_TOPIC = "smart_toddler/safety/status"
LOCK_STATUS_TOPIC = "smart_toddler/lock/status"


# Returns the payload timestamp, or creates a current timestamp if missing.
def _timestamp(payload):
    return payload.get("timestamp") or now_iso()


# Adds a new alert or replaces an existing alert with the same id.
def _upsert_alert(alert):
    global _next_alert_id

    alert_id = alert.get("id") or _next_alert_id
    if isinstance(alert_id, int) or str(alert_id).isdigit():
        _next_alert_id = max(_next_alert_id, int(alert_id) + 1)
    else:
        _next_alert_id += 1
    alert["id"] = alert_id

    existing_index = next((index for index, item in enumerate(_current_state["alerts"]) if item.get("id") == alert_id), None)
    if existing_index is None:
        _current_state["alerts"].append(alert)
    else:
        _current_state["alerts"][existing_index] = alert


# Converts ESP32 1/0, true/false, or text values into a Python boolean.
def _device_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "locked", "close", "near")
    return False


# Converts the ESP32 lock flag into a readable lock status string.
def _lock_status(value):
    if value is None:
        return "unknown"
    if isinstance(value, str) and value.strip().lower() in ("locked", "unlocked", "unknown"):
        return value.strip().lower()
    return "locked" if _device_bool(value) else "unlocked"


# Updates the in-memory dashboard state based on an MQTT topic and payload.
def update_state_from_mqtt(topic, payload):
    timestamp = _timestamp(payload)
    raw_data = payload.get("data", {})
    data = raw_data if isinstance(raw_data, dict) else {}

    with _state_lock:
        if topic == ENVIRONMENT_STATUS_TOPIC:
            _current_state["environment"].update({
                "node_id": payload.get("node_id"),
                "status": payload.get("status"),
                "temperature": data.get("temperature", payload.get("temperature")),
                "humidity": data.get("humidity", payload.get("humidity")),
                "light": data.get("light_level", data.get("light", payload.get("light"))),
                "last_updated": timestamp
            })

            motion_detected = data.get("motion_detected", payload.get("motion_detected"))
            sound_level = data.get("sound_level", payload.get("sound_level"))

            if motion_detected is not None:
                _current_state["motion"].update({
                    "detected": bool(motion_detected),
                    "last_updated": timestamp
                })

            if sound_level is not None:
                _current_state["sound"].update({
                    "level": sound_level,
                    "last_updated": timestamp
                })

        if topic == SAFETY_STATUS_TOPIC:
            has_scalar_data = raw_data not in (None, {}) and not isinstance(raw_data, dict)
            has_kids_close = has_scalar_data or any(key in data for key in ("kids_close", "kid_close", "child_close", "boundary_alert")) or "kids_close" in payload

            _current_state["safety"].update({
                "node_id": payload.get("node_id"),
                "status": payload.get("status"),
                "last_updated": timestamp
            })

            if has_kids_close:
                kids_close_value = raw_data if has_scalar_data else data.get(
                    "kids_close",
                    data.get("kid_close", data.get("child_close", data.get("boundary_alert", payload.get("kids_close"))))
                )
                kids_close = _device_bool(kids_close_value)
                _current_state["safety"].update({
                    "kids_close": kids_close,
                    "boundary_alert": kids_close
                })

            if has_kids_close and _current_state["safety"]["kids_close"]:
                _upsert_alert(make_alert(
                    alert_id=payload.get("id", "safety_boundary"),
                    severity=payload.get("severity", "high"),
                    message=payload.get("message", "Kid is close to the safety boundary"),
                    source=payload.get("node_id", "safety"),
                    timestamp=timestamp,
                    alert_type=payload.get("alert_type", "boundary")
                ))

        if topic == LOCK_STATUS_TOPIC:
            has_scalar_data = raw_data not in (None, {}) and not isinstance(raw_data, dict)
            has_lock_value = has_scalar_data or any(key in data for key in ("lock_value", "lock_status", "locked", "lock")) or any(key in payload for key in ("lock_value", "lock_status", "locked", "lock"))

            _current_state["lock"].update({
                "node_id": payload.get("node_id"),
                "status": payload.get("status"),
                "last_updated": timestamp
            })

            if has_lock_value:
                lock_value = raw_data if has_scalar_data else data.get(
                    "lock_value",
                    data.get(
                        "lock_status",
                        data.get(
                            "locked",
                            data.get(
                                "lock",
                                payload.get("lock_value", payload.get("lock_status", payload.get("locked", payload.get("lock"))))
                            )
                        )
                    )
                )
                _current_state["lock"].update({
                    "lock_value": lock_value,
                    "lock_status": _lock_status(lock_value)
                })

        if "/control/" in topic:
            motion_detected = data.get("motion_detected", data.get("motion", payload.get("motion_detected")))
            sound_level = data.get("sound_level", data.get("sound", payload.get("sound_level")))
            cry_detected = data.get("cry_detected", payload.get("cry_detected"))

            if motion_detected is not None:
                _current_state["motion"].update({
                    "detected": bool(motion_detected),
                    "last_updated": timestamp
                })

            if sound_level is not None or cry_detected is not None:
                _current_state["sound"].update({
                    "level": sound_level,
                    "cry_detected": bool(cry_detected),
                    "last_updated": timestamp
                })

        if topic.endswith("/alert") or "/system/alert" in topic:
            _upsert_alert(make_alert(
                alert_id=payload.get("id"),
                severity=payload.get("severity", "high"),
                message=payload.get("message", "System alert triggered"),
                source=payload.get("node_id", payload.get("source", "system")),
                timestamp=timestamp,
                alert_type=payload.get("alert_type", "alert")
            ))

    return get_current_state()


# Returns a safe copy of the latest known system state.
def get_current_state():
    with _state_lock:
        return deepcopy(_current_state)


# Clears one alert by id, or clears all alerts when no id is provided.
def clear_alert(alert_id=None):
    with _state_lock:
        if alert_id is None:
            _current_state["alerts"] = []
            _current_state["safety"]["boundary_alert"] = False
            return None

        try:
            numeric_id = int(alert_id)
        except (TypeError, ValueError):
            numeric_id = alert_id

        _current_state["alerts"] = [alert for alert in _current_state["alerts"] if alert.get("id") != numeric_id]
        if not _current_state["alerts"]:
            _current_state["safety"]["boundary_alert"] = False
        return numeric_id
