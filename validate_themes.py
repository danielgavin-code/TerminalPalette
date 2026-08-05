#!/usr/bin/env python3
"""Validate the TerminalPalette theme collection.

Dependency-free. Development only — never imported by a request path.

    python validate_themes.py          # summary + failures
    python validate_themes.py --table  # full contrast table for every theme

Checks schema integrity (counts, required fields, uniqueness, RGB/hex
agreement, valid moods and seasons, unique display order) and WCAG contrast:

    foreground vs background  >= 4.5:1
    cursor     vs background  >= 3.0:1
"""

import math
import sys

from app.themes import (
    MAX_ENVIRONMENTS, THEMES, VALID_ENVIRONMENTS, VALID_MOODS, VALID_SEASONS,
    active_themes,
)

# No hardcoded total. The collection size is whatever the active data holds;
# these ids were removed in the similarity audit and must not come back.
REMOVED_IDS = {
    # first pass
    "moss",           # -> salt-marsh
    "pine",           # -> evergreen
    "quiet-violet",   # -> eclipse
    "terminal-gray",  # -> charcoal
    "glacier",        # -> blue-ledger
    "sepia-screen",   # -> autumn-ledger
    # second pass (user-confirmed by visual review)
    "trading-floor",  # -> bloomberg-classic
    "coffee-house",   # -> cedar
    "linen",          # -> warm-paper
    "typewriter",     # -> warm-paper
    "winter-harbor",  # -> coastal-slate
    "rain-window",    # -> coastal-slate
    "steel-blue",     # -> midnight-blue
}

# Perceptual bands for the similarity audit, on the weighted dE00 score.
BANDS = (
    (2.50, "STRONG duplicate"),
    (4.00, "PROBABLE duplicate"),
    (8.00, "related but distinct"),
    (float("inf"), "clearly distinct"),
)


def band_for(score):
    for limit, label in BANDS:
        if score < limit:
            return label
    return BANDS[-1][1]
ENV_FLOOR = 3

FG_MIN = 4.5
CURSOR_MIN = 3.0
FG_PREFERRED = 7.0

REQUIRED = (
    "id", "name", "description", "moods", "category",
    "background", "foreground", "cursor", "palette",
    "inspired_by", "created", "version", "active", "season",
    "featured", "display_order", "environments",
)

# Stated independently of app.themes so this verifies the assignments rather
# than simply echoing them back.
EXPECTED_ENVIRONMENTS = {
    "production": {"closing-bell", "copper", "charcoal", "obsidian"},
    "uat": {"blue-ledger", "ocean-glass", "harbor-fog", "arctic-glass",
            "midnight-blue"},
    "development": {"evergreen", "forest", "sage-field", "salt-marsh"},
    "dr": {"amber-terminal", "autumn-ledger", "desert-clay", "cedar"},
    "maintenance": {"data-center", "warm-paper", "parchment"},
    "neutral": {"graphite", "midnight-blue", "monochrome", "ivory-console",
                "bloomberg-classic"},
}


# --- WCAG relative luminance ------------------------------------------------

def _channel(value):
    v = value / 255.0
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = (_channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(rgb_a, rgb_b):
    la, lb = luminance(rgb_a), luminance(rgb_b)
    if lb > la:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


def hex_to_rgb(value):
    h = value.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


# --- perceptual colour distance: sRGB -> linear -> XYZ -> CIELAB -> dE00 ----

# D65 reference white, 2-degree observer.
_WHITE = (95.047, 100.0, 108.883)


def rgb_to_xyz(rgb):
    r, g, b = (_channel(c) for c in rgb)          # linearised, 0..1
    r, g, b = r * 100.0, g * 100.0, b * 100.0
    return (
        r * 0.4124564 + g * 0.3575761 + b * 0.1804375,
        r * 0.2126729 + g * 0.7151522 + b * 0.0721750,
        r * 0.0193339 + g * 0.1191920 + b * 0.9503041,
    )


def rgb_to_lab(rgb):
    x, y, z = rgb_to_xyz(rgb)
    xn, yn, zn = _WHITE

    def f(t):
        return t ** (1.0 / 3.0) if t > 216.0 / 24389.0 else (841.0 / 108.0) * t + 4.0 / 29.0

    fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
    return (116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz))


