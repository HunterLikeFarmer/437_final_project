from flask import jsonify, request, send_from_directory

from command_service import handle_command
from event_service import get_recent_events
from mqtt_client import is_mqtt_connected
from state_store import clear_alert, get_current_state
from utils import make_error_response


# Registers all frontend static routes and JSON API routes on the Flask app.
def register_routes(app):
    @app.get("/")
    # Serves the dashboard HTML page from the frontend folder.
    def index():
        return send_from_directory(app.config["FRONTEND_FOLDER"], "index.html")

    @app.get("/css/<path:filename>")
    # Serves frontend CSS files through Flask.
    def frontend_css(filename):
        return send_from_directory(f"{app.config['FRONTEND_FOLDER']}/css", filename)

    @app.get("/js/<path:filename>")
    # Serves frontend JavaScript files through Flask.
    def frontend_js(filename):
        return send_from_directory(f"{app.config['FRONTEND_FOLDER']}/js", filename)

    @app.get("/api/health")
    # Returns backend health and MQTT connection status.
    def health():
        return jsonify({
            "status": "ok",
            "service": "smart-toddler-backend",
            "mqtt_connected": is_mqtt_connected()
        })

    @app.get("/api/status")
    # Returns the latest in-memory system state for dashboard polling.
    def status():
        return jsonify(get_current_state())

    @app.get("/api/events")
    # Returns recent event logs from SQLite for the event panel.
    def events():
        try:
            limit = min(max(int(request.args.get("limit", 50)), 1), 200)
        except ValueError:
            return make_error_response("limit must be a number", 400)

        return jsonify({"events": get_recent_events(limit)})

    @app.post("/api/commands")
    # Accepts a dashboard command and forwards it through the command service.
    def commands():
        data = request.get_json(silent=True) or {}
        payload, status_code = handle_command(data)
        return jsonify(payload), status_code

    @app.post("/api/reset-alert")
    # Clears one active alert or all active alerts.
    def reset_alert():
        data = request.get_json(silent=True) or {}
        alert_id = clear_alert(data.get("alert_id"))
        return jsonify({
            "status": "cleared",
            "alert_id": alert_id
        })
