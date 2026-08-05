"""Theme data for TerminalPalette.

Single source of truth. Rendered into the template and serialised once into a
JSON script block for the client; never duplicated in CSS or JS source.

Two-tier colour model — intentional, do not collapse:

  palette                       decorative three-swatch strip on the card
  background/foreground/cursor  functional PuTTY values in the details panel

The two may differ. The card strip shows the palette; the details panel shows
the functional values, which are held to WCAG contrast minimums
(foreground >= 4.5:1, cursor >= 3:1 against background). Run
`python validate_themes.py --table` to check.

Seasonal rotation: every theme carries `active`, `season` and `display_order`.
Only active themes are rendered. Rotating a set later means editing those data
values only — there is no scheduling logic, no date reading, and no visible
season filter.
"""

VALID_SEASONS = {"permanent", "spring", "summer", "autumn", "winter"}

# Internal-only environment recommendations. Never rendered, never filtered on,
# never exposed in the interface — see ENVIRONMENTS below.
VALID_ENVIRONMENTS = {
    "production", "uat", "development", "dr", "maintenance", "neutral",
}
MAX_ENVIRONMENTS = 2

# (key, display label, sprite icon) — keys are the normalised internal ids.
MOOD_DEFS = [
    ("focused", "Focused", "target"),
    ("calm", "Calm", "leaf"),
    ("warm", "Warm", "flame"),
    ("cool", "Cool", "drop"),
    ("late-night", "Late Night", "moon"),
    ("minimal", "Minimal", "minimal"),
    ("vintage", "Vintage", "clock"),
]
VALID_MOODS = {key for key, _, _ in MOOD_DEFS}


def _c(value):
    """Expand a hex string into the {hex, rgb} pair used by the UI."""
    h = value.lstrip("#").upper()
    return {"hex": "#" + h, "rgb": [int(h[i:i + 2], 16) for i in (0, 2, 4)]}


def _theme(display_order, theme_id, name, description, moods, category,
           background, foreground, cursor, palette, inspired_by, created,
           featured=False, active=True, season="permanent", version="1.0"):
    return {
        "id": theme_id,
        "name": name,
        "description": description,
        "moods": moods,
        "category": category,
        "background": _c(background),
        "foreground": _c(foreground),
        "cursor": _c(cursor),
        "palette": [c.upper() for c in palette],
        "inspired_by": inspired_by,
        "created": created,
        "version": version,
        "active": active,
        "season": season,
        "featured": featured,
        "display_order": display_order,
        # Filled in from ENVIRONMENTS once THEMES is built. Empty is valid.
        "environments": [],
    }


