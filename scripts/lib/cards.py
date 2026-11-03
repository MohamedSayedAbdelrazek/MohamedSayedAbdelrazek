"""Static cards: hero banner, `php artisan about` terminal, tech-stack rack, link buttons and footer."""

from __future__ import annotations

import random

import content as C

from .core import animate, document, esc, fmt, mix, mono_width, reveal, text_width
from .icons import TECH, icon

W = 900


# --------------------------------------------------------------------------- #
# Hero
# --------------------------------------------------------------------------- #


def _role_typer(t: dict[str, str], x: float, y: float, size: float) -> tuple[str, str]:
    """Typing / deleting cycle through C.ROLES. Returns (defs, body)."""
    cw = mono_width(1, size)
    type_s, delete_s, hold, gap = 0.055, 0.028, 1.7, 0.35
    starts, cursor = [], []
    clock = 0.3
    for role in C.ROLES:
        starts.append(clock)
        clock += len(role) * type_s + hold + len(role) * delete_s + gap
    dur = clock

    defs, body = [], []
    for i, role in enumerate(C.ROLES):
        s, n = starts[i], len(role)
        frames = [(0.0, 0)]
        for k in range(1, n + 1):
            frames.append((s + k * type_s, k * cw))
        end_hold = s + n * type_s + hold
        for k in range(n - 1, -1, -1):
            frames.append((end_hold + (n - k) * delete_s, k * cw))
        cursor += [(ft, fw) for ft, fw in frames[1:]]
        anim = animate("width", frames, dur, calc="discrete")
        defs.append(
            f'<clipPath id="role{i}"><rect x="{fmt(x)}" y="{fmt(y - size)}" width="0" height="{fmt(size * 1.5)}">{anim}</rect></clipPath>'
        )
        body.append(
            f'<text x="{fmt(x)}" y="{fmt(y)}" class="m" font-size="{size}" fill="{t["text"]}" clip-path="url(#role{i})">{esc(role)}</text>'
        )
    cursor.sort()
    cx = animate("x", [(0.0, fmt(x))] + [(ct, fmt(x + cw_)) for ct, cw_ in cursor], dur, calc="discrete")
    body.append(
        f'<g class="blink"><rect x="{fmt(x)}" y="{fmt(y - size * 0.86)}" width="{fmt(cw * 0.95)}" height="{fmt(size * 1.12)}" '
        f'rx="1.5" fill="{t["accent"]}">{cx}</rect></g>'
    )
    return "".join(defs), "".join(body)


