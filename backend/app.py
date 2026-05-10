import argparse
import socket

from flask import Flask
from flask_cors import CORS

from config import Config
from database import init_db
from mqtt_client import start_mqtt_client
from routes import register_routes


# Creates and configures the Flask app, database, routes, and MQTT client.
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    init_db(app.config["DATABASE_PATH"])
    register_routes(app)
    start_mqtt_client(app)

    return app


def parse_args():
    parser = argparse.ArgumentParser(description="Run the Smart Toddler Flask dashboard.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--testing",
        action="store_true",
        help="Host only on this computer at localhost for local testing."
    )
    mode_group.add_argument(
        "--production",
        action="store_true",
        help="Host on all network interfaces so other computers on the LAN can access it."
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Override the Flask port."
    )
    return parser.parse_args()


def get_lan_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return None


def get_runtime_options(app, args):
    host = app.config["FLASK_HOST"]
    port = args.port or app.config["FLASK_PORT"]
    debug = app.config["FLASK_DEBUG"]

    if args.testing:
        host = "127.0.0.1"
        debug = True
    elif args.production:
        host = "0.0.0.0"
        debug = False

    return host, port, debug


def print_startup_urls(host, port):
    print(f"Local dashboard: http://localhost:{port}")

    if host == "0.0.0.0":
        lan_ip = get_lan_ip()
        if lan_ip:
            print(f"LAN dashboard:   http://{lan_ip}:{port}")
        else:
            print(f"LAN dashboard:   http://<this-computer-ip>:{port}")


if __name__ == "__main__":
    args = parse_args()
    flask_app = create_app()
    host, port, debug = get_runtime_options(flask_app, args)
    print_startup_urls(host, port)
    flask_app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=False
    )
