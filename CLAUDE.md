# TerminalPalette

Flask site for TerminalPalette.org. Currently a bare scaffold: one route
serving one placeholder page, no design applied yet.

## Stack

- Python 3 / Flask (application factory + blueprint)
- Jinja2 templates (ships with Flask)
- python-dotenv for local environment loading
- No database, no JavaScript, no CSS framework, no build step

Dependencies are exactly Flask and python-dotenv. See `requirements.txt`.

## Deployment

DreamHost shared hosting via Passenger.

- `passenger_wsgi.py` — Passenger entry point. **Contains a TODO: the Python
  interpreter path must be confirmed on the server before deployment works.**
  It is deliberately left unset rather than guessed.
- `wsgi.py` — exposes `application` for any WSGI server; imported by
  `passenger_wsgi.py`.
- `run.py` — local dev server only, port 5001 (5000 is taken by FIXReader and
  macOS AirPlay Receiver).

## Layout

```
TerminalPalette/
  CLAUDE.md
  .gitignore
  .env.example          # copy to .env; .env is gitignored
  requirements.txt
  config.py             # Config / DevelopmentConfig / ProductionConfig
  passenger_wsgi.py     # DreamHost Passenger entry point
  wsgi.py               # WSGI `application` object
  run.py                # local dev server, port 5001
  app/
    __init__.py         # create_app(config_name)
    routes.py           # blueprint `main`, single route "/" -> index.html
    templates/
      base.html         # semantic skeleton, unstyled
      index.html        # extends base, placeholder <h1>
    static/
      css/              # empty (.gitkeep)
      img/              # empty (.gitkeep)
```

## Theme data

`app/themes.py` is the single source of truth for all 43 themes. It is
rendered into the template and serialised once into a JSON script block for
the client — JavaScript holds no second copy.

Each theme carries a **two-tier colour model**, which is intentional and must
not be collapsed: `palette` is the decorative three-swatch strip on the card;
`background` / `foreground` / `cursor` are the functional PuTTY values shown
in the details panel. They may differ. Functional values are held to WCAG
minimums — foreground 4.5:1 and cursor 3:1 against background.

**Seasonal rotation.** Every theme carries `active`, `season`
(`permanent` / `spring` / `summer` / `autumn` / `winter`) and `display_order`.
Only `active` themes render, ordered by `display_order`. There is no
scheduling logic, no date reading, and no visible season filter — rotating a
set later means editing those data values only.

Run `python validate_themes.py --table` after any theme edit. It checks
schema, uniqueness, RGB/hex agreement, moods, seasons, and contrast.

## Configuration

`config.py` reads `SECRET_KEY` and `FLASK_ENV` from the environment.
`create_app()` selects a config class by name, defaulting to production when
`FLASK_ENV` is unset — an unconfigured environment should never land in debug
mode. `DevelopmentConfig` carries a throwaway `SECRET_KEY` fallback so the dev
server runs without a `.env`; production has no such fallback.

## Local development

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py            # http://127.0.0.1:5001
```

## Rules

These constrain work in this repo until lifted.

- **No visual design.** No color scheme, no layout, no styling beyond plain
  unstyled semantic HTML. The design reference is not available yet.
- **No dependencies** beyond Flask and python-dotenv.
- **No JavaScript, build tooling, or CSS frameworks.**
- **No pages or routes** beyond the single index route.
- **No git commands.** The repository owner handles git directly.
- **Ask when a decision is genuinely ambiguous** rather than guessing.

## Decisions Log

<!-- Intentionally empty. Record notable decisions here as they are made. -->
