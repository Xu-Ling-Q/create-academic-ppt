#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const bundledNodeModules = path.join(path.dirname(path.dirname(process.execPath)), "node_modules");
const bundledRequire = fs.existsSync(bundledNodeModules)
  ? createRequire(path.join(bundledNodeModules, "__codex_require__.js"))
  : null;
const browserCandidates = [
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  path.join(process.env.LOCALAPPDATA || "", "Google", "Chrome", "Application", "chrome.exe"),
  path.join(process.env.LOCALAPPDATA || "", "Microsoft", "Edge", "Application", "msedge.exe"),
];

const VALID_FORMATS = new Set(["html", "svg", "png", "pdf", "tiff", "share", "webm"]);
const DEFAULT_FORMATS = ["html", "svg"];
const VALID_STATUSES = new Set(["verified", "inferred", "proposed", "not-yet-available", "excluded"]);
const ESCAPE_RE = /[&<>"']/g;
const ESCAPE_MAP = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
};

function parseArgs(argv) {
  const args = { formats: DEFAULT_FORMATS.slice(), scale: 1, strict: false, check: false };
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    const next = () => {
      if (index + 1 >= argv.length) {
        throw new Error(`Missing value for ${token}`);
      }
      index += 1;
      return argv[index];
    };
    if (token === "--ir") args.ir = next();
    else if (token === "--out") args.out = next();
    else if (token === "--formats") args.formats = next().split(",").map((item) => item.trim()).filter(Boolean);
    else if (token === "--scale") args.scale = Number(next());
    else if (token === "--strict") args.strict = true;
    else if (token === "--check") args.check = true;
    else if (token === "--help" || token === "-h") args.help = true;
    else throw new Error(`Unknown argument: ${token}`);
  }
  return args;
}

function usage() {
  return [
    "Usage: node render_interactive_html.mjs --ir <file.json> --out <dir> [options]",
    "",
    "Options:",
    "  --formats html,svg,png,pdf,tiff,share,webm",
    "  --scale <number>       Browser export scale, default 1",
    "  --check                Validate IR and report optional exporters",
    "  --strict               Fail when requested optional exporters are unavailable",
  ].join("\n");
}

function escapeXml(value) {
  return String(value ?? "").replace(ESCAPE_RE, (char) => ESCAPE_MAP[char]);
}

function escapeJson(value) {
  return JSON.stringify(value).replace(/</g, "\\u003c").replace(/>/g, "\\u003e").replace(/&/g, "\\u0026");
}

