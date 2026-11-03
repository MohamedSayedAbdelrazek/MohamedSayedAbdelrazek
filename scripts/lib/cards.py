"""Static cards: hero banner, "About me", tech stack, link buttons and footer.

Design rules: Geist for everything people read, body text >= 16px and labels >= 13px at the
900px viewBox, every text colour >= 4.5:1 on its background, one-time fade-ins, and at most
one slow loop per card.
"""

from __future__ import annotations

import content as C

from .core import document, esc, fmt, mix, reveal, text_width, wrap
from .icons import TECH, icon

W = 900
RADIUS = 20  # outer corner radius shared by every card
PAD = 48


def _frame(t: dict[str, str], h: float, *, glow: bool = False) -> str:
    """Card background + hairline border, optionally with a soft static glow."""
    out = []
    if glow:
        out.append(
            "<defs>"
            f'<radialGradient id="glow" cx="0.5" cy="0" r="0.75"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow"]}"/>'
            f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>'
            "</defs>"
        )
    out.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{fmt(h - 1)}" rx="{RADIUS - 0.5}" fill="{t["bg"]}" stroke="{t["line"]}"/>')
    if glow:
        out.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{fmt(h - 1)}" rx="{RADIUS - 0.5}" fill="url(#glow)"/>')
    return "".join(out)


def _title(t: dict[str, str], text: str, y: float) -> str:
    return (
        f'<rect x="{PAD}" y="{fmt(y - 24)}" width="4" height="26" rx="2" fill="{t["accent"]}"/>'
        f'<text x="{PAD + 16}" y="{fmt(y)}" class="s" font-size="24" font-weight="600" fill="{t["text"]}">{esc(text)}</text>'
    )


# --------------------------------------------------------------------------- #
# Hero
# --------------------------------------------------------------------------- #

ROLE_HOLD = 5.5  # seconds each role stays on screen
ROLE_FADE = 1.2


# A slow, soft halo on the availability dot.
HALO_CSS = (
    ".halo{transform-box:fill-box;transform-origin:center;animation:halo 4s ease-out infinite}"
    "@keyframes halo{0%{transform:scale(1);opacity:.35}70%,100%{transform:scale(2.6);opacity:0}}"
)


def _roles_css() -> str:
    n = len(C.ROLES)
    period = n * ROLE_HOLD
    a = ROLE_FADE / period * 100
    b = ROLE_HOLD / period * 100
    c = (ROLE_HOLD + ROLE_FADE) / period * 100
    css = f"@keyframes role{{0%{{opacity:0}}{a:.2f}%{{opacity:1}}{b:.2f}%{{opacity:1}}{c:.2f}%{{opacity:0}}100%{{opacity:0}}}}"
    for i in range(n):
        css += f".r{i}{{animation:role {period:g}s ease-in-out {i * ROLE_HOLD - ROLE_FADE:g}s infinite}}"
    return css


def _pill(x: float, y: float, w: float, h: float, fill: str, stroke: str) -> str:
    return f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="{fmt(h / 2)}" fill="{fill}" stroke="{stroke}"/>'


def hero(t: dict[str, str]) -> str:
    H = 372
    cx = W / 2
    name_size = 56.0
    while text_width(C.FULL_NAME, name_size, "sans", 800, -0.025 * name_size) > W - 2 * PAD:
        name_size -= 1
    tag_size = 18.0
    while text_width(C.TAGLINE, tag_size) > W - 2 * PAD and tag_size > 16:
        tag_size -= 0.5
    for role in C.ROLES:
        assert text_width(role, 24, "sans", 600) < W - 2 * PAD, f"role too long: {role}"

    out = [_frame(t, H, glow=True)]

    out.append(
        f'<g opacity="0">{reveal(0.1, dy=6)}'
        f'<text x="{cx}" y="98" text-anchor="middle" class="s" font-size="19" fill="{t["muted"]}">{esc(C.GREETING)}</text></g>'
    )
    out.append(
        f'<g opacity="0">{reveal(0.25, dy=10, dur=0.9)}'
        f'<text x="{cx}" y="160" text-anchor="middle" class="s" font-size="{fmt(name_size)}" font-weight="800" '
        f'letter-spacing="{fmt(-0.025 * name_size)}" fill="{t["text"]}">{esc(C.FULL_NAME)}</text></g>'
    )
    # Only the first role is visible without animation; CSS crossfades through the rest.
    roles = "".join(
        f'<text x="{cx}" y="208" text-anchor="middle" class="s r{i}" font-size="24" font-weight="600" '
        f'fill="{t["accent"]}" opacity="{1 if i == 0 else 0}">{esc(role)}</text>'
        for i, role in enumerate(C.ROLES)
    )
    out.append(f'<g opacity="0">{reveal(0.5, dy=6)}{roles}</g>')
    out.append(
        f'<g opacity="0">{reveal(0.7, dy=6)}'
        f'<text x="{cx}" y="250" text-anchor="middle" class="s" font-size="{fmt(tag_size)}" fill="{t["muted"]}">{esc(C.TAGLINE)}</text></g>'
    )

    # Pills: what I'm doing now + availability.
    ph, size = 40, 15
    label, value = C.CURRENTLY
    label_w = text_width(label + ":", size, "sans", 400)
    value_w = text_width(value, size, "sans", 600)
    w1 = 18 + 18 + 10 + label_w + 6 + value_w + 18
    w2 = 18 + 10 + 12 + text_width(C.STATUS, size, "sans", 600) + 18
    gap = 12
    x1 = cx - (w1 + gap + w2) / 2
    x2 = x1 + w1 + gap
    py = 286
    base = py + ph / 2 + size * 0.36
    accent_tint = mix(t["bg"], t["accent"], 0.10)
    ok_tint = mix(t["bg"], t["ok"], 0.10)
    cap = (  # a small graduation cap
        f'<g transform="translate({fmt(x1 + 18)} {fmt(py + ph / 2 - 9)})" fill="none" stroke="{t["accent"]}" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round">'
        '<path d="M1 6.5 9 3l8 3.5-8 3.5z"/><path d="M4.5 8.2v4.3c1.4 1.4 7.6 1.4 9 0V8.2"/><path d="M17 6.5v4.5"/></g>'
    )
    out.append(
        f'<g opacity="0">{reveal(0.9, dy=6)}'
        + _pill(x1, py, w1, ph, accent_tint, mix(t["bg"], t["accent"], 0.28))
        + cap
        + f'<text x="{fmt(x1 + 46)}" y="{fmt(base)}" class="s" font-size="{size}" fill="{t["muted"]}">{esc(label)}:</text>'
        f'<text x="{fmt(x1 + 46 + label_w + 6)}" y="{fmt(base)}" class="s" font-size="{size}" font-weight="600" fill="{t["text"]}">{esc(value)}</text>'
        + _pill(x2, py, w2, ph, ok_tint, mix(t["bg"], t["ok"], 0.28))
        + f'<circle cx="{fmt(x2 + 23)}" cy="{fmt(py + ph / 2)}" r="4.5" fill="{t["ok"]}" class="halo"/>'
        f'<circle cx="{fmt(x2 + 23)}" cy="{fmt(py + ph / 2)}" r="4.5" fill="{t["ok"]}"/>'
        f'<text x="{fmt(x2 + 40)}" y="{fmt(base)}" class="s" font-size="{size}" font-weight="600" fill="{t["ok"]}">{esc(C.STATUS)}</text>'
        "</g>"
    )
    assert x1 > PAD, "hero pills are too wide"

    return document(
        W,
        H,
        "".join(out),
        title=f"{C.FULL_NAME} — {C.ROLES[0]}",
        desc=f"{C.GREETING} {C.FULL_NAME}, {C.ROLES[0]}. {C.TAGLINE} {label}: {value}. {C.STATUS}.",
        fonts=[("sans", 400), ("sans", 600), ("sans", 800)],
        css=_roles_css() + HALO_CSS,
    )


# --------------------------------------------------------------------------- #
# About me
# --------------------------------------------------------------------------- #


def about(t: dict[str, str]) -> str:
    top = 124
    col_gap = 56
    left_w = 372
    rx = PAD + left_w + col_gap
    label_w = 118
    vx = rx + label_w
    value_w = W - PAD - vx

    body_size, body_lh = 17, 27
    bio = wrap(C.ABOUT_BIO, body_size, left_w)
    bio_h = len(bio) * body_lh

    row_h = 66
    facts_h = len(C.ABOUT_FACTS) * row_h - 18
    H = top + max(bio_h, facts_h) + 40

    out = [_frame(t, H), f'<g opacity="0">{reveal(0.05)}{_title(t, "About me", 74)}</g>']
    lines = "".join(
        f'<text x="{PAD}" y="{top + 12 + i * body_lh}" class="s" font-size="{body_size}" fill="{t["muted"]}">{esc(line)}</text>'
        for i, line in enumerate(bio)
    )
    out.append(f'<g opacity="0">{reveal(0.2, dy=6)}{lines}</g>')
    out.append(f'<path d="M{rx - col_gap / 2} {top - 6}v{fmt(max(bio_h, facts_h))}" stroke="{t["line"]}"/>')

    for i, (label, headline, detail) in enumerate(C.ABOUT_FACTS):
        y = top + 12 + i * row_h
        for text, size, weight in ((headline, 17, 600), (detail, 15, 400)):
            assert text_width(text, size, "sans", weight) <= value_w, f"about fact too long: {text}"
        assert text_width(label, 14, "sans", 600) < label_w - 12, f"about label too long: {label}"
        colour = t["accent"] if i == 0 else t["dim"]
        out.append(
            f'<g opacity="0">{reveal(0.3 + i * 0.1, dy=6)}'
            f'<text x="{rx}" y="{y}" class="s" font-size="14" font-weight="600" fill="{colour}">{esc(label)}</text>'
            f'<text x="{vx}" y="{y}" class="s" font-size="17" font-weight="600" fill="{t["text"]}">{esc(headline)}</text>'
            f'<text x="{vx}" y="{y + 23}" class="s" font-size="15" fill="{t["muted"]}">{esc(detail)}</text>'
            "</g>"
        )

    return document(
        W,
        H,
        "".join(out),
        title="About me",
        desc=C.ABOUT_BIO + " " + " ".join(f"{l}: {h}, {d}." for l, h, d in C.ABOUT_FACTS),
        fonts=[("sans", 400), ("sans", 600)],
    )


# --------------------------------------------------------------------------- #
# Tech stack
# --------------------------------------------------------------------------- #


def stack(t: dict[str, str]) -> str:
    top = 112
    row_h, chip_h = 64, 40
    label_w = 184
    chips_x0 = PAD + label_w
    size = 15
    H = top + len(C.STACK) * row_h + 28

    out = [_frame(t, H), f'<g opacity="0">{reveal(0.05)}{_title(t, "Tech stack", 74)}</g>']
    for i, (group, caption, keys) in enumerate(C.STACK):
        y = top + i * row_h
        mid = y + row_h / 2
        g = [f'<g opacity="0">{reveal(0.15 + i * 0.08, dy=6, dur=0.6)}']
        current = i == 0
        if current:
            g.append(f'<rect x="{PAD - 16}" y="{y + 4}" width="{W - 2 * PAD + 32}" height="{row_h - 8}" rx="14" fill="{mix(t["bg"], t["accent"], 0.07)}"/>')
        elif i > 1:
            g.append(f'<path d="M{PAD} {y}H{W - PAD}" stroke="{t["grid"]}"/>')
        g.append(
            f'<text x="{PAD}" y="{fmt(mid - 3)}" class="s" font-size="17" font-weight="600" fill="{t["text"]}">{esc(group)}</text>'
            f'<text x="{PAD}" y="{fmt(mid + 17)}" class="s" font-size="13" fill="{t["accent"] if current else t["dim"]}">{esc(caption)}</text>'
        )
        chip_bg = mix(t["bg"], t["accent"], 0.13) if current else t["raised"]
        cx = chips_x0
        cy = mid - chip_h / 2
        for key in keys:
            label = TECH[key][0]
            cw = 12 + 20 + 9 + text_width(label, size, "sans", 600) + 14
            g.append(
                f'<rect x="{fmt(cx)}" y="{fmt(cy)}" width="{fmt(cw)}" height="{chip_h}" rx="10" fill="{chip_bg}"/>'
                + icon(key, t, cx + 12, cy + 10, 20, chip_bg)
                + f'<text x="{fmt(cx + 41)}" y="{fmt(mid + size * 0.36)}" class="s" font-size="{size}" font-weight="600" fill="{t["text"]}">{esc(label)}</text>'
            )
            cx += cw + 10
        assert cx - 10 <= W - PAD, f"stack row too wide: {group}"
        g.append("</g>")
        out.append("".join(g))

    every = "; ".join(f"{group} ({caption}): " + ", ".join(TECH[k][0] for k in keys) for group, caption, keys in C.STACK)
    return document(
        W,
        H,
        "".join(out),
        title="Tech stack",
        desc=f"Technologies I work with. {every}.",
        fonts=[("sans", 400), ("sans", 600), ("sans", 800)],
    )


# --------------------------------------------------------------------------- #
# Link buttons
# --------------------------------------------------------------------------- #


def button(t: dict[str, str], link: dict[str, str], index: int) -> str:
    # Sized to its own text (no chevron) so all three fit on one row at GitHub's ~830px width.
    h = 58
    w = round(56 + max(text_width(link["label"], 15, "sans", 600), text_width(link["sub"], 13)) + 18)
    out = [
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="13.5" fill="{t["panel"]}" stroke="{t["line"]}"/>',
        f'<rect x="11" y="12" width="34" height="34" rx="9" fill="{t["raised"]}"/>',
        icon(link["icon"], t, 18, 19, 20, t["raised"]),
        f'<text x="56" y="26" class="s" font-size="15" font-weight="600" fill="{t["text"]}">{esc(link["label"])}</text>',
        f'<text x="56" y="44" class="s" font-size="13" fill="{t["dim"]}">{esc(link["sub"])}</text>',
    ]
    return document(
        w,
        h,
        f'<g opacity="0">{reveal(0.2 + index * 0.12)}{"".join(out)}</g>',
        title=link["label"],
        desc=f'{link["label"]}: {link["sub"]}',
        fonts=[("sans", 400), ("sans", 600), ("sans", 800)],
    )


# --------------------------------------------------------------------------- #
# Footer
# --------------------------------------------------------------------------- #


def footer(t: dict[str, str]) -> str:
    H = 176
    cx = W / 2
    size = 26
    while text_width(C.FOOTER_LINE, size, "sans", 600) > W - 2 * PAD:
        size -= 1
    bar = 56
    out = [
        _frame(t, H, glow=True),
        f'<g opacity="0">{reveal(0.2, dy=8, dur=0.9)}'
        f'<text x="{cx}" y="82" text-anchor="middle" class="s" font-size="{size}" font-weight="600" fill="{t["text"]}">{esc(C.FOOTER_LINE)}</text>'
        f'<text x="{cx}" y="118" text-anchor="middle" class="s" font-size="17" fill="{t["muted"]}">{esc(C.FOOTER_SUB)}</text>'
        f'<rect x="{cx - bar / 2}" y="140" width="{bar}" height="3" rx="1.5" fill="{t["accent"]}" opacity="0.8"/>'
        "</g>",
    ]
    return document(
        W,
        H,
        "".join(out),
        title="Thanks for visiting",
        desc=f"{C.FOOTER_LINE} {C.FOOTER_SUB}",
        fonts=[("sans", 400), ("sans", 600)],
    )