def ciede2000(lab1, lab2):
    """CIEDE2000 colour difference. Sharma et al. formulation."""
    l1, a1, b1 = lab1
    l2, a2, b2 = lab2

    c1 = math.hypot(a1, b1)
    c2 = math.hypot(a2, b2)
    c_bar = (c1 + c2) / 2.0
    g = 0.5 * (1.0 - math.sqrt(c_bar ** 7 / (c_bar ** 7 + 25.0 ** 7))) if c_bar > 0 else 0.0

    a1p, a2p = (1.0 + g) * a1, (1.0 + g) * a2
    c1p, c2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360.0 if (a1p or b1) else 0.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360.0 if (a2p or b2) else 0.0

    dlp = l2 - l1
    dcp = c2p - c1p
    if c1p * c2p == 0:
        dhp = 0.0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    elif h2p - h1p > 180:
        dhp = h2p - h1p - 360.0
    else:
        dhp = h2p - h1p + 360.0
    dHp = 2.0 * math.sqrt(c1p * c2p) * math.sin(math.radians(dhp) / 2.0)

    lp_bar = (l1 + l2) / 2.0
    cp_bar = (c1p + c2p) / 2.0
    if c1p * c2p == 0:
        hp_bar = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hp_bar = (h1p + h2p) / 2.0
    elif h1p + h2p < 360:
        hp_bar = (h1p + h2p + 360.0) / 2.0
    else:
        hp_bar = (h1p + h2p - 360.0) / 2.0

    t = (1.0
         - 0.17 * math.cos(math.radians(hp_bar - 30.0))
         + 0.24 * math.cos(math.radians(2.0 * hp_bar))
         + 0.32 * math.cos(math.radians(3.0 * hp_bar + 6.0))
         - 0.20 * math.cos(math.radians(4.0 * hp_bar - 63.0)))

    d_theta = 30.0 * math.exp(-(((hp_bar - 275.0) / 25.0) ** 2))
    rc = 2.0 * math.sqrt(cp_bar ** 7 / (cp_bar ** 7 + 25.0 ** 7)) if cp_bar > 0 else 0.0
    sl = 1.0 + (0.015 * (lp_bar - 50.0) ** 2) / math.sqrt(20.0 + (lp_bar - 50.0) ** 2)
    sc = 1.0 + 0.045 * cp_bar
    sh = 1.0 + 0.015 * cp_bar * t
    rt = -math.sin(math.radians(2.0 * d_theta)) * rc

    return math.sqrt(
        (dlp / sl) ** 2 + (dcp / sc) ** 2 + (dHp / sh) ** 2
        + rt * (dcp / sc) * (dHp / sh)
    )


def delta_e_hex(hex_a, hex_b):
    return ciede2000(rgb_to_lab(hex_to_rgb(hex_a)), rgb_to_lab(hex_to_rgb(hex_b)))


# Background dominates what a terminal looks like, so it carries most weight.
WEIGHTS = {"background": 0.50, "foreground": 0.30, "cursor": 0.20}


def theme_distance(a, b):
    parts = {role: delta_e_hex(a[role]["hex"], b[role]["hex"]) for role in WEIGHTS}
    palette = sum(delta_e_hex(x, y) for x, y in zip(a["palette"], b["palette"])) / 3.0
    weighted = sum(parts[role] * w for role, w in WEIGHTS.items())
    return {"weighted": weighted, "palette": palette, **parts}


