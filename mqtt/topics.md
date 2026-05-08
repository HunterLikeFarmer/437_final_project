# MQTT Topics

Topic pattern:

```text
smart_toddler/<node>/<message_type>
```

Backend subscriptions:

```text
smart_toddler/environment/status
smart_toddler/safety/status
smart_toddler/system/alert
smart_toddler/system/heartbeat
```

Backend command publishing:

```text
smart_toddler/<node>/command
```

Common topics:

| Topic | Direction | Purpose |
|---|---|---|
| `smart_toddler/environment/status` | Device to backend | Temperature, humidity, light, sound, and motion updates |
| `smart_toddler/safety/status` | Device to backend | Kid proximity and lock status |
| `smart_toddler/control/status` | Device to backend | Motion, sound, and command acknowledgments |
| `smart_toddler/environment/command` | Backend to device | Environment node commands |
| `smart_toddler/safety/command` | Backend to device | Safety node commands |
| `smart_toddler/control/command` | Backend to device | Lullaby, reset, and control hub commands |
| `smart_toddler/system/alert` | Device to backend | Alert notification |
| `smart_toddler/system/heartbeat` | Device to backend | Device alive check |
