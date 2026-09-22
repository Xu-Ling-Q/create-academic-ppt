# Interactive HTML and Multi-Format Export

Use this layer when an academic deck, paper figure, technical roadmap, or
graphical abstract also needs an inspectable web view or a format bundle.
The layer is inspired by the strengths of Archify-style workflows: a typed
intermediate representation, deterministic layout/rendering, self-contained
HTML, and export from one scene description. It is an optional delivery layer
inside `create-academic-ppt`, not a second evidence workflow.

## Shared visual IR

Keep the canonical scene in JSON. Coordinates are CSS/SVG pixels in the
declared canvas. Do not put unverified claims into labels merely because the
HTML surface makes them easy to edit.

```json
{
  "version": "academic-visual-ir/1",
  "meta": {
    "id": "example-method",
    "title": "Verified method overview",
    "kind": "publication-figure",
    "language": "en",
    "revision": "2026-08-29",
    "status": "verified"
  },
  "canvas": {
    "width": 1600,
    "height": 900,
    "background": "#F7F9FC"
  },
  "groups": [],
  "nodes": [
    {
      "id": "input",
      "label": "Input sequence",
      "kind": "data",
      "x": 80,
      "y": 390,
      "w": 220,
      "h": 100,
      "source": "paper:sec.3",
      "status": "verified",
      "tags": ["input"]
    }
  ],
  "edges": [],
  "steps": []
}
```

Required top-level fields are `version`, `meta`, `canvas`, `nodes`, and
`edges`. `groups` and `steps` are optional. A node requires `id`, `label`,
`x`, `y`, `w`, and `h`. An edge requires `source` and `target`. Use
`source` on nodes, and `provenance` on scientific edges; use
`status: "proposed"` only for explicitly proposed content.

Useful optional node fields:

- `subtitle`, `kind`, `shape`, `fill`, `stroke`, `textColor`;
- `source`, `status`, `tags`, `detail`, `href`, `provenance`;
- `focus` for an initial inspection target, or place `focusNode` in `meta`.

Useful optional edge fields:

- `id`, `label`, `kind`, `points`, `color`, `width`, `dash`;
- `provenance`, `status`, and `directed` when an edge is scientific evidence.

## Interaction contract

The self-contained HTML renderer should provide only interactions that aid
inspection:

- fit-to-view, reset, pan, and wheel zoom;
- search labels, tags, and provenance ids;
- click a node to focus its local neighborhood;
- optional step/path selection from the IR;
- light/dark theme switch;
- print/export controls that invoke browser-native behavior;
- an accessible side panel with the selected node's source and status.

Do not use animation to imply causality that the evidence does not establish.
Do not hide required labels behind hover-only states. Keep the SVG readable
when JavaScript is disabled.

## Export matrix

The bridge script has a dependency-light core:

| Format | Renderer | Editability | Use |
|---|---|---:|---|
| HTML | inline SVG + CSS + JS | scene source editable | interactive review/share |
| SVG | same SVG scene | text/vector editable | vector source |
| PNG | Playwright screenshot with bundled or system Chrome/Edge | raster | preview/share |
| PDF | Playwright print with bundled or system Chrome/Edge | vector-ish browser PDF | review/handout |
| TIFF | sharp from PNG | raster | venue-specific fallback |
| WebM | optional browser capture | video | narrated or animated preview |
| PPTX | Presentations skill and `@oai/artifact-tool` | editable objects | talks/editable source |
| EPS | publication conversion route | vector | only when venue requires |

HTML, SVG, and PPTX are not interchangeable. The IR keeps their content in
sync, but each output has different editability and typography behavior.
Always run the publication and presentation audits on the output that will be
submitted or presented.

## Command

From the installed skill directory:

```bash
node scripts/render_interactive_html.mjs --ir work/visual-ir.json --out outputs/visual-ir --formats html,svg,png,pdf,tiff,share
```

Use `--check` to validate the IR and report which optional exporters are
available without writing output. The renderer never needs a network request.
PNG/PDF/share/TIFF use local `playwright`, with bundled or system Chrome/Edge
as the browser target, plus `sharp` when available. If a requested optional
exporter is unavailable, the command writes an export manifest with the reason
and exits non-zero only when `--strict` is supplied.

## QA additions

Record:

- IR id and revision;
- source/status coverage for nodes and edges;
- exact export command and runtime versions;
- generated formats and unavailable optional formats;
- browser viewport and scale used for raster/PDF output;
- whether the HTML was checked with JavaScript disabled and at mobile width.

The bridge is a renderer, not a scientific validator. Evidence QA, formula
QA, final-size typography QA, vector QA, and PPTX editability QA remain
mandatory from the primary `create-academic-ppt` route.