def _lifecycle(t: dict[str, str], x0: float, y0: float, w: float, h: float) -> str:
    """The request-lifecycle card: a packet travels through the stack and comes back as 200 OK."""
    dur = 8.0
    req_start, req_end = 0.3, 3.3
    res_start, res_end = 3.9, 5.7
    pad = 20
    nw, nh = 90.0, 30.0
    gap = (w - 2 * pad - 3 * nw) / 2
    cols = [x0 + pad + i * (nw + gap) for i in range(3)]
    row1, row2 = y0 + 56, y0 + 122
    slots = [(cols[0], row1), (cols[1], row1), (cols[2], row1), (cols[2], row2), (cols[1], row2), (cols[0], row2)]
    centres = [(sx + nw / 2, sy + nh / 2) for sx, sy in slots]

    seg = [abs(centres[i + 1][0] - centres[i][0]) + abs(centres[i + 1][1] - centres[i][1]) for i in range(5)]
    total = sum(seg)
    frac = [sum(seg[:i]) / total for i in range(6)]
    path = "M" + " L".join(f"{fmt(cx)} {fmt(cy)}" for cx, cy in centres)
    back = "M" + " L".join(f"{fmt(cx)} {fmt(cy)}" for cx, cy in reversed(centres))

    out = [
        f'<rect x="{fmt(x0)}" y="{fmt(y0)}" width="{fmt(w)}" height="{fmt(h)}" rx="14" fill="{t["panel"]}" stroke="{t["line"]}"/>',
        f'<text x="{fmt(x0 + pad)}" y="{fmt(y0 + 25)}" class="m" font-size="11" font-weight="700" fill="{t["ok"]}">{C.REQUEST[0]}</text>',
        f'<text x="{fmt(x0 + pad + mono_width(len(C.REQUEST[0]) + 1, 11))}" y="{fmt(y0 + 25)}" class="m" font-size="11" fill="{t["muted"]}">{esc(C.REQUEST[1])}</text>',
        f'<text x="{fmt(x0 + w - pad)}" y="{fmt(y0 + 25)}" text-anchor="end" class="m" font-size="11" fill="{t["dim"]}">HTTP/1.1</text>',
        f'<path d="M{fmt(x0)} {fmt(y0 + 38)}h{fmt(w)}" stroke="{t["line"]}"/>',
    ]

    # Edges (behind the packet and nodes), drawn as flowing dashes.
    out.append(f'<path d="{path}" stroke="{t["line"]}" stroke-width="1.5" fill="none" stroke-dasharray="3 4" class="flow"/>')

    # Packets: request (accent) and response (ok). They travel under the nodes.
    def packet(colour: str, motion_path: str, start: float, end: float) -> str:
        motion = (
            f'<animateMotion dur="{fmt(dur)}s" repeatCount="indefinite" path="{motion_path}" '
            f'keyPoints="0;0;1;1" keyTimes="0;{start / dur:.4f};{end / dur:.4f};1" calcMode="linear"/>'
        )
        vis = animate("opacity", [(0, 0), (start - 0.01, 0), (start, 1), (end, 1), (end + 0.15, 0)], dur)
        return (
            f'<g opacity="0">{vis}<g>{motion}<circle r="11" fill="{colour}" opacity="0.18"/>'
            f'<circle r="4.2" fill="{colour}"/></g></g>'
        )

    out.append(packet(t["accent"], path, req_start, req_end))
    out.append(packet(t["ok"], back, res_start, res_end))

    for i, (name, (sx, sy)) in enumerate(zip(C.LIFECYCLE, slots)):
        arrive = req_start + frac[i] * (req_end - req_start)
        ret = res_start + (1 - frac[i]) * (res_end - res_start)
        tint_a, tint_ok = mix(t["panel"], t["accent"], 0.14), mix(t["panel"], t["ok"], 0.14)
        if i == len(C.LIFECYCLE) - 1:  # the database holds the request while "querying"
            stroke = [(arrive - 0.05, t["line"]), (arrive, t["accent"]), (res_start - 0.05, t["accent"]), (res_start, t["ok"]), (res_start + 0.5, t["line"])]
            fill = [(arrive - 0.05, t["panel"]), (arrive, tint_a), (res_start - 0.05, tint_a), (res_start, tint_ok), (res_start + 0.5, t["panel"])]
        elif i == 0:  # the client lights up green once the response lands
            stroke = [(arrive, t["accent"]), (arrive + 0.5, t["line"]), (ret - 0.05, t["line"]), (ret, t["ok"]), (dur - 0.4, t["ok"]), (dur, t["line"])]
            fill = [(arrive, tint_a), (arrive + 0.5, t["panel"]), (ret - 0.05, t["panel"]), (ret, tint_ok), (dur - 0.4, tint_ok), (dur, t["panel"])]
        else:
            stroke = [(arrive - 0.05, t["line"]), (arrive, t["accent"]), (arrive + 0.5, t["line"]), (ret - 0.05, t["line"]), (ret, t["ok"]), (ret + 0.5, t["line"])]
            fill = [(arrive - 0.05, t["panel"]), (arrive, tint_a), (arrive + 0.5, t["panel"]), (ret - 0.05, t["panel"]), (ret, tint_ok), (ret + 0.5, t["panel"])]
        dot = [(f, t["dim"] if c == t["line"] else c) for f, c in stroke]
        out.append(
            f'<rect x="{fmt(sx)}" y="{fmt(sy)}" width="{fmt(nw)}" height="{fmt(nh)}" rx="8" fill="{t["panel"]}" stroke="{t["line"]}">'
            f"{animate('stroke', stroke, dur)}{animate('fill', fill, dur)}</rect>"
            f'<circle cx="{fmt(sx + 12)}" cy="{fmt(sy + nh / 2)}" r="3" fill="{t["dim"]}">{animate("fill", dot, dur)}</circle>'
            f'<text x="{fmt(sx + 21)}" y="{fmt(sy + nh / 2 + 3.6)}" class="m" font-size="10" fill="{t["muted"]}">{esc(name)}</text>'
        )

    # Status ticker + response.
    sy = y0 + h - 44
    out.append(f'<path d="M{fmt(x0)} {fmt(sy - 18)}h{fmt(w)}" stroke="{t["line"]}"/>')
    phases = [
        ("routing request…", req_start, req_end),
        ("querying database…", req_end, res_start),
        ("building response…", res_start, res_end),
    ]
    for label, a, b in phases:
        vis = animate("opacity", [(0, 0), (a, 1), (b, 0)], dur, calc="discrete")
        out.append(f'<text x="{fmt(x0 + pad)}" y="{fmt(sy)}" class="m" font-size="11" fill="{t["dim"]}" opacity="0">{esc(label)}{vis}</text>')
    shown = animate("opacity", [(0, 0), (res_end, 1), (dur - 0.3, 0)], dur, calc="discrete")
    body_w = mono_width(len(C.RESPONSE_BODY), 11)
    typing = [(0.0, 0)] + [(res_end + 0.1 + k * 0.022, fmt(mono_width(k, 11))) for k in range(1, len(C.RESPONSE_BODY) + 1)]
    typing.append((dur - 0.3, 0))
    out.append(
        f'<g opacity="0">{shown}'
        f'<text x="{fmt(x0 + pad)}" y="{fmt(sy)}" class="m" font-size="11" font-weight="700" fill="{t["ok"]}">200 OK</text>'
        f'<text x="{fmt(x0 + pad + mono_width(7, 11))}" y="{fmt(sy)}" class="m" font-size="11" fill="{t["dim"]}">application/json</text>'
        f'<text x="{fmt(x0 + w - pad)}" y="{fmt(sy)}" text-anchor="end" class="m" font-size="11" fill="{t["muted"]}">38 ms</text>'
        f'<clipPath id="json"><rect x="{fmt(x0 + pad)}" y="{fmt(sy + 8)}" width="0" height="18">{animate("width", typing, dur, calc="discrete")}</rect></clipPath>'
        f'<text x="{fmt(x0 + pad)}" y="{fmt(sy + 22)}" class="m" font-size="11" fill="{t["text"]}" clip-path="url(#json)">{esc(C.RESPONSE_BODY)}</text>'
        "</g>"
    )
    assert body_w < w - 2 * pad, "RESPONSE_BODY is too long for the lifecycle card"
    return "".join(out)