THEMES = [
    # --- 1-8: the original set, ordering preserved ------------------------
    _theme(1, "cape-cod-morning", "Cape Cod Morning",
           "Light background with muted coastal tones.",
           ["calm", "warm", "minimal"], "Warm",
           "#F2F0E0", "#3B3A37", "#B07C3A",
           ["#F2F0E0", "#6C786E", "#D7A46A"],
           "Cape Cod mornings", "May 18, 2025", featured=True),
    _theme(2, "bloomberg-classic", "Bloomberg Classic",
           "Near-black background with green foreground and cursor.",
           ["focused", "vintage"], "Vintage",
           "#050505", "#C9C6BE", "#7CA85F",
           ["#050505", "#343638", "#729C5D"],
           "Financial data terminals", "May 18, 2025", featured=True),
    _theme(3, "ocean-glass", "Ocean Glass",
           "Dark teal background with pale blue foreground and cursor.",
           ["cool", "calm"], "Cool",
           "#17323E", "#D3DFE2", "#7FB0BC",
           ["#17323E", "#477681", "#9AC0CA"],
           "Sea glass", "May 18, 2025", featured=True),
    _theme(4, "warm-paper", "Warm Paper",
           "Paper-toned background with dark brown text.",
           ["warm", "minimal", "vintage"], "Warm",
           "#EEE9DF", "#3A362F", "#8A7A5F",
           ["#EEE9DF", "#D9D0C1", "#A99982"],
           "Uncoated paper stock", "May 18, 2025", featured=True),
    _theme(5, "graphite", "Graphite",
           "Neutral dark gray background with a blue-gray cursor.",
           ["minimal", "focused"], "Minimal",
           "#292B2D", "#C6C9CC", "#7C8F9E",
           ["#292B2D", "#424446", "#647785"],
           "Pencil graphite", "May 18, 2025", featured=True),
    _theme(6, "forest", "Forest",
           "Dark green background with light neutral text.",
           ["calm", "focused"], "Calm",
           "#213C32", "#E5DED1", "#7FA87E",
           ["#213C32", "#E5DED1", "#749873"],
           "Northern woodland", "May 18, 2025", featured=True),
    _theme(7, "midnight-blue", "Midnight Blue",
           "Dark navy background with muted blue foreground and cursor.",
           ["late-night", "cool"], "Late Night",
           "#111B2C", "#C8D2E2", "#5E86B4",
           ["#111B2C", "#283A59", "#42688D"],
           "Night sky over water", "May 18, 2025", featured=True),
    _theme(8, "amber-terminal", "Amber Terminal",
           "Dark brown background with amber foreground and cursor.",
           ["vintage", "warm", "late-night"], "Vintage",
           "#251E17", "#E0C9A6", "#E99800",
           ["#251E17", "#724515", "#E99800"],
           "Amber CRT displays", "May 18, 2025", featured=True),
    # --- 9-18: coastal, then cold water -----------------------------------
    _theme(9, "harbor-fog", "Harbor Fog",
           "Pale gray background with slate blue cursor.",
           ["calm", "cool", "minimal"], "Cool",
           "#E8E9E7", "#33383A", "#5F7480",
           ["#E8E9E7", "#B4BDC0", "#6E8089"],
           "Fog over a harbor", "June 2, 2025"),
    _theme(10, "atlantic-dawn", "Atlantic Dawn",
           "Dark blue-gray background with a warm tan cursor.",
           ["cool", "calm"], "Cool",
           "#1B2A38", "#DCE2E6", "#C98F5C",
           ["#1B2A38", "#3E5A70", "#E0A96D"],
           "First light at sea", "June 2, 2025"),
    _theme(11, "salt-marsh", "Salt Marsh",
           "Dark olive-gray background with a muted green cursor.",
           ["calm", "minimal"], "Calm",
           "#2A3129", "#DDD9C9", "#9AA86B",
           ["#2A3129", "#5C6B4C", "#AEB98A"],
           "Tidal marsh grass", "June 2, 2025"),
    _theme(12, "coastal-slate", "Coastal Slate",
           "Dark gray background with a pale blue-green cursor.",
           ["cool", "minimal", "focused"], "Cool",
           "#2E3438", "#D2D6D8", "#86A2AC",
           ["#2E3438", "#55636A", "#93AEB8"],
           "Wet slate on a shoreline", "June 2, 2025"),
    _theme(13, "deep-sea", "Deep Sea",
           "Very dark blue background with a mid-teal cursor.",
           ["cool", "late-night"], "Cool",
           "#0E1F2A", "#CBDCE2", "#4E93A6",
           ["#0E1F2A", "#1F4757", "#3E8296"],
           "Deep water", "June 9, 2025"),
    _theme(14, "arctic-glass", "Arctic Glass",
           "Pale cyan-gray background with a teal cursor.",
           ["cool", "minimal"], "Cool",
           "#E7F3F2", "#2E3639", "#3F7180",
           ["#E7F3F2", "#C2D6DA", "#4E8494"],
           "Ice under overcast light", "June 9, 2025"),
    # --- 19-24: greens ----------------------------------------------------
    _theme(15, "evergreen", "Evergreen",
           "Very dark green background with a mid-green cursor.",
           ["calm", "focused"], "Calm",
           "#17281F", "#D8E0D2", "#6FA070",
           ["#17281F", "#2F4A36", "#6FA070"],
           "Evergreen stands", "June 23, 2025"),
    _theme(16, "cedar", "Cedar",
           "Dark red-brown background with a warm orange cursor.",
           ["warm", "vintage"], "Warm",
           "#2B211B", "#E2D3C2", "#C08A57",
           ["#2B211B", "#6A4630", "#C08A57"],
           "Cedar heartwood", "June 30, 2025"),
    _theme(17, "olive-terminal", "Olive Terminal",
           "Dark olive background with a muted yellow-green cursor.",
           ["vintage", "focused"], "Vintage",
           "#262819", "#DCDAC4", "#A0A64E",
           ["#262819", "#4C512F", "#A0A64E"],
           "Olive drab equipment", "June 30, 2025"),
    _theme(18, "sage-field", "Sage Field",
           "Pale green-gray background with a muted green cursor.",
           ["calm", "minimal", "warm"], "Calm",
           "#EDEFE6", "#33372F", "#5F6F4C",
           ["#EDEFE6", "#C3CCB6", "#7E8F6A"],
           "Sage fields", "June 30, 2025"),
    # --- 25-31: dark neutrals and night --------------------------------
    _theme(19, "obsidian", "Obsidian",
           "Near-black background with a cool gray cursor.",
           ["minimal", "late-night", "focused"], "Minimal",
           "#121213", "#D2D0CC", "#6E7C86",
           ["#121213", "#2C2E31", "#68767F"],
           "Volcanic glass", "July 7, 2025"),
    _theme(20, "eclipse", "Eclipse",
           "Near-black violet background with a muted purple cursor.",
           ["late-night", "minimal"], "Late Night",
           "#16151A", "#D4D1D8", "#9A7FB0",
           ["#16151A", "#312E3A", "#9A7FB0"],
           "A solar eclipse", "July 7, 2025"),
    _theme(21, "charcoal", "Charcoal",
           "Dark neutral gray background with a mid-gray cursor.",
           ["minimal", "focused"], "Minimal",
           "#202224", "#CCCECF", "#8C9195",
           ["#202224", "#3A3D40", "#8C9195"],
           "Charcoal sticks", "July 7, 2025"),
    _theme(22, "night-shift", "Night Shift",
           "Very dark blue-gray background with a warm tan cursor.",
           ["late-night", "focused"], "Late Night",
           "#14171C", "#C9CFD6", "#C08A5E",
           ["#14171C", "#2C333C", "#C08A5E"],
           "Overnight shifts", "July 14, 2025"),
    _theme(23, "data-center", "Data Center",
           "Very dark green-gray background with a muted teal cursor.",
           ["focused", "cool", "late-night"], "Focused",
           "#101416", "#C6D0CF", "#4E9C8A",
           ["#101416", "#25302F", "#4E9C8A"],
           "Server room lighting", "July 14, 2025"),
    # --- 32-35: warm earth ------------------------------------------------
    _theme(24, "copper", "Copper",
           "Dark brown background with a copper-orange cursor.",
           ["warm", "vintage"], "Warm",
           "#241C18", "#E4D2C2", "#C4794B",
           ["#241C18", "#6B3F27", "#C4794B"],
           "Oxidized copper", "July 21, 2025"),
    _theme(25, "autumn-ledger", "Autumn Ledger",
           "Warm cream background with a red-brown cursor.",
           ["warm", "vintage"], "Warm",
           "#F1EADD", "#3A332A", "#97613A",
           ["#F1EADD", "#C8A67E", "#97613A"],
           "Ledger paper in autumn", "July 21, 2025"),
    # --- 36-40: papers and light consoles ------------------------------
    _theme(26, "parchment", "Parchment",
           "Aged cream background with a dark gold cursor.",
           ["vintage", "warm", "minimal"], "Vintage",
           "#F3EEE0", "#3A352B", "#8A6F42",
           ["#F3EEE0", "#DACDAE", "#8A6F42"],
           "Aged parchment", "July 28, 2025"),
    _theme(27, "ivory-console", "Ivory Console",
           "Ivory background with a muted olive-brown cursor.",
           ["minimal", "warm"], "Minimal",
           "#F7EFDA", "#35332D", "#6F6950",
           ["#F7EFDA", "#DCD6C4", "#7A7358"],
           "Ivory console panels", "August 11, 2025"),
    # --- 41-43: neutral, ruled, and dusk ----------------------------------
    _theme(28, "monochrome", "Monochrome",
           "Light gray background with a mid-gray cursor.",
           ["minimal", "focused"], "Minimal",
           "#F2F2F2", "#2B2B2B", "#6E6E6E",
           ["#F2F2F2", "#C2C2C2", "#6E6E6E"],
           "Monochrome displays", "August 11, 2025"),
    _theme(29, "blue-ledger", "Blue Ledger",
           "Pale blue-gray background with a mid-blue cursor.",
           ["cool", "focused", "minimal"], "Cool",
           "#EAEEF7", "#2F343B", "#4C6B94",
           ["#EAEEF7", "#BFCBDC", "#4C6B94"],
           "Blue-ruled ledger paper", "August 11, 2025"),
    # --- 44 --------------------------------------------------------------
    _theme(30, "closing-bell", "Closing Bell",
           "Dark charcoal background with restrained red accents.",
           ["focused", "late-night"], "Late Night",
           "#1A1614", "#E2DBD3", "#B8503F",
           ["#1A1614", "#3A2A26", "#B8503F"],
           "Market close operations", "August 18, 2025"),
]


