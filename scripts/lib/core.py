"""Shared building blocks: themes, embedded fonts, text metrics, colour and SMIL helpers.

Every card is a self-contained SVG. GitHub renders README images through <img>,
which blocks external requests, so fonts are embedded as base64 and all motion
is done with SMIL / CSS that lives inside the file itself.
"""

from __future__ import annotations

import base64
import functools
import html
import json
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[2]
FONT_DIR = ROOT / "scripts" / "fonts"
ICON_FILE = ROOT / "scripts" / "icons.json"

# --------------------------------------------------------------------------- #
# Themes
# --------------------------------------------------------------------------- #

THEMES: dict[str, dict[str, str]] = {
    "dark": {
        "bg": "#0A0A0D",
        "panel": "#111116",
        "raised": "#18181F",
        "line": "#26262F",
        "grid": "#1F1F27",
        "text": "#F4F4F5",
        "muted": "#A1A1AA",
        "dim": "#6B6B76",
        "accent": "#FF2D20",
        "accent2": "#FF8A3D",
        "shine": "#FFD2BD",
        "ok": "#3DD68C",
        "warn": "#F5B83D",
        "info": "#7AA2F7",
        "glow": "0.32",
    },
    "light": {
        "bg": "#FBFBF9",
        "panel": "#FFFFFF",
        "raised": "#F3F3EF",
        "line": "#E2E2DC",
        "grid": "#E6E6E0",
        "text": "#17171C",
        "muted": "#52525B",
        "dim": "#8E8E98",
        "accent": "#E8231A",
        "accent2": "#F2652A",
        "shine": "#FFB089",
        "ok": "#12A05A",
        "warn": "#B97F05",
        "info": "#3B63D9",
        "glow": "0.16",
    },
}

# --------------------------------------------------------------------------- #
# Fonts
# --------------------------------------------------------------------------- #

FONT_FILES: dict[tuple[str, int], str] = {
    ("sans", 400): "geist-400.woff2",
    ("sans", 600): "geist-600.woff2",
    ("sans", 800): "geist-800.woff2",
    ("mono", 400): "jetbrains-mono-400.woff2",
    ("mono", 700): "jetbrains-mono-700.woff2",
}
FAMILY = {"sans": "Geist", "mono": "JBMono"}
FALLBACK = {
    "sans": "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif",
    "mono": "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace",
}


@functools.cache
def _font_b64(name: str) -> str:
    return base64.b64encode((FONT_DIR / name).read_bytes()).decode("ascii")


def font_css(used: Iterable[tuple[str, int]]) -> str:
    rules = []
    for family, weight in sorted(set(used)):
        rules.append(
            f"@font-face{{font-family:{FAMILY[family]};font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{_font_b64(FONT_FILES[(family, weight)])}) format('woff2')}}"
        )
    rules.append(f".s{{font-family:{FAMILY['sans']},{FALLBACK['sans']}}}")
    rules.append(f".m{{font-family:{FAMILY['mono']},{FALLBACK['mono']}}}")
    return "".join(rules)


@functools.cache
def _metrics(family: str, weight: int):
    from fontTools.ttLib import TTFont  # imported lazily: only needed when measuring

    font = TTFont(FONT_DIR / FONT_FILES[(family, weight)])
    return font.getBestCmap(), font["hmtx"].metrics, font["head"].unitsPerEm


def text_width(text: str, size: float, family: str = "sans", weight: int = 400, tracking: float = 0.0) -> float:
    """Advance width of `text` in px (no kerning, so it errs on the wide side)."""
    cmap, hmtx, upem = _metrics(family, weight)
    units = sum(hmtx[cmap.get(ord(ch), ".notdef")][0] for ch in text)
    return units * size / upem + tracking * max(len(text) - 1, 0)


MONO_ADVANCE = 0.6  # JetBrains Mono: 600 / 1000 units per em


def mono_width(chars: int, size: float) -> float:
    return chars * size * MONO_ADVANCE


# --------------------------------------------------------------------------- #
# Icons
# --------------------------------------------------------------------------- #


@functools.cache
def brand_icons() -> dict[str, dict[str, str]]:
    return json.loads(ICON_FILE.read_text())["icons"]


# --------------------------------------------------------------------------- #
# Colour
# --------------------------------------------------------------------------- #