def hero(t: dict[str, str]) -> str:
    H = 400
    pad = 56
    card_w = 336.0
    card_x = W - pad - card_w
    out = [
        "<defs>",
        f'<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1.2" cy="1.2" r="1.2" fill="{t["grid"]}"/></pattern>',
        '<radialGradient id="fade" cx="0.62" cy="0.35" r="0.75"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>',
        f'<mask id="dotmask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>',
        f'<radialGradient id="glowA"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow"]}"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>',
        f'<radialGradient id="glowB"><stop offset="0" stop-color="{t["accent2"]}" stop-opacity="{float(t["glow"]) * 0.6:.2f}"/><stop offset="1" stop-color="{t["accent2"]}" stop-opacity="0"/></radialGradient>',
        f'<linearGradient id="ember" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">'
        f'<stop offset="0" stop-color="{t["accent"]}"/><stop offset="0.42" stop-color="{t["accent2"]}"/>'
        f'<stop offset="0.5" stop-color="{t["shine"]}"/><stop offset="0.58" stop-color="{t["accent2"]}"/><stop offset="1" stop-color="{t["accent"]}"/>'
        '<animateTransform attributeName="gradientTransform" type="translate" values="-700 0;700 0;700 0" keyTimes="0;0.55;1" dur="7s" repeatCount="indefinite"/>'
        "</linearGradient>",
        f'<linearGradient id="mark" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent2"]}"/></linearGradient>',
        f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="20"/></clipPath>',
        f'<clipPath id="nameclip"><rect x="0" y="86" width="{fmt(card_x - 10)}" height="146"/></clipPath>',
    ]

    # Name sizing: shrink if a longer name would run into the lifecycle card.
    name_size = 60.0
    widest = max(text_width(C.NAME_LINE_1, 1, "sans", 800), text_width(C.NAME_LINE_2 + ".", 1, "sans", 800))
    name_size = min(name_size, (card_x - pad - 24) / (widest - 0.03 * max(len(C.NAME_LINE_1), len(C.NAME_LINE_2))))
    tracking = -0.03 * name_size

    role_defs, role_body = _role_typer(t, pad + mono_width(2, 19), 268, 19)
    tag_size = 16.0
    while text_width(C.TAGLINE, tag_size) > card_x - pad - 24 and tag_size > 12:
        tag_size -= 0.5
    out += [role_defs, "</defs>", '<g clip-path="url(#frame)">']
    out += [
        f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>',
        f'<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#dotmask)"/>',
        f'<circle cx="790" cy="30" r="320" fill="url(#glowA)">'
        '<animate attributeName="r" values="300;350;300" dur="9s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"/></circle>',
        f'<circle cx="60" cy="430" r="260" fill="url(#glowB)">'
        '<animate attributeName="r" values="260;220;260" dur="11s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"/></circle>',
        "</g>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="19.5" fill="none" stroke="{t["line"]}"/>',
    ]

    # Top bar: monogram, handle, availability pill.
    out.append(
        f'<g opacity="0">{reveal(0.05)}'
        f'<rect x="{pad}" y="30" width="32" height="32" rx="9" fill="url(#mark)"/>'
        f'<text x="{pad + 16}" y="51" text-anchor="middle" class="s" font-weight="800" font-size="13" fill="#fff" letter-spacing="-0.3">{esc(C.MONOGRAM)}</text>'
        f'<text x="{pad + 46}" y="51" class="m" font-size="13" fill="{t["muted"]}">{esc(C.HANDLE)}</text>'
        "</g>"
    )
    pill_text_w = mono_width(len(C.STATUS), 11)
    pill_w = pill_text_w + 44
    px = W - pad - pill_w
    out.append(
        f'<g opacity="0">{reveal(0.15)}'
        f'<rect x="{fmt(px)}" y="31" width="{fmt(pill_w)}" height="30" rx="15" fill="{mix(t["bg"], t["ok"], 0.1)}" stroke="{mix(t["bg"], t["ok"], 0.4)}"/>'
        f'<circle cx="{fmt(px + 18)}" cy="46" r="4" fill="{t["ok"]}" class="pulse"/>'
        f'<circle cx="{fmt(px + 18)}" cy="46" r="4" fill="{t["ok"]}"/>'
        f'<text x="{fmt(px + 31)}" y="50" class="m" font-size="11" font-weight="700" fill="{t["ok"]}" letter-spacing="0.4">{esc(C.STATUS)}</text>'
        "</g>"
    )

    # Name.
    ease = 'calcMode="spline" keyTimes="0;1" keySplines="0.16 1 0.3 1"'
    out.append('<g clip-path="url(#nameclip)">')
    for i, (line, fill, y) in enumerate([(C.NAME_LINE_1, t["text"], 152), (C.NAME_LINE_2, "url(#ember)", 218)]):
        begin = 0.2 + i * 0.14
        dot = f'<tspan fill="{t["accent"]}">.</tspan>' if i == 1 else ""
        out.append(
            f'<g transform="translate(0 80)"><animateTransform attributeName="transform" type="translate" from="0 80" to="0 0" '
            f'begin="{begin}s" dur="1.1s" fill="freeze" {ease}/>'
            f'<text x="{pad - 3}" y="{y}" class="s" font-weight="800" font-size="{fmt(name_size)}" letter-spacing="{fmt(tracking)}" fill="{fill}">{esc(line)}{dot}</text></g>'
        )
    out.append("</g>")

    # Role typer + tagline.
    out.append(
        f'<g opacity="0">{reveal(0.7)}'
        f'<text x="{pad}" y="268" class="m" font-size="19" font-weight="700" fill="{t["accent"]}">$</text>'
        f"{role_body}"
        f'<text x="{pad}" y="303" class="s" font-size="{fmt(tag_size)}" fill="{t["muted"]}">{esc(C.TAGLINE)}</text>'
        "</g>"
    )

    # Lifecycle card.
    out.append(f'<g opacity="0">{reveal(0.45, dy=10)}{_lifecycle(t, card_x, 84, card_w, 232)}</g>')

    # Bottom strip: core stack chips + location / site.
    out.append(f'<g opacity="0">{reveal(0.9)}<path d="M{pad} 338H{W - pad}" stroke="{t["line"]}"/>')
    cx = pad
    for chip in C.HERO_CHIPS:
        cwid = mono_width(len(chip), 11) + 22
        out.append(
            f'<rect x="{fmt(cx)}" y="352" width="{fmt(cwid)}" height="26" rx="7" fill="{t["raised"]}" stroke="{t["line"]}"/>'
            f'<text x="{fmt(cx + 11)}" y="369" class="m" font-size="11" fill="{t["muted"]}">{esc(chip)}</text>'
        )
        cx += cwid + 8
    site_w = mono_width(len(C.WEBSITE), 11)
    loc_w = mono_width(len(C.LOCATION), 11)
    sx = W - pad - site_w
    out.append(f'<text x="{fmt(sx)}" y="369" class="m" font-size="11" fill="{t["muted"]}">{esc(C.WEBSITE)}</text>')
    out.append(icon("globe", t, sx - 20, 357, 15, t["bg"]))
    lx = sx - 20 - 22 - loc_w
    out.append(f'<text x="{fmt(lx)}" y="369" class="m" font-size="11" fill="{t["muted"]}">{esc(C.LOCATION)}</text>')
    out.append(
        f'<path d="M{fmt(lx - 11)} 371.5c-3.6-4-5.4-6.9-5.4-9.2a5.4 5.4 0 0 1 10.8 0c0 2.3-1.8 5.2-5.4 9.2z" fill="none" stroke="{t["accent"]}" stroke-width="1.6"/>'
        f'<circle cx="{fmt(lx - 11)}" cy="362.4" r="1.8" fill="{t["accent"]}"/>'
    )
    out.append("</g>")
    assert cx < lx - 30, "HERO_CHIPS collide with the location label"

    css = (
        ".flow{animation:flow 1.2s linear infinite}@keyframes flow{to{stroke-dashoffset:-14}}"
    )
    return document(
        W,
        H,
        "".join(out),
        title=f"{C.FULL_NAME} — {C.ROLES[0]}",
        desc=f"{C.TAGLINE} Animated banner showing a request flowing through {' → '.join(C.LIFECYCLE)}.",
        fonts=[("sans", 400), ("sans", 800), ("mono", 400), ("mono", 700)],
        css=css,
    )


