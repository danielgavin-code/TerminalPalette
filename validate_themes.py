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

import sys

from app.themes import (
    MAX_ENVIRONMENTS, THEMES, VALID_ENVIRONMENTS, VALID_MOODS, VALID_SEASONS,
    active_themes,
)

EXPECTED_COUNT = 44
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
    "production": {"closing-bell", "trading-floor", "copper", "charcoal",
                   "obsidian"},
    "uat": {"blue-ledger", "ocean-glass", "harbor-fog", "steel-blue",
            "arctic-glass"},
    "development": {"evergreen", "forest", "moss", "pine", "sage-field"},
    "dr": {"amber-terminal", "autumn-ledger", "desert-clay", "cedar"},
    "maintenance": {"terminal-gray", "data-center", "warm-paper", "parchment",
                    "typewriter"},
    "neutral": {"graphite", "midnight-blue", "monochrome", "ivory-console",
                "linen", "bloomberg-classic"},
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


# --- checks -----------------------------------------------------------------

def check_schema(themes):
    errors = []
    seen_ids, seen_names, seen_orders = {}, {}, {}

    if len(themes) != EXPECTED_COUNT:
        errors.append(f"expected {EXPECTED_COUNT} themes, found {len(themes)}")

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


def main():
    show_table = "--table" in sys.argv
    active = active_themes()

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