# --------------------------------------------------------------------------
# Environment recommendations — internal metadata only.
#
# Kept as one table rather than scattered across the theme entries so the
# whole mapping can be read and revised in a single place. Themes absent from
# this table keep an empty list, which is valid and deliberate: a theme is
# listed only where its palette genuinely suits that context.
#
# Nothing here reaches the interface. There is no environment filter, badge,
# label, or tooltip, and the field is not part of any search index. It exists
# so the recommendations are recorded for possible future use.
# --------------------------------------------------------------------------
ENVIRONMENTS = {
    # Dark backgrounds with restrained high-attention accents.
    "closing-bell": ["production"],
    "copper": ["production"],
    "charcoal": ["production"],
    "obsidian": ["production"],
    # Controlled blue and blue-gray.
    "blue-ledger": ["uat"],
    "ocean-glass": ["uat"],
    "harbor-fog": ["uat"],
    "arctic-glass": ["uat"],
    # Green and natural tones.
    "evergreen": ["development"],
    # Inherited from Moss: same dark olive-green family.
    "salt-marsh": ["development"],
    "forest": ["development"],
    "sage-field": ["development"],
    # Amber, orange and copper caution tones.
    "amber-terminal": ["dr"],
    "autumn-ledger": ["dr"],
    "cedar": ["dr"],
    # Paper and neutral technical palettes for planned work.
    "data-center": ["maintenance"],
    "warm-paper": ["maintenance"],
    "parchment": ["maintenance"],
    # General-purpose daily drivers.
    "graphite": ["neutral"],
    # uat inherited from Steel Blue: dark navy with a mid-blue cursor
    # already matches the controlled-blue convention for UAT.
    "midnight-blue": ["neutral", "uat"],
    "monochrome": ["neutral"],
    "ivory-console": ["neutral"],
    "bloomberg-classic": ["neutral"],
}

for _theme_entry in THEMES:
    _theme_entry["environments"] = list(ENVIRONMENTS.get(_theme_entry["id"], []))
del _theme_entry


def active_themes():
    """Active themes in display order. The only list the UI should render."""
    return sorted((t for t in THEMES if t["active"]),
                  key=lambda t: t["display_order"])


def initial_theme():
    """The theme selected on first paint, taken from the data itself."""
    themes = active_themes()
    return themes[0] if themes else None


def build_moods():
    """Sidebar filters. Counts are derived from active data, never hardcoded."""
    active = active_themes()
    moods = [{"key": "all", "label": "All Themes", "icon": "grid",
              "count": len(active)}]
    for key, label, icon in MOOD_DEFS:
        moods.append({
            "key": key,
            "label": label,
            "icon": icon,
            "count": sum(1 for t in active if key in t["moods"]),
        })
    return moods
