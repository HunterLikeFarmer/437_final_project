# API Reference

Base URL:

```text
http://localhost:5000
```

## GET /api/health

Returns backend health and MQTT connection status.

## GET /api/status

Returns the latest in-memory dashboard state.

The environmental node updates room readings through `smart_toddler/environment/status`, and the safety node updates boundary and lock state through `smart_toddler/safety/status`.

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
    "boundary_alert": true,
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
  "target": "safety",
  "command": "unlock",
  "value": true
}
```

Response:

```json
{
  "status": "sent",
  "target": "safety",
  "command": "unlock"
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
