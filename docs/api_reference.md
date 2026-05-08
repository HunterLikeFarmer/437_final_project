# API Reference

Base URL:

```text
http://localhost:5000
```

## GET /api/health

Returns backend health and MQTT connection status.

## GET /api/status

Returns the latest in-memory dashboard state.

The environmental node updates room readings through `smart_toddler/environment/status`, the safety node updates kid proximity through `smart_toddler/safety/status`, and the lock node updates lock state through `smart_toddler/lock/status`.

```json
{
  "environment": {
    "node_id": "environment_1",
    "status": "ok",
    "temperature": 22,
    "humidity": 45,
    "light": 1200
  },
  "motion": {
    "detected": true
  },
  "sound": {
    "level": 512
  },
  "safety": {
    "node_id": "safety_1",
    "status": "ok",
    "kids_close": true,
    "boundary_alert": true
  },
  "lock": {
    "node_id": "lock_1",
    "status": "ok",
    "lock_value": 0,
    "lock_status": "unlocked"
  }
}
```

## GET /api/events?limit=50

Returns recent event log entries from SQLite.

## POST /api/commands

Request:

```json
{
  "target": "lock",
  "command": "lock",
  "value": true
}
```

Response:

```json
{
  "status": "sent",
  "target": "lock",
  "command": "lock"
}
```

The backend publishes lock commands to `smart_toddler/lock/command`.

Lock payload sent over MQTT:

```json
{
  "command": "lock",
  "value": true,
  "source": "web_dashboard",
  "timestamp": "2026-05-07T12:02:00Z"
}
```

Unlock payload sent over MQTT:

```json
{
  "command": "unlock",
  "value": false,
  "source": "web_dashboard",
  "timestamp": "2026-05-07T12:03:00Z"
}
```

## POST /api/reset-alert

Request:

```json
{
  "alert_id": 1
}
```

Use an empty body to clear all active alerts.