# --------------------------------------------------------------------------- #
# Terminal: php artisan about
# --------------------------------------------------------------------------- #


def terminal(t: dict[str, str]) -> str:
    size, lh, cols = 14, 20, 100
    cw = mono_width(1, size)
    left, top_bar = 30, 42
    first = top_bar + 34
    dur = 28.0
    type_start, per_char = 0.6, 0.045
    command = "php artisan about --only=developer"

    prompt = [
        ("mohamed", t["ok"], 700),
        ("@", t["dim"], 400),
        ("backend", t["accent2"], 700),
        (" ~/profile", t["info"], 400),
        (" git:(", t["dim"], 400),
        ("main", t["accent"], 400),
        (")", t["dim"], 400),
        (" $ ", t["text"], 400),
    ]
    prompt_len = sum(len(s) for s, _, _ in prompt)

    def segs(row: int, parts: list[tuple[int, str, str, int]]) -> str:
        y = first + row * lh
        return "".join(
            f'<text x="{fmt(left + col * cw)}" y="{y}" class="m" font-size="{size}" font-weight="{wt}" fill="{fill}" xml:space="preserve">{esc(s)}</text>'
            for col, s, fill, wt in parts
        )

    def prompt_parts() -> list[tuple[int, str, str, int]]:
        parts, col = [], 0
        for s, fill, wt in prompt:
            parts.append((col, s, fill, wt))
            col += len(s)
        return parts

    # Build output rows.
    rows: list[list[tuple[int, str, str, int]]] = [[]]  # blank after the command
    for section, items in C.ABOUT:
        dots = cols - 2 - len(section) - 1
        rows.append([(2, section, t["ok"], 700), (3 + len(section), "." * dots, t["dim"], 400)])
        for key, value, style in items:
            n = cols - 2 - len(key) - len(value) - 2
            assert n >= 3, f"about line too long: {key}"
            colour = {"ok": t["ok"], "link": t["accent2"]}.get(style or "", t["text"])
            rows.append(
                [
                    (2, key, t["text"], 400),
                    (3 + len(key), "." * n, t["dim"], 400),
                    (cols - len(value), value, colour, 700 if style == "ok" else 400),
                ]
            )
        rows.append([])
    total_rows = 1 + len(rows) + 1
    H = first + (total_rows - 1) * lh + 26

    out = [
        "<defs>",
        f'<clipPath id="win"><rect width="{W}" height="{H}" rx="14"/></clipPath>',
    ]
    type_end = type_start + len(command) * per_char
    typing = [(0.0, 0)] + [(type_start + k * per_char, fmt(k * cw)) for k in range(1, len(command) + 1)] + [(dur - 0.8, 0)]
    out.append(
        f'<clipPath id="cmd"><rect x="{fmt(left + prompt_len * cw)}" y="{first - lh + 4}" width="0" height="{lh}">'
        f'{animate("width", typing, dur, calc="discrete")}</rect></clipPath>'
    )
    out.append("</defs>")
    out.append(
        f'<g clip-path="url(#win)"><rect width="{W}" height="{H}" fill="{t["panel"]}"/>'
        f'<rect width="{W}" height="{top_bar}" fill="{t["raised"]}"/>'
        f'<path d="M0 {top_bar}.5H{W}" stroke="{t["line"]}"/></g>'
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="13.5" fill="none" stroke="{t["line"]}"/>'
    )
    for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
        out.append(f'<circle cx="{22 + i * 20}" cy="21" r="6" fill="{c}"/>')
    out.append(
        f'<text x="{W / 2}" y="25.5" text-anchor="middle" class="m" font-size="12" fill="{t["dim"]}">mohamed@backend: ~/profile</text>'
        f'<text x="{W - 22}" y="25.5" text-anchor="end" class="m" font-size="11" fill="{t["dim"]}">zsh · {cols}×{total_rows}</text>'
    )

    fade = animate("opacity", [(0, 1), (dur - 1.4, 1), (dur - 0.8, 0), (dur, 0)], dur)
    out.append(f"<g>{fade}")
    out.append(segs(0, prompt_parts()))
    out.append(
        f'<text x="{fmt(left + prompt_len * cw)}" y="{first}" class="m" font-size="{size}" fill="{t["text"]}" clip-path="url(#cmd)">{esc(command)}</text>'
    )
    print_start, per_row = type_end + 0.35, 0.07
    for r, parts in enumerate(rows, start=1):
        if not parts:
            continue
        at = print_start + r * per_row
        vis = animate("opacity", [(0, 0), (at, 1)], dur, calc="discrete")
        out.append(f'<g opacity="0">{vis}{segs(r, parts)}</g>')
    last = len(rows) + 1
    final_at = print_start + last * per_row + 0.2
    vis = animate("opacity", [(0, 0), (final_at, 1)], dur, calc="discrete")
    out.append(f'<g opacity="0">{vis}{segs(last, prompt_parts())}</g>')
    out.append("</g>")

    # Cursor: follows typing, hides while output prints, then idles on the last prompt.
    cx = [(0.0, fmt(left + prompt_len * cw))] + [(type_start + k * per_char, fmt(left + (prompt_len + k) * cw)) for k in range(1, len(command) + 1)]
    cx += [(final_at, fmt(left + prompt_len * cw))]
    cy = [(0.0, first - lh + 5), (final_at, first + (last - 1) * lh + 5)]
    cop = [(0.0, 1), (type_end + 0.3, 0), (final_at, 1), (dur - 0.8, 0)]
    out.append(
        f'<g class="blink"><rect x="0" y="0" width="{fmt(cw)}" height="{lh - 2}" rx="1.5" fill="{t["accent"]}" opacity="0.9">'
        f'{animate("x", cx, dur, calc="discrete")}{animate("y", cy, dur, calc="discrete")}{animate("opacity", cop, dur, calc="discrete")}</rect></g>'
    )
    return document(
        W,
        H,
        "".join(out),
        title="php artisan about — Mohamed Sayed",
        desc="Terminal running php artisan about, listing profile, stack, mindset and contact details. "
        + " ".join(f"{k}: {v}." for _, items in C.ABOUT for k, v, _ in items),
        fonts=[("mono", 400), ("mono", 700)],
    )


