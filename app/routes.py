"""Routes for TerminalPalette."""

from flask import Blueprint, render_template

from app.themes import MOODS, THEMES

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html", themes=THEMES, moods=MOODS)
