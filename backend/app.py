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


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(
        host=flask_app.config["FLASK_HOST"],
        port=flask_app.config["FLASK_PORT"],
        debug=True,
        use_reloader=False
    )
