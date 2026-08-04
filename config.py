"""Configuration classes for TerminalPalette.

Values come from the environment. run.py and passenger_wsgi.py load .env via
python-dotenv before importing this module, so os.environ is already populated
by the time these classes are read.
"""

import os


class Config:
    """Base configuration. Shared by all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY")
    FLASK_ENV = os.environ.get("FLASK_ENV", "production")

    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Local development."""

    DEBUG = True
    # Convenience only: lets the dev server run without a .env present.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-key-not-for-production")


class ProductionConfig(Config):
    """Deployed on DreamHost via Passenger."""

    DEBUG = False


# Looked up by name in app/__init__.py:create_app().
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
