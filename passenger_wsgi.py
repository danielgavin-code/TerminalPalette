"""DreamHost Passenger entry point.

Passenger looks for this file at the application root and imports the
module-level `application` object from it.

------------------------------------------------------------------------------
TODO — CONFIRM THE INTERPRETER PATH ON THE SERVER BEFORE THIS WILL WORK.
------------------------------------------------------------------------------
Passenger will otherwise run this under the system Python, which does not have
Flask installed. The path below is intentionally left unset rather than guessed.

On the server, activate the virtualenv and run:

    which python3

Then set INTERPRETER to that absolute path, e.g. something under
/home/<user>/<domain>/venv/bin/. Do not copy a path from another machine or
another site — confirm it on this server.

The re-exec block below is the standard DreamHost pattern: if the running
interpreter is not the intended one, replace the process with the correct one.
------------------------------------------------------------------------------
"""

import os
import sys

# TODO: set to the absolute path of the venv's python3 on the server.
INTERPRETER = None

if INTERPRETER and sys.executable != INTERPRETER:
    os.execl(INTERPRETER, INTERPRETER, *sys.argv)

sys.path.insert(0, os.path.dirname(__file__))

from wsgi import application  # noqa: E402,F401  (Passenger imports this name)
