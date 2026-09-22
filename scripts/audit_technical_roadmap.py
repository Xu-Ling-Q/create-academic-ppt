#!/usr/bin/env python3
"""Audit the semantic contract and geometry of an academic technical roadmap."""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable


NODE_KINDS = {
    "goal",
    "question",
    "hypothesis",
    "work-package",
    "data",
    "method",
    "experiment",
    "mechanism",
    "decision",
    "output",
    "validation",
    "risk-control",
    "milestone",
    "contribution",
    "uncertainty",
    "scene",
    "annotation",
}
EDGE_KINDS = {
    "flow",
    "dependency",
    "evidence",
    "validation",
    "feedback",
    "uncertainty",
    "decision",
}
CORE_KINDS = {
    "goal",
    "question",
    "hypothesis",
    "work-package",
    "data",
    "method",
    "experiment",
    "mechanism",
    "decision",
    "output",
    "validation",
    "risk-control",
    "milestone",
    "contribution",
    "uncertainty",
}
METHOD_KINDS = {"method", "experiment", "mechanism"}
WAIVER_RULES = {
    "branch",
    "merge",
    "feedback_loop",
    "risk_control",
    "milestone",
    "validation",
    "contribution",
    "missing_bbox",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="roadmap contract JSON file")
    parser.add_argument("--strict", action="store_true", help="fail on warnings")
    parser.add_argument(
        "--semantic-only",
        action="store_true",
        help="skip geometry and typography checks; useful before layout",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def as_number(value: Any) -> float | None:
    return (
        float(value)
        if not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
        else None
    )


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def point(value: Any) -> tuple[float, float] | None:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        return None
    x, y = as_number(value[0]), as_number(value[1])
    return (x, y) if x is not None and y is not None else None


def bbox(value: Any) -> tuple[float, float, float, float] | None:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return None
    values = [as_number(item) for item in value]
    if any(item is None for item in values):
        return None
    x, y, width, height = (float(item) for item in values)
    return (x, y, width, height) if width > 0 and height > 0 else None


def rect_area_overlap(first: tuple[float, float, float, float], second: tuple[float, float, float, float]) -> float:
    x1, y1, w1, h1 = first
    x2, y2, w2, h2 = second
    return max(0.0, min(x1 + w1, x2 + w2) - max(x1, x2)) * max(
        0.0, min(y1 + h1, y2 + h2) - max(y1, y2)
    )


def orientation(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def on_segment(a: tuple[float, float], b: tuple[float, float], p: tuple[float, float]) -> bool:
    eps = 1e-7
    return (
        min(a[0], b[0]) - eps <= p[0] <= max(a[0], b[0]) + eps
        and min(a[1], b[1]) - eps <= p[1] <= max(a[1], b[1]) + eps
        and abs(orientation(a, b, p)) <= eps
    )


def segments_intersect(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
    d: tuple[float, float],
) -> bool:
    eps = 1e-7
    o1, o2 = orientation(a, b, c), orientation(a, b, d)
    o3, o4 = orientation(c, d, a), orientation(c, d, b)
    if ((o1 > eps and o2 < -eps) or (o1 < -eps and o2 > eps)) and (
        (o3 > eps and o4 < -eps) or (o3 < -eps and o4 > eps)
    ):
        return True
    return (
        (abs(o1) <= eps and on_segment(a, b, c))
        or (abs(o2) <= eps and on_segment(a, b, d))
        or (abs(o3) <= eps and on_segment(c, d, a))
        or (abs(o4) <= eps and on_segment(c, d, b))
    )


def polyline_segments(points: list[tuple[float, float]]) -> Iterable[tuple[tuple[float, float], tuple[float, float]]]:
    return zip(points, points[1:])


def point_in_rect(p: tuple[float, float], rect: tuple[float, float, float, float]) -> bool:
    x, y, width, height = rect
    return x <= p[0] <= x + width and y <= p[1] <= y + height


def segment_hits_rect(a: tuple[float, float], b: tuple[float, float], rect: tuple[float, float, float, float]) -> bool:
    if point_in_rect(a, rect) or point_in_rect(b, rect):
        return True
    x, y, width, height = rect
    corners = [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]
    return any(segments_intersect(a, b, corners[index], corners[(index + 1) % 4]) for index in range(4))


def reachable(start: str, targets: set[str], graph: dict[str, set[str]]) -> bool:
    if start in targets:
        return True
    seen = {start}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for next_node in graph.get(current, set()):
            if next_node in targets:
                return True
            if next_node not in seen:
                seen.add(next_node)
                queue.append(next_node)
    return False


def waiver_map(raw: Any, warnings: list[str], errors: list[str]) -> dict[str, str]:
    if raw is None:
        return {}
    if not isinstance(raw, list):
        errors.append("waivers must be a list of {rule, reason} objects.")
        return {}
    result: dict[str, str] = {}
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            errors.append(f"waivers[{index}] must be an object.")
            continue
        rule, reason = item.get("rule"), item.get("reason")
        if rule not in WAIVER_RULES:
            errors.append(f"waivers[{index}] uses unknown rule {rule!r}.")
        if not nonempty(reason):
            errors.append(f"waivers[{index}] must include a non-empty reason.")
        elif isinstance(rule, str):
            result[rule] = reason.strip()
    return result


def audit_manifest(data: Any, semantic_only: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    facts: dict[str, Any] = {}

    if not isinstance(data, dict):
        return {"ok": False, "errors": ["Manifest root must be a JSON object."], "warnings": [], "facts": {}}

    waivers = waiver_map(data.get("waivers"), warnings, errors)
    canvas = data.get("canvas")
    if not isinstance(canvas, dict):
        errors.append("canvas must be an object with width_mm and height_mm.")
        canvas = {}
    width, height = as_number(canvas.get("width_mm")), as_number(canvas.get("height_mm"))
    min_font = as_number(canvas.get("min_font_pt"))
    if width is None or width <= 0 or height is None or height <= 0:
        errors.append("canvas.width_mm and canvas.height_mm must be positive numbers.")
        width = width or 0.0
        height = height or 0.0
    if min_font is None or min_font <= 0:
        errors.append("canvas.min_font_pt must be a positive number.")
        min_font = 7.0

    stages = data.get("stages")
    stage_ids: set[str] = set()
    stage_order: dict[str, float] = {}
    if not isinstance(stages, list) or not stages:
        errors.append("stages must be a non-empty list.")
        stages = []
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict) or not nonempty(stage.get("id")):
            errors.append(f"stages[{index}] must include a non-empty id.")
            continue
        stage_id = stage["id"].strip()
        if stage_id in stage_ids:
            errors.append(f"duplicate stage id: {stage_id}.")
        stage_ids.add(stage_id)
        order = as_number(stage.get("order"))
        if order is None:
            errors.append(f"stage {stage_id} must include numeric order.")
        else:
            stage_order[stage_id] = order

    lanes = data.get("lanes")
    lane_ids: set[str] = set()
    if not isinstance(lanes, list) or not lanes:
        errors.append("lanes must be a non-empty list.")
        lanes = []
    for index, lane in enumerate(lanes):
        if not isinstance(lane, dict) or not nonempty(lane.get("id")):
            errors.append(f"lanes[{index}] must include a non-empty id.")
            continue
        lane_id = lane["id"].strip()
        if lane_id in lane_ids:
            errors.append(f"duplicate lane id: {lane_id}.")
        lane_ids.add(lane_id)

    raw_nodes = data.get("nodes")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        errors.append("nodes must be a non-empty list.")
        raw_nodes = []
    nodes: dict[str, dict[str, Any]] = {}
    node_rects: dict[str, tuple[float, float, float, float]] = {}
    for index, node in enumerate(raw_nodes):
        if not isinstance(node, dict):
            errors.append(f"nodes[{index}] must be an object.")
            continue
        node_id = node.get("id")
        if not nonempty(node_id):
            errors.append(f"nodes[{index}] must include a non-empty id.")
            continue
        node_id = node_id.strip()
        if node_id in nodes:
            errors.append(f"duplicate node id: {node_id}.")
            continue
        kind = node.get("kind")
        if kind not in NODE_KINDS:
            errors.append(f"node {node_id} uses unknown kind {kind!r}.")
        if not nonempty(node.get("label")):
            errors.append(f"node {node_id} must include a non-empty label.")
        if kind != "annotation" and not nonempty(node.get("source")):
            errors.append(f"node {node_id} must include source status or locator.")
        if node.get("stage") not in stage_ids:
            errors.append(f"node {node_id} references unknown stage {node.get('stage')!r}.")
        if node.get("lane") not in lane_ids:
            errors.append(f"node {node_id} references unknown lane {node.get('lane')!r}.")
        rect = bbox(node.get("bbox"))
        if rect is None:
            if "bbox" not in node and "missing_bbox" in waivers:
                pass
            elif "bbox" not in node:
                warnings.append(f"node {node_id} has no bbox; layout checks are incomplete.")
            else:
                errors.append(f"node {node_id} has an invalid bbox [x, y, width, height].")
        else:
            node_rects[node_id] = rect
            x, y, node_width, node_height = rect
            if width and (x < 0 or y < 0 or x + node_width > width or y + node_height > height):
                errors.append(f"node {node_id} lies outside the canvas.")
        font_pt = as_number(node.get("font_pt"))
        if font_pt is not None and font_pt < min_font:
            errors.append(f"node {node_id} font is {font_pt:.2f} pt, below canvas minimum {min_font:.2f} pt.")
        nodes[node_id] = node

    raw_edges = data.get("edges")
    if not isinstance(raw_edges, list):
        errors.append("edges must be a list.")
        raw_edges = []
    edges: list[dict[str, Any]] = []
    graph: dict[str, set[str]] = defaultdict(set)
    reverse_graph: dict[str, set[str]] = defaultdict(set)
    edge_points: list[list[tuple[float, float]]] = []
    for index, edge in enumerate(raw_edges):
        if not isinstance(edge, dict):
            errors.append(f"edges[{index}] must be an object.")
            continue
        source, target, kind = edge.get("source"), edge.get("target"), edge.get("kind")
        if source not in nodes or target not in nodes:
            errors.append(f"edge {index} references an unknown source or target.")
            continue
        if kind not in EDGE_KINDS:
            errors.append(f"edge {index} uses unknown kind {kind!r}.")
        graph[source].add(target)
        reverse_graph[target].add(source)
        edges.append(edge)
        points_raw = edge.get("points")
        if points_raw is None:
            edge_points.append([])
        elif not isinstance(points_raw, list) or len(points_raw) < 2 or any(point(item) is None for item in points_raw):
            errors.append(f"edge {index} points must contain at least two [x, y] points.")
            edge_points.append([])
        else:
            points = [point(item) for item in points_raw]
            concrete_points = [item for item in points if item is not None]
            edge_points.append(concrete_points)
            if not semantic_only and width and height:
                if any(item[0] < 0 or item[1] < 0 or item[0] > width or item[1] > height for item in concrete_points):
                    errors.append(f"edge {index} has points outside the canvas.")

    kind_sets = {kind: {node_id for node_id, node in nodes.items() if node.get("kind") == kind} for kind in NODE_KINDS}
    facts.update(
        {
            "canvas_width_mm": width,
            "canvas_height_mm": height,
            "min_font_pt": min_font,
            "stages": len(stage_ids),
            "lanes": len(lane_ids),
            "nodes": len(nodes),
            "edges": len(edges),
            "node_kinds": {kind: len(ids) for kind, ids in kind_sets.items() if ids},
        }
    )

    def require_kind(kind: str, rule: str | None = None) -> None:
        if not kind_sets.get(kind):
            if rule and rule in waivers:
                return
            errors.append(f"roadmap requires at least one {kind} node.")

    require_kind("goal")
    require_kind("question")
    require_kind("work-package")
    if not (kind_sets.get("method") or kind_sets.get("experiment") or kind_sets.get("mechanism")):
        errors.append("roadmap requires at least one method, experiment, or mechanism node.")
    require_kind("output")
    require_kind("validation", "validation")

    core_nodes = {node_id for node_id, node in nodes.items() if node.get("kind") in CORE_KINDS}
    for node_id in sorted(core_nodes):
        degree = len(graph.get(node_id, set())) + len(reverse_graph.get(node_id, set()))
        if degree == 0:
            errors.append(f"core node {node_id} is disconnected from the route.")

    goals = kind_sets.get("goal", set())
    questions = kind_sets.get("question", set())
    work_packages = kind_sets.get("work-package", set())
    methodish = set().union(*(kind_sets.get(kind, set()) for kind in METHOD_KINDS))
    outputs = kind_sets.get("output", set())
    validations = kind_sets.get("validation", set())
    contributions = kind_sets.get("contribution", set())

    for goal in goals:
        if questions and not reachable(goal, questions, graph):
            errors.append(f"goal {goal} does not reach a scientific question.")
    for question in questions:
        if methodish or work_packages:
            if not reachable(question, methodish | work_packages, graph):
                errors.append(f"question {question} does not reach a work package or method.")
    for work_package in work_packages:
        if methodish and not reachable(work_package, methodish, graph):
            errors.append(f"work package {work_package} has no reachable method or experiment.")
        if outputs and not reachable(work_package, outputs, graph):
            errors.append(f"work package {work_package} has no reachable output.")
    for output in outputs:
        if validations and not reachable(output, validations, graph):
            if "validation" not in waivers:
                errors.append(f"output {output} has no reachable validation node.")
    if contributions:
        for contribution in contributions:
            if not reverse_graph.get(contribution):
                errors.append(f"contribution {contribution} has no supporting incoming edge.")
        if validations and not any(reachable(validation, contributions, graph) for validation in validations):
            if "contribution" not in waivers:
                errors.append("no validation node reaches a contribution endpoint.")

    outdegrees = {node_id: len(graph.get(node_id, set())) for node_id in core_nodes}
    indegrees = {node_id: len(reverse_graph.get(node_id, set())) for node_id in core_nodes}
    branch_nodes = [node_id for node_id, degree in outdegrees.items() if degree > 1]
    merge_nodes = [node_id for node_id, degree in indegrees.items() if degree > 1]
    facts["branch_nodes"] = branch_nodes
    facts["merge_nodes"] = merge_nodes
    if not branch_nodes and "branch" not in waivers:
        warnings.append("route has no explicit branch; add one or record a branch waiver.")
    if not merge_nodes and "merge" not in waivers:
        warnings.append("route has no explicit merge; add one or record a merge waiver.")
    if not any(edge.get("kind") == "feedback" for edge in edges) and "feedback_loop" not in waivers:
        warnings.append("route has no feedback edge; add a closed loop or record a feedback_loop waiver.")
    if not kind_sets.get("risk-control") and "risk_control" not in waivers:
        warnings.append("route has no risk-control node; add one or record a risk_control waiver.")
    if not kind_sets.get("milestone") and "milestone" not in waivers:
        warnings.append("route has no milestone node; add one or record a milestone waiver.")

    if not semantic_only:
        for first_id, first_rect in node_rects.items():
            first_node = nodes[first_id]
            for second_id, second_rect in node_rects.items():
                if first_id >= second_id:
                    continue
                if first_node.get("allow_overlap") or nodes[second_id].get("allow_overlap"):
                    continue
                if rect_area_overlap(first_rect, second_rect) > 0.25:
                    warnings.append(f"nodes {first_id} and {second_id} overlap; mark an intentional inset explicitly.")

        missing_bbox = [node_id for node_id in nodes if node_id not in node_rects]
        if missing_bbox and "missing_bbox" not in waivers:
            warnings.append("one or more nodes lack geometry; final layout QA is incomplete.")

        crossing_pairs: list[list[int]] = []
        for first_index, first_edge in enumerate(edges):
            first_points = edge_points[first_index]
            if len(first_points) < 2:
                continue
            for second_index in range(first_index + 1, len(edges)):
                second_edge = edges[second_index]
                if first_edge.get("source") in {second_edge.get("source"), second_edge.get("target")} or first_edge.get("target") in {second_edge.get("source"), second_edge.get("target")}:
                    continue
                second_points = edge_points[second_index]
                if len(second_points) < 2:
                    continue
                if any(segments_intersect(a, b, c, d) for a, b in polyline_segments(first_points) for c, d in polyline_segments(second_points)):
                    crossing_pairs.append([first_index, second_index])
        facts["edge_crossings"] = crossing_pairs
        if crossing_pairs:
            warnings.append(f"{len(crossing_pairs)} connector crossing pair(s) detected; reroute or document them.")

        node_edge_hits: list[dict[str, Any]] = []
        for edge_index, edge in enumerate(edges):
            points = edge_points[edge_index]
            if len(points) < 2:
                continue
            for node_id, rect in node_rects.items():
                if node_id in {edge.get("source"), edge.get("target")}:
                    continue
                if any(segment_hits_rect(a, b, rect) for a, b in polyline_segments(points)):
                    node_edge_hits.append({"edge": edge_index, "node": node_id})
        facts["node_edge_hits"] = node_edge_hits
        if node_edge_hits:
            warnings.append(f"{len(node_edge_hits)} connector(s) pass through an unrelated node.")

        stage_backtracks: list[int] = []
        for edge_index, edge in enumerate(edges):
            if edge.get("kind") == "feedback":
                continue
            source_stage = nodes[edge["source"]].get("stage")
            target_stage = nodes[edge["target"]].get("stage")
            if source_stage in stage_order and target_stage in stage_order and stage_order[target_stage] < stage_order[source_stage]:
                stage_backtracks.append(edge_index)
        facts["stage_backtracks"] = stage_backtracks
        if stage_backtracks:
            warnings.append("one or more non-feedback edges move backward across stage order.")

        long_labels: list[str] = []
        for node_id, node in nodes.items():
            label = str(node.get("label", ""))
            rect = node_rects.get(node_id)
            if rect is None:
                continue
            x, y, node_width, node_height = rect
            font_pt = as_number(node.get("font_pt")) or min_font
            chars_per_line = max(8.0, node_width * 1.4)
            estimated_lines = max(1, math.ceil(len(label) / chars_per_line))
            required_height = estimated_lines * font_pt * 0.38 + 3.0
            if required_height > node_height + 0.5 or (node_width < 14 and len(label) > 24) or len(label) > 100:
                long_labels.append(node_id)
        facts["dense_labels"] = long_labels
        if long_labels:
            warnings.append("some labels are likely to wrap or overflow at final size: " + ", ".join(long_labels) + ".")

        if len(nodes) > 40:
            warnings.append("route contains more than 40 nodes; consider an inset or appendix for secondary detail.")
        if len(edges) > 60:
            warnings.append("route contains more than 60 connectors; bundle secondary evidence paths.")

    facts["waivers"] = waivers
    return {"ok": not errors, "errors": errors, "warnings": warnings, "facts": facts}


def human_report(report: dict[str, Any], path: Path, strict: bool) -> str:
    facts = report.get("facts", {})
    lines = [
        f"Technical roadmap audit: {path.resolve()}",
        f"Canvas: {facts.get('canvas_width_mm', '?')} x {facts.get('canvas_height_mm', '?')} mm",
        f"Nodes: {facts.get('nodes', 0)} | Edges: {facts.get('edges', 0)} | Stages: {facts.get('stages', 0)} | Lanes: {facts.get('lanes', 0)}",
        f"Branches: {len(facts.get('branch_nodes', []))} | Merges: {len(facts.get('merge_nodes', []))} | Crossings: {len(facts.get('edge_crossings', []))}",
        "",
    ]
    errors = report.get("errors", [])
    warnings = report.get("warnings", [])
    if errors:
        lines.append("Errors:")
        lines.extend(f"- {item}" for item in errors)
    if warnings:
        lines.append("Warnings:")
        lines.extend(f"- {item}" for item in warnings)
    if not errors and not warnings:
        lines.append("PASS: semantic and layout checks passed.")
    elif not errors and not strict:
        lines.append("PASS: no blocking errors; review warnings before delivery.")
    else:
        lines.append("FAIL: blocking errors or strict-mode warnings remain.")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report = {"ok": False, "errors": [f"could not read JSON manifest: {exc}"], "warnings": [], "facts": {}}
    else:
        report = audit_manifest(data, semantic_only=args.semantic_only)
    strict_failure = args.strict and bool(report.get("warnings"))
    report["ok"] = bool(report.get("ok")) and not strict_failure
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(human_report(report, args.manifest, args.strict))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
