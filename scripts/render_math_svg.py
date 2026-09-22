#!/usr/bin/env python3
"""Render a MathText/LaTeX-subset formula to vector SVG with a .tex sidecar."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a LaTeX-subset formula to cropped vector SVG."
    )
    parser.add_argument("--formula", required=True, help="Formula without outer dollar signs.")
    parser.add_argument("--output", required=True, type=Path, help="Output .svg path.")
    parser.add_argument("--font-size", type=float, default=10.0, help="Font size in points.")
    parser.add_argument(
        "--fontset",
        choices=("stix", "stixsans", "cm", "dejavusans", "dejavuserif"),
        default="stix",
    )
    parser.add_argument("--color", default="#27313D", help="Formula color.")
    parser.add_argument("--dpi", type=float, default=300.0)
    parser.add_argument("--force", action="store_true", help="Overwrite existing outputs.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = args.output.resolve()
    if output.suffix.lower() != ".svg":
        print("error: --output must end in .svg", file=sys.stderr)
        return 2

    source = output.with_suffix(".tex")
    existing = [path for path in (output, source) if path.exists()]
    if existing and not args.force:
        print(f"error: output exists: {existing[0]} (use --force)", file=sys.stderr)
        return 2

    try:
        import matplotlib

        matplotlib.use("Agg")
        from matplotlib import rcParams
        from matplotlib.font_manager import FontProperties
        from matplotlib.mathtext import math_to_image
    except ImportError:
        print(
            "error: Matplotlib is required. Install it in the active Python environment.",
            file=sys.stderr,
        )
        return 3

    formula = args.formula.strip()
    if formula.startswith("$") and formula.endswith("$") and len(formula) >= 2:
        formula = formula[1:-1]
    if not formula:
        print("error: formula is empty", file=sys.stderr)
        return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    rcParams["mathtext.fontset"] = args.fontset
    rcParams["svg.fonttype"] = "path"
    expression = f"${formula}$"

    try:
        math_to_image(
            expression,
            output,
            prop=FontProperties(size=args.font_size),
            dpi=args.dpi,
            format="svg",
            color=args.color,
        )
    except Exception as exc:  # Matplotlib reports unsupported commands here.
        print(f"error: formula render failed: {exc}", file=sys.stderr)
        return 4

    rendered = output.read_text(encoding="utf-8")
    if "<svg" not in rendered or ("<path" not in rendered and "<text" not in rendered):
        print("error: renderer did not produce a valid vector SVG", file=sys.stderr)
        return 5

    source.write_text(formula + "\n", encoding="utf-8")
    print(f"svg={output}")
    print(f"tex={source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
