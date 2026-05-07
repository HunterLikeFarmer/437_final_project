import json

import paho.mqtt.client as mqtt

from event_service import create_event, process_mqtt_event
from state_store import update_state_from_mqtt
from utils import now_iso, safe_json_loads


_mqtt_client = None
_mqtt_connected = False


# Creates the MQTT client, connects to the broker, and starts its background loop.
def start_mqtt_client(app):
    global _mqtt_client

    client = mqtt.Client(client_id=app.config["MQTT_CLIENT_ID"])
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.user_data_set(app)
    _mqtt_client = client

    try:
        client.connect(app.config["MQTT_HOST"], app.config["MQTT_PORT"], keepalive=60)
        client.loop_start()
        create_event("backend", "system", "low", "MQTT client started")
    except Exception as error:
        create_event("backend", "system_error", "medium", f"MQTT connection failed: {error}")

    return client


# Subscribes to dashboard topics after a successful MQTT broker connection.
def on_connect(client, userdata, flags, rc):
    global _mqtt_connected
    _mqtt_connected = rc == 0

    if rc == 0:
        client.subscribe("smart_toddler/+/status")
        client.subscribe("smart_toddler/system/alert")
        client.subscribe("smart_toddler/system/heartbeat")
        create_event("mqtt", "system", "low", "Connected to MQTT broker")
    else:
        create_event("mqtt", "system_error", "medium", f"MQTT connect returned code {rc}")


# Marks the MQTT connection as offline when the broker disconnects.
def on_disconnect(client, userdata, rc):
    global _mqtt_connected
    _mqtt_connected = False
    create_event("mqtt", "system_error", "medium", f"Disconnected from MQTT broker with code {rc}")


# Handles incoming MQTT messages by updating state and logging events.
def on_message(client, userdata, msg):
    payload = safe_json_loads(msg.payload)
    topic = msg.topic
    update_state_from_mqtt(topic, payload)
    process_mqtt_event(topic, payload)


# Publishes a command payload to an MQTT topic for a device node.
def publish_command(topic, payload):
    if "timestamp" not in payload:
        payload["timestamp"] = now_iso()

    if _mqtt_client is None:
        create_event("backend", "system_error", "medium", "MQTT client not available for command publish", payload)
        return False

    result = _mqtt_client.publish(topic, json.dumps(payload))
    success = result.rc == mqtt.MQTT_ERR_SUCCESS
    if not success:
        create_event("backend", "system_error", "medium", f"Failed to publish MQTT command to {topic}", payload)
    return success


# Reports whether the backend is currently connected to MQTT.
def is_mqtt_connected():
    return _mqtt_connected
