"""Hand-drawn isometric illustration for the hero: a developer at a desk with two monitors.

Everything is computed from a tiny isometric projection so the geometry stays consistent.
Motion is CSS only (so `prefers-reduced-motion` stops it) and deliberately slow:
code scrolls on one screen, a bar chart breathes on the other, the hands type,
steam rises from the mug and the phone glows now and then.
"""

from __future__ import annotations

import math

from .core import fmt, mix

COS, SIN = math.cos(math.radians(30)), 0.5
S = 24.0  # px per world unit before fitting


def P(x: float, y: float, z: float) -> tuple[float, float]:
    """World (x right-down, y left-down, z up) -> screen."""
    return ((x - y) * COS * S, (x + y) * SIN * S - z * S)


def _pts(*pts: tuple[float, float]) -> str:
    return " ".join(f"{fmt(round(px, 2))},{fmt(round(py, 2))}" for px, py in pts)


def poly(fill: str, *pts: tuple[float, float], extra: str = "") -> str:
    return f'<polygon points="{_pts(*pts)}" fill="{fill}" {extra}/>'


def box(x, y, z, dx, dy, dz, top, left, right, *, round_: bool = False) -> str:
    """Visible faces of an axis-aligned box: top, +y face ("left") and +x face ("right")."""
    j = 'stroke-linejoin="round"' if round_ else ""
    t = poly(top, P(x, y, z + dz), P(x + dx, y, z + dz), P(x + dx, y + dy, z + dz), P(x, y + dy, z + dz), extra=j)
    l = poly(left, P(x, y + dy, z + dz), P(x + dx, y + dy, z + dz), P(x + dx, y + dy, z), P(x, y + dy, z), extra=j)
    r = poly(right, P(x + dx, y, z + dz), P(x + dx, y + dy, z + dz), P(x + dx, y + dy, z), P(x + dx, y, z), extra=j)
    return l + r + t


def face_matrix(x: float, y_left: float, z_top: float) -> str:
    """Matrix mapping local (u right, v down, in px) onto the +x face, origin at its top-left corner."""
    ox, oy = P(x, y_left, z_top)
    return f"matrix({COS:.4f} {-SIN} 0 1 {fmt(round(ox, 2))} {fmt(round(oy, 2))})"


def palette(t: dict[str, str]) -> dict[str, str]:
    dark = int(t["bg"][1:3], 16) < 0x60
    a, a2 = t["accent"], t["accent2"]
    if dark:
        return {
            "floor": mix(t["bg"], a, 0.15), "floor_edge": mix(t["bg"], a, 0.08),
            "desk_top": "#2C3248", "desk_left": "#232839", "desk_right": "#1C2030", "leg": "#2A2F43",
            "mon_top": "#2A2F45", "mon_left": "#1F2333", "mon_right": "#171A27", "screen": "#0B0E1A",
            "key_top": "#3A4160", "key_side": "#2A3048",
            "shirt": mix("#4A3FB8", a, 0.25), "shirt_shade": "#3A3192", "pants": "#22263A",
            "skin": "#D9A27C", "hair": "#16141F", "phones": "#2C2A45", "cup": a,
            "seat": "#2F3550", "seat_side": "#232840", "steam": "#C9C4F2", "plant": "#5FD49B", "pot": "#3A4160",
            "code": [a, a2, t["ok"], "#F0C674", "#8892B0"], "chart": [a, a2, mix(a, "#FFFFFF", 0.3)], "axis": "#2E3450",
        }
    return {
        "floor": mix(t["bg"], a, 0.09), "floor_edge": mix(t["bg"], a, 0.17),
        "desk_top": "#FFFFFF", "desk_left": "#E7E5F3", "desk_right": "#D7D3EC", "leg": "#CFCBE6",
        "mon_top": "#3B3A55", "mon_left": "#2E2D45", "mon_right": "#25243A", "screen": "#151629",
        "key_top": "#F1F0F8", "key_side": "#D7D3EC",
        "shirt": a, "shirt_shade": mix(a, "#000000", 0.25), "pants": "#2D2B45",
        "skin": "#D9A27C", "hair": "#1B1928", "phones": "#2C2A45", "cup": a,
        "seat": "#3B3A55", "seat_side": "#2E2D45", "steam": mix(t["bg"], a, 0.45), "plant": "#2FA36B", "pot": "#D7D3EC",
        "code": ["#A996FF", "#8B97FF", "#5FD49B", "#F0C674", "#8892B0"], "chart": ["#A996FF", "#8B97FF", "#C9BEFF"], "axis": "#2E3050",
    }


