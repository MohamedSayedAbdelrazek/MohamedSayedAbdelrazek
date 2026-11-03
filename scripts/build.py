"""Generate the profile artwork.

    python scripts/build.py                 # static cards -> assets/
    python scripts/build.py stats --out D   # live GitHub dashboard -> D/ (needs GITHUB_TOKEN)
    python scripts/build.py stats --mock    # dashboard with fake data, for local previews
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import content as C  # noqa: E402
from lib import cards, stats  # noqa: E402
from lib.core import ROOT, THEMES  # noqa: E402


def write(path: Path, svg: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    print(f"  {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}  ({len(svg.encode()) / 1024:.0f} KB)")


def build_static(out: Path) -> None:
    for name, theme in THEMES.items():
        write(out / f"hero-{name}.svg", cards.hero(theme))
        write(out / f"terminal-{name}.svg", cards.terminal(theme))
        write(out / f"stack-{name}.svg", cards.stack(theme))
        write(out / f"footer-{name}.svg", cards.footer(theme))
        for i, link in enumerate(C.LINKS):
            write(out / f"btn-{link['id']}-{name}.svg", cards.button(theme, link, i))


def build_stats(out: Path, use_mock: bool) -> None:
    login = os.environ.get("PROFILE_LOGIN", C.LOGIN)
    if use_mock:
        data = stats.mock(login)
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("GITHUB_TOKEN is not set (use --mock for a local preview)")
        data = stats.fetch(login, token)
    for name, theme in THEMES.items():
        write(out / f"stats-{name}.svg", stats.dashboard(theme, data))
    summary = {k: v for k, v in data.items() if k != "days"}
    (out / "stats.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", nargs="?", choices=["static", "stats"], default="static")
    parser.add_argument("--out", type=Path, help="output directory")
    parser.add_argument("--mock", action="store_true", help="render the dashboard with fake data")
    args = parser.parse_args()

    if args.target == "static":
        build_static(args.out or ROOT / "assets")
    else:
        build_stats(args.out or ROOT / "dist", args.mock)


if __name__ == "__main__":
    main()
