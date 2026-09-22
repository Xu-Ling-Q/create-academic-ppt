#!/usr/bin/env python3
"""Audit whether PowerPoint slides contain editable objects.

The auditor reads a PPTX as an OPC ZIP package; it does not require
PowerPoint or third-party Python packages.  A slide is considered suspiciously
image-only when it contains one or more picture shapes and no text shapes,
non-text shapes/connectors, tables, or charts.

Exit codes:
    0  Valid PPTX and no unapproved image-only slides.
    1  Valid PPTX with one or more unapproved image-only slides.
    2  Invalid PPTX or invalid command-line input.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import sys
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set
from xml.etree import ElementTree as ET


PRESENTATION_NAMESPACES = {
    "http://schemas.openxmlformats.org/presentationml/2006/main",
    "http://purl.oclc.org/ooxml/presentationml/main",
}


class AuditError(Exception):
    """Raised when a file is not a readable, structurally valid PPTX."""


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _namespace(tag: str) -> str:
    return tag[1:].split("}", 1)[0] if tag.startswith("{") else ""


def _is_presentation_element(element: ET.Element, local_name: str) -> bool:
    return (
        _local_name(element.tag) == local_name
        and _namespace(element.tag) in PRESENTATION_NAMESPACES
    )


def _parse_xml(data: bytes, member_name: str) -> ET.Element:
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        raise AuditError(f"malformed XML in {member_name}: {exc}") from exc


def _read_member(package: zipfile.ZipFile, member_name: str) -> bytes:
    try:
        return package.read(member_name)
    except KeyError as exc:
        raise AuditError(f"missing required PPTX member: {member_name}") from exc
    except (RuntimeError, OSError, zipfile.BadZipFile) as exc:
        raise AuditError(f"cannot read {member_name}: {exc}") from exc


def _relationship_id(element: ET.Element) -> str | None:
    """Return the namespaced relationship id, not the numeric slide id."""

    for attribute, value in element.attrib.items():
        if attribute.startswith("{") and _local_name(attribute) == "id":
            return value
    return None


def _resolve_part(source_part: str, target: str) -> str:
    target = target.replace("\\", "/")
    if target.startswith("/"):
        resolved = posixpath.normpath(target.lstrip("/"))
    else:
        resolved = posixpath.normpath(
            posixpath.join(posixpath.dirname(source_part), target)
        )
    if resolved in {"", ".", ".."} or resolved.startswith("../"):
        raise AuditError(f"invalid relationship target: {target}")
    return resolved


def _slide_parts_in_order(package: zipfile.ZipFile) -> List[str]:
    content_types = _parse_xml(
        _read_member(package, "[Content_Types].xml"), "[Content_Types].xml"
    )
    if _local_name(content_types.tag) != "Types":
        raise AuditError("[Content_Types].xml does not contain a Types root")

    presentation_part = "ppt/presentation.xml"
    presentation = _parse_xml(
        _read_member(package, presentation_part), presentation_part
    )
    if not _is_presentation_element(presentation, "presentation"):
        raise AuditError("ppt/presentation.xml does not contain a presentation root")

    slide_ids: List[str] = []
    for element in presentation.iter():
        if _is_presentation_element(element, "sldId"):
            relationship_id = _relationship_id(element)
            if not relationship_id:
                raise AuditError("a slide entry has no relationship id")
            slide_ids.append(relationship_id)

    if not slide_ids:
        return []

    rels_part = "ppt/_rels/presentation.xml.rels"
    relationships = _parse_xml(_read_member(package, rels_part), rels_part)
    if _local_name(relationships.tag) != "Relationships":
        raise AuditError(f"{rels_part} does not contain a Relationships root")

    relation_targets: Dict[str, str] = {}
    external_relations: Set[str] = set()
    for relationship in relationships.iter():
        if _local_name(relationship.tag) != "Relationship":
            continue
        relationship_id = relationship.attrib.get("Id")
        target = relationship.attrib.get("Target")
        if not relationship_id or not target:
            continue
        if relationship.attrib.get("TargetMode", "").lower() == "external":
            external_relations.add(relationship_id)
            continue
        relation_targets[relationship_id] = _resolve_part(presentation_part, target)

    members = set(package.namelist())
    slide_parts: List[str] = []
    for relationship_id in slide_ids:
        if relationship_id in external_relations:
            raise AuditError(
                f"slide relationship {relationship_id} has an external target"
            )
        slide_part = relation_targets.get(relationship_id)
        if not slide_part:
            raise AuditError(
                f"slide relationship {relationship_id} has no package target"
            )
        if slide_part not in members:
            raise AuditError(f"missing slide part: {slide_part}")
        slide_parts.append(slide_part)
    return slide_parts


def _effective_descendants(element: ET.Element) -> Iterable[ET.Element]:
    """Yield descendants while counting one branch of mc:AlternateContent.

    PowerPoint files can store both a modern Choice and a compatibility
    Fallback. Counting both would report the same visual object twice. The
    first Choice is preferred, with Fallback used when no Choice is present.
    """

    for child in element:
        if _local_name(child.tag) == "AlternateContent":
            choice = next(
                (item for item in child if _local_name(item.tag) == "Choice"),
                None,
            )
            fallback = next(
                (item for item in child if _local_name(item.tag) == "Fallback"),
                None,
            )
            selected = choice if choice is not None else fallback
            if selected is not None:
                yield from _effective_descendants(selected)
            continue
        yield child
        yield from _effective_descendants(child)


def _has_direct_text_body(shape: ET.Element) -> bool:
    return any(_is_presentation_element(child, "txBody") for child in shape)


def _graphic_frame_kind(frame: ET.Element) -> str:
    descendants = list(_effective_descendants(frame))
    data_uris = [
        item.attrib.get("uri", "").lower()
        for item in descendants
        if _local_name(item.tag) == "graphicData"
    ]
    if any("table" in uri for uri in data_uris) or any(
        _local_name(item.tag) == "tbl" for item in descendants
    ):
        return "table"
    if any("chart" in uri for uri in data_uris) or any(
        _local_name(item.tag) == "chart" for item in descendants
    ):
        return "chart"
    return "non_text"


def _audit_slide(slide_xml: bytes, member_name: str, slide_number: int) -> Dict[str, int]:
    slide = _parse_xml(slide_xml, member_name)
    if not _is_presentation_element(slide, "sld"):
        raise AuditError(f"{member_name} does not contain a slide root")

    shape_trees = [
        item for item in slide.iter() if _is_presentation_element(item, "spTree")
    ]
    if not shape_trees:
        raise AuditError(f"{member_name} has no slide shape tree")

    counts = {
        "editable_text_shapes": 0,
        "non_text_shapes_connectors": 0,
        "pictures": 0,
        "tables": 0,
        "charts": 0,
    }

    for element in _effective_descendants(shape_trees[0]):
        if _is_presentation_element(element, "sp"):
            if _has_direct_text_body(element):
                counts["editable_text_shapes"] += 1
            else:
                counts["non_text_shapes_connectors"] += 1
        elif _is_presentation_element(element, "cxnSp"):
            counts["non_text_shapes_connectors"] += 1
        elif _is_presentation_element(element, "pic"):
            counts["pictures"] += 1
        elif _is_presentation_element(element, "graphicFrame"):
            kind = _graphic_frame_kind(element)
            if kind == "table":
                counts["tables"] += 1
            elif kind == "chart":
                counts["charts"] += 1
            else:
                counts["non_text_shapes_connectors"] += 1
        elif _is_presentation_element(element, "contentPart"):
            counts["non_text_shapes_connectors"] += 1

    return {"slide": slide_number, **counts}


def audit_pptx(path: Path, allowed_image_only: Set[int]) -> Dict[str, object]:
    if not path.is_file():
        raise AuditError(f"file not found: {path}")

    try:
        with zipfile.ZipFile(path, "r") as package:
            corrupt_member = package.testzip()
            if corrupt_member:
                raise AuditError(f"corrupt ZIP member: {corrupt_member}")
            slide_parts = _slide_parts_in_order(package)
            slides = [
                _audit_slide(
                    _read_member(package, slide_part), slide_part, slide_number
                )
                for slide_number, slide_part in enumerate(slide_parts, start=1)
            ]
    except AuditError:
        raise
    except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
        raise AuditError(f"not a readable PPTX ZIP package: {exc}") from exc

    out_of_range = sorted(
        number for number in allowed_image_only if number > len(slides)
    )
    if out_of_range:
        numbers = ", ".join(str(number) for number in out_of_range)
        raise ValueError(f"allowed slide number(s) out of range: {numbers}")

    unapproved: List[int] = []
    allowed_suspicious: List[int] = []
    for slide in slides:
        image_only = (
            slide["pictures"] > 0
            and slide["editable_text_shapes"] == 0
            and slide["non_text_shapes_connectors"] == 0
            and slide["tables"] == 0
            and slide["charts"] == 0
        )
        slide_number = slide["slide"]
        slide["suspicious_image_only"] = image_only
        slide["image_only_allowed"] = image_only and slide_number in allowed_image_only
        if image_only:
            if slide_number in allowed_image_only:
                slide["status"] = "image-only-allowed"
                allowed_suspicious.append(slide_number)
            else:
                slide["status"] = "image-only-unapproved"
                unapproved.append(slide_number)
        else:
            slide["status"] = "ok"

    count_fields = (
        "editable_text_shapes",
        "non_text_shapes_connectors",
        "pictures",
        "tables",
        "charts",
    )
    totals = {
        field: sum(int(slide[field]) for slide in slides) for field in count_fields
    }
    return {
        "ok": not unapproved,
        "file": str(path.resolve()),
        "slide_count": len(slides),
        "slides": slides,
        "totals": totals,
        "allowed_image_only_slides": allowed_suspicious,
        "unapproved_image_only_slides": unapproved,
    }


def _parse_allowed_slides(value: str) -> Set[int]:
    if not value.strip():
        return set()
    numbers: Set[int] = set()
    for raw_item in value.split(","):
        item = raw_item.strip()
        if not item:
            raise argparse.ArgumentTypeError(
                "expected comma-separated positive slide numbers"
            )
        try:
            number = int(item)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                f"invalid slide number: {item!r}"
            ) from exc
        if number <= 0:
            raise argparse.ArgumentTypeError("slide numbers must be positive")
        numbers.add(number)
    return numbers


def _human_report(report: Dict[str, object]) -> str:
    slides = report["slides"]
    assert isinstance(slides, list)
    lines = [
        f"PPTX editability audit: {report['file']}",
        f"Slides: {report['slide_count']}",
        "",
        "Slide | Text shapes | Non-text/connectors | Pictures | Tables | Charts | Status",
        "------|-------------|---------------------|----------|--------|--------|------------------------",
    ]
    for slide in slides:
        assert isinstance(slide, dict)
        status = {
            "ok": "OK",
            "image-only-allowed": "IMAGE-ONLY (allowed)",
            "image-only-unapproved": "IMAGE-ONLY (unapproved)",
        }[str(slide["status"])]
        lines.append(
            f"{slide['slide']:>5} | {slide['editable_text_shapes']:>11} | "
            f"{slide['non_text_shapes_connectors']:>19} | {slide['pictures']:>8} | "
            f"{slide['tables']:>6} | {slide['charts']:>6} | {status}"
        )

    totals = report["totals"]
    assert isinstance(totals, dict)
    lines.extend(
        [
            "",
            "Totals: "
            f"text={totals['editable_text_shapes']}, "
            f"non-text/connectors={totals['non_text_shapes_connectors']}, "
            f"pictures={totals['pictures']}, tables={totals['tables']}, "
            f"charts={totals['charts']}",
        ]
    )
    unapproved = report["unapproved_image_only_slides"]
    assert isinstance(unapproved, list)
    if unapproved:
        lines.append(
            "FAIL: unapproved suspicious image-only slide(s): "
            + ", ".join(str(number) for number in unapproved)
        )
    else:
        lines.append("PASS: no unapproved suspicious image-only slides.")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit editable objects in a PowerPoint .pptx file."
    )
    parser.add_argument("pptx", type=Path, help="path to the .pptx file")
    parser.add_argument(
        "--allow-image-only",
        default=set(),
        type=_parse_allowed_slides,
        metavar="SLIDES",
        help="comma-separated slide numbers permitted to be image-only",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of the human report",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        report = audit_pptx(args.pptx, args.allow_image_only)
    except ValueError as exc:
        if args.json:
            print(
                json.dumps(
                    {"ok": False, "error": "invalid_arguments", "message": str(exc)},
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except AuditError as exc:
        if args.json:
            print(
                json.dumps(
                    {"ok": False, "error": "invalid_pptx", "message": str(exc)},
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(_human_report(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
