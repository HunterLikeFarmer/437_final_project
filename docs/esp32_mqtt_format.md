# ESP32 MQTT Message Format Guide

This guide explains the MQTT format that ESP32 or Arduino device code should follow when communicating with the Smart Toddler Dashboard.

## Broker Settings

Use the same MQTT broker that the Flask backend uses.

```text
Host: backend machine IP address or localhost during local testing
Port: 1883
Authentication: none for the local class project setup
```

Each ESP32 should use a unique MQTT client id, such as:

```text
smart_toddler_environment_1
smart_toddler_safety_1
smart_toddler_lock_1
smart_toddler_control_1
```

## Topic Pattern

All topics should follow this structure:

```text
smart_toddler/<node>/<message_type>
```

Valid node names:

```text
environment
safety
lock
control
system
```

Common message types:

```text
status
command
alert
heartbeat
```

## Topics The Current Backend Listens To

The current backend and frontend expect the environmental, safety, and lock nodes to publish these topics:

```text
smart_toddler/environment/status
smart_toddler/safety/status
smart_toddler/lock/status
```

The environmental payload stays the same as `ESP_Environmental_Node.ino`. The safety payload should contain only whether the kid got close. The lock payload should contain only whether the lock is locked.

## Topics ESP32 Devices Should Publish

Environment node:

```text
smart_toddler/environment/status
```

Safety node:

```text
smart_toddler/safety/status
```

Lock node:

```text
smart_toddler/lock/status
```

Control node:

```text
smart_toddler/control/status
```

Any node can publish an alert:

```text
smart_toddler/system/alert
```

Any node can publish a heartbeat:

```text
smart_toddler/system/heartbeat
```

## Topics ESP32 Devices Should Subscribe To

Environment node:

```text
smart_toddler/environment/command
```

Lock node:

```text
smart_toddler/lock/command
```

Control node:

```text
smart_toddler/control/command
```

## Required JSON Rules

All MQTT payloads must be valid JSON.

Use these common fields whenever possible:

```json
{
  "node_id": "environment_1",
  "timestamp": "2026-05-07T12:00:00Z",
  "status": "ok",
  "data": {}
}
```

Field meanings:

| Field | Required | Meaning |
|---|---|---|
| `node_id` | Yes | Unique name of the ESP32 node |
| `timestamp` | Recommended | Time the message was created |
| `status` | Recommended | Device state, usually `ok`, `online`, `ready`, or `error` |
| `data` | Yes for status messages | Sensor values or device state |

If the ESP32 does not have accurate time, it may omit `timestamp`. The backend will create its own timestamp.

## Environment Status Payload

Publish to:

```text
smart_toddler/environment/status
```

Payload:

```json
{
  "node_id": "environment_1",
  "status": "ok",
  "data": {
    "temperature": 22.5,
    "humidity": 44,
    "light_level": 310,
    "sound_level": 120,
    "motion_detected": 1
  }
}
```

Expected units:

| Field | Unit |
|---|---|
| `temperature` | Celsius |
| `humidity` | Percent |
| `light_level` | Raw sensor value or lux, but keep it consistent |
| `sound_level` | Raw analog sound sensor value |
| `motion_detected` | Digital PIR value, usually `0` or `1` |

## Safety Status Payload

Publish to:

```text
smart_toddler/safety/status
```

Payload:

```json
{
  "node_id": "safety_1",
  "status": "ok",
  "data": {
    "kids_close": 1
  }
}
```

Field meanings:

| Field | Meaning |
|---|---|
| `kids_close` | `1` means the kid is close to the safety boundary, `0` means clear |

The `data` object for `smart_toddler/safety/status` should contain only this one field. The backend also accepts the compact form `"data": 1` or `"data": 0`.

## Lock Status Payload

Publish to:

```text
smart_toddler/lock/status
```

Payload:

```json
{
  "node_id": "lock_1",
  "status": "ok",
  "data": {
    "lock_value": 0
  }
}
```

