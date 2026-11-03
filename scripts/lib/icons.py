"""Technology registry and icon drawing (brand marks from simple-icons, the rest hand-drawn)."""

from __future__ import annotations

from .core import brand_icons, fmt, readable

# key -> (label, simple-icons slug or None, colour override or None)
TECH: dict[str, tuple[str, str | None, str | None]] = {
    "php": ("PHP", "php", None),
    "laravel": ("Laravel", "laravel", None),
    "csharp": ("C#", None, "#9B4F96"),
    "dotnet": (".NET", None, "#512BD4"),
    "mysql": ("MySQL", None, "#4479A1"),
    "restapi": ("REST APIs", None, "#14B8A6"),
    "postman": ("Postman", "postman", None),
    "html5": ("HTML5", "html5", None),
    "css": ("CSS3", "css", "#1572B6"),
    "java": ("Java", "openjdk", "#ED8B00"),
    "cplusplus": ("C++", "cplusplus", None),
    "python": ("Python", "python", None),
    "git": ("Git", "git", None),
    "github": ("GitHub", "github", "text"),
    "vscode": ("VS Code", None, "#23A9F2"),
    "patterns": ("Design Patterns", None, "accent"),
    "architecture": ("System Design", None, "accent2"),
    "problems": ("Problem Solving", None, "ok"),
    "teamwork": ("Teamwork", None, "info"),
    "linkedin": ("LinkedIn", None, "#0A66C2"),
    "gmail": ("Email", "gmail", None),
    "globe": ("Portfolio", None, "accent2"),
}


# Solid badges carry white text, so their colour is kept as-is instead of being lightened.
BADGES = {"csharp", "dotnet", "linkedin"}


def colour(key: str, theme: dict[str, str], on: str) -> str:
    _, slug, override = TECH[key]
    if override in theme:
        base = theme[override]  # theme token such as "accent" or "text"
    elif override:
        base = override
    else:
        base = "#" + brand_icons()[slug]["hex"]
    return base if key in BADGES else readable(base, on, 2.6)


def _custom(key: str, c: str) -> str:
    stroke = f'fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    if key == "csharp":
        return (
            f'<path d="M12 1.5 21.1 6.75v10.5L12 22.5 2.9 17.25V6.75z" fill="{c}"/>'
            '<text x="12" y="15.4" text-anchor="middle" class="s" font-weight="800" font-size="8.6" fill="#fff">C#</text>'
        )
    if key == "dotnet":
        return (
            f'<rect x="1.5" y="1.5" width="21" height="21" rx="4.5" fill="{c}"/>'
            '<text x="12" y="14.6" text-anchor="middle" class="s" font-weight="800" font-size="7.4" fill="#fff">.NET</text>'
        )
    if key == "mysql":
        return (
            f'<ellipse cx="12" cy="5.5" rx="8" ry="3" {stroke}/>'
            f'<path d="M4 5.5v13c0 1.66 3.58 3 8 3s8-1.34 8-3v-13M4 12c0 1.66 3.58 3 8 3s8-1.34 8-3" {stroke}/>'
        )
    if key == "restapi":
        return f'<text x="12" y="17" text-anchor="middle" class="m" font-weight="700" font-size="15" fill="{c}">{{}}</text>'
    if key == "vscode":
        return f'<path d="M8 6.5 2.5 12 8 17.5M16 6.5l5.5 5.5-5.5 5.5M13.6 4.5l-3.2 15" {stroke}/>'
    if key == "linkedin":
        return (
            f'<rect x="1.5" y="1.5" width="21" height="21" rx="4.5" fill="{c}"/>'
            '<text x="12" y="17.3" text-anchor="middle" class="s" font-weight="800" font-size="13" fill="#fff">in</text>'
        )
    if key == "globe":
        return (
            f'<circle cx="12" cy="12" r="9.5" {stroke}/><ellipse cx="12" cy="12" rx="4.2" ry="9.5" {stroke}/>'
            f'<path d="M2.8 9h18.4M2.8 15h18.4" {stroke}/>'
        )
    if key == "patterns":
        return (
            f'<rect x="3" y="3" width="7.5" height="7.5" rx="1.6" fill="{c}"/>'
            f'<rect x="13.5" y="3" width="7.5" height="7.5" rx="1.6" {stroke}/>'
            f'<rect x="3" y="13.5" width="7.5" height="7.5" rx="1.6" {stroke}/>'
            f'<rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.6" fill="{c}"/>'
        )
    if key == "architecture":
        return (
            f'<path d="M12 7v4M12 11H5.5v6M12 11h6.5v6" {stroke}/>'
            f'<rect x="8.5" y="2" width="7" height="5.5" rx="1.4" fill="{c}"/>'
            f'<rect x="2" y="16.5" width="7" height="5.5" rx="1.4" fill="{c}"/>'
            f'<rect x="15" y="16.5" width="7" height="5.5" rx="1.4" fill="{c}"/>'
        )
    if key == "problems":
        return (
            f'<circle cx="12" cy="12" r="9.5" {stroke}/><circle cx="12" cy="12" r="5.2" {stroke}/>'
            f'<circle cx="12" cy="12" r="1.9" fill="{c}"/>'
        )
    if key == "teamwork":
        return (
            f'<circle cx="8.5" cy="8" r="3.2" {stroke}/><circle cx="16.5" cy="9" r="2.6" {stroke}/>'
            f'<path d="M2.5 20.5c0-3.6 2.7-6.2 6-6.2s6 2.6 6 6.2M15.2 14.4c3.3-.4 6.3 1.9 6.3 5.6" {stroke}/>'
        )
    raise KeyError(key)


def icon(key: str, theme: dict[str, str], x: float, y: float, size: float, on: str) -> str:
    """Draw the icon for `key` in a size x size box at (x, y), legible on background `on`."""
    c = colour(key, theme, on)
    slug = TECH[key][1]
    inner = f'<path d="{brand_icons()[slug]["path"]}" fill="{c}"/>' if slug else _custom(key, c)
    return f'<svg x="{fmt(x)}" y="{fmt(y)}" width="{fmt(size)}" height="{fmt(size)}" viewBox="0 0 24 24" overflow="visible">{inner}</svg>'