def self_check():
    """Validate the colour pipeline against published reference values."""
    rows = []
    white, black = rgb_to_lab([255, 255, 255]), rgb_to_lab([0, 0, 0])
    rows.append(("sRGB #FFFFFF -> L*", f"{white[0]:.2f}", "100.00"))
    rows.append(("sRGB #000000 -> L*", f"{black[0]:.2f}", "0.00"))
    rows.append(("dE00 white vs black", f"{ciede2000(white, black):.2f}", "100.00"))
    red = rgb_to_lab([255, 0, 0])
    rows.append(("sRGB #FF0000 -> Lab",
                 f"{red[0]:.2f},{red[1]:.2f},{red[2]:.2f}", "53.24,80.09,67.20"))
    # Sharma CIEDE2000 test vectors, given directly in Lab.
    rows.append(("dE00 Sharma pair 1",
                 f"{ciede2000((50, 2.6772, -79.7751), (50, 0.0, -82.7485)):.4f}", "2.0425"))
    rows.append(("dE00 Sharma pair 2",
                 f"{ciede2000((50, 3.1571, -77.2803), (50, 0.0, -82.7485)):.4f}", "2.8615"))
    rows.append(("dE00 Sharma pair 3",
                 f"{ciede2000((50, 2.8361, -74.0200), (50, 0.0, -82.7485)):.4f}", "3.4412"))
    rows.append(("dE00 identical colour", f"{delta_e_hex('#213C32', '#213C32'):.4f}", "0.0000"))
    return rows


def similarity_report(themes, top=15):
    pairs = []
    for i, a in enumerate(themes):
        for b in themes[i + 1:]:
            d = theme_distance(a, b)
            pairs.append((d["weighted"], a, b, d))
    pairs.sort(key=lambda p: p[0])
    return pairs[:top]


# --- checks -----------------------------------------------------------------

def check_schema(themes):
    errors = []
    seen_ids, seen_names, seen_orders = {}, {}, {}

    active = [t for t in themes if t.get("active")]
    if len(themes) != len(active):
        errors.append(f"{len(themes) - len(active)} inactive entr(ies) present; "
                      "the collection total must equal the active count")
    for t in themes:
        if t.get("id") in REMOVED_IDS:
            errors.append(f"'{t['id']}' was removed in the audit but is present again")

    for t in themes:
        label = t.get("name") or t.get("id") or "<unnamed>"

        for field in REQUIRED:
            if field not in t:
                errors.append(f"{label}: missing field '{field}'")
        if any(f not in t for f in REQUIRED):
            continue

        tid = t["id"]
        if not tid.replace("-", "").isalnum() or tid != tid.lower() or " " in tid:
            errors.append(f"{label}: id '{tid}' is not lowercase URL-safe")
        if tid in seen_ids:
            errors.append(f"duplicate id '{tid}'")
        seen_ids[tid] = True
        if t["name"] in seen_names:
            errors.append(f"duplicate name '{t['name']}'")
        seen_names[t["name"]] = True
        if t["display_order"] in seen_orders:
            errors.append(f"{label}: duplicate display_order {t['display_order']}")
        seen_orders[t["display_order"]] = True

        for role in ("background", "foreground", "cursor"):
            colour = t[role]
            if set(colour) != {"hex", "rgb"}:
                errors.append(f"{label}: {role} needs exactly hex and rgb keys")
                continue
            rgb = colour["rgb"]
            if len(rgb) != 3 or not all(isinstance(c, int) and 0 <= c <= 255 for c in rgb):
                errors.append(f"{label}: {role} rgb {rgb} is not three ints 0-255")
            elif hex_to_rgb(colour["hex"]) != list(rgb):
                errors.append(
                    f"{label}: {role} hex {colour['hex']} != rgb {rgb}")

        if not isinstance(t["palette"], list) or len(t["palette"]) != 3:
            errors.append(f"{label}: palette must hold exactly 3 colours")
        else:
            for swatch in t["palette"]:
                if len(swatch.lstrip('#')) != 6:
                    errors.append(f"{label}: bad palette swatch '{swatch}'")

        if not 1 <= len(t["moods"]) <= 3:
            errors.append(f"{label}: has {len(t['moods'])} moods, expected 1-3")
        for mood in t["moods"]:
            if mood not in VALID_MOODS:
                errors.append(f"{label}: unknown mood '{mood}'")
        if t["season"] not in VALID_SEASONS:
            errors.append(f"{label}: unknown season '{t['season']}'")

        envs = t["environments"]
        if not isinstance(envs, list):
            errors.append(f"{label}: environments must be a list, got {type(envs).__name__}")
        else:
            if len(envs) > MAX_ENVIRONMENTS:
                errors.append(
                    f"{label}: {len(envs)} environments, max is {MAX_ENVIRONMENTS}")
            if len(set(envs)) != len(envs):
                errors.append(f"{label}: duplicate environment values {envs}")
            for env in envs:
                if env not in VALID_ENVIRONMENTS:
                    errors.append(f"{label}: unknown environment '{env}'")
        for field in ("description", "inspired_by", "category", "created", "version"):
            if not str(t[field]).strip():
                errors.append(f"{label}: '{field}' is empty")

    return errors


