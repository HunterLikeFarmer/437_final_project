# Smart Toddler Care & Safety Dashboard

A local dashboard for toddler room monitoring. ESP32 or Arduino nodes publish sensor data to MQTT. A Flask backend receives those MQTT messages, stores recent events in SQLite, and serves a browser dashboard.

## Project Structure

```text
backend/   Flask API, MQTT client, state store, SQLite helpers
frontend/  Browser dashboard built with HTML, CSS, and vanilla JavaScript
mqtt/      Mosquitto config plus topic and sample message docs
data/      Runtime SQLite database location
docs/      Architecture and API notes
```

## Setup

Create a virtual environment and install Python dependencies:

```bash
.venv/Scripts/activate
pip install -r requirements.txt
```

## Start MQTT Broker

With Mosquitto installed:

```bash
mosquitto -c mqtt/mosquitto.conf
```

## Start Flask Backend

```bash
python backend/app.py
```

Open the dashboard at:

```text
http://localhost:5000
```

The frontend can also be opened directly from `frontend/index.html`. When opened as a local file, it will call `http://localhost:5000` for API requests.

## API

- `GET /api/health`
- `GET /api/status`
- `GET /api/events?limit=50`
- `POST /api/commands`
- `POST /api/reset-alert`

See `docs/api_reference.md` for examples.

## MQTT Topics

The backend subscribes to:

```text
smart_toddler/environment/status
smart_toddler/safety/status
smart_toddler/lock/status
smart_toddler/system/alert
smart_toddler/system/heartbeat
```

The backend publishes commands to:

```text
smart_toddler/<node>/command
```

See `mqtt/topics.md` and `mqtt/sample_messages.md` for details.

## Troubleshooting

- If the dashboard says `Offline`, make sure Flask is running on port `5000`.
- If MQTT commands are only `queued`, make sure Mosquitto is running on port `1883`.
- If the database is missing, start Flask once; it creates `data/app.db` automatically.
