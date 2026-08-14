# Deployment

Production setup for [terminalpalette.org](https://terminalpalette.org).

> **`app.cgi` and `.htaccess` in this repo were reconstructed, not copied from
> the server.** They were written to match the setup described here, but the
> live files were not available when they were added. Diff them against
> `~/terminalpalette.org/app.cgi` and `~/terminalpalette.org/.htaccess` on the
> server and reconcile any difference **before** relying on them or letting a
> `git pull` overwrite the working copies.

## Host

| | |
|---|---|
| Provider | DreamHost, shared hosting |
| User | `dangavin` |
| Server | `iad1-shared-b7-15.dreamhost.com` |
| Path | `/home/dangavin/terminalpalette.org` |
| Live URL | https://terminalpalette.org |
| Domains | `.com` and `.net` redirect to `.org` |

## How requests are served

**CGI, not Passenger.** `.htaccess` routes every request that is not an
existing file or directory to `app.cgi`, which runs the Flask app through
`wsgiref.handlers.CGIHandler`.

`passenger_wsgi.py` is present in the repo and is **not used in production**.
Its `INTERPRETER` constant is still an unset `TODO`; it would not work if
Passenger were enabled. It is kept only as a record of the original intent.
Do not assume from its presence that Passenger is running.

Request path:

```
request → .htaccess (mod_rewrite) → app.cgi → wsgi.py → app/__init__.py:create_app()
```

Static assets live under `app/static/`, which is not their public URL path, so
they do not match the "existing file" condition and are served by Flask.

## Python and dependencies

| | |
|---|---|
| Interpreter | `/usr/bin/python3` — the system Python, **3.12.3** |
| Virtualenv | none; packages are installed into the account's user site-packages |

Install a dependency with:

```bash
pip3 install --user --break-system-packages <package>
```

`--break-system-packages` is required: the system Python is Debian-managed and
PEP 668 marks it externally managed, so plain `--user` is refused. The flag
sounds alarming but only permits writing to `~/.local/`; nothing system-wide is
touched.

Runtime dependencies are exactly the two in `requirements.txt`:

```
Flask
python-dotenv
```

## Environment

`.env` lives at `/home/dangavin/terminalpalette.org/.env`. It is **gitignored,
exists only on the server, and is never in the repo.**

```
FLASK_ENV=production
SECRET_KEY=<random value>
```

Permissions: `chmod 600 .env` — readable only by `dangavin`.

`create_app()` defaults to production when `FLASK_ENV` is unset, so a missing
`.env` cannot silently put the site into debug mode. `SECRET_KEY` has no
production fallback, so it must be present.

Generate a new key with:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Deploying

```bash
ssh dangavin@iad1-shared-b7-15.dreamhost.com
cd ~/terminalpalette.org && git pull origin main
```

**No restart is needed.** CGI spawns a fresh process per request, so the next
request picks up the new code. There is no worker to signal, no `touch
tmp/restart.txt`, no cache to clear.

Before deploying, from the repo root:

```bash
python3 validate_themes.py
```

It must print `All checks passed.` A failure means the theme data is
inconsistent and the site should not be deployed.

After deploying, confirm `app.cgi` is still executable — a fresh clone or a
mode change will break the site with a 500:

```bash
chmod 755 app.cgi
```

## Logs

```
~/logs/terminalpalette.org/http/error.log
```

Python tracebacks from a failing CGI process land here. `tail -f` it while
reproducing a 500.

## Local development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 run.py
```

Runs at http://127.0.0.1:5001. **Port 5001, not 5000** — 5000 is taken by
FIXReader and by the macOS AirPlay Receiver.

Local development uses a virtualenv; the server does not. That difference is
deliberate: shared hosting has no venv, so `app.cgi` adds the user
site-packages directory to `sys.path` explicitly.

## Theme rotation

Rotation is a **data-only** operation. There is no scheduler, no cron job, no
date logic anywhere in the application — rotating themes means editing values
in `app/themes.py` and deploying.

### The three fields

| Field | Values | Meaning |
|---|---|---|
| `active` | `True` / `False` | **The only thing that decides what renders.** `active_themes()` is the sole list the UI sees. |
| `rotation` | `core`, `seasonal`, `limited`, `archived` | *Why* the theme is in the collection. Metadata only — never displayed, filtered on, or searchable. |
| `season` | `permanent`, `spring`, `summer`, `autumn`, `winter` | *When* a seasonal theme surfaces. Metadata only. |

`rotation` and `season` are independent and answer different questions. A
theme can be `rotation: seasonal` with `season: winter`, or `rotation: core`
with `season: permanent`. Neither one causes anything to happen on its own.

### Rotating a theme out

Set `active=False` and give it a `rotation` of `seasonal` or `archived`.

**Never delete a theme.** Deletion loses the palette, its contrast record, and
its `display_order` slot. An inactive theme keeps its slot and comes back
exactly where it was, which is why `display_order` is unique and ascending but
not contiguous.

The validator enforces this: an inactive theme whose `rotation` is `core` or
`limited` is an error, because a theme that is not rendering for no recorded
reason is a mistake rather than a rotation.

```python
_theme(5, "graphite", "Graphite",
       ...,
       "Pencil graphite", "May 18, 2025", featured=True,
       active=False, season="winter", rotation="seasonal"),
```

### Rotating a theme back in

Set `active=True`. Before doing so, check it against the live collection —
palettes that were distinct a year ago may collide with themes added since:

```bash
python3 validate_themes.py --similar --include-inactive
```

Anything landing in the STRONG or PROBABLE band against an active theme should
not come back without a redesign.

### Updating `EXPECTED_ACTIVE`

`validate_themes.py` holds a deliberate tripwire:

```python
EXPECTED_ACTIVE = 37
```

**It is stated, not derived.** Any change to the number of active themes fails
validation until this constant is updated to match. That is the point: it
catches an accidental addition, removal, or `active` flag flipped by mistake.

So a rotation is always at least two edits:

1. the `active` / `rotation` / `season` values in `app/themes.py`
2. `EXPECTED_ACTIVE` in `validate_themes.py`

Other floors that can block a rotation:

- **`ENV_FLOOR = 3`** — every environment must keep at least three *active*
  themes. A rotated-out theme keeps its environment recommendation but no
  longer counts toward coverage.
- Every mood must keep at least two active themes.

### Quarterly checklist

```bash
# 1. edit app/themes.py — active / rotation / season
# 2. update EXPECTED_ACTIVE in validate_themes.py
python3 validate_themes.py                              # must pass
python3 validate_themes.py --table                      # contrast review
python3 validate_themes.py --similar                    # live collection
# 3. commit, then:
ssh dangavin@iad1-shared-b7-15.dreamhost.com
cd ~/terminalpalette.org && git pull origin main
```

`python3 validate_themes.py` must pass before every deploy, rotation or not.