# --------------------------------------------------------------------------- #
# Tech stack rack
# --------------------------------------------------------------------------- #


def stack(t: dict[str, str]) -> str:
    rng = random.Random(7)
    rack_x, rack_w = 24, W - 48
    rail = 24
    unit_x, unit_w = rack_x + rail + 8, rack_w - 2 * rail - 16
    unit_h, unit_gap, top = 62, 8, 92
    H = top + len(C.STACK) * (unit_h + unit_gap) - unit_gap + 12 + 24
    rack_top, rack_bottom = top - 12, H - 24
    chip_font, chip_h = 13, 36
    left_block = 168
    eq_bars, eq_w, eq_gap = 7, 4, 5
    eq_span = eq_bars * eq_w + (eq_bars - 1) * eq_gap

    out = [
        "<defs>",
        f'<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{t["accent"]}" stop-opacity="0.09"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></linearGradient>',
        f'<linearGradient id="eq" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent2"]}"/></linearGradient>',
        f'<linearGradient id="mark" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent2"]}"/></linearGradient>',
        f'<clipPath id="rackclip"><rect x="{unit_x}" y="{rack_top}" width="{unit_w}" height="{rack_bottom - rack_top}"/></clipPath>',
        "</defs>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="19.5" fill="{t["bg"]}" stroke="{t["line"]}"/>',
    ]
    # Header.
    out.append(
        f'<rect x="{rack_x + 4}" y="24" width="28" height="28" rx="8" fill="url(#mark)"/>'
        + "".join(
            f'<rect x="{rack_x + 11}" y="{31 + k * 5}" width="14" height="3" rx="1.5" fill="#fff" opacity="{0.95 - k * 0.25:.2f}"/>'
            for k in range(3)
        )
        + f'<text x="{rack_x + 44}" y="44" class="s" font-size="19" font-weight="600" fill="{t["text"]}">Tech Stack</text>'
        f'<text x="{rack_x + 44 + text_width("Tech Stack", 19, "sans", 600) + 12}" y="43.5" class="m" font-size="11" fill="{t["dim"]}">rack-01 · {len(C.STACK)} units</text>'
    )
    status = "all systems operational"
    sw = mono_width(len(status), 11)
    out.append(
        f'<circle cx="{fmt(W - rack_x - sw - 16)}" cy="39.5" r="3.6" fill="{t["ok"]}" class="pulse"/>'
        f'<circle cx="{fmt(W - rack_x - sw - 16)}" cy="39.5" r="3.6" fill="{t["ok"]}"/>'
        f'<text x="{W - rack_x - 4}" y="43.5" text-anchor="end" class="m" font-size="11" fill="{t["muted"]}">{status}</text>'
    )

    # Rack frame and rails.
    out.append(
        f'<rect x="{rack_x}" y="{rack_top}" width="{rack_w}" height="{rack_bottom - rack_top}" rx="12" fill="{t["raised"]}" stroke="{t["line"]}"/>'
    )
    for rx in (rack_x + 4, rack_x + rack_w - rail + 4):
        out.append(f'<rect x="{rx}" y="{rack_top + 6}" width="{rail - 8}" height="{rack_bottom - rack_top - 12}" rx="5" fill="{t["panel"]}" stroke="{t["line"]}"/>')
        for i in range(len(C.STACK)):
            uy = top + i * (unit_h + unit_gap)
            for hy in (uy + 12, uy + unit_h - 12):
                out.append(f'<circle cx="{rx + (rail - 8) / 2}" cy="{hy}" r="2.6" fill="{t["bg"]}" stroke="{t["line"]}"/>')

    for i, (unit, caption, keys) in enumerate(C.STACK):
        uy = top + i * (unit_h + unit_gap)
        g = [f'<g opacity="0">{reveal(0.15 + i * 0.12, dy=6, dur=0.6)}']
        g.append(f'<rect x="{unit_x}" y="{uy}" width="{unit_w}" height="{unit_h}" rx="9" fill="{t["panel"]}" stroke="{t["line"]}"/>')
        g.append(
            f'<text x="{unit_x + 16}" y="{uy + 27}" class="m" font-size="10" fill="{t["dim"]}">U{i + 1:02d}</text>'
            f'<text x="{unit_x + 44}" y="{uy + 27}" class="m" font-size="11.5" font-weight="700" fill="{t["text"]}">{esc(unit)}</text>'
            f'<text x="{unit_x + 16}" y="{uy + 45}" class="m" font-size="10" fill="{t["dim"]}">{esc(caption)}</text>'
        )
        # LEDs.
        lx = unit_x + left_block - 16
        for k, colour in enumerate((t["ok"], t["warn"])):
            d = rng.uniform(0.7, 2.6)
            delay = rng.uniform(0, 2)
            g.append(
                f'<circle cx="{lx}" cy="{uy + 23 + k * 16}" r="3.2" fill="{colour}" class="led" style="animation-duration:{d:.2f}s;animation-delay:-{delay:.2f}s"/>'
            )
        g.append(f'<path d="M{unit_x + left_block} {uy + 12}v{unit_h - 24}" stroke="{t["line"]}"/>')

        # Chips. A crowded unit first gives up its activity meter, and only then shrinks its labels.
        chips_x0 = unit_x + left_block + 16

        def chip_widths(size: float) -> list[float]:
            return [34 + text_width(TECH[k][0], size, "sans", 600) + 12 for k in keys]

        def fits(size: float, room: float) -> bool:
            return chips_x0 + sum(chip_widths(size)) + 10 * (len(keys) - 1) <= room

        with_meter = unit_x + unit_w - 16 - eq_span - 24
        meter = fits(chip_font, with_meter)
        font = chip_font
        while not fits(font, with_meter if meter else unit_x + unit_w - 16) and font > 10:
            font -= 0.5
        widths = chip_widths(font)
        cx = chips_x0
        cy = uy + (unit_h - chip_h) / 2
        for key, cwid in zip(keys, widths):
            g.append(
                f'<rect x="{fmt(cx)}" y="{fmt(cy)}" width="{fmt(cwid)}" height="{chip_h}" rx="9" fill="{t["raised"]}" stroke="{t["line"]}"/>'
                + icon(key, t, cx + 10, cy + 9, 18, t["raised"])
                + f'<text x="{fmt(cx + 35)}" y="{fmt(cy + chip_h / 2 + font * 0.36)}" class="s" font-size="{fmt(font)}" font-weight="600" fill="{t["text"]}">{esc(TECH[key][0])}</text>'
            )
            cx += cwid + 10

        # Activity meter.
        ex = unit_x + unit_w - 16 - eq_span
        base = uy + unit_h - 15
        for b in range(eq_bars if meter else 0):
            hs = [rng.uniform(4, 30) for _ in range(6)]
            hs.append(hs[0])
            d = rng.uniform(1.6, 3.2)
            vals_h = ";".join(f"{h:.1f}" for h in hs)
            vals_y = ";".join(f"{base - h:.1f}" for h in hs)
            g.append(
                f'<rect x="{ex + b * (eq_w + eq_gap)}" y="{base - hs[0]:.1f}" width="{eq_w}" height="{hs[0]:.1f}" rx="1.5" fill="url(#eq)" opacity="0.85">'
                f'<animate attributeName="height" values="{vals_h}" dur="{d:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="y" values="{vals_y}" dur="{d:.2f}s" repeatCount="indefinite"/></rect>'
            )
        if meter:
            g.append(f'<path d="M{ex - 2} {base + 0.5}h{eq_span + 4}" stroke="{t["line"]}"/>')
        g.append("</g>")
        out.append("".join(g))

    # Scanning light sweeping down the rack.
    band = 90
    out.append(
        f'<g clip-path="url(#rackclip)"><rect x="{unit_x}" y="{rack_top - band}" width="{unit_w}" height="{band}" fill="url(#scan)">'
        f'<animate attributeName="y" values="{rack_top - band};{rack_bottom};{rack_bottom}" keyTimes="0;0.6;1" dur="7s" repeatCount="indefinite"/></rect></g>'
    )
    css = ".led{animation:led 1.4s steps(2,jump-none) infinite}@keyframes led{0%{opacity:1}50%{opacity:.22}100%{opacity:1}}"
    every = ", ".join(TECH[k][0] for _, _, keys in C.STACK for k in keys)
    return document(
        W,
        H,
        "".join(out),
        title="Tech stack",
        desc=f"Server rack showing the technologies I work with: {every}.",
        fonts=[("sans", 600), ("sans", 800), ("mono", 400), ("mono", 700)],
        css=css,
    )