# --------------------------------------------------------------------------- #
# Screens
# --------------------------------------------------------------------------- #


def _code_screen(c: dict[str, str], w: float, h: float) -> str:
    """Rows of coloured tokens that scroll upwards forever (two copies for a seamless loop)."""
    rows = [  # (indent, [(token width, colour index), ...])
        (0, [(10, 0), (16, 1), (8, 4)]),
        (0, [(6, 4)]),
        (6, [(8, 0), (12, 3), (10, 4)]),
        (6, [(14, 1), (6, 4), (10, 2)]),
        (12, [(9, 0), (18, 2)]),
        (12, [(12, 3), (8, 1), (6, 4)]),
        (6, [(5, 4)]),
        (6, [(10, 0), (14, 1)]),
        (12, [(16, 2), (7, 4)]),
        (6, [(5, 4)]),
        (0, [(4, 4)]),
        (0, [(12, 1), (9, 0)]),
    ]
    lh = 5.2
    block = len(rows) * lh
    tokens = []
    for copy in range(2):
        for i, (indent, toks) in enumerate(rows):
            y = 4 + copy * block + i * lh
            x = 4 + indent * 0.9
            for tw, ci in toks:
                tw *= 0.9
                if x + tw > w - 3:
                    break
                tokens.append(f'<rect x="{fmt(round(x, 1))}" y="{fmt(round(y, 1))}" width="{fmt(round(tw, 1))}" height="2.4" rx="1.2" fill="{c["code"][ci]}"/>')
                x += tw + 2.2
    css = f"@keyframes scroll{{to{{transform:translateY(-{block:.1f}px)}}}}"
    body = (
        f'<clipPath id="codeclip"><rect width="{fmt(w)}" height="{fmt(h)}" rx="1.5"/></clipPath>'
        f'<g clip-path="url(#codeclip)"><rect width="{fmt(w)}" height="{fmt(h)}" fill="{c["screen"]}"/>'
        f'<g class="scroll">{"".join(tokens)}</g>'
        f'<rect y="0" width="{fmt(w)}" height="5" fill="{c["screen"]}" opacity="0.6"/></g>'
    )
    return body, css


def _chart_screen(c: dict[str, str], w: float, h: float) -> str:
    out = [f'<rect width="{fmt(w)}" height="{fmt(h)}" rx="1.5" fill="{c["screen"]}"/>']
    # A small "card" header and two KPI pills.
    out.append(f'<rect x="4" y="4" width="18" height="2.6" rx="1.3" fill="{c["code"][4]}"/>')
    out.append(f'<rect x="{fmt(w - 16)}" y="4" width="12" height="2.6" rx="1.3" fill="{c["code"][2]}"/>')
    base = h - 5
    out.append(f'<path d="M4 {fmt(base + 0.6)}H{fmt(w - 4)}" stroke="{c["axis"]}" stroke-width="0.8"/>')
    n = 6
    gap = 2.4
    bw = (w - 8 - gap * (n - 1)) / n
    heights = [0.45, 0.7, 0.55, 0.85, 0.65, 0.95]
    for i, k in enumerate(heights):
        bh = (h - 16) * k
        x = 4 + i * (bw + gap)
        out.append(
            f'<rect class="bar" style="animation-delay:-{i * 0.7:.1f}s" x="{fmt(round(x, 2))}" y="{fmt(round(base - bh, 2))}" '
            f'width="{fmt(round(bw, 2))}" height="{fmt(round(bh, 2))}" rx="1" fill="{c["chart"][i % 3]}"/>'
        )
    return "".join(out)


# --------------------------------------------------------------------------- #
# Scene
# --------------------------------------------------------------------------- #