Field meanings:

| Field | Meaning |
|---|---|
| `lock_value` | `1` means locked, `0` means unlocked |

The `data` object for `smart_toddler/lock/status` should contain only this one field. The backend also accepts the compact form `"data": 1` or `"data": 0`.

The backend converts `lock_value` into dashboard text:

```text
1 -> locked
0 -> unlocked
```

## Control Status Payload

Publish motion, sound, or command acknowledgment state to:

```text
smart_toddler/control/status
```

Payload:

```json
{
  "node_id": "control_1",
  "timestamp": "2026-05-07T12:00:10Z",
  "status": "ok",
  "data": {
    "motion_detected": true,
    "sound_level": 62,
    "cry_detected": false
  }
}
```

## Alert Payload

Publish urgent alerts to:

```text
smart_toddler/system/alert
```

Payload:

```json
{
  "node_id": "safety_1",
  "timestamp": "2026-05-07T12:01:10Z",
  "severity": "high",
  "alert_type": "boundary",
  "message": "Safety boundary alert triggered"
}
```

Allowed `severity` values:

```text
low
medium
high
critical
```

## Heartbeat Payload

Publish periodically to:

```text
smart_toddler/system/heartbeat
```

Payload:

```json
{
  "node_id": "environment_1",
  "timestamp": "2026-05-07T12:00:30Z",
  "status": "online"
}
```

A heartbeat every 10 to 30 seconds is reasonable for this project.

## Command Payloads From Backend

ESP32 devices should subscribe to their command topic and expect payloads like this:

```json
{
  "command": "unlock",
  "value": false,
  "source": "web_dashboard",
  "timestamp": "2026-05-07T12:02:00Z"
}
```

For the lock feature, the lock edge device should subscribe to:

```text
smart_toddler/lock/command
```

Lock command:

```json
{
  "command": "lock",
  "value": true,
  "source": "web_dashboard",
  "timestamp": "2026-05-07T12:02:00Z"
}
```

Unlock command:

```json
{
  "command": "unlock",
  "value": false,
  "source": "web_dashboard",
  "timestamp": "2026-05-07T12:03:00Z"
}
```

The ESP32 should treat `command` as the primary instruction. The `value` field is the desired lock state: `true` means locked and `false` means unlocked.

Supported commands:

| Command | Target Topic | Meaning |
|---|---|---|
| `play_lullaby` | `smart_toddler/control/command` | Start playing a lullaby |
| `stop_lullaby` | `smart_toddler/control/command` | Stop the lullaby |
| `lock` | `smart_toddler/lock/command` | Lock the safety device |
| `unlock` | `smart_toddler/lock/command` | Unlock the safety device |
| `reset_alarm` | `smart_toddler/control/command` | Reset local alarm output |

## Command Acknowledgment

After receiving a command, the ESP32 should publish an acknowledgment to its status topic.

Example:

```json
{
  "node_id": "lock_1",
  "timestamp": "2026-05-07T12:02:01Z",
  "command": "unlock",
  "status": "received"
}
```

After a lock state change, publish the normal lock status again so the dashboard button follows the actual device state:

```json
{
  "node_id": "lock_1",
  "status": "ok",
  "data": {
    "lock_value": 1
  }
}
```

For failed commands:

```json
{
  "node_id": "lock_1",
  "timestamp": "2026-05-07T12:02:01Z",
  "command": "unlock",
  "status": "error",
  "message": "Lock motor did not respond"
}
```

## ESP32 Implementation Checklist

- Connect to Wi-Fi before connecting to MQTT.
- Reconnect to MQTT automatically if the connection drops.
- Publish only valid JSON strings.
- Use the exact topic names shown in this guide.
- Keep `node_id` stable for each physical device.
- Publish status after startup and after important sensor changes.
- Subscribe to the command topic that matches the node type.
- Publish a command acknowledgment after receiving a command.
