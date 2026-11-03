"""Live GitHub activity dashboard: fetch from the GraphQL API, render as an animated SVG."""

from __future__ import annotations

import datetime as dt
import json
import random
import urllib.request
from collections import Counter

from .core import animate, document, esc, fmt, mix, mono_width, readable, reveal, text_width

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
    """Digits roll into place like a mechanical counter."""
    text = f"{value:,}"
    cw = mono_width(1, size)
    lh = size * 1.25
    out = [f'<clipPath id="{uid}"><rect x="{fmt(x - 2)}" y="{fmt(y - size)}" width="{fmt(cw * len(text) + 4)}" height="{fmt(size * 1.3)}"/></clipPath>']
    out.append(f'<g clip-path="url(#{uid})">')
    digit_index = 0
    for i, ch in enumerate(text):
        cx = x + i * cw
        if not ch.isdigit():
            out.append(f'<text x="{fmt(cx)}" y="{fmt(y)}" class="m" font-size="{size}" font-weight="700" fill="{t["text"]}">{ch}</text>')
            continue
        target = 10 + int(ch)  # roll through a full turn before landing
        strip = "".join(
            f'<text x="{fmt(cx)}" y="{fmt(y + k * lh)}" class="m" font-size="{size}" font-weight="700" fill="{t["text"]}">{k % 10}</text>'
            for k in range(target + 1)
        )
        delay = begin + digit_index * 0.08
        out.append(
            f'<g transform="translate(0 {fmt(-target * lh)})">'
            f'<animateTransform attributeName="transform" type="translate" from="0 0" to="0 {fmt(-target * lh)}" begin="{fmt(delay)}s" dur="1.6s" '
            f'fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.12 0.9 0.2 1"/>{strip}</g>'
        )
        digit_index += 1
    out.append("</g>")
    return "".join(out)


