#!/usr/bin/env python3
"""Audit publication figure assets across vector, raster, and PPTX formats."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys
from typing import Any
import xml.etree.ElementTree as ET
import zipfile


EMU_PER_MM = 36000.0
PT_PER_MM = 72.0 / 25.4
SVG_VECTOR_TAGS = {
    "path",
    "line",
    "polyline",
    "polygon",
    "rect",
    "circle",
    "ellipse",
    "text",
    "use",
}
ASCII_MATH_RE = re.compile(
    r"(?:\b[A-Za-z][A-Za-z0-9]*_[<{(]?[A-Za-z0-9]|"
    r"[A-Za-z0-9)]\^[{(]?[A-Za-z0-9]|\bR\^\d|H_<)"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--target-width-mm", type=float)
    parser.add_argument(
        "--art-kind", choices=("line", "mixed", "photo"), default="mixed"
    )
    parser.add_argument("--min-font-pt", type=float, default=7.0)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def make_result(path: Path, file_format: str) -> dict[str, Any]:
    return {
        "path": str(path),
        "format": file_format,
        "facts": {},
        "notes": [],
        "warnings": [],
        "errors": [],
    }


def add_warning(result: dict[str, Any], message: str) -> None:
    if message not in result["warnings"]:
        result["warnings"].append(message)


def add_note(result: dict[str, Any], message: str) -> None:
    if message not in result["notes"]:
        result["notes"].append(message)


def add_error(result: dict[str, Any], message: str) -> None:
    if message not in result["errors"]:
        result["errors"].append(message)


def parse_length(value: str | None) -> tuple[float | None, str | None]:
    if value is None:
        return None, None
    match = re.fullmatch(
        r"\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([A-Za-z%]*)\s*",
        value,
    )
    if not match:
        return None, None
    return float(match.group(1)), match.group(2).lower() or "user"


def length_to_mm(value: float, unit: str) -> float | None:
    factors = {
        "mm": 1.0,
        "cm": 10.0,
        "in": 25.4,
        "pt": 25.4 / 72.0,
        "pc": 25.4 / 6.0,
        "px": 25.4 / 96.0,
        "user": 25.4 / 96.0,
    }
    factor = factors.get(unit)
    return value * factor if factor is not None else None


def style_value(element: ET.Element, key: str) -> str | None:
    if key in element.attrib:
        return element.attrib[key]
    style = element.attrib.get("style", "")
    for part in style.split(";"):
        if ":" not in part:
            continue
        name, value = part.split(":", 1)
        if name.strip() == key:
            return value.strip()
    return None


def suspicious_math(texts: list[str]) -> list[str]:
    matches: list[str] = []
    for text in texts:
        compact = " ".join(text.split())
        if ASCII_MATH_RE.search(compact) and compact not in matches:
            matches.append(compact[:180])
    return matches[:12]


def final_user_unit_pt(
    value: float,
    unit: str,
    target_width_mm: float | None,
    viewbox_width: float | None,
    declared_width_mm: float | None,
) -> float | None:
    if unit == "pt" and target_width_mm is None:
        return value
    if unit in {"mm", "cm", "in", "pc", "pt"}:
        mm = length_to_mm(value, unit)
        if mm is None:
            return None
        if target_width_mm and declared_width_mm:
            mm *= target_width_mm / declared_width_mm
        return mm * PT_PER_MM
    physical_width = target_width_mm or declared_width_mm
    if physical_width and viewbox_width:
        return value / viewbox_width * physical_width * PT_PER_MM
    return None


def audit_svg(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    result = make_result(path, "svg")
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        add_error(result, f"Invalid SVG/XML: {exc}")
        return result
    if local_name(root.tag) != "svg":
        add_error(result, "Root element is not <svg>.")
        return result

    viewbox = None
    raw_viewbox = root.attrib.get("viewBox")
    if raw_viewbox:
        try:
            parts = [float(part) for part in re.split(r"[ ,]+", raw_viewbox.strip())]
            if len(parts) == 4 and parts[2] > 0 and parts[3] > 0:
                viewbox = parts
        except ValueError:
            pass
    if not viewbox:
        add_error(result, "SVG is missing a valid viewBox.")

    width_value, width_unit = parse_length(root.attrib.get("width"))
    height_value, height_unit = parse_length(root.attrib.get("height"))
    declared_width_mm = (
        length_to_mm(width_value, width_unit)
        if width_value is not None and width_unit is not None
        else None
    )
    declared_height_mm = (
        length_to_mm(height_value, height_unit)
        if height_value is not None and height_unit is not None
        else None
    )
    final_width_mm = args.target_width_mm or declared_width_mm
    if args.target_width_mm is None and width_unit in {"px", "user"}:
        add_warning(
            result,
            "SVG width is expressed in CSS pixels/user units; set --target-width-mm for publication-size checks.",
        )

    elements = list(root.iter())
    vector_count = sum(local_name(element.tag) in SVG_VECTOR_TAGS for element in elements)
    images = [element for element in elements if local_name(element.tag) == "image"]
    foreign = [element for element in elements if local_name(element.tag) == "foreignObject"]
    gradients = [
        element
        for element in elements
        if local_name(element.tag) in {"linearGradient", "radialGradient"}
    ]
    texts = ["".join(element.itertext()) for element in elements if local_name(element.tag) == "text"]
    formula_warnings = suspicious_math(texts)

    if vector_count == 0:
        add_error(result, "SVG contains no recognized vector or text elements.")
    if images:
        add_warning(result, f"SVG contains {len(images)} raster/image element(s); verify each is intentional.")
    if foreign:
        add_warning(result, "SVG contains foreignObject content that may not survive journal conversion.")
    if formula_warnings:
        add_warning(
            result,
            "Visible SVG text contains possible ASCII fake math using '_' or '^': "
            + " | ".join(formula_warnings),
        )

    font_points: list[float] = []
    stroke_points: list[float] = []
    viewbox_width = viewbox[2] if viewbox else None
    for element in elements:
        font_raw = style_value(element, "font-size")
        font_value, font_unit = parse_length(font_raw)
        if font_value is not None and font_unit is not None:
            point_size = final_user_unit_pt(
                font_value,
                font_unit,
                args.target_width_mm,
                viewbox_width,
                declared_width_mm,
            )
            if point_size is not None:
                font_points.append(point_size)
        stroke_raw = style_value(element, "stroke-width")
        stroke_value, stroke_unit = parse_length(stroke_raw)
        if stroke_value is not None and stroke_unit is not None:
            point_size = final_user_unit_pt(
                stroke_value,
                stroke_unit,
                args.target_width_mm,
                viewbox_width,
                declared_width_mm,
            )
            if point_size is not None and point_size > 0:
                stroke_points.append(point_size)

    if font_points and min(font_points) < args.min_font_pt:
        add_warning(
            result,
            f"Minimum SVG font is {min(font_points):.2f} pt at final width; target is at least {args.min_font_pt:.2f} pt.",
        )
    if stroke_points and min(stroke_points) < 0.35:
        add_warning(
            result,
            f"Minimum SVG stroke is {min(stroke_points):.2f} pt at final width; inspect thin-line survival.",
        )

    aspect = viewbox[2] / viewbox[3] if viewbox else None
    result["facts"].update(
        {
            "viewBox": viewbox,
            "declared_width_mm": round(declared_width_mm, 3) if declared_width_mm else None,
            "declared_height_mm": round(declared_height_mm, 3) if declared_height_mm else None,
            "target_width_mm": final_width_mm,
            "aspect_ratio": round(aspect, 6) if aspect else None,
            "vector_elements": vector_count,
            "image_elements": len(images),
            "text_elements": len(texts),
            "gradient_elements": len(gradients),
            "minimum_font_pt": round(min(font_points), 3) if font_points else None,
            "minimum_stroke_pt": round(min(stroke_points), 3) if stroke_points else None,
        }
    )
    return result


def resolve_pdf_object(value: Any) -> Any:
    try:
        return value.get_object()
    except AttributeError:
        return value


def pdf_font_embedded(font: Any) -> bool:
    font = resolve_pdf_object(font)
    candidates = [font]
    descendants = resolve_pdf_object(font.get("/DescendantFonts", [])) if hasattr(font, "get") else []
    if descendants:
        candidates.extend(resolve_pdf_object(item) for item in descendants)
    for candidate in candidates:
        if not hasattr(candidate, "get"):
            continue
        descriptor = resolve_pdf_object(candidate.get("/FontDescriptor"))
        if descriptor and any(descriptor.get(key) is not None for key in ("/FontFile", "/FontFile2", "/FontFile3")):
            return True
    return False


def audit_pdf(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    result = make_result(path, "pdf")
    try:
        from pypdf import PdfReader
    except ImportError:
        add_error(result, "pypdf is required to audit PDF files.")
        return result
    try:
        reader = PdfReader(str(path))
    except Exception as exc:
        add_error(result, f"PDF could not be opened: {exc}")
        return result

    page_count = len(reader.pages)
    if page_count != 1:
        add_error(result, f"Publication figure PDF must contain one page; found {page_count}.")
    if page_count == 0:
        return result

    page = reader.pages[0]
    crop = page.cropbox
    width_pt = float(crop.width)
    height_pt = float(crop.height)
    width_mm = width_pt / PT_PER_MM
    height_mm = height_pt / PT_PER_MM
    if args.target_width_mm and abs(width_mm / args.target_width_mm - 1.0) > 0.05:
        add_warning(
            result,
            f"PDF crop width is {width_mm:.2f} mm, not the intended {args.target_width_mm:.2f} mm; export a tight final-size page.",
        )
    resources = resolve_pdf_object(page.get("/Resources", {}))
    fonts = resolve_pdf_object(resources.get("/Font", {})) if hasattr(resources, "get") else {}
    xobjects = resolve_pdf_object(resources.get("/XObject", {})) if hasattr(resources, "get") else {}
    image_count = 0
    if hasattr(xobjects, "values"):
        for obj in xobjects.values():
            resolved = resolve_pdf_object(obj)
            if hasattr(resolved, "get") and resolved.get("/Subtype") == "/Image":
                image_count += 1
    font_values = list(fonts.values()) if hasattr(fonts, "values") else []
    embedded_count = sum(pdf_font_embedded(font) for font in font_values)
    if font_values and embedded_count < len(font_values):
        add_warning(result, f"Only {embedded_count}/{len(font_values)} PDF font resource(s) appear embedded.")
    if image_count:
        add_warning(result, f"PDF contains {image_count} image XObject(s); verify raster content and effective DPI.")
    try:
        text = page.extract_text() or ""
    except Exception:
        text = ""
    math_hits = suspicious_math([text])
    if math_hits:
        add_warning(result, "Extracted PDF text contains possible ASCII fake math: " + " | ".join(math_hits))

    target_width = args.target_width_mm or width_mm
    result["facts"].update(
        {
            "page_count": page_count,
            "crop_width_mm": round(width_mm, 3),
            "crop_height_mm": round(height_mm, 3),
            "target_width_mm": target_width,
            "aspect_ratio": round(width_pt / height_pt, 6) if height_pt else None,
            "font_resources": len(font_values),
            "embedded_font_resources": embedded_count,
            "image_xobjects": image_count,
        }
    )
    return result


def audit_pptx(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    result = make_result(path, "pptx")
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            slides = sorted(
                name
                for name in names
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
            )
            if len(slides) != 1:
                add_error(result, f"Paper-figure PPTX source must contain one slide; found {len(slides)}.")
            presentation_xml = ET.fromstring(archive.read("ppt/presentation.xml"))
            slide_size = next((e for e in presentation_xml.iter() if local_name(e.tag) == "sldSz"), None)
            width_mm = height_mm = None
            if slide_size is not None:
                width_mm = float(slide_size.attrib.get("cx", 0)) / EMU_PER_MM
                height_mm = float(slide_size.attrib.get("cy", 0)) / EMU_PER_MM

            picture_count = shape_count = office_math_count = 0
            texts: list[str] = []
            for slide_name in slides:
                root = ET.fromstring(archive.read(slide_name))
                picture_count += sum(local_name(e.tag) == "pic" for e in root.iter())
                shape_count += sum(local_name(e.tag) == "sp" for e in root.iter())
                office_math_count += sum(local_name(e.tag) in {"oMath", "oMathPara"} for e in root.iter())
                texts.extend((e.text or "") for e in root.iter() if local_name(e.tag) == "t")
            media = [name for name in names if name.startswith("ppt/media/") and not name.endswith("/")]
    except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
        add_error(result, f"PPTX could not be audited: {exc}")
        return result

    add_note(result, "PPTX is an editable authoring source, not the default journal submission master.")
    if args.target_width_mm and width_mm and abs(width_mm / args.target_width_mm - 1.0) > 0.05:
        add_warning(
            result,
            f"PPTX canvas width is {width_mm:.2f} mm and will scale to {args.target_width_mm:.2f} mm; verify all text and strokes at final size.",
        )
    if picture_count == 1 and shape_count <= 2 and len(texts) <= 1:
        add_warning(result, "PPTX appears to be a full-slide image rather than an editable figure.")
    math_hits = suspicious_math(texts)
    if math_hits:
        add_warning(
            result,
            "Visible PPTX text contains possible ASCII fake math using '_' or '^': "
            + " | ".join(math_hits),
        )
    if office_math_count == 0 and math_hits:
        add_warning(result, "No native Office Math objects were found; verify vector formula assets or grouped scripts.")

    aspect = width_mm / height_mm if width_mm and height_mm else None
    result["facts"].update(
        {
            "slide_count": len(slides),
            "slide_width_mm": round(width_mm, 3) if width_mm else None,
            "slide_height_mm": round(height_mm, 3) if height_mm else None,
            "target_width_mm": args.target_width_mm,
            "aspect_ratio": round(aspect, 6) if aspect else None,
            "shapes": shape_count,
            "pictures": picture_count,
            "media_files": len(media),
            "text_runs": len(texts),
            "office_math_elements": office_math_count,
        }
    )
    return result


def audit_raster(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    result = make_result(path, path.suffix.lower().lstrip("."))
    try:
        from PIL import Image
    except ImportError:
        add_error(result, "Pillow is required to audit raster images.")
        return result
    try:
        with Image.open(path) as image:
            width_px, height_px = image.size
            file_format = (image.format or result["format"]).lower()
            dpi_info = image.info.get("dpi")
            dpi_x = float(dpi_info[0]) if dpi_info and dpi_info[0] else None
            mode = image.mode
    except Exception as exc:
        add_error(result, f"Raster image could not be opened: {exc}")
        return result

    result["format"] = file_format
    threshold = {"line": 1200.0, "mixed": 600.0, "photo": 300.0}[args.art_kind]
    effective_dpi = None
    if args.target_width_mm:
        effective_dpi = width_px / (args.target_width_mm / 25.4)
    elif dpi_x:
        effective_dpi = dpi_x
    else:
        add_warning(result, "Raster image has no reliable DPI metadata; set --target-width-mm.")
    if effective_dpi and effective_dpi < threshold:
        add_warning(
            result,
            f"Effective resolution is {effective_dpi:.1f} dpi; {args.art_kind} artwork target is {threshold:.0f} dpi.",
        )
    if file_format in {"jpeg", "jpg"} and args.art_kind != "photo":
        add_warning(result, "JPEG is not recommended for line or mixed artwork.")
    result["facts"].update(
        {
            "width_px": width_px,
            "height_px": height_px,
            "mode": mode,
            "dpi_metadata": round(dpi_x, 3) if dpi_x else None,
            "effective_dpi": round(effective_dpi, 3) if effective_dpi else None,
            "target_width_mm": args.target_width_mm,
            "aspect_ratio": round(width_px / height_px, 6) if height_px else None,
        }
    )
    return result


def audit_eps(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    result = make_result(path, "eps")
    try:
        header = path.read_text(encoding="latin-1", errors="replace")[:20000]
    except OSError as exc:
        add_error(result, f"EPS could not be opened: {exc}")
        return result
    match = re.search(
        r"^%%(?:HiRes)?BoundingBox:\s*([+-]?\d+(?:\.\d+)?)\s+([+-]?\d+(?:\.\d+)?)\s+([+-]?\d+(?:\.\d+)?)\s+([+-]?\d+(?:\.\d+)?)",
        header,
        re.MULTILINE,
    )
    if not match:
        add_error(result, "EPS is missing a parseable BoundingBox.")
        return result
    x1, y1, x2, y2 = map(float, match.groups())
    width_pt = x2 - x1
    height_pt = y2 - y1
    if width_pt <= 0 or height_pt <= 0:
        add_error(result, "EPS BoundingBox has invalid dimensions.")
    add_warning(result, "EPS audit is limited; render it independently and verify fonts and transparency.")
    result["facts"].update(
        {
            "bounding_width_mm": round(width_pt / PT_PER_MM, 3),
            "bounding_height_mm": round(height_pt / PT_PER_MM, 3),
            "target_width_mm": args.target_width_mm,
            "aspect_ratio": round(width_pt / height_pt, 6) if height_pt else None,
        }
    )
    return result


def detect_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".svg":
        return "svg"
    if suffix == ".pdf":
        return "pdf"
    if suffix == ".pptx":
        return "pptx"
    if suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}:
        return "raster"
    if suffix in {".eps", ".ps"}:
        return "eps"
    return "unknown"


def audit_file(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.exists() or not resolved.is_file():
        result = make_result(resolved, "unknown")
        add_error(result, "File does not exist or is not a regular file.")
        return result
    file_format = detect_format(resolved)
    if file_format == "svg":
        return audit_svg(resolved, args)
    if file_format == "pdf":
        return audit_pdf(resolved, args)
    if file_format == "pptx":
        return audit_pptx(resolved, args)
    if file_format == "raster":
        return audit_raster(resolved, args)
    if file_format == "eps":
        return audit_eps(resolved, args)
    result = make_result(resolved, "unknown")
    add_error(result, "Unsupported figure format.")
    return result


def add_cross_format_warnings(results: list[dict[str, Any]]) -> None:
    ratios = [
        (result, result["facts"].get("aspect_ratio"))
        for result in results
        if result["facts"].get("aspect_ratio")
    ]
    if len(ratios) < 2:
        return
    baseline = ratios[0][1]
    for result, ratio in ratios[1:]:
        if baseline and abs(ratio / baseline - 1.0) > 0.015:
            add_warning(result, f"Aspect ratio {ratio:.4f} differs from the first audited asset {baseline:.4f} by more than 1.5%.")


def print_human(results: list[dict[str, Any]], strict: bool) -> None:
    for result in results:
        failed = bool(result["errors"]) or (strict and bool(result["warnings"]))
        status = "FAIL" if failed else ("WARN" if result["warnings"] else "PASS")
        print(f"[{status}] {result['path']} ({result['format']})")
        for key, value in result["facts"].items():
            if value is not None:
                print(f"  {key}: {value}")
        for message in result["notes"]:
            print(f"  note: {message}")
        for message in result["warnings"]:
            print(f"  warning: {message}")
        for message in result["errors"]:
            print(f"  error: {message}")


def main() -> int:
    args = parse_args()
    if args.target_width_mm is not None and args.target_width_mm <= 0:
        print("error: --target-width-mm must be positive", file=sys.stderr)
        return 2
    if args.min_font_pt <= 0:
        print("error: --min-font-pt must be positive", file=sys.stderr)
        return 2
    results = [audit_file(path, args) for path in args.files]
    add_cross_format_warnings(results)
    for result in results:
        result["ok"] = not result["errors"] and not (args.strict and result["warnings"])
    payload = {
        "ok": all(result["ok"] for result in results),
        "strict": args.strict,
        "target_width_mm": args.target_width_mm,
        "art_kind": args.art_kind,
        "files": results,
    }
    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_human(results, args.strict)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
