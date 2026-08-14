"""Routes for TerminalPalette."""

from flask import Blueprint, Response, abort, render_template

from app.putty import reg_filename, reg_for_theme
from app.themes import active_themes, build_moods, initial_theme

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template(
        "index.html",
        themes=active_themes(),
        moods=build_moods(),
        initial=initial_theme(),
    )


@main.route("/themes/<theme_id>.reg")
def theme_reg(theme_id):
    """A PuTTY session registry file for one theme.

    Only active themes are downloadable — the set the page can offer. The
    body is built per request and held in memory; nothing is written to disk.
    """
    theme = next((t for t in active_themes() if t["id"] == theme_id), None)
    if theme is None:
        abort(404)

    return Response(
        reg_for_theme(theme),
        mimetype="application/octet-stream",
        headers={
            "Content-Disposition":
                'attachment; filename="{}"'.format(reg_filename(theme)),
            "Cache-Control": "no-store",
        },
    )
