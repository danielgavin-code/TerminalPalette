"""WSGI entry point.

Exposes the module-level `application` object that WSGI servers expect.
passenger_wsgi.py imports from here.
"""

from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402  (must follow load_dotenv)

application = create_app()