def check_contrast(themes):
    errors, rows = [], []
    for t in themes:
        if any(f not in t for f in ("background", "foreground", "cursor", "name")):
            continue
        bg = t["background"]["rgb"]
        fg_ratio = contrast(t["foreground"]["rgb"], bg)
        cur_ratio = contrast(t["cursor"]["rgb"], bg)
        rows.append((t["name"], t["background"]["hex"], t["foreground"]["hex"],
                     t["cursor"]["hex"], fg_ratio, cur_ratio))
        if fg_ratio < FG_MIN:
            errors.append(f"{t['name']}: foreground {fg_ratio:.2f}:1 < {FG_MIN}:1")
        if cur_ratio < CURSOR_MIN:
            errors.append(f"{t['name']}: cursor {cur_ratio:.2f}:1 < {CURSOR_MIN}:1")
    return errors, rows


def check_environments(themes):
    """Verify the recommendations match the agreed assignment table exactly."""
    errors = []
    by_id = {t["id"]: t for t in themes if "id" in t}

    actual = {env: set() for env in VALID_ENVIRONMENTS}
    for t in themes:
        for env in t.get("environments", []):
            if env in actual:
                actual[env].add(t["id"])

    for env, expected_ids in EXPECTED_ENVIRONMENTS.items():
        for missing in sorted(expected_ids - actual[env]):
            errors.append(f"'{missing}' should be assigned to {env}")
        for extra in sorted(actual[env] - expected_ids):
            errors.append(f"'{extra}' unexpectedly assigned to {env}")
        for tid in expected_ids:
            if tid not in by_id:
                errors.append(f"{env}: no theme with id '{tid}'")

    for env, ids in sorted(actual.items()):
        if len(ids) < ENV_FLOOR:
            errors.append(f"environment '{env}' has {len(ids)} themes; "
                          f"floor is {ENV_FLOOR}")

    bell = by_id.get("closing-bell")
    if bell is None:
        errors.append("Closing Bell is missing from the collection")
    elif "production" not in bell.get("environments", []):
        errors.append("Closing Bell must include the 'production' environment")

    return errors, actual


def check_moods(themes):
    errors = []
    counts = {m: sum(1 for t in themes if m in t.get("moods", [])) for m in VALID_MOODS}
    for mood, n in sorted(counts.items()):
        if n < 2:
            errors.append(f"mood '{mood}' has {n} theme(s); needs multiple")
    return errors, counts