# --------------------------------------------------------------------------- #
# Link buttons
# --------------------------------------------------------------------------- #


def button(t: dict[str, str], link: dict[str, str], index: int) -> str:
    h = 58
    w = max(
        max(text_width(l["label"], 15, "sans", 600), mono_width(len(l["sub"]), 11)) for l in C.LINKS
    ) + 62 + 36
    w = round(w)
    period = 6.0
    start = 1.0 + index * 0.6
    out = [
        "<defs>",
        f'<linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["text"]}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{t["text"]}" stop-opacity="0.09"/><stop offset="1" stop-color="{t["text"]}" stop-opacity="0"/></linearGradient>',
        f'<clipPath id="bc"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="13"/></clipPath>',
        "</defs>",
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="13.5" fill="{t["panel"]}" stroke="{t["line"]}"/>',
        f'<rect x="12" y="12" width="34" height="34" rx="9" fill="{t["raised"]}" stroke="{t["line"]}"/>',
        icon(link["icon"], t, 19, 19, 20, t["raised"]),
        f'<text x="60" y="27" class="s" font-size="15" font-weight="600" fill="{t["text"]}">{esc(link["label"])}</text>',
        f'<text x="60" y="44" class="m" font-size="11" fill="{t["dim"]}">{esc(link["sub"])}</text>',
        f'<g transform="translate({w - 26} {h / 2 - 5})"><path d="M0 0l5 5-5 5" fill="none" stroke="{t["muted"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<animateTransform attributeName="transform" type="translate" values="{w - 26} {h / 2 - 5};{w - 22} {h / 2 - 5};{w - 26} {h / 2 - 5}" dur="1.8s" repeatCount="indefinite"/></g>',
        f'<g clip-path="url(#bc)"><rect x="-120" y="0" width="110" height="{h}" fill="url(#sh)" transform="skewX(-18)">'
        f'<animate attributeName="x" values="-120;-120;{w + 40};{w + 40}" keyTimes="0;{start / (period + start):.3f};{(start + 1.2) / (period + start):.3f};1" dur="{period + start}s" repeatCount="indefinite"/></rect></g>',
    ]
    return document(
        w,
        h,
        "".join(out),
        title=link["label"],
        desc=f'{link["label"]}: {link["sub"]}',
        fonts=[("sans", 600), ("sans", 800), ("mono", 400), ("mono", 700)],
    )