function number(value, fallback = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function loadOptional(name) {
  const loaders = bundledRequire ? [require, bundledRequire] : [require];
  let lastError = null;
  for (const loader of loaders) {
    try {
      return { module: loader(name), error: null };
    } catch (error) {
      lastError = error;
    }
  }
  return { module: null, error: lastError instanceof Error ? lastError.message : String(lastError) };
}

function findBrowserExecutable() {
  for (const candidate of browserCandidates) {
    if (candidate && fs.existsSync(candidate)) {
      return candidate;
    }
  }
  return null;
}

function validateIr(ir) {
  const errors = [];
  const warnings = [];
  if (!ir || typeof ir !== "object" || Array.isArray(ir)) {
    return { errors: ["IR must be a JSON object."], warnings };
  }
  for (const field of ["version", "meta", "canvas", "nodes", "edges"]) {
    if (!(field in ir)) errors.push(`Missing required top-level field: ${field}`);
  }
  if (!ir.canvas || number(ir.canvas.width) <= 0 || number(ir.canvas.height) <= 0) {
    errors.push("canvas.width and canvas.height must be positive numbers.");
  }
  if (!Array.isArray(ir.nodes)) errors.push("nodes must be an array.");
  if (!Array.isArray(ir.edges)) errors.push("edges must be an array.");
  const ids = new Set();
  for (const [index, node] of (ir.nodes ?? []).entries()) {
    if (!node || typeof node !== "object") {
      errors.push(`nodes[${index}] must be an object.`);
      continue;
    }
    for (const field of ["id", "label", "x", "y", "w", "h"]) {
      if (!(field in node)) errors.push(`nodes[${index}] is missing ${field}.`);
    }
    if (ids.has(node.id)) errors.push(`Duplicate node id: ${node.id}`);
    ids.add(node.id);
    if (number(node.w) <= 0 || number(node.h) <= 0) warnings.push(`Node ${node.id} has non-positive size.`);
    if (node.status && !VALID_STATUSES.has(node.status)) warnings.push(`Node ${node.id} uses unknown status ${node.status}.`);
    if (!node.source) warnings.push(`Node ${node.id} has no source provenance.`);
  }
  for (const [index, edge] of (ir.edges ?? []).entries()) {
    if (!edge || typeof edge !== "object") {
      errors.push(`edges[${index}] must be an object.`);
      continue;
    }
    for (const field of ["source", "target"]) {
      if (!(field in edge)) errors.push(`edges[${index}] is missing ${field}.`);
    }
    if (!ids.has(edge.source)) errors.push(`Edge ${edge.id ?? index} references missing source node ${edge.source}.`);
    if (!ids.has(edge.target)) errors.push(`Edge ${edge.id ?? index} references missing target node ${edge.target}.`);
    if (edge.status && !VALID_STATUSES.has(edge.status)) warnings.push(`Edge ${edge.id ?? index} uses unknown status ${edge.status}.`);
    if (!edge.provenance) warnings.push(`Edge ${edge.id ?? index} has no provenance field.`);
  }
  for (const step of ir.steps ?? []) {
    if (step && (!step.id || !step.label)) warnings.push("Each step should have both id and label.");
  }
  return { errors, warnings };
}

function linePoints(edge, nodesById) {
  if (Array.isArray(edge.points) && edge.points.length >= 2) {
    return edge.points.map((point) => Array.isArray(point) ? [number(point[0]), number(point[1])] : [number(point.x), number(point.y)]);
  }
  const source = nodesById.get(edge.source);
  const target = nodesById.get(edge.target);
  if (!source || !target) return [];
  return [
    [number(source.x) + number(source.w) / 2, number(source.y) + number(source.h) / 2],
    [number(target.x) + number(target.w) / 2, number(target.y) + number(target.h) / 2],
  ];
}

function pathData(points) {
  if (points.length < 2) return "";
  if (points.length === 2) {
    return `M ${points[0][0]} ${points[0][1]} L ${points[1][0]} ${points[1][1]}`;
  }
  return points.map((point, index) => `${index === 0 ? "M" : "L"} ${point[0]} ${point[1]}`).join(" ");
}

function wrapText(text, maxChars) {
  const raw = String(text ?? "").trim();
  if (!raw) return [];
  const lines = [];
  let current = "";
  for (const word of raw.split(/\s+/)) {
    const candidate = current ? `${current} ${word}` : word;
    if (current && candidate.length > maxChars) {
      lines.push(current);
      current = word;
    } else {
      current = candidate;
    }
  }
  if (current) lines.push(current);
  return lines.slice(0, 4);
}

function nodeFill(node) {
  if (node.fill) return node.fill;
  const palette = {
    data: "#E4F1FF",
    method: "#E7F5EC",
    mechanism: "#FFF0D7",
    validation: "#F0E9FF",
    decision: "#FFE4E4",
    output: "#E6F7F6",
    goal: "#EEF1F5",
    annotation: "#FFFFFF",
  };
  return palette[node.kind] ?? "#FFFFFF";
}

function nodeShape(node, attrs) {
  const shape = node.shape ?? "rounded";
  if (shape === "circle") {
    const radius = Math.min(number(node.w), number(node.h)) / 2;
    return `<circle cx="${number(node.x) + number(node.w) / 2}" cy="${number(node.y) + number(node.h) / 2}" r="${radius}" ${attrs}/>`;
  }
  if (shape === "diamond") {
    const cx = number(node.x) + number(node.w) / 2;
    const cy = number(node.y) + number(node.h) / 2;
    const points = `${cx},${node.y} ${number(node.x) + number(node.w)},${cy} ${cx},${number(node.y) + number(node.h)} ${node.x},${cy}`;
    return `<polygon points="${points}" ${attrs}/>`;
  }
  const radius = shape === "rect" ? 0 : 14;
  return `<rect x="${number(node.x)}" y="${number(node.y)}" width="${number(node.w)}" height="${number(node.h)}" rx="${radius}" ${attrs}/>`;
}

function buildSvg(ir) {
  const width = number(ir.canvas.width);
  const height = number(ir.canvas.height);
  const nodesById = new Map((ir.nodes ?? []).map((node) => [node.id, node]));
  const title = escapeXml(ir.meta?.title ?? ir.meta?.id ?? "Academic visual");
  const description = escapeXml(ir.meta?.description ?? "Evidence-grounded academic visual");
  const background = escapeXml(ir.canvas.background ?? "#F7F9FC");
  const groups = (ir.groups ?? []).map((group) => {
    const label = group.label
      ? `<text x="${number(group.x) + 18}" y="${number(group.y) + 28}" class="group-label">${escapeXml(group.label)}</text>`
      : "";
    return `<g class="ir-group" data-group-id="${escapeXml(group.id ?? "")}">
      <rect x="${number(group.x)}" y="${number(group.y)}" width="${number(group.w)}" height="${number(group.h)}" rx="18" class="group-box"/>
      ${label}
    </g>`;
  }).join("\n");
  const edges = (ir.edges ?? []).map((edge, index) => {
    const points = linePoints(edge, nodesById);
    const d = pathData(points);
    if (!d) return "";
    const color = escapeXml(edge.color ?? "#536273");
    const dash = edge.dash ? `stroke-dasharray="${escapeXml(edge.dash)}"` : "";
    const label = edge.label && points.length >= 2
      ? `<text x="${(points[0][0] + points[points.length - 1][0]) / 2}" y="${(points[0][1] + points[points.length - 1][1]) / 2 - 8}" class="edge-label">${escapeXml(edge.label)}</text>`
      : "";
    return `<g class="ir-edge" data-edge-id="${escapeXml(edge.id ?? `edge-${index}`)}" data-source="${escapeXml(edge.source)}" data-target="${escapeXml(edge.target)}" data-status="${escapeXml(edge.status ?? "unlabeled")}" data-provenance="${escapeXml(edge.provenance ?? "")}">
      <path d="${d}" fill="none" stroke="${color}" stroke-width="${number(edge.width, 3)}" ${dash} marker-end="${edge.directed === false ? "" : "url(#arrow)"}"/>
      ${label}
    </g>`;
  }).join("\n");
  const nodes = (ir.nodes ?? []).map((node) => {
    const fill = escapeXml(nodeFill(node));
    const stroke = escapeXml(node.stroke ?? "#344454");
    const textColor = escapeXml(node.textColor ?? "#182431");
    const labelLines = wrapText(node.label, Math.max(10, Math.floor(number(node.w) / 12))).slice(0, 2);
    const subtitleLimit = labelLines.length > 1 ? 1 : 2;
    const subtitleLines = wrapText(node.subtitle, Math.max(12, Math.floor(number(node.w) / 8))).slice(0, subtitleLimit);
    const textX = number(node.x) + 18;
    const labelY = number(node.y) + 32;
    const subtitleY = number(node.y) + number(node.h) - (subtitleLines.length > 1 ? 34 : 18);
    const labelSvg = labelLines.map((line, lineIndex) => `<tspan x="${textX}" dy="${lineIndex === 0 ? 0 : 22}">${escapeXml(line)}</tspan>`).join("");
    const subtitleSvg = subtitleLines.map((line, lineIndex) => `<tspan x="${textX}" dy="${lineIndex === 0 ? 0 : 16}">${escapeXml(line)}</tspan>`).join("");
    const detail = escapeXml(node.detail ?? "");
    return `<g class="ir-node" tabindex="0" role="button" data-node-id="${escapeXml(node.id)}" data-label="${escapeXml(node.label)}" data-kind="${escapeXml(node.kind ?? "node")}" data-status="${escapeXml(node.status ?? "unlabeled")}" data-source="${escapeXml(node.source ?? "")}" data-provenance="${escapeXml(node.provenance ?? node.source ?? "")}" data-tags="${escapeXml((node.tags ?? []).join(","))}" data-detail="${detail}">
      ${nodeShape(node, `fill="${fill}" stroke="${stroke}" stroke-width="2"`)}
      <text x="${textX}" y="${labelY}" fill="${textColor}" class="node-label">${labelSvg}</text>
      ${subtitleLines.length ? `<text x="${textX}" y="${subtitleY}" fill="${textColor}" class="node-subtitle">${subtitleSvg}</text>` : ""}
    </g>`;
  }).join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" role="img" aria-labelledby="ir-title ir-desc">
  <title id="ir-title">${title}</title>
  <desc id="ir-desc">${description}</desc>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto" markerUnits="strokeWidth">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#536273"/>
    </marker>
    <style>
      .group-box { fill: none; stroke: #B9C4D0; stroke-width: 2; stroke-dasharray: 8 8; }
      .group-label { fill: #536273; font: 600 18px Arial, sans-serif; }
      .edge-label { fill: #536273; font: 14px Arial, sans-serif; }
      .node-label { font: 600 20px Arial, sans-serif; }
      .node-subtitle { font: 14px Arial, sans-serif; opacity: .8; }
      .node-status { fill: #536273; font: 11px Arial, sans-serif; letter-spacing: .4px; }
      .ir-node { cursor: pointer; outline: none; }
      .ir-node:focus .node-label, .ir-node:hover .node-label { text-decoration: underline; }
      .ir-node.is-dimmed, .ir-edge.is-dimmed { opacity: .16; }
      .ir-node.is-selected rect, .ir-node.is-selected circle, .ir-node.is-selected polygon { stroke: #0B6E99; stroke-width: 4; }
      .ir-edge.is-selected path { stroke: #0B6E99; stroke-width: 5; }
    </style>
  </defs>
  <rect width="${width}" height="${height}" fill="${background}"/>
  <g class="ir-groups">${groups}</g>
  <g class="ir-edges">${edges}</g>
  <g class="ir-nodes">${nodes}</g>
</svg>`;
}

function buildHtml(ir, svg) {
  const width = number(ir.canvas.width);
  const height = number(ir.canvas.height);
  const payload = escapeJson(ir);
  const title = escapeXml(ir.meta?.title ?? ir.meta?.id ?? "Academic visual");
  const steps = (ir.steps ?? []).map((step) => `<option value="${escapeXml(step.id)}">${escapeXml(step.label)}</option>`).join("");
  const svgWithoutXml = svg.replace(/^<\?xml[^>]*>\s*/i, "");
  return `<!doctype html>
<html lang="${escapeXml(ir.meta?.language ?? "en")}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="${escapeXml(ir.meta?.description ?? title)}">
<title>${title}</title>
<style>
:root { color-scheme: light; --bg:#F7F9FC; --panel:#FFFFFF; --ink:#182431; --muted:#536273; --line:#D8E0E8; --accent:#0B6E99; }
:root.dark { color-scheme: dark; --bg:#121820; --panel:#1B2530; --ink:#F4F7FA; --muted:#B9C4D0; --line:#3A4856; --accent:#70C7E8; }
* { box-sizing:border-box; }
html,body { margin:0; height:100%; min-height:100%; background:var(--bg); color:var(--ink); font-family:Arial, sans-serif; }
body { min-height:100vh; display:grid; grid-template-rows:auto 1fr; }
header { display:flex; flex-wrap:wrap; align-items:center; gap:8px; padding:10px 14px; border-bottom:1px solid var(--line); background:var(--panel); }
h1 { margin:0 12px 0 0; font-size:18px; line-height:1.2; }
button, input, select { font:inherit; color:inherit; background:var(--panel); border:1px solid var(--line); border-radius:6px; min-height:34px; }
button { cursor:pointer; padding:0 10px; }
button:hover, button:focus, select:focus, input:focus { border-color:var(--accent); outline:2px solid color-mix(in srgb, var(--accent) 24%, transparent); }
input { min-width:180px; padding:0 10px; }
select { padding:0 8px; }
main { min-height:0; display:grid; grid-template-columns:minmax(0,1fr) 280px; }
#stage { position:relative; overflow:hidden; min-height:0; background:var(--bg); }
#viewport { width:100%; height:100%; touch-action:none; cursor:grab; }
#viewport.dragging { cursor:grabbing; }
#viewport svg { display:block; width:${width}px; height:${height}px; max-width:none; transform-origin:0 0; }
aside { overflow:auto; padding:16px; border-left:1px solid var(--line); background:var(--panel); }
aside h2 { font-size:14px; margin:0 0 10px; }
dl { margin:0; font-size:13px; }
dt { color:var(--muted); margin-top:12px; }
dd { margin:3px 0 0; overflow-wrap:anywhere; }
.hint { margin-top:18px; color:var(--muted); font-size:12px; line-height:1.45; }
.badge { display:inline-block; padding:2px 6px; border:1px solid var(--line); border-radius:999px; font-size:11px; }
@media (max-width: 760px) {
  main { grid-template-columns:1fr; grid-template-rows:minmax(0,1fr) auto; }
  aside { max-height:190px; border-left:0; border-top:1px solid var(--line); }
  header { align-items:stretch; }
  h1 { flex-basis:100%; }
  input { flex:1 1 150px; min-width:0; }
}
@media print {
  @page { size: ${width}px ${height}px; margin: 0; }
  header, aside { display:none !important; }
  html, body { width:${width}px; height:${height}px; background:white; }
  body, main, #stage, #viewport { display:block; overflow:visible; }
  #viewport svg { width:${width}px; height:${height}px; transform:none !important; }
}
</style>
</head>
<body>
<header>
  <h1>${title}</h1>
  <input id="search" type="search" placeholder="Search labels, tags, sources" aria-label="Search">
  <select id="step" aria-label="Focus step"><option value="">All steps</option>${steps}</select>
  <button id="fit" type="button">Fit</button>
  <button id="reset" type="button">Reset</button>
  <button id="theme" type="button">Theme</button>
  <button id="print" type="button">Print / PDF</button>
</header>
<main>
  <section id="stage" aria-label="Interactive academic visual">
    <div id="viewport">${svgWithoutXml}</div>
  </section>
  <aside>
    <h2>Selection</h2>
    <dl>
      <dt>Label</dt><dd id="selected-label">None</dd>
      <dt>Kind</dt><dd id="selected-kind">-</dd>
      <dt>Status</dt><dd id="selected-status">-</dd>
      <dt>Source</dt><dd id="selected-source">-</dd>
      <dt>Detail</dt><dd id="selected-detail">-</dd>
      <dt>Provenance</dt><dd id="selected-provenance">-</dd>
    </dl>
    <p class="hint">The HTML view is an inspection companion. Use the audited vector PDF/SVG or editable PPTX for formal delivery.</p>
  </aside>
</main>
<script>
(() => {
  const ir = ${payload};
  const root = document.documentElement;
  const stage = document.getElementById("stage");
  const viewport = document.getElementById("viewport");
  const svg = viewport.querySelector("svg");
  const search = document.getElementById("search");
  const step = document.getElementById("step");
  const nodes = [...viewport.querySelectorAll(".ir-node")];
  const edges = [...viewport.querySelectorAll(".ir-edge")];
  const nodeById = new Map(nodes.map((node) => [node.dataset.nodeId, node]));
  const edgeByNode = new Map();
  let scale = 1;
  let tx = 0;
  let ty = 0;
  let dragging = false;
  let dragStart = null;

  for (const edge of ir.edges || []) {
    for (const id of [edge.source, edge.target]) {
      if (!edgeByNode.has(id)) edgeByNode.set(id, []);
      edgeByNode.get(id).push(edge.id || (edge.source + "-" + edge.target));
    }
  }

  function applyTransform() {
    svg.style.transform = "translate(" + tx + "px," + ty + "px) scale(" + scale + ")";
  }

  function fit() {
    const pad = 30;
    const width = Math.max(1, stage.clientWidth - pad);
    const height = Math.max(1, stage.clientHeight - pad);
    scale = Math.min(width / ir.canvas.width, height / ir.canvas.height);
    scale = Math.max(0.1, Math.min(scale, 1.5));
    tx = (stage.clientWidth - ir.canvas.width * scale) / 2;
    ty = (stage.clientHeight - ir.canvas.height * scale) / 2;
    applyTransform();
  }

  function reset() {
    scale = 1;
    tx = 0;
    ty = 0;
    applyTransform();
  }

  function setSelection(node) {
    for (const item of nodes) item.classList.remove("is-selected");
    for (const edge of edges) edge.classList.remove("is-selected");
    if (!node) {
      document.getElementById("selected-label").textContent = "None";
      document.getElementById("selected-kind").textContent = "-";
      document.getElementById("selected-status").textContent = "-";
      document.getElementById("selected-source").textContent = "-";
      document.getElementById("selected-detail").textContent = "-";
      document.getElementById("selected-provenance").textContent = "-";
      return;
    }
    node.classList.add("is-selected");
    const nodeId = node.dataset.nodeId;
    const connected = new Set(edgeByNode.get(nodeId) || []);
    for (const edge of edges) {
      if (connected.has(edge.dataset.edgeId)) edge.classList.add("is-selected");
    }
    document.getElementById("selected-label").textContent = node.dataset.label || "-";
    document.getElementById("selected-kind").textContent = node.dataset.kind || "-";
    document.getElementById("selected-status").textContent = node.dataset.status || "-";
    document.getElementById("selected-source").textContent = node.dataset.source || "-";
    document.getElementById("selected-detail").textContent = node.dataset.detail || "-";
    document.getElementById("selected-provenance").textContent = node.dataset.provenance || "-";
  }

  function applyFilter() {
    const term = search.value.trim().toLowerCase();
    const stepId = step.value;
    const activeStep = (ir.steps || []).find((item) => item.id === stepId);
    const activeIds = new Set(activeStep?.nodeIds || []);
    for (const node of nodes) {
      const haystack = [
        node.dataset.nodeId,
        node.dataset.kind,
        node.dataset.status,
        node.dataset.source,
        node.dataset.tags,
        node.textContent,
      ].join(" ").toLowerCase();
      const matchSearch = !term || haystack.includes(term);
      const matchStep = !stepId || activeIds.has(node.dataset.nodeId);
      node.classList.toggle("is-dimmed", !(matchSearch && matchStep));
    }
    for (const edge of edges) {
      const source = nodeById.get(edge.dataset.source);
      const target = nodeById.get(edge.dataset.target);
      const visible = !source?.classList.contains("is-dimmed") && !target?.classList.contains("is-dimmed");
      edge.classList.toggle("is-dimmed", !visible);
    }
  }

  search.addEventListener("input", applyFilter);
  step.addEventListener("change", applyFilter);
  document.getElementById("fit").addEventListener("click", fit);
  document.getElementById("reset").addEventListener("click", reset);
  document.getElementById("theme").addEventListener("click", () => root.classList.toggle("dark"));
  document.getElementById("print").addEventListener("click", () => window.print());

  for (const node of nodes) {
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        setSelection(node);
      }
    });
  }

  viewport.addEventListener("click", (event) => {
    const node = event.target.closest?.(".ir-node");
    if (node) setSelection(node);
  });
  viewport.addEventListener("pointerdown", (event) => {
    if (event.target.closest?.(".ir-node")) return;
    dragging = true;
    dragStart = { x: event.clientX - tx, y: event.clientY - ty };
    viewport.classList.add("dragging");
    viewport.setPointerCapture(event.pointerId);
  });
  viewport.addEventListener("pointermove", (event) => {
    if (!dragging) return;
    tx = event.clientX - dragStart.x;
    ty = event.clientY - dragStart.y;
    applyTransform();
  });
  viewport.addEventListener("pointerup", () => {
    dragging = false;
    viewport.classList.remove("dragging");
  });
  viewport.addEventListener("wheel", (event) => {
    event.preventDefault();
    const rect = stage.getBoundingClientRect();
    const oldScale = scale;
    const factor = event.deltaY < 0 ? 1.1 : 0.9;
    scale = Math.max(0.1, Math.min(4, scale * factor));
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    tx = x - (x - tx) * (scale / oldScale);
    ty = y - (y - ty) * (scale / oldScale);
    applyTransform();
  }, { passive: false });

  window.addEventListener("resize", fit);
  fit();
  const initialNodeId = ir.meta?.focusNode || (ir.nodes || []).find((item) => item && item.focus)?.id || null;
  const initial = initialNodeId ? nodes.find((node) => node.dataset.nodeId === initialNodeId) : null;
  if (initial) setSelection(initial);
  window.__IR_READY__ = true;
})();
</script>
</body>
</html>`;
}

async function exportRasterAndPdf(page, ir, outDir, formats) {
  const results = {};
  const needsRaster = formats.some((format) => ["png", "share", "tiff"].includes(format));
  const needsPdf = formats.includes("pdf");
  const sharp = loadOptional("sharp");
  let tempCapture = null;

  if (needsRaster) {
    tempCapture = path.join(outDir, `${ir.meta?.id ?? "academic-visual"}.capture.png`);
    await page.locator("#stage").screenshot({ path: tempCapture });
    const basePng = path.join(outDir, `${ir.meta?.id ?? "academic-visual"}.png`);
    if (formats.includes("png")) {
      fs.copyFileSync(tempCapture, basePng);
      results.png = { status: "generated", path: basePng };
    }
    if (formats.includes("share")) {
      const sharePath = path.join(outDir, `${ir.meta?.id ?? "academic-visual"}-share.png`);
      if (sharp.module) {
        await sharp.module(tempCapture).resize(1200, 630, { fit: "contain", background: "#FFFFFF" }).png().toFile(sharePath);
        results.share = { status: "generated", path: sharePath };
      } else {
        fs.copyFileSync(tempCapture, sharePath);
        results.share = { status: "generated", path: sharePath, note: "sharp unavailable; exported as a direct screenshot." };
      }
    }
    if (formats.includes("tiff")) {
      if (sharp.module) {
        const tiffPath = path.join(outDir, `${ir.meta?.id ?? "academic-visual"}.tiff`);
        await sharp.module(tempCapture).tiff({ compression: "lzw" }).toFile(tiffPath);
        results.tiff = { status: "generated", path: tiffPath };
      } else {
        results.tiff = { status: "unavailable", reason: `sharp unavailable: ${sharp.error}` };
      }
    }
  }

  if (needsPdf) {
    const pdfPath = path.join(outDir, `${ir.meta?.id ?? "academic-visual"}.pdf`);
    await page.pdf({
      path: pdfPath,
      width: `${number(ir.canvas.width)}px`,
      height: `${number(ir.canvas.height)}px`,
      margin: { top: "0", right: "0", bottom: "0", left: "0" },
      printBackground: true,
      preferCSSPageSize: true,
    });
    results.pdf = { status: "generated", path: pdfPath };
  }

  if (tempCapture && fs.existsSync(tempCapture)) {
    fs.unlinkSync(tempCapture);
  }

  return results;
}

async function exportInteractiveAssets(ir, outDir, formats, scale) {
  const results = {};
  const playwright = loadOptional("playwright");
  const browserExecutable = findBrowserExecutable();
  if (!playwright.module) {
    for (const format of formats) {
      if (["png", "share", "pdf", "tiff", "webm"].includes(format)) {
        results[format] = { status: "unavailable", reason: `playwright unavailable: ${playwright.error}` };
      }
    }
    return results;
  }

  let browser;
  try {
    browser = await playwright.module.chromium.launch({ headless: true });
  } catch (error) {
    if (browserExecutable) {
      try {
        browser = await playwright.module.chromium.launch({ headless: true, executablePath: browserExecutable });
      } catch (fallbackError) {
        const reason = fallbackError instanceof Error ? fallbackError.message : String(fallbackError);
        for (const format of formats) {
          if (["png", "share", "pdf", "tiff", "webm"].includes(format)) {
            results[format] = { status: "unavailable", reason: `browser launch failed: ${reason}` };
          }
        }
        return results;
      }
    } else {
      const reason = error instanceof Error ? error.message : String(error);
      for (const format of formats) {
        if (["png", "share", "pdf", "tiff", "webm"].includes(format)) {
          results[format] = { status: "unavailable", reason: `browser launch failed: ${reason}` };
        }
      }
      return results;
    }
  }

  try {
    const viewportWidth = number(ir.canvas.width) + 320;
    const viewportHeight = number(ir.canvas.height) + 120;
    const page = await browser.newPage({
      viewport: { width: Math.max(960, viewportWidth), height: Math.max(720, viewportHeight) },
      deviceScaleFactor: Math.max(1, scale),
    });
    await page.goto(pathToFileURL(path.join(outDir, `${ir.meta?.id ?? "academic-visual"}.html`)).href, { waitUntil: "load" });
    await page.waitForFunction(() => window.__IR_READY__ === true, null, { timeout: 5000 }).catch(() => {});
    const browserResults = await exportRasterAndPdf(page, ir, outDir, formats);
    Object.assign(results, browserResults);
    if (formats.includes("webm")) {
      results.webm = {
        status: "unavailable",
        reason: "WebM capture is not automated in this bridge; use a browser recording flow if you need video.",
      };
    }
  } finally {
    await browser.close();
  }

  return results;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
    return;
  }
  if (!args.ir) throw new Error("--ir is required.");
  if (!args.out && !args.check) throw new Error("--out is required unless --check is used.");
  if (!Number.isFinite(args.scale) || args.scale <= 0) throw new Error("--scale must be a positive number.");

  const formats = [...new Set(args.formats)];
  const invalid = formats.filter((format) => !VALID_FORMATS.has(format));
  if (invalid.length) throw new Error(`Unknown format(s): ${invalid.join(", ")}`);

  const irPath = path.resolve(args.ir);
  const ir = JSON.parse(fs.readFileSync(irPath, "utf8"));
  const validation = validateIr(ir);
  if (validation.errors.length) {
    for (const message of validation.errors) console.error(`ERROR ${message}`);
    process.exitCode = 2;
    return;
  }
  for (const message of validation.warnings) console.warn(`WARN ${message}`);

  const playwright = loadOptional("playwright");
  const sharp = loadOptional("sharp");
  console.log(`IR valid: ${ir.meta?.id ?? "academic-visual"} (${ir.version})`);
  console.log(`Optional exporters: playwright=${playwright.module ? "available" : "missing"}; browser=${findBrowserExecutable() ? "available" : "missing"}; sharp=${sharp.module ? "available" : "missing"}`);
  if (args.check) return;

  const outDir = path.resolve(args.out);
  fs.mkdirSync(outDir, { recursive: true });
  const svg = buildSvg(ir);
  const html = buildHtml(ir, svg);
  const id = ir.meta?.id ?? "academic-visual";
  const manifest = {
    id,
    revision: ir.meta?.revision ?? null,
    requested: formats,
    generated: {},
    unavailable: {},
    warnings: validation.warnings,
  };

  if (formats.includes("svg")) {
    const svgPath = path.join(outDir, `${id}.svg`);
    fs.writeFileSync(svgPath, svg, "utf8");
    manifest.generated.svg = svgPath;
  }
  if (formats.includes("html")) {
    const htmlPath = path.join(outDir, `${id}.html`);
    fs.writeFileSync(htmlPath, html, "utf8");
    manifest.generated.html = htmlPath;
  }

  const browserFormats = formats.filter((format) => ["png", "share", "pdf", "tiff", "webm"].includes(format));
  if (browserFormats.length) {
    const browserResults = await exportInteractiveAssets(ir, outDir, browserFormats, args.scale);
    for (const [format, info] of Object.entries(browserResults)) {
      if (info.status === "generated") {
        manifest.generated[format] = info.path;
      } else {
        manifest.unavailable[format] = info.reason;
      }
    }
  }

  const manifestPath = path.join(outDir, `${id}.exports.json`);
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + "\n", "utf8");
  console.log(`Export manifest: ${manifestPath}`);

  if (args.strict && Object.keys(manifest.unavailable).length) {
    console.error(`Missing requested exporters: ${Object.keys(manifest.unavailable).join(", ")}`);
    process.exitCode = 3;
  }
}

main().catch((error) => {
  console.error(`ERROR ${error instanceof Error ? error.message : String(error)}`);
  console.error(usage());
  process.exitCode = 1;
});