def print_similarity(active, top=15):
    """Development-only similarity audit. Never rendered on the site."""
    print("colour pipeline self-check (sRGB -> XYZ -> CIELAB -> dE00)")
    print(f"  {'check':<24} {'computed':<24} reference")
    for name, got, want in self_check():
        flag = "" if got.split(",")[0][:5] == want.split(",")[0][:5] else "   <-- MISMATCH"
        print(f"  {name:<24} {got:<24} {want}{flag}")

    print(f"\nweighting: background {WEIGHTS['background']:.0%}, "
          f"foreground {WEIGHTS['foreground']:.0%}, cursor {WEIGHTS['cursor']:.0%}")
    print(f"closest {top} pairs of {len(active)} active themes "
          f"({len(active) * (len(active) - 1) // 2} comparisons)\n")
    print(f"{'#':>2} {'pair':<38} {'total':>6} {'bg':>6} {'fg':>6} {'cur':>6} "
          f"{'pal':>6}  {'L/D':<7} band")
    print("-" * 100)

    def tone(t):
        return "light" if luminance(t["background"]["rgb"]) > 0.4 else "dark"

    rows = similarity_report(active, top)
    for i, (w, a, b, d) in enumerate(rows, 1):
        pair = f"{a['name']} / {b['name']}"
        ld = f"{tone(a)[0].upper()}/{tone(b)[0].upper()}"
        print(f"{i:>2} {pair:<38} {w:6.2f} {d['background']:6.2f} "
              f"{d['foreground']:6.2f} {d['cursor']:6.2f} {d['palette']:6.2f}  "
              f"{ld:<7} {band_for(w)}")

    # Detail block for anything needing a manual look.
    flagged = [(w, a, b, d) for w, a, b, d in rows if w < BANDS[1][0]]
    if flagged:
        print(f"\n{len(flagged)} pair(s) in STRONG/PROBABLE bands — review manually:")
        for w, a, b, d in flagged:
            for t in (a, b):
                fg = contrast(t["foreground"]["rgb"], t["background"]["rgb"])
                cur = contrast(t["cursor"]["rgb"], t["background"]["rgb"])
                print(f"    {t['name']:<20} {t['background']['hex']} {t['foreground']['hex']} "
                      f"{t['cursor']['hex']}  {tone(t):<5} fg {fg:5.2f}:1 cur {cur:4.2f}:1  "
                      f"moods={','.join(t['moods'])}  env={','.join(t['environments']) or '-'}")
            print(f"    -> weighted {w:.2f} ({band_for(w)})\n")

    print("Lower total = more similar. Background carries the most weight "
          "because it dominates the terminal.")
    print(f"Bands: STRONG < {BANDS[0][0]}, PROBABLE < {BANDS[1][0]}, "
          f"related < {BANDS[2][0]}, else clearly distinct.")


def main():
    show_table = "--table" in sys.argv
    show_similar = "--similar" in sys.argv
    active = active_themes()

    if show_similar:
        print_similarity(active)
        print()

    schema_errors = check_schema(THEMES)
    contrast_errors, rows = check_contrast(THEMES)
    mood_errors, counts = check_moods(active)
    env_errors, env_map = check_environments(THEMES)

    if show_table:
        print(f"{'Theme':<20} {'Background':<10} {'Foreground':<10} {'Cursor':<10} "
              f"{'FG':>7} {'CUR':>7}")
        print("-" * 70)
        for name, bg, fg, cur, fr, cr in rows:
            flag = "" if fr >= FG_MIN and cr >= CURSOR_MIN else "  <-- FAIL"
            print(f"{name:<20} {bg:<10} {fg:<10} {cur:<10} "
                  f"{fr:>6.2f}:1 {cr:>6.2f}:1{flag}")
        print()

    below_preferred = [(n, fr) for n, _, _, _, fr, _ in rows if fr < FG_PREFERRED]

    print(f"themes defined : {len(THEMES)}")
    print(f"active themes  : {len(active)}")
    print(f"mood counts    : " + ", ".join(f"{m}={counts[m]}" for m in sorted(counts)))
    print("environments   :")
    for env in sorted(EXPECTED_ENVIRONMENTS):
        names = sorted(t["name"] for t in THEMES if env in t.get("environments", []))
        print(f"    {env:<12} {len(names)}  {', '.join(names)}")
    unassigned = [t["name"] for t in THEMES if not t.get("environments")]
    print(f"    {'(none)':<12} {len(unassigned)}  {', '.join(sorted(unassigned))}")
    print(f"foreground >= {FG_PREFERRED}:1 : "
          f"{len(rows) - len(below_preferred)}/{len(rows)}"
          + ("" if not below_preferred
             else "  below: " + ", ".join(f"{n} {r:.2f}:1" for n, r in below_preferred)))

    errors = schema_errors + contrast_errors + mood_errors + env_errors
    if errors:
        print(f"\n{len(errors)} PROBLEM(S):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
