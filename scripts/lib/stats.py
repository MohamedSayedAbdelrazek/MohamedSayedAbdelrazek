"""Live GitHub activity dashboard: fetch from the GraphQL API, render as an animated SVG."""

from __future__ import annotations

import datetime as dt
import json
import random
import urllib.request
from collections import Counter

from .core import document, esc, fmt, mix, readable, reveal, text_width

W = 900
API = "https://api.github.com/graphql"

QUERY = """
query($login: String!, $after: String) {
  user(login: $login) {
    login
    pullRequests { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
    repositories(first: 100, after: $after, ownerAffiliations: OWNER, privacy: PUBLIC) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        isFork
        stargazerCount
        languages(first: 12, orderBy: { field: SIZE, direction: DESC }) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #


def _post(token: str, variables: dict) -> dict:
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise RuntimeError(f"GitHub API error: {payload['errors']}")
    return payload["data"]["user"]


def fetch(login: str, token: str) -> dict:
    user = _post(token, {"login": login, "after": None})
    repos = list(user["repositories"]["nodes"])
    page = user["repositories"]["pageInfo"]
    while page["hasNextPage"]:
        more = _post(token, {"login": login, "after": page["endCursor"]})["repositories"]
        repos += more["nodes"]
        page = more["pageInfo"]

    cc = user["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    languages: Counter[str] = Counter()
    colours: dict[str, str] = {}
    for repo in repos:
        if repo["isFork"]:
            continue
        for edge in repo["languages"]["edges"]:
            languages[edge["node"]["name"]] += edge["size"]
            if edge["node"]["color"]:
                colours[edge["node"]["name"]] = edge["node"]["color"]
    return summarise(
        login=user["login"],
        days=[(d["date"], d["contributionCount"]) for d in days],
        commits=cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        prs=user["pullRequests"]["totalCount"],
        stars=sum(r["stargazerCount"] for r in repos if not r["isFork"]),
        repos=user["repositories"]["totalCount"],
        total=cc["contributionCalendar"]["totalContributions"],
        languages=[(name, size, colours.get(name, "#8B8B95")) for name, size in languages.most_common()],
    )


def mock(login: str) -> dict:
    """Deterministic fake data for local previews (never published)."""
    rng = random.Random(42)
    today = dt.date.today()
    start = today - dt.timedelta(days=today.weekday() + 1 + 52 * 7)
    days = []
    d = start
    while d <= today:
        busy = 0.55 + 0.4 * ((d - start).days / 371)
        n = 0 if rng.random() > busy else int(rng.expovariate(0.28))
        days.append((d.isoformat(), n))
        d += dt.timedelta(days=1)
    langs = [("C#", 412000, "#178600"), ("PHP", 301000, "#4F5D95"), ("Blade", 120000, "#f7523f"), ("JavaScript", 96000, "#f1e05a"), ("CSS", 61000, "#663399"), ("HTML", 40000, "#e34c26"), ("Python", 12000, "#3572A5")]
    return summarise(login=login, days=days, commits=612, prs=23, stars=19, repos=16, total=sum(n for _, n in days), languages=langs)


def summarise(*, login, days, commits, prs, stars, repos, total, languages) -> dict:
    counts = [n for _, n in days]
    # Current streak: today may still be empty, so start counting from yesterday in that case.
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:
        i -= 1
    current = 0
    while i >= 0 and counts[i] > 0:
        current += 1
        i -= 1
    longest = run = 0
    for n in counts:
        run = run + 1 if n else 0
        longest = max(longest, run)
    best_date, best = max(days, key=lambda d: d[1]) if days else ("", 0)
    weekday_totals = Counter()
    for date, n in days:
        weekday_totals[dt.date.fromisoformat(date).strftime("%A")] += n
    busiest = weekday_totals.most_common(1)[0][0] if weekday_totals else "-"
    lang_total = sum(size for _, size, _ in languages) or 1
    return {
        "login": login,
        "days": days,
        "total": total,
        "commits": commits,
        "prs": prs,
        "stars": stars,
        "repos": repos,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best_date, "count": best},
        "busiest_weekday": busiest,
        "active_days": sum(1 for n in counts if n),
        "languages": [(name, size / lang_total, colour) for name, size, colour in languages],
        "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #


def _odometer(t: dict[str, str], value: int, x: float, y: float, size: float, uid: str, begin: float) -> str:
    """Digits roll into place once, like a mechanical counter (each digit sits in a fixed-width cell)."""
    text = f"{value:,}"
    digit_w = max(text_width(str(d), size, "sans", 600) for d in range(10))
    comma_w = text_width(",", size, "sans", 600)
    lh = size * 1.25
    total = sum(digit_w if ch.isdigit() else comma_w for ch in text)
    out = [f'<clipPath id="{uid}"><rect x="{fmt(x - 2)}" y="{fmt(y - size)}" width="{fmt(total + 4)}" height="{fmt(size * 1.3)}"/></clipPath>']
    out.append(f'<g clip-path="url(#{uid})">')
    cx = x
    digit_index = 0
    for ch in text:
        if not ch.isdigit():
            out.append(f'<text x="{fmt(cx)}" y="{fmt(y)}" class="s" font-size="{size}" font-weight="600" fill="{t["text"]}">{ch}</text>')
            cx += comma_w
            continue
        mid = cx + digit_w / 2
        target = 10 + int(ch)  # roll through a full turn before landing
        strip = "".join(
            f'<text x="{fmt(mid)}" y="{fmt(y + k * lh)}" text-anchor="middle" class="s" font-size="{size}" font-weight="600" fill="{t["text"]}">{k % 10}</text>'
            for k in range(target + 1)
        )
        delay = begin + digit_index * 0.08
        out.append(
            f'<g transform="translate(0 {fmt(-target * lh)})">'
            f'<animateTransform attributeName="transform" type="translate" from="0 0" to="0 {fmt(-target * lh)}" begin="{fmt(delay)}s" dur="1.6s" '
            f'fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.12 0.9 0.2 1"/>{strip}</g>'
        )
        cx += digit_w
        digit_index += 1
    out.append("</g>")
    return "".join(out)


def _panel(t: dict[str, str], x: float, y: float, w: float, h: float) -> str:
    return f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="14" fill="{t["panel"]}" stroke="{t["line"]}"/>'


def dashboard(t: dict[str, str], data: dict) -> str:
    pad = 28
    inner = W - 2 * pad
    out: list[str] = []

    # Header.
    title_w = text_width("Activity Monitor", 24, "sans", 600)
    out.append(
        f'<rect x="{pad}" y="34" width="4" height="26" rx="2" fill="{t["accent"]}"/>'
        f'<text x="{pad + 16}" y="58" class="s" font-size="24" font-weight="600" fill="{t["text"]}">Activity Monitor</text>'
        f'<text x="{fmt(pad + 16 + title_w + 14)}" y="57" class="s" font-size="14" fill="{t["dim"]}">github.com/{esc(data["login"])}</text>'
        f'<text x="{W - pad}" y="57" text-anchor="end" class="s" font-size="13" fill="{t["dim"]}">Updated {esc(data["generated"])}</text>'
    )

    # KPI tiles.
    tiles = [
        ("Contributions", data["total"], "last 12 months"),
        ("Commits", data["commits"], "last 12 months"),
        ("Pull requests", data["prs"], "all time"),
        ("Public repos", data["repos"], "owned"),
        ("Stars earned", data["stars"], "across repos"),
    ]
    gap = 12
    tw = (inner - gap * (len(tiles) - 1)) / len(tiles)
    ty, th = 86, 108
    for i, (label, value, sub) in enumerate(tiles):
        x = pad + i * (tw + gap)
        out.append(
            f'<g opacity="0">{reveal(0.1 + i * 0.07, dy=6, dur=0.5)}'
            + _panel(t, x, ty, tw, th)
            + f'<text x="{fmt(x + 18)}" y="{ty + 30}" class="s" font-size="14" font-weight="600" fill="{t["muted"]}">{label}</text>'
            + _odometer(t, value, x + 18, ty + 70, 32, f"odo{i}", 0.3 + i * 0.1)
            + f'<text x="{fmt(x + 18)}" y="{ty + 92}" class="s" font-size="13" fill="{t["dim"]}">{sub}</text>'
            "</g>"
        )

    # Heatmap.
    hy = ty + th + 14
    hh = 236
    out.append(_panel(t, pad, hy, inner, hh))
    out.append(
        f'<text x="{pad + 22}" y="{hy + 34}" class="s" font-size="17" font-weight="600" fill="{t["text"]}">Contributions in the last year</text>'
        f'<text x="{W - pad - 22}" y="{hy + 34}" text-anchor="end" class="s" font-size="14" fill="{t["muted"]}">'
        f'<tspan fill="{t["text"]}" font-weight="600">{data["total"]:,}</tspan> contributions · {data["active_days"]} active days</text>'
    )
    days = data["days"]
    first = dt.date.fromisoformat(days[0][0]) if days else dt.date.today()
    offset = (first.weekday() + 1) % 7  # GitHub weeks start on Sunday
    cell, step = 11, 14
    weeks = (offset + len(days) + 6) // 7
    grid_w = weeks * step - (step - cell)
    label_col = 40
    gx = pad + 22 + label_col + max(0, (inner - 44 - label_col - grid_w) / 2)
    gy = hy + 76
    levels = [mix(t["raised"], t["line"], 0.6)] + [mix(t["raised"], t["accent"], a) for a in (0.3, 0.6, 1.0)] + [t["accent2"]]
    # Quartiles of the active days, like GitHub's own graph, so a single huge day doesn't flatten the rest.
    active = sorted(n for _, n in days if n)
    cuts = [active[min(len(active) - 1, int(len(active) * q))] for q in (0.25, 0.5, 0.75)] if active else [1, 2, 3]

    def level(n: int) -> int:
        if n == 0:
            return 0
        return 1 + sum(n > c for c in cuts)

    month_seen = set()
    last_label_x = -100.0
    for idx, (date, n) in enumerate(days):
        pos = idx + offset
        col, row = divmod(pos, 7)
        x = gx + col * step
        y = gy + row * step
        d = dt.date.fromisoformat(date)
        if d.day <= 7 and row == 0 or (idx == 0 and d.day <= 20):
            key = (d.year, d.month)
            if key not in month_seen and col < weeks - 2 and x - last_label_x > 34:
                month_seen.add(key)
                last_label_x = x
                out.append(f'<text x="{fmt(x)}" y="{gy - 12}" class="s" font-size="13" fill="{t["dim"]}">{d.strftime("%b")}</text>')
        out.append(
            f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{cell}" height="{cell}" rx="2.6" fill="{levels[level(n)]}" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{0.6 + col * 0.02 + row * 0.01:.3f}s" dur="0.4s" fill="freeze"/>'
            f"<title>{date}: {n}</title></rect>"
        )
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="{fmt(gx - 10)}" y="{fmt(gy + row * step + 10)}" text-anchor="end" class="s" font-size="13" fill="{t["dim"]}">{name}</text>')
    # Legend + highlights.
    ly = gy + 7 * step + 22
    less_w = text_width("Less", 13)
    lx = gx + grid_w - text_width("More", 13) - 8 - 5 * step
    out.append(f'<text x="{fmt(lx - 8)}" y="{ly + 10}" text-anchor="end" class="s" font-size="13" fill="{t["dim"]}">Less</text>')
    for k, c in enumerate(levels):
        out.append(f'<rect x="{fmt(lx + k * step)}" y="{ly}" width="{cell}" height="{cell}" rx="2.6" fill="{c}"/>')
    out.append(f'<text x="{fmt(lx + 5 * step + 5)}" y="{ly + 10}" class="s" font-size="13" fill="{t["dim"]}">More</text>')
    best = data["best_day"]
    if best["count"]:
        bd = dt.date.fromisoformat(best["date"]).strftime("%b %d, %Y")
        peak = f'Best day: <tspan fill="{t["text"]}">{best["count"]} on {bd}</tspan>   ·   Busiest weekday: <tspan fill="{t["text"]}">{data["busiest_weekday"]}</tspan>'
        out.append(f'<text x="{fmt(gx)}" y="{ly + 10}" class="s" font-size="13" fill="{t["dim"]}" xml:space="preserve">{peak}</text>')
    assert lx - 8 - less_w > gx + 400, "heatmap legend collides with the highlights"

    # Bottom row: languages + streaks.
    by = hy + hh + 14
    bh = 204
    lw = 512
    out.append(_panel(t, pad, by, lw, bh))
    out.append(f'<text x="{pad + 22}" y="{by + 34}" class="s" font-size="17" font-weight="600" fill="{t["text"]}">Languages</text>')
    out.append(f'<text x="{pad + lw - 22}" y="{by + 34}" text-anchor="end" class="s" font-size="13" fill="{t["dim"]}">by code size in public repos</text>')
    langs = data["languages"][:6]
    if len(data["languages"]) > 6:
        langs = langs[:5]
        langs.append(("Other", 1 - sum(p for _, p, _ in langs), t["dim"]))
    bar_x, bar_y, bar_w = pad + 22, by + 54, lw - 44
    out.append(f'<clipPath id="barclip"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="10" rx="5"/></clipPath>')
    out.append(f'<g clip-path="url(#barclip)"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="10" fill="{t["raised"]}"/>')
    cx = bar_x
    for k, (name, share, colour) in enumerate(langs):
        seg = bar_w * share
        colour = readable(colour, t["panel"], 2.2)
        out.append(
            f'<rect x="{fmt(cx)}" y="{bar_y}" width="0" height="10" fill="{colour}">'
            f'<animate attributeName="width" from="0" to="{fmt(max(seg - 2, 0.5))}" begin="{0.9 + k * 0.12:.2f}s" dur="0.8s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/></rect>'
        )
        cx += seg
    out.append("</g>")
    col_w = (lw - 44) / 2
    for k, (name, share, colour) in enumerate(langs):
        col, row = divmod(k, 3)
        x = pad + 22 + col * col_w
        y = by + 104 + row * 32
        colour = readable(colour, t["panel"], 2.2)
        out.append(
            f'<g opacity="0">{reveal(1.0 + k * 0.08)}<circle cx="{fmt(x + 5)}" cy="{y - 5}" r="5" fill="{colour}"/>'
            f'<text x="{fmt(x + 18)}" y="{y}" class="s" font-size="15" font-weight="600" fill="{t["text"]}">{esc(name)}</text>'
            f'<text x="{fmt(x + col_w - 28)}" y="{y}" text-anchor="end" class="s" font-size="14" fill="{t["muted"]}">{share * 100:.1f}%</text></g>'
        )

    sx = pad + lw + 12
    sw2 = W - pad - sx
    out.append(_panel(t, sx, by, sw2, bh))
    out.append(f'<text x="{sx + 22}" y="{by + 34}" class="s" font-size="17" font-weight="600" fill="{t["text"]}">Streaks</text>')
    # Ring: current vs longest.
    r = 40
    rcx, rcy = sx + 22 + r + 5, by + 48 + (bh - 48) / 2
    circ = 2 * 3.14159265 * r
    ratio = data["current_streak"] / data["longest_streak"] if data["longest_streak"] else 0
    out.append(f'<circle cx="{fmt(rcx)}" cy="{fmt(rcy)}" r="{r}" fill="none" stroke="{t["raised"]}" stroke-width="9"/>')
    out.append(
        f'<circle cx="{fmt(rcx)}" cy="{fmt(rcy)}" r="{r}" fill="none" stroke="{t["accent"]}" stroke-width="9" stroke-linecap="round" '
        f'stroke-dasharray="{fmt(circ)}" stroke-dashoffset="{fmt(circ)}" transform="rotate(-90 {fmt(rcx)} {fmt(rcy)})">'
        f'<animate attributeName="stroke-dashoffset" from="{fmt(circ)}" to="{fmt(circ * (1 - max(ratio, 0.02)))}" begin="1.1s" dur="1.4s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/></circle>'
    )
    out.append(
        f'<text x="{fmt(rcx)}" y="{fmt(rcy + 6)}" text-anchor="middle" class="s" font-size="26" font-weight="600" fill="{t["text"]}">{data["current_streak"]}</text>'
        f'<text x="{fmt(rcx)}" y="{fmt(rcy + 24)}" text-anchor="middle" class="s" font-size="13" fill="{t["dim"]}">{"day" if data["current_streak"] == 1 else "days"}</text>'
    )
    tx = rcx + r + 28

    def days_(n: int) -> str:
        return f"{n} day" if n == 1 else f"{n} days"

    facts = [
        ("Current streak", days_(data["current_streak"])),
        ("Longest streak", days_(data["longest_streak"])),
        ("Active days", f"{data['active_days']} of {len(data['days'])}"),
    ]
    for k, (lab, val) in enumerate(facts):
        y = by + 74 + k * 46
        out.append(
            f'<g opacity="0">{reveal(1.2 + k * 0.1)}<text x="{fmt(tx)}" y="{y}" class="s" font-size="13" fill="{t["dim"]}">{lab}</text>'
            f'<text x="{fmt(tx)}" y="{y + 21}" class="s" font-size="17" font-weight="600" fill="{t["text"]}">{esc(val)}</text></g>'
        )

    H = by + bh + pad
    frame = f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="19.5" fill="{t["bg"]}" stroke="{t["line"]}"/>'
    return document(
        W,
        H,
        frame + "".join(out),
        title="GitHub activity",
        desc=(
            f"{data['total']} contributions in the last year, {data['commits']} commits, {data['prs']} pull requests, "
            f"{data['repos']} public repositories, {data['stars']} stars. Current streak {data['current_streak']} days, "
            f"longest {data['longest_streak']} days. Top languages: "
            + ", ".join(f"{n} {p * 100:.0f}%" for n, p, _ in data["languages"][:5])
            + "."
        ),
        fonts=[("sans", 400), ("sans", 600)],
    )