# --------------------------------------------------------------------------- #
# Footer
# --------------------------------------------------------------------------- #


def footer(t: dict[str, str]) -> str:
    H = 190
    dur = 14.0
    left = 40
    out = [
        "<defs>",
        f'<linearGradient id="ember" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent2"]}"/></linearGradient>',
        "</defs>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="19.5" fill="{t["bg"]}" stroke="{t["line"]}"/>',
    ]
    # Giant outlined status code that draws itself.
    big = 'x="862" y="160" text-anchor="end" class="s" font-size="150" font-weight="800" letter-spacing="-6"'
    out.append(f'<text {big} fill="none" stroke="{t["line"]}" stroke-width="1.4">200</text>')
    out.append(
        f'<text {big} fill="none" stroke="url(#ember)" stroke-width="1.6" stroke-dasharray="1400" stroke-dashoffset="1400">200'
        f'{animate("stroke-dashoffset", [(0, 1400), (0.4, 1400), (4.2, 0), (dur - 1.6, 0), (dur - 0.4, -1400), (dur, -1400)], dur)}</text>'
    )

    # Response headers, typed one after another.
    clock = 0.4
    for i, (k, v) in enumerate(C.FOOTER_HEADERS):
        y = 50 + i * 24
        n = len(k) + 1 + len(v)
        frames = [(0.0, 0)] + [(clock + j * 0.03, fmt(mono_width(j, 13))) for j in range(1, n + 1)] + [(dur - 0.5, 0)]
        clock += n * 0.03 + 0.25
        kc, vc, kw = (t["ok"], t["text"], 700) if i == 0 else (t["dim"], t["muted"], 400)
        out.append(
            f'<clipPath id="h{i}"><rect x="{left}" y="{y - 16}" width="0" height="22">{animate("width", frames, dur, calc="discrete")}</rect></clipPath>'
            f'<g clip-path="url(#h{i})"><text x="{left}" y="{y}" class="m" font-size="13" font-weight="{kw}" fill="{kc}">{esc(k)}</text>'
            f'<text x="{fmt(left + mono_width(len(k) + 1, 13))}" y="{y}" class="m" font-size="13" font-weight="{kw if i == 0 else 400}" fill="{vc}">{esc(v)}</text></g>'
        )

    # Sign-off line with the key word highlighted.
    line = C.FOOTER_LINE
    word = "reliable"
    before, _, after = line.partition(word)
    size = 26
    w_before = text_width(before, size, "sans", 800, -0.5)
    w_word = text_width(word, size, "sans", 800, -0.5)
    y = 152
    out.append(
        f'<g opacity="0">{reveal(clock, dy=8)}'
        f'<text x="{left}" y="{y}" class="s" font-size="{size}" font-weight="800" letter-spacing="-0.5" fill="{t["text"]}">{esc(before)}'
        f'<tspan fill="url(#ember)">{esc(word)}</tspan>{esc(after)}</text>'
        f'<path d="M{fmt(left + w_before)} {y + 10}h{fmt(w_word)}" stroke="url(#ember)" stroke-width="3" stroke-linecap="round" '
        f'stroke-dasharray="{fmt(w_word)}" stroke-dashoffset="{fmt(w_word)}">'
        f'{animate("stroke-dashoffset", [(0, fmt(w_word)), (clock + 0.5, fmt(w_word)), (clock + 1.3, 0), (dur - 0.6, 0), (dur, fmt(w_word))], dur)}</path>'
        "</g>"
    )
    return document(
        W,
        H,
        "".join(out),
        title="HTTP/1.1 200 OK",
        desc=f"{line} Thanks for visiting.",
        fonts=[("sans", 800), ("mono", 400), ("mono", 700)],
    )
