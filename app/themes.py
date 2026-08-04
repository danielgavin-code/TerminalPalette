"""Theme data for TerminalPalette.

Single source of truth. These values are rendered into the template and
serialised once into a JSON script block for the client; they are never
duplicated in CSS or JS source.

Each theme has:
    name, slug, description, detail, category, moods[], colors{...}

`description` is the short card line; `detail` is the longer details-panel
paragraph. `moods` drives the sidebar filters. The three colors are, in order,
the same values shown in the card colour strip and the details-panel RGB
groups; hex is the only stored representation.
"""

THEMES = [
    {
        "name": "Cape Cod Morning",
        "slug": "cape-cod-morning",
        "description": "Light background with muted sage and tan.",
        "detail": (
            "A light, low-contrast palette with muted sage and tan accents. "
            "Suited to long sessions in bright rooms."
        ),
        "category": "Warm",
        "moods": ["Warm", "Calm"],
        "colors": {
            "background": "#F2F0E0",
            "foreground": "#6C786E",
            "cursor": "#D7A46A",
        },
    },
    {
        "name": "Bloomberg Classic",
        "slug": "bloomberg-classic",
        "description": "Near-black background with green text.",
        "detail": (
            "A near-black background with green foreground text and a green "
            "cursor. Holds contrast at small type sizes."
        ),
        "category": "Vintage",
        "moods": ["Vintage", "Focused"],
        "colors": {
            "background": "#050505",
            "foreground": "#343638",
            "cursor": "#729C5D",
        },
    },
    {
        "name": "Ocean Glass",
        "slug": "ocean-glass",
        "description": "Desaturated blues on a dark teal base.",
        "detail": (
            "A dark teal background with desaturated blue text and a pale blue "
            "cursor. All three values sit in the same blue-green range."
        ),
        "category": "Cool",
        "moods": ["Cool", "Calm"],
        "colors": {
            "background": "#17323E",
            "foreground": "#477681",
            "cursor": "#9AC0CA",
        },
    },
    {
        "name": "Warm Paper",
        "slug": "warm-paper",
        "description": "Paper-toned background, low contrast.",
        "detail": (
            "A paper-toned background with little separation between background "
            "and foreground. The cursor sits a step darker than both."
        ),
        "category": "Warm",
        "moods": ["Warm", "Minimal"],
        "colors": {
            "background": "#EEE9DF",
            "foreground": "#D9D0C1",
            "cursor": "#A99982",
        },
    },
    {
        "name": "Graphite",
        "slug": "graphite",
        "description": "Neutral grays with a blue-gray accent.",
        "detail": (
            "Neutral dark grays for background and foreground, with a blue-gray "
            "cursor. Separation between the two grays is narrow."
        ),
        "category": "Minimal",
        "moods": ["Minimal", "Focused"],
        "colors": {
            "background": "#292B2D",
            "foreground": "#424446",
            "cursor": "#647785",
        },
    },
    {
        "name": "Forest",
        "slug": "forest",
        "description": "Dark green background with light text.",
        "detail": (
            "A dark green background with light neutral text. The cursor is a "
            "mid-green several steps lighter than the background."
        ),
        "category": "Calm",
        "moods": ["Calm", "Focused"],
        "colors": {
            "background": "#213C32",
            "foreground": "#E5DED1",
            "cursor": "#749873",
        },
    },
    {
        "name": "Midnight Blue",
        "slug": "midnight-blue",
        "description": "Dark navy with mid-blue accents.",
        "detail": (
            "A dark navy background with mid-blue foreground and cursor values. "
            "All three sit within the same blue range."
        ),
        "category": "Late Night",
        "moods": ["Late Night", "Cool"],
        "colors": {
            "background": "#111B2C",
            "foreground": "#283A59",
            "cursor": "#42688D",
        },
    },
    {
        "name": "Amber Terminal",
        "slug": "amber-terminal",
        "description": "Dark brown base with amber highlights.",
        "detail": (
            "A dark brown background with amber foreground and cursor values, "
            "after the amber CRT displays it is named for."
        ),
        "category": "Vintage",
        "moods": ["Vintage", "Warm", "Late Night"],
        "colors": {
            "background": "#251E17",
            "foreground": "#724515",
            "cursor": "#E99800",
        },
    },
]

# Sidebar mood filters. Order is presentational; counts are derived from the
# assignments above so they cannot drift out of sync with THEMES.
_MOOD_ICONS = [
    ("Focused", "target"),
    ("Calm", "leaf"),
    ("Warm", "flame"),
    ("Cool", "drop"),
    ("Late Night", "moon"),
    ("Minimal", "minimal"),
    ("Vintage", "clock"),
]


def _build_moods():
    moods = [
        {"key": "all", "label": "All Themes", "icon": "grid", "count": len(THEMES)}
    ]
    for label, icon in _MOOD_ICONS:
        moods.append(
            {
                "key": label,
                "label": label,
                "icon": icon,
                "count": sum(1 for t in THEMES if label in t["moods"]),
            }
        )
    return moods


MOODS = _build_moods()
