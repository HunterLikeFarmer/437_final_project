# API Reference

Base URL:

```text
http://localhost:5000
```

## GET /api/health

Returns backend health and MQTT connection status.

## GET /api/status

Returns the latest in-memory dashboard state.

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
