"""Application factory for TerminalPalette."""

import os

from flask import Flask

from config import config_by_name


def create_app(config_name=None):
    """Build and return a configured Flask application.

    config_name: "development" or "production". Falls back to FLASK_ENV, then
    to "production" so an unset environment never lands in debug mode.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "production")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["production"]))

    from app.routes import main

    app.register_blueprint(main)

    return app
