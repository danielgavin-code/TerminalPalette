#!/usr/bin/python3
# =============================================================================
# CGI entry point for TerminalPalette on DreamHost shared hosting.
#
# THE ABSOLUTE PATHS BELOW ARE SERVER-SPECIFIC. If the deploy path, the account
# username, or the system Python version changes, APP_ROOT and USER_SITE must
# be updated to match, and the shebang above must point at the interpreter that
# actually exists on the server. Nothing here is portable between hosts.
#
# Current values match:
#   host    iad1-shared-b7-15.dreamhost.com
#   user    dangavin
#   path    /home/dangavin/terminalpalette.org
#   python  /usr/bin/python3  (3.12.3, system interpreter, no virtualenv)
#
# This file must be executable on the server: chmod 755 app.cgi
#
# NOTE: passenger_wsgi.py is also in this repo and is NOT used in production.
# Requests reach this file through .htaccess. See DEPLOYMENT.md.
# =============================================================================

import os
import sys

APP_ROOT = "/home/dangavin/terminalpalette.org"

# Dependencies are installed with `pip3 install --user`, which lands in the
# account's user site-packages rather than a virtualenv. CGI does not always
# inherit a HOME that lets Python find it, so it is added explicitly.
USER_SITE = os.path.expanduser("~/.local/lib/python3.12/site-packages")

for path in (APP_ROOT, USER_SITE):
    if path not in sys.path:
        sys.path.insert(0, path)

from wsgiref.handlers import CGIHandler  # noqa: E402

# wsgi.py loads .env and builds the app; FLASK_ENV there selects the config.
from wsgi import application  # noqa: E402

CGIHandler().run(application)