def scene(t: dict[str, str], x: float, y: float, w: float, h: float) -> tuple[str, str]:
    """Return (svg, css) for the illustration fitted into the box (x, y, w, h)."""
    c = palette(t)
    parts: list[str] = []

    # Floor: a soft isometric tile.
    fx0, fx1, fy0, fy1 = -0.2, 7.3, 0.0, 7.1
    parts.append(
        poly(c["floor_edge"], P(fx1, fy0, 0), P(fx1, fy1, 0), P(fx1, fy1, -0.35), P(fx1, fy0, -0.35), extra='stroke-linejoin="round"')
        + poly(c["floor_edge"], P(fx0, fy1, 0), P(fx1, fy1, 0), P(fx1, fy1, -0.35), P(fx0, fy1, -0.35))
        + poly(c["floor"], P(fx0, fy0, 0), P(fx1, fy0, 0), P(fx1, fy1, 0), P(fx0, fy1, 0))
    )

    # Plant in the back corner.
    parts.append(box(0.3, 6.1, 0, 0.75, 0.75, 0.9, c["pot"], mix(c["pot"], "#000000", 0.12), mix(c["pot"], "#000000", 0.22)))
    px, py = P(0.68, 6.48, 0.9)
    leaves = "".join(
        f'<ellipse cx="{fmt(round(px + dx, 1))}" cy="{fmt(round(py - dy, 1))}" rx="{rx}" ry="{ry}" fill="{c["plant"]}" '
        f'opacity="{op}" transform="rotate({rot} {fmt(round(px + dx, 1))} {fmt(round(py - dy, 1))})"/>'
        for dx, dy, rx, ry, rot, op in [(-8, 16, 5, 13, -28, 0.9), (7, 18, 5, 14, 26, 0.9), (0, 24, 5, 15, 0, 1), (-3, 10, 4, 10, -55, 0.8), (5, 9, 4, 10, 55, 0.8)]
    )
    parts.append(f'<g class="sway">{leaves}</g>')

    # Desk legs, then the top.
    dz = 2.6
    for lx, ly in ((1.1, 0.9), (3.75, 0.9), (1.1, 6.0), (3.75, 6.0)):
        parts.append(box(lx, ly, 0, 0.14, 0.14, dz, c["leg"], c["leg"], mix(c["leg"], "#000000", 0.15)))
    parts.append(box(0.9, 0.7, dz, 3.1, 5.6, 0.2, c["desk_top"], c["desk_left"], c["desk_right"]))
    top = dz + 0.2

    # Monitors (y grows to the left on screen, so the left screen has the larger y).
    css = []
    for i, (y0, y1) in enumerate(((0.95, 3.4), (3.6, 6.05))):
        mid = (y0 + y1) / 2
        parts.append(box(1.05, mid - 0.5, top, 0.8, 1.0, 0.05, c["mon_top"], c["mon_left"], c["mon_right"]))
        parts.append(box(1.2, mid - 0.1, top, 0.14, 0.2, 0.75, c["mon_left"], c["mon_left"], c["mon_right"]))
        z0, z1 = top + 0.6, top + 2.6
        parts.append(box(1.35, y0, z0, 0.16, y1 - y0, z1 - z0, c["mon_top"], c["mon_left"], c["mon_right"]))
        inset = 0.09
        sw = (y1 - y0 - 2 * inset) * S
        sh = (z1 - z0 - 2 * inset) * S
        if i == 1:
            body, scroll_css = _code_screen(c, sw, sh)
            css.append(scroll_css)
        else:
            body = _chart_screen(c, sw, sh)
        parts.append(f'<g transform="{face_matrix(1.51, y1 - inset, z1 - inset)}">{body}</g>')

    # Phone, mug + steam, keyboard.
    parts.append(box(3.05, 1.0, top, 0.55, 0.32, 0.04, c["mon_left"], c["mon_left"], c["mon_right"]))
    gx, gy = P(3.32, 1.16, top + 0.05)
    parts.append(f'<ellipse class="glow" cx="{fmt(round(gx, 1))}" cy="{fmt(round(gy, 1))}" rx="5" ry="3" fill="{t["accent"]}"/>')
    mx, my = P(3.3, 5.6, top)
    r = 0.28 * S
    mh = 0.55 * S
    parts.append(
        f'<path d="M{fmt(round(mx - r, 1))} {fmt(round(my, 1))}v{fmt(round(-mh, 1))}h{fmt(round(2 * r, 1))}v{fmt(round(mh, 1))}'
        f'a{fmt(round(r, 1))} {fmt(round(r * 0.5, 1))} 0 0 1 {fmt(round(-2 * r, 1))} 0z" fill="{c["cup"]}"/>'
        f'<ellipse cx="{fmt(round(mx, 1))}" cy="{fmt(round(my - mh, 1))}" rx="{fmt(round(r, 1))}" ry="{fmt(round(r * 0.5, 1))}" fill="{mix(c["cup"], "#000000", 0.35)}"/>'
        f'<path d="M{fmt(round(mx + r, 1))} {fmt(round(my - mh * 0.75, 1))}c5 0 5 7 0 7" fill="none" stroke="{c["cup"]}" stroke-width="2"/>'
    )
    for k, dx in enumerate((-3, 2.5)):
        sx, sy = mx + dx, my - mh - 4
        parts.append(
            f'<path class="steam" style="animation-delay:-{k * 2:.0f}s" d="M{fmt(round(sx, 1))} {fmt(round(sy, 1))}'
            f'c-3 -4 3 -6 0 -10c-3 -4 3 -6 0 -10" fill="none" stroke="{c["steam"]}" stroke-width="1.6" stroke-linecap="round"/>'
        )
    parts.append(box(2.85, 2.75, top, 0.75, 2.0, 0.06, c["key_top"], c["key_side"], mix(c["key_side"], "#000000", 0.1)))
    # Key rows on the keyboard top.
    for row in range(3):
        kx = 2.95 + row * 0.2
        a, b = P(kx, 2.85, top + 0.07), P(kx, 4.65, top + 0.07)
        parts.append(f'<path d="M{fmt(round(a[0], 1))} {fmt(round(a[1], 1))}L{fmt(round(b[0], 1))} {fmt(round(b[1], 1))}" stroke="{c["key_side"]}" stroke-width="1.6" stroke-dasharray="3 1.6"/>')

    # Chair.
    parts.append(box(5.45, 3.55, 0.12, 0.2, 0.2, 1.35, c["seat_side"], c["seat_side"], mix(c["seat_side"], "#000000", 0.2)))
    parts.append(box(5.05, 3.05, 0, 1.0, 1.1, 0.12, c["seat_side"], c["seat_side"], mix(c["seat_side"], "#000000", 0.2)))
    parts.append(box(4.95, 2.95, 1.45, 1.3, 1.3, 0.22, c["seat"], c["seat_side"], mix(c["seat_side"], "#000000", 0.15), round_=True))

    # Person: legs under the desk, arms to the keyboard, torso, head with headphones.
    seat = 1.67
    for ly in (3.15, 3.85):
        parts.append(box(4.3, ly, seat, 1.45, 0.5, 0.36, c["pants"], mix(c["pants"], "#000000", 0.15), mix(c["pants"], "#000000", 0.3)))

    def stroke_path(points, colour, width, cls="") -> str:
        d = "M" + " L".join(f"{fmt(round(px, 1))} {fmt(round(py, 1))}" for px, py in points)
        klass = f' class="{cls}"' if cls else ""
        return f'<path{klass} d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'

    arm_w = 0.44 * S
    sh_z = 3.75
    for side, (sy, ey, hy) in enumerate(((3.0, 2.85, 3.35), (4.6, 4.8, 4.15))):
        shoulder, elbow, hand = P(5.55, sy, sh_z - 0.1), P(4.6, ey, 3.1), P(3.45, hy, top + 0.2)
        cls = "tapA" if side == 0 else "tapB"
        parts.append(
            f'<g class="{cls}">{stroke_path([shoulder, elbow, hand], c["shirt_shade"], arm_w)}'
            f'<circle cx="{fmt(round(hand[0], 1))}" cy="{fmt(round(hand[1], 1))}" r="{fmt(round(arm_w * 0.45, 1))}" fill="{c["skin"]}"/></g>'
        )
    # Torso: a rounded back seen from behind, a little wider at the shoulders than at the waist.
    torso = [P(5.95, 4.35, seat + 0.35), P(5.95, 3.25, seat + 0.35), P(5.62, 2.95, sh_z), P(5.62, 4.65, sh_z)]
    parts.append(poly(c["shirt"], *torso, extra=f'stroke="{c["shirt"]}" stroke-width="{fmt(0.75 * S)}" stroke-linejoin="round"'))
    for sy in (3.0, 4.6):  # shoulder caps
        cx_, cy_ = P(5.62, sy, sh_z - 0.15)
        parts.append(f'<circle cx="{fmt(round(cx_, 1))}" cy="{fmt(round(cy_, 1))}" r="{fmt(round(0.5 * S, 1))}" fill="{c["shirt"]}"/>')
    a, b = P(5.9, 3.8, seat + 0.6), P(5.66, 3.8, sh_z - 0.4)
    parts.append(f'<path d="M{fmt(round(a[0], 1))} {fmt(round(a[1], 1))}L{fmt(round(b[0], 1))} {fmt(round(b[1], 1))}" stroke="{c["shirt_shade"]}" stroke-width="1.6" stroke-linecap="round" opacity="0.55"/>')
    nx, ny = P(5.55, 3.8, sh_z + 0.3)
    parts.append(f'<rect x="{fmt(round(nx - 5, 1))}" y="{fmt(round(ny - 4, 1))}" width="10" height="12" rx="4" fill="{mix(c["skin"], "#000000", 0.15)}"/>')
    hx, hy_ = P(5.5, 3.8, sh_z + 0.95)
    hr = 0.68 * S
    parts.append(
        '<g class="nod">'
        f'<ellipse cx="{fmt(round(hx - hr * 0.95, 1))}" cy="{fmt(round(hy_ + 3, 1))}" rx="3" ry="4.5" fill="{c["skin"]}"/>'
        f'<circle cx="{fmt(round(hx, 1))}" cy="{fmt(round(hy_, 1))}" r="{fmt(round(hr, 1))}" fill="{c["hair"]}"/>'
        f'<path d="M{fmt(round(hx - hr * 1.02, 1))} {fmt(round(hy_ + 1, 1))}a{fmt(round(hr * 1.02, 1))} {fmt(round(hr * 1.05, 1))} 0 0 1 {fmt(round(hr * 2.04, 1))} 0" '
        f'fill="none" stroke="{c["phones"]}" stroke-width="4" stroke-linecap="round"/>'
        f'<rect x="{fmt(round(hx - hr - 4.5, 1))}" y="{fmt(round(hy_ - 3, 1))}" width="9" height="14" rx="4.5" fill="{c["phones"]}"/>'
        f'<rect x="{fmt(round(hx - hr - 2, 1))}" y="{fmt(round(hy_ + 0.5, 1))}" width="4" height="7" rx="2" fill="{t["accent"]}"/>'
        f'<rect x="{fmt(round(hx + hr - 4.5, 1))}" y="{fmt(round(hy_ - 3, 1))}" width="9" height="14" rx="4.5" fill="{c["phones"]}"/>'
        f'<rect x="{fmt(round(hx + hr - 2, 1))}" y="{fmt(round(hy_ + 0.5, 1))}" width="4" height="7" rx="2" fill="{t["accent"]}"/>'
        "</g>"
    )

    # Fit the drawing into the requested box.
    xs, ys = [], []
    for wx, wy, wz in ((fx0, fy0, 0), (fx1, fy0, -0.35), (fx1, fy1, -0.35), (fx0, fy1, 0), (1.35, 6.05, top + 2.6), (1.35, 0.95, top + 2.6), (0.68, 6.48, 2.7), (5.5, 3.8, 5.6)):
        sx, sy = P(wx, wy, wz)
        xs.append(sx)
        ys.append(sy)
    bw, bh = max(xs) - min(xs), max(ys) - min(ys)
    k = min(w / bw, h / bh)
    ox = x + (w - bw * k) / 2 - min(xs) * k
    oy = y + (h - bh * k) / 2 - min(ys) * k
    svg = f'<g transform="translate({fmt(round(ox, 2))} {fmt(round(oy, 2))}) scale({k:.4f})">{"".join(parts)}</g>'

    css.append(
        ".scroll{animation:scroll 14s linear infinite}"
        ".bar{transform-box:fill-box;transform-origin:50% 100%;animation:bar 7s ease-in-out infinite}"
        "@keyframes bar{0%,100%{transform:scaleY(.55)}50%{transform:scaleY(1)}}"
        ".tapA{animation:tap 1.6s ease-in-out infinite}.tapB{animation:tap 1.6s ease-in-out -.8s infinite}"
        "@keyframes tap{0%,100%{transform:translateY(0)}50%{transform:translateY(1.6px)}}"
        ".steam{animation:steam 4s ease-in-out infinite;opacity:0}"
        "@keyframes steam{0%{opacity:0;transform:translateY(4px)}35%{opacity:.75}100%{opacity:0;transform:translateY(-8px)}}"
        ".glow{animation:glow 6s ease-in-out infinite;opacity:.15}"
        "@keyframes glow{0%,70%,100%{opacity:.15}80%,90%{opacity:.85}}"
        ".nod{transform-box:fill-box;transform-origin:50% 100%;animation:nod 8s ease-in-out infinite}"
        "@keyframes nod{0%,100%{transform:rotate(0)}50%{transform:rotate(-3deg)}}"
        ".sway{transform-box:fill-box;transform-origin:50% 100%;animation:sway 9s ease-in-out infinite}"
        "@keyframes sway{0%,100%{transform:rotate(-2deg)}50%{transform:rotate(2deg)}}"
    )
    return svg, "".join(css)
