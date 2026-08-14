"""Routes for TerminalPalette."""

from flask import Blueprint, Response, abort, render_template

from app.putty import reg_filename, reg_for_theme
from app.themes import active_themes, build_moods, initial_theme

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template(
        "index.html",
        page="explore",
        themes=active_themes(),
        moods=build_moods(),
        initial=initial_theme(),
    )


# `page` drives the active nav underline in base.html. Passing it from the
# view keeps the nav out of the templates' hands and avoids relying on a
# child-template `set` reaching the parent.
#
# The article pages carry the same sidebar and details panel, so they need the
# collection and a seed theme too. They pass no `moods`: without a theme grid
# there is nothing to filter, so the sidebar omits that list. The seed is the
# display-order first theme; app.js swaps in the stored selection if there is
# one. These pages never shuffle.
def _article(template, page):
    return render_template(
        template,
        page=page,
        themes=active_themes(),
        initial=initial_theme(),
    )


@main.route("/guide")
def guide():
    return _article("guide.html", "guide")


@main.route("/about")
def about():
    return _article("about.html", "about")


@main.route("/lookbook")
def lookbook():
    return _article("lookbook.html", "lookbook")


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
