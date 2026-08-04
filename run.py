"""Local development server.

Port 5001, not 5000: 5000 is taken by FIXReader and macOS AirPlay Receiver.

    python run.py
"""

from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402  (must follow load_dotenv)

# Explicitly development: this file is only ever the local dev server, and
# create_app() otherwise defaults to production when FLASK_ENV is unset.
app = create_app("development")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
