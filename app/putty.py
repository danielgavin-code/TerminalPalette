"""PuTTY session registry file generation.

Built in memory from the theme data on every request — nothing is written to
disk and nothing is cached.

The site's premise is three functional colours per theme, so only PuTTY's six
foreground/background/cursor slots are theme-driven. Colour6 through Colour21
are PuTTY's own ANSI defaults, reproduced verbatim: inventing an ANSI ramp
from a three-colour palette would be guesswork.
"""

# .reg files are a Windows format; regedit expects CRLF regardless of the
# platform that produced the file.
CRLF = "\r\n"

REG_HEADER = "Windows Registry Editor Version 5.00"
SESSIONS_KEY = r"HKEY_CURRENT_USER\Software\SimonTatham\PuTTY\Sessions"

# PuTTY's defaults for Colour6-21, in PuTTY's own order: ANSI black, black
# bold, red, red bold, green, green bold, yellow, yellow bold, blue, blue
# bold, magenta, magenta bold, cyan, cyan bold, white, white bold.
ANSI_DEFAULTS = (
    "0,0,0", "85,85,85",
    "187,0,0", "255,85,85",
    "0,187,0", "85,255,85",
    "187,187,0", "255,255,85",
    "0,0,187", "85,85,255",
    "187,0,187", "255,85,255",
    "0,187,187", "85,255,255",
    "187,187,187", "255,255,255",
)


def munge(name):
    """Escape a session name the way PuTTY's own mungestr() does.

    PuTTY percent-escapes space, backslash, asterisk, question mark, percent,
    anything outside printable ASCII, and a leading dot. Everything else is
    passed through, so "Cape Cod Morning" becomes "Cape%20Cod%20Morning".
    """
    out = []
    for i, ch in enumerate(name):
        unsafe = (
            ch in " \\*?%"
            or ch < " " or ch > "~"
            or (ch == "." and i == 0)
        )
        out.append("%%%02X" % ord(ch) if unsafe else ch)
    return "".join(out)


def _rgb(colour):
    """A theme colour as PuTTY's decimal "r,g,b" string."""
    return "{},{},{}".format(*colour["rgb"])


def colour_values(theme):
    """Colour0-21 for a theme, in order.

    Colour0/1  foreground, normal and bold
    Colour2/3  background, normal and bold
    Colour4    cursor text — the background, so the character under the
               cursor stays legible against the cursor block
    Colour5    cursor
    """
    fg = _rgb(theme["foreground"])
    bg = _rgb(theme["background"])
    cursor = _rgb(theme["cursor"])
    return (fg, fg, bg, bg, bg, cursor) + ANSI_DEFAULTS


def reg_for_theme(theme):
    """The complete .reg file for one theme, as a str with CRLF endings."""
    lines = [
        REG_HEADER,
        "",
        "[{}\\{}]".format(SESSIONS_KEY, munge(theme["name"])),
    ]
    lines += ['"Colour{}"="{}"'.format(i, value)
              for i, value in enumerate(colour_values(theme))]
    # regedit wants a trailing blank line after the last value.
    lines.append("")
    return CRLF.join(lines)


def reg_filename(theme):
    """Download filename, e.g. "cape-cod-morning.reg"."""
    return "{}.reg".format(theme["id"])
