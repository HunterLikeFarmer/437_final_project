from database import insert_command
from event_service import create_event
from mqtt_client import publish_command
from utils import now_iso, validate_required_fields


ALLOWED_COMMANDS = {
    "play_lullaby",
    "stop_lullaby",
    "lock",
    "unlock",
    "reset_alarm",
    "set_dashboard_mode"
}

ALLOWED_TARGETS = {"environment", "safety", "control", "system"}


# Validates a browser command, logs it, and publishes it to MQTT.
def handle_command(command_request):
    error = validate_required_fields(command_request, ["target", "command"])
    if error:
        return {"status": "error", "message": error}, 400

    target = command_request["target"]
    command = command_request["command"]

    if target not in ALLOWED_TARGETS:
        return {"status": "error", "message": f"Unsupported target: {target}"}, 400

    if command not in ALLOWED_COMMANDS:
        return {"status": "error", "message": f"Unsupported command: {command}"}, 400

    payload = {
        "command": command,
        "value": command_request.get("value"),
        "source": "web_dashboard",
        "timestamp": now_iso()
    }

    mqtt_target = "control" if target == "system" else target
    topic = f"smart_toddler/{mqtt_target}/command"
    was_sent = publish_command(topic, payload)

    insert_command(command, target, payload)
    create_event("web_dashboard", "command_sent", "low", f"Command sent: {command} -> {target}", payload)

    if not was_sent:
        return {
            "status": "queued",
            "target": target,
            "command": command,
            "message": "Command was logged, but MQTT publish did not confirm success"
        }, 202

    return {
        "status": "sent",
        "target": target,
        "command": command
    }, 200
