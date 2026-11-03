"""Technology registry and icon drawing (brand marks from simple-icons, the rest hand-drawn)."""

from __future__ import annotations

from .core import brand_icons, fmt, readable

# key -> (label, simple-icons slug or None, colour override or None)
TECH: dict[str, tuple[str, str | None, str | None]] = {
    "php": ("PHP", "php", None),
    "laravel": ("Laravel", "laravel", None),
    "csharp": ("C#", None, "#9B4F96"),
    "dotnet": (".NET", None, "#512BD4"),
    "efcore": ("EF Core", None, "#6A3FC9"),
    "linq": ("LINQ", None, "accent2"),
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
    "ml": ("Machine Learning", None, "accent"),
    "imageproc": ("Image Processing", None, "accent2"),
    "linkedin": ("LinkedIn", None, "#0A66C2"),
    "gmail": ("Email", "gmail", None),
    "globe": ("Portfolio", None, "accent2"),
}


# Solid badges carry white text, so their colour is kept as-is instead of being lightened.
BADGES = {"csharp", "dotnet", "efcore", "linkedin"}


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
        return (
            f'<path d="M9 4C7 4 6 5 6 7v2.5c0 1.2-.8 2.2-2 2.5 1.2.3 2 1.3 2 2.5V17c0 2 1 3 3 3'
            f'M15 4c2 0 3 1 3 3v2.5c0 1.2.8 2.2 2 2.5-1.2.3-2 1.3-2 2.5V17c0 2-1 3-3 3" {stroke}/>'
        )
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
    if key == "efcore":
        return (
            f'<rect x="1.5" y="1.5" width="21" height="21" rx="4.5" fill="{c}"/>'
            '<text x="12" y="15.6" text-anchor="middle" class="s" font-weight="800" font-size="9.6" fill="#fff">EF</text>'
        )
    if key == "linq":  # a query funnel
        return f'<path d="M3.5 4.5h17l-6.5 7.8v6.2l-4 2v-8.2z" {stroke}/>'
    if key == "ml":  # a tiny neural network
        nodes = [(4.5, 7), (4.5, 17), (12, 4.5), (12, 12), (12, 19.5), (19.5, 12)]
        edges = [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 5), (3, 5), (4, 5)]
        lines = "".join(
            f"M{nodes[a][0]} {nodes[a][1]}L{nodes[b][0]} {nodes[b][1]}" for a, b in edges
        )
        dots = "".join(f'<circle cx="{x}" cy="{y}" r="2.3" fill="{c}"/>' for x, y in nodes)
        return f'<path d="{lines}" fill="none" stroke="{c}" stroke-width="1.2" opacity="0.7"/>{dots}'
    if key == "imageproc":  # a photo: frame, sun and hills
        return (
            f'<rect x="2.5" y="4" width="19" height="16" rx="3" {stroke}/>'
            f'<circle cx="8.5" cy="9.5" r="1.9" fill="{c}"/>'
            f'<path d="M3.5 18l5.2-5.2 3.6 3.6 2.6-2.6 5.6 5.2" {stroke}/>'
        )
    raise KeyError(key)


def icon(key: str, theme: dict[str, str], x: float, y: float, size: float, on: str) -> str:
    """Draw the icon for `key` in a size x size box at (x, y), legible on background `on`."""
    c = colour(key, theme, on)
    slug = TECH[key][1]
    inner = f'<path d="{brand_icons()[slug]["path"]}" fill="{c}"/>' if slug else _custom(key, c)
    return f'<svg x="{fmt(x)}" y="{fmt(y)}" width="{fmt(size)}" height="{fmt(size)}" viewBox="0 0 24 24" overflow="visible">{inner}</svg>'