def _rgb(hex_: str) -> tuple[float, float, float]:
    hex_ = hex_.lstrip("#")
    return tuple(int(hex_[i : i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def _hex(rgb: Sequence[float]) -> str:
    return "#" + "".join(f"{round(max(0, min(1, c)) * 255):02X}" for c in rgb)


def mix(a: str, b: str, t: float) -> str:
    ra, rb = _rgb(a), _rgb(b)
    return _hex([x + (y - x) * t for x, y in zip(ra, rb)])


def _luminance(hex_: str) -> float:
    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in _rgb(hex_))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def readable(fg: str, bg: str, minimum: float = 3.0) -> str:
    """Nudge a brand colour towards white/black until it reads on `bg`."""
    target = "#FFFFFF" if _luminance(bg) < 0.5 else "#000000"
    colour = fg
    step = 0.0
    while contrast(colour, bg) < minimum and step < 1:
        step += 0.05
        colour = mix(fg, target, step)
    return colour


# --------------------------------------------------------------------------- #
# Markup helpers
# --------------------------------------------------------------------------- #


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def fmt(n: float) -> str:
    """Compact number formatting for coordinates."""
    return f"{n:.2f}".rstrip("0").rstrip(".") if isinstance(n, float) else str(n)


def animate(
    attr: str,
    frames: Sequence[tuple[float, object]],
    dur: float,
    *,
    calc: str = "linear",
    repeat: str = "indefinite",
    fill: str | None = None,
    begin: str | None = None,
    tag: str = "animate",
    extra: str = "",
) -> str:
    """Build a SMIL animation from (seconds, value) frames inside a `dur` cycle."""
    pts = sorted(frames, key=lambda f: f[0])
    if pts[0][0] > 0:
        pts.insert(0, (0.0, pts[0][1]))
    if calc != "discrete" and pts[-1][0] < dur:
        pts.append((dur, pts[-1][1]))
    times = [min(max(t / dur, 0.0), 1.0) for t, _ in pts]
    times[0] = 0.0
    if calc != "discrete":
        times[-1] = 1.0
    key_times = ";".join(f"{t:.4f}".rstrip("0").rstrip(".") or "0" for t in times)
    values = ";".join(str(v) for _, v in pts)
    parts = [
        f'<{tag} attributeName="{attr}"' if tag != "animateTransform" else f'<{tag} attributeName="transform" type="{attr}"',
        f'dur="{fmt(dur)}s"',
        f'values="{values}"',
        f'keyTimes="{key_times}"',
        f'calcMode="{calc}"',
        f'repeatCount="{repeat}"' if repeat else "",
        f'fill="{fill}"' if fill else "",
        f'begin="{begin}"' if begin else "",
        extra,
    ]
    return " ".join(p for p in parts if p) + "/>"


def reveal(begin: float, *, dy: float = 0, dur: float = 0.7) -> str:
    """One-shot fade + rise used for entrance animations (stays visible afterwards)."""
    ease = 'keySplines="0.2 0.8 0.2 1"'
    out = (
        f'<animate attributeName="opacity" from="0" to="1" begin="{fmt(begin)}s" dur="{fmt(dur)}s" '
        f'fill="freeze" calcMode="spline" keyTimes="0;1" {ease}/>'
    )
    if dy:
        out += (
            f'<animateTransform attributeName="transform" type="translate" from="0 {fmt(dy)}" to="0 0" '
            f'begin="{fmt(begin)}s" dur="{fmt(dur)}s" fill="freeze" calcMode="spline" keyTimes="0;1" {ease}/>'
        )
    return out


BASE_CSS = (
    ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.4s ease-out infinite}"
    "@keyframes pulse{0%{transform:scale(1);opacity:.55}100%{transform:scale(3.2);opacity:0}}"
    ".blink{animation:blink 1.05s steps(1,end) infinite}"
    "@keyframes blink{50%{opacity:0}}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)


def document(
    width: float,
    height: float,
    body: str,
    *,
    title: str,
    desc: str,
    fonts: Iterable[tuple[str, int]],
    css: str = "",
) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(width)}" height="{fmt(height)}" '
        f'viewBox="0 0 {fmt(width)} {fmt(height)}" role="img" aria-labelledby="t d">'
        f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>'
        f"<style>{font_css(fonts)}{BASE_CSS}{css}</style>\n{body}\n</svg>\n"
    )
