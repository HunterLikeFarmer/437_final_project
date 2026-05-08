# Sample MQTT Messages

## Environment Status

Topic:

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

## Safety Status

Topic:

```text
smart_toddler/safety/status
```

Payload:

```json
{
  "node_id": "safety_1",
  "status": "ok",
  "data": {
    "kids_close": 1,
    "lock_status": 0
  }
}
```

`kids_close` should be `1` when the kid is close to the safety boundary and `0` otherwise.

`lock_status` should be `1` for locked and `0` for unlocked.

## Alert

Topic:

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

## Command

Topic:

```text
smart_toddler/safety/command
```

Payload:

```json
{
  "command": "unlock",
  "value": true,
  "source": "web_dashboard",
  "timestamp": "2026-05-07T12:02:00Z"
}
```
