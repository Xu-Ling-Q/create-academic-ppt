#!/usr/bin/env python3
"""Validate the packaged create-academic-ppt skill and its example assets."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".py", ".mjs", ".ps1", ".tex", ".txt"}
SECRET_PATTERNS = (
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
)


def fail(message: str) -> None:
    raise RuntimeError(message)


def check_required_files() -> None:
    required = (
        "SKILL.md",
        "agents/openai.yaml",
        "references/publication-main-figure.md",
        "references/raster-to-editable.md",
        "scripts/audit_publication_figure.py",
        "scripts/audit_editability.py",
        "scripts/run_wisart_image.ps1",
        "examples/academic-visual-ir.json",
        "examples/a2g-case-study/A2G_current_best_main_figure_editable.svg",
        "examples/a2g-case-study/A2G_current_best_main_figure_editable.pptx",
        "examples/a2g-case-study/A2G_current_best_main_figure_vector.pdf",
        "examples/a2g-case-study/A2G_current_best_figure_manifest.json",
    )
    for relative in required:
        if not (ROOT / relative).is_file():
            fail(f"missing required file: {relative}")


def check_skill_frontmatter() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("SKILL.md is missing YAML frontmatter")
    frontmatter = text.split("---\n", 2)
    if len(frontmatter) < 3 or "name: create-academic-ppt" not in frontmatter[1]:
        fail("SKILL.md frontmatter does not declare create-academic-ppt")


def check_references() -> None:
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for match in re.findall(r"`((?:references|scripts)/[^`]+)`", skill_text):
        relative = match.split()[0]
        if not (ROOT / relative).exists():
            fail(f"SKILL.md references missing path: {relative}")


def check_example_metadata() -> None:
    ir = json.loads((ROOT / "examples/academic-visual-ir.json").read_text(encoding="utf-8"))
    if not isinstance(ir, dict):
        fail("academic visual IR must be a JSON object")

    manifest_path = ROOT / "examples/a2g-case-study/A2G_current_best_figure_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key, filename in manifest.get("artifacts", {}).items():
        if not (manifest_path.parent / filename).is_file():
            fail(f"manifest artifact is missing: {key} -> {filename}")


def check_svg() -> None:
    svg_path = ROOT / "examples/a2g-case-study/A2G_current_best_main_figure_editable.svg"
    root = ET.parse(svg_path).getroot()
    if root.tag.rsplit("}", 1)[-1] != "svg":
        fail("example SVG root is not <svg>")
    images = [node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "image"]
    if images:
        fail(f"example SVG unexpectedly contains {len(images)} image element(s)")


def check_text_for_secrets() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                fail(f"possible credential pattern found in {path.relative_to(ROOT)}")


def main() -> int:
    try:
        check_required_files()
        check_skill_frontmatter()
        check_references()
        check_example_metadata()
        check_svg()
        check_text_for_secrets()
    except (OSError, ValueError, ET.ParseError, RuntimeError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 1
    print("create-academic-ppt repository validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