def dashboard(t: dict[str, str], data: dict) -> str:
    pad = 24
    H = 566
    out = [
        "<defs>",
        f'<linearGradient id="mark" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent2"]}"/></linearGradient>',
        f'<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["accent2"]}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{t["accent2"]}" stop-opacity="0.1"/><stop offset="1" stop-color="{t["accent2"]}" stop-opacity="0"/></linearGradient>',
        "</defs>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="19.5" fill="{t["bg"]}" stroke="{t["line"]}"/>',
    ]

    # Header.
    out.append(
        f'<rect x="{pad}" y="22" width="28" height="28" rx="8" fill="url(#mark)"/>'
        f'<path d="M{pad + 7} {41}l4-6 4 3 6-8" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<text x="{pad + 40}" y="42" class="s" font-size="19" font-weight="600" fill="{t["text"]}">Activity Monitor</text>'
        f'<text x="{fmt(pad + 40 + text_width("Activity Monitor", 19, "sans", 600) + 12)}" y="41.5" class="m" font-size="11" fill="{t["dim"]}">github.com/{esc(data["login"])}</text>'
    )
    synced = f"synced {data['generated']}"
    sw = mono_width(len(synced), 11)
    out.append(
        f'<circle cx="{fmt(W - pad - sw - 16)}" cy="37.5" r="3.6" fill="{t["accent"]}" class="pulse"/>'
        f'<circle cx="{fmt(W - pad - sw - 16)}" cy="37.5" r="3.6" fill="{t["accent"]}"/>'
        f'<text x="{W - pad}" y="41.5" text-anchor="end" class="m" font-size="11" fill="{t["muted"]}">{synced}</text>'
    )

    # KPI tiles.
    tiles = [
        ("CONTRIBUTIONS", data["total"], "last 12 months"),
        ("COMMITS", data["commits"], "last 12 months"),
        ("PULL REQUESTS", data["prs"], "all time"),
        ("PUBLIC REPOS", data["repos"], "owned"),
        ("STARS EARNED", data["stars"], "across repos"),
    ]
    gap = 12
    tw = (W - 2 * pad - gap * (len(tiles) - 1)) / len(tiles)
    ty, th = 68, 96
    for i, (label, value, sub) in enumerate(tiles):
        x = pad + i * (tw + gap)
        out.append(
            f'<g opacity="0">{reveal(0.1 + i * 0.07, dy=6, dur=0.5)}'
            f'<rect x="{fmt(x)}" y="{ty}" width="{fmt(tw)}" height="{th}" rx="12" fill="{t["panel"]}" stroke="{t["line"]}"/>'
            f'<rect x="{fmt(x + 16)}" y="{ty + 18}" width="6" height="6" rx="1.5" fill="{t["accent"] if i == 0 else t["dim"]}"/>'
            f'<text x="{fmt(x + 28)}" y="{ty + 24.5}" class="m" font-size="10" font-weight="700" fill="{t["muted"]}" letter-spacing="0.6">{label}</text>'
            + _odometer(t, value, x + 16, ty + 62, 28, f"odo{i}", 0.3 + i * 0.1)
            + f'<text x="{fmt(x + 16)}" y="{ty + 82}" class="m" font-size="10" fill="{t["dim"]}">{sub}</text>'
            "</g>"
        )

    # Heatmap.
    hy = ty + th + 14
    hh = 196
    out.append(f'<rect x="{pad}" y="{hy}" width="{W - 2 * pad}" height="{hh}" rx="12" fill="{t["panel"]}" stroke="{t["line"]}"/>')
    out.append(
        f'<text x="{pad + 18}" y="{hy + 28}" class="s" font-size="14" font-weight="600" fill="{t["text"]}">Contribution heatmap</text>'
        f'<text x="{W - pad - 18}" y="{hy + 28}" text-anchor="end" class="m" font-size="11" fill="{t["muted"]}">'
        f'<tspan fill="{t["text"]}" font-weight="700">{data["total"]:,}</tspan> contributions · {data["active_days"]} active days</text>'
    )
    days = data["days"]
    first = dt.date.fromisoformat(days[0][0]) if days else dt.date.today()
    offset = (first.weekday() + 1) % 7  # GitHub weeks start on Sunday
    cell, step = 11, 14
    weeks = (offset + len(days) + 6) // 7
    grid_w = weeks * step - (step - cell)
    gx = pad + 18 + 30 + max(0, (W - 2 * pad - 36 - 30 - grid_w) / 2)
    gy = hy + 58
    levels = [mix(t["raised"], t["line"], 0.7)] + [mix(t["raised"], t["accent"], a) for a in (0.32, 0.62, 1.0)] + [t["accent2"]]
    # Quartiles of the active days, like GitHub's own graph, so a single huge day doesn't flatten the rest.
    active = sorted(n for _, n in days if n)
    cuts = [active[min(len(active) - 1, int(len(active) * q))] for q in (0.25, 0.5, 0.75)] if active else [1, 2, 3]

    def level(n: int) -> int:
        if n == 0:
            return 0
        return 1 + sum(n > c for c in cuts)

    month_seen = set()
    for idx, (date, n) in enumerate(days):
        pos = idx + offset
        col, row = divmod(pos, 7)
        x = gx + col * step
        y = gy + row * step
        d = dt.date.fromisoformat(date)
        if d.day <= 7 and row == 0 or (idx == 0 and d.day <= 20):
            key = (d.year, d.month)
            if key not in month_seen and col < weeks - 1:
                month_seen.add(key)
                out.append(f'<text x="{fmt(x)}" y="{gy - 10}" class="m" font-size="9.5" fill="{t["dim"]}">{d.strftime("%b")}</text>')
        out.append(
            f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{cell}" height="{cell}" rx="2.6" fill="{levels[level(n)]}" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{0.6 + col * 0.022 + row * 0.012:.3f}s" dur="0.35s" fill="freeze"/>'
            f"<title>{date}: {n}</title></rect>"
        )
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="{fmt(gx - 8)}" y="{fmt(gy + row * step + 9)}" text-anchor="end" class="m" font-size="9.5" fill="{t["dim"]}">{name}</text>')
    # Sweep highlight across the grid.
    out.append(
        f'<clipPath id="gridclip"><rect x="{fmt(gx - 3)}" y="{gy - 3}" width="{fmt(grid_w + 6)}" height="{7 * step + 3}"/></clipPath>'
        f'<g clip-path="url(#gridclip)"><rect x="{fmt(gx - 120)}" y="{gy - 4}" width="120" height="{7 * step + 4}" fill="url(#sweep)">'
        f'<animate attributeName="x" values="{fmt(gx - 120)};{fmt(gx - 120)};{fmt(gx + grid_w)};{fmt(gx + grid_w)}" keyTimes="0;0.25;0.75;1" dur="8s" repeatCount="indefinite"/></rect></g>'
    )
    # Legend.
    ly = gy + 7 * step + 14
    lx = gx + grid_w - 5 * step - 34
    out.append(f'<text x="{fmt(lx - 8)}" y="{ly + 9}" text-anchor="end" class="m" font-size="9.5" fill="{t["dim"]}">less</text>')
    for k, c in enumerate(levels):
        out.append(f'<rect x="{fmt(lx + k * step)}" y="{ly}" width="{cell}" height="{cell}" rx="2.6" fill="{c}"/>')
    out.append(f'<text x="{fmt(lx + 5 * step + 4)}" y="{ly + 9}" class="m" font-size="9.5" fill="{t["dim"]}">more</text>')
    best = data["best_day"]
    if best["count"]:
        bd = dt.date.fromisoformat(best["date"]).strftime("%b %d, %Y")
        out.append(
            f'<text x="{fmt(gx)}" y="{ly + 9}" class="m" font-size="9.5" fill="{t["dim"]}">peak: '
            f'<tspan fill="{t["muted"]}">{best["count"]} on {bd}</tspan> · busiest weekday: <tspan fill="{t["muted"]}">{data["busiest_weekday"]}</tspan></text>'
        )

    # Bottom row: languages + streaks.
    by = hy + hh + 14
    bh = H - by - pad
    lw = 520
    out.append(f'<rect x="{pad}" y="{by}" width="{lw}" height="{bh}" rx="12" fill="{t["panel"]}" stroke="{t["line"]}"/>')
    out.append(f'<text x="{pad + 18}" y="{by + 28}" class="s" font-size="14" font-weight="600" fill="{t["text"]}">Languages</text>')
    out.append(f'<text x="{pad + lw - 18}" y="{by + 28}" text-anchor="end" class="m" font-size="10" fill="{t["dim"]}">by code size · public repos</text>')
    langs = data["languages"][:6]
    if len(data["languages"]) > 6:
        langs = langs[:5]
        langs.append(("Other", 1 - sum(p for _, p, _ in langs), t["dim"]))
    bar_x, bar_y, bar_w = pad + 18, by + 44, lw - 36
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
    col_w = (lw - 36) / 2
    for k, (name, share, colour) in enumerate(langs):
        col, row = divmod(k, 3)
        x = pad + 18 + col * col_w
        y = by + 82 + row * 22
        colour = readable(colour, t["panel"], 2.2)
        out.append(
            f'<g opacity="0">{reveal(1.0 + k * 0.08)}<circle cx="{fmt(x + 4)}" cy="{y - 4}" r="4" fill="{colour}"/>'
            f'<text x="{fmt(x + 16)}" y="{y}" class="s" font-size="12.5" font-weight="600" fill="{t["text"]}">{esc(name)}</text>'
            f'<text x="{fmt(x + col_w - 24)}" y="{y}" text-anchor="end" class="m" font-size="11" fill="{t["muted"]}">{share * 100:.1f}%</text></g>'
        )

    sx = pad + lw + 12
    sw2 = W - pad - sx
    out.append(f'<rect x="{sx}" y="{by}" width="{sw2}" height="{bh}" rx="12" fill="{t["panel"]}" stroke="{t["line"]}"/>')
    out.append(f'<text x="{sx + 18}" y="{by + 28}" class="s" font-size="14" font-weight="600" fill="{t["text"]}">Streaks</text>')
    # Ring: current vs longest.
    r = 40
    rcx, rcy = sx + 18 + r + 4, by + 44 + r + 4
    circ = 2 * 3.14159265 * r
    ratio = data["current_streak"] / data["longest_streak"] if data["longest_streak"] else 0
    out.append(f'<circle cx="{fmt(rcx)}" cy="{fmt(rcy)}" r="{r}" fill="none" stroke="{t["raised"]}" stroke-width="9"/>')
    out.append(
        f'<circle cx="{fmt(rcx)}" cy="{fmt(rcy)}" r="{r}" fill="none" stroke="url(#mark)" stroke-width="9" stroke-linecap="round" '
        f'stroke-dasharray="{fmt(circ)}" stroke-dashoffset="{fmt(circ)}" transform="rotate(-90 {fmt(rcx)} {fmt(rcy)})">'
        f'<animate attributeName="stroke-dashoffset" from="{fmt(circ)}" to="{fmt(circ * (1 - max(ratio, 0.02)))}" begin="1.1s" dur="1.4s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/></circle>'
    )
    out.append(
        f'<text x="{fmt(rcx)}" y="{fmt(rcy + 4)}" text-anchor="middle" class="m" font-size="24" font-weight="700" fill="{t["text"]}">{data["current_streak"]}</text>'
        f'<text x="{fmt(rcx)}" y="{fmt(rcy + 20)}" text-anchor="middle" class="m" font-size="9.5" fill="{t["dim"]}">{"day" if data["current_streak"] == 1 else "days"}</text>'
    )
    tx = rcx + r + 26
    def days_(n: int) -> str:
        return f"{n} day" if n == 1 else f"{n} days"

    facts = [
        ("CURRENT STREAK", days_(data["current_streak"])),
        ("LONGEST STREAK", days_(data["longest_streak"])),
        ("ACTIVE DAYS", f"{data['active_days']} / {len(data['days'])}"),
    ]
    for k, (lab, val) in enumerate(facts):
        y = by + 56 + k * 31
        out.append(
            f'<g opacity="0">{reveal(1.2 + k * 0.1)}<text x="{fmt(tx)}" y="{y}" class="m" font-size="9.5" font-weight="700" fill="{t["dim"]}" letter-spacing="0.5">{lab}</text>'
            f'<text x="{fmt(tx)}" y="{y + 15}" class="m" font-size="13" font-weight="700" fill="{t["text"]}">{esc(val)}</text></g>'
        )

    return document(
        W,
        H,
        "".join(out),
        title="GitHub activity",
        desc=(
            f"{data['total']} contributions in the last year, {data['commits']} commits, {data['prs']} pull requests, "
            f"{data['repos']} public repositories, {data['stars']} stars. Current streak {data['current_streak']} days, "
            f"longest {data['longest_streak']} days. Top languages: "
            + ", ".join(f"{n} {p * 100:.0f}%" for n, p, _ in data["languages"][:5])
            + "."
        ),
        fonts=[("sans", 600), ("mono", 400), ("mono", 700)],
    )
