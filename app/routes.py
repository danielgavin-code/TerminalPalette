"""Routes for TerminalPalette."""

from flask import Blueprint, render_template

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
