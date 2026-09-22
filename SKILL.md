---
name: create-academic-ppt
description: Create evidence-grounded academic PowerPoint decks, publication-ready paper figures, and integrated technical-roadmap or graphical-abstract canvases from papers, research notes, datasets, source code, figures, or style references. Use for research meetings, thesis defenses, conference talks, literature reviews, grant or NSFC research routes, code-grounded model architecture diagrams, journal or conference main figures, single-canvas method figures, editable PPTX or SVG sources, submission exports in PDF, SVG, EPS, TIFF, or PNG, verified mathematical typesetting, and GPT-image-2/WisArt visual references that must be reconstructed into provenance-tracked, semantically editable SVG/PPTX artifacts.
---

# Create Academic PPT, Paper Figures, and Research Roadmaps

Build an academic presentation, a publication-ready paper figure, or an
integrated technical roadmap from traceable evidence. Route the request before
applying layout, typography, or delivery defaults.

## Load the required workflow

- For a deck or any editable PPTX source, load and follow the installed `Presentations` skill. Use `@oai/artifact-tool` from JavaScript ES modules; do not use `python-pptx`.
- For a final publication PDF, load and follow the installed `PDF` skill to render and inspect the exported file.
- For generated raster references or scientific illustrations, load and follow the installed `imagegen` skill.

Load these bundled references only when their route begins:

- Read [references/academic-deck-playbook.md](references/academic-deck-playbook.md) for presentation mode.
- Read [references/publication-main-figure.md](references/publication-main-figure.md) for a paper main figure, journal figure, method figure, or submission asset.
- Read [references/style-selection-and-qa.md](references/style-selection-and-qa.md) before style exploration or final visual QA.
- Read [references/code-grounded-architecture.md](references/code-grounded-architecture.md) before drawing an architecture from code.
- Read [references/technical-roadmap.md](references/technical-roadmap.md) for a research technical route, grant roadmap, multi-stage method overview, or process-driven graphical abstract.
- Read [references/math-typesetting.md](references/math-typesetting.md) whenever equations, tensor notation, subscripts, superscripts, Greek symbols, matrices, or probability expressions appear.
- Read [references/custom-image-api.md](references/custom-image-api.md) before using a user-specified image endpoint, model, or credential.
- Read [references/wisart-image-api.md](references/wisart-image-api.md) when the user selects the official WisArt API.
- Read [references/raster-to-editable.md](references/raster-to-editable.md) whenever GPT-image-2 or another raster image is used as a visual source for an editable SVG/PPTX deliverable.
- Read [references/interactive-html-and-export.md](references/interactive-html-and-export.md) when the user requests an HTML interface, interactive preview, shareable figure, or multi-format export bundle.

## Route the output mode first

Choose exactly one primary mode. Use the first matching route:

1. **Presentation** for a multi-slide narrative, defense, talk, or meeting.
2. **Technical-roadmap** for a single research route that must show objective,
   scientific questions, work packages, methods, outputs, validation, stages,
   milestones, risks, branches, or feedback loops.
3. **Publication-figure** for one paper figure focused on a method, model,
   mechanism, or result; it may be a single integrated path or a true composite.
4. **Graphical-abstract** for a compact paper or public-facing summary. Use the
   technical-roadmap contract when it depicts a process and the publication
   contract when it depicts one mechanism without a research-program route.

### Presentation mode

Use this mode for a group meeting, defense, proposal, lecture, conference talk, or multi-slide narrative.

Defaults when the user omits them:

- Use 12 slides for a research-group presentation, adapting to evidence and duration.
- Use 16:9 widescreen.
- Use the user's primary language while preserving exact scientific notation and established terms.
- Deliver a distinct editable `.pptx`.

### Technical-roadmap mode

Use this mode for a technical route, research roadmap, proposal method map,
multi-stage study design, or process-driven graphical abstract. It is a single
integrated canvas, even when the source is delivered as a one-slide PPTX.

Defaults when the user omits them:

- Read `references/technical-roadmap.md` and create an evidence-led contract
  manifest before drawing.
- Make the semantic chain visible: objective -> question -> work package ->
  method/experiment -> output/evidence -> validation -> contribution.
- Use two to five phase bands or swimlanes, a dominant reading path, explicit
  milestones, and decision gates where the research actually branches.
- Add mechanism, data, experiment, uncertainty, risk-control, or local scene
  insets only when they carry evidence. Do not fill the canvas with equal
  decorative boxes.
- Show branches, merges, and feedback as named relationships. If the study is
  intentionally linear, record a waiver in the roadmap contract rather than
  fabricating complexity.
- Use generated images only for scene atoms, component vocabulary, or depth
  cues. Rebuild topology, labels, arrows, formulas, and stage bands as editable
  SVG/PPTX objects.
- Deliver one cropped vector PDF, editable SVG, PNG preview, and one-slide
  editable PPTX when useful or requested, plus the contract manifest and QA
  report. Do not deliver a four-panel board as the route itself.

### Publication-figure mode

Use this mode for `Figure 1`, a paper main figure, journal submission figure, method overview, model architecture figure, or a request for one publishable image.

Defaults when the venue is unknown:

- Create one semantically integrated figure, not a slide and not a decorative 2x2 board.
- Use a double-column width of 180 mm unless the content clearly fits a single column.
- Keep the caption, slide title, provenance footer, page number, and production notes outside the artwork.
- Deliver a cropped vector PDF as the primary submission asset, an editable SVG as the vector source, and a PNG preview.
- Deliver an editable one-page PPTX source only when requested or useful; PPTX is not the default submission format.
- Produce EPS or TIFF only when the venue requires it.

One PPT slide is not automatically one integrated paper figure. A slide containing `(a)` through `(d)` remains a composite multi-panel figure.

Do not apply presentation font-size, title, margin, or 16:9 defaults to a publication figure. Do not apply publication-scale typography to a presentation deck.

## Add the interactive delivery layer when requested

Treat interactive HTML as an optional delivery layer across all four primary
modes, not as a replacement for the evidence-led route. Use one shared
academic visual IR as the canonical scene description:

1. Keep the evidence ledger, route contract, formulas, and scientific
   terminology authoritative.
2. Project the verified scene into the IR's typed nodes, edges, groups, steps,
   and provenance fields. Nodes keep a `source` provenance, and scientific
   edges keep a separate `provenance` field plus an explicit status such as
   `inferred`, `proposed`, or `not-yet-available`.
3. Render the same IR to self-contained HTML and vector SVG. Add search,
   pan/zoom, theme switching, step/path focus, node inspection, and a print
   view only when they help the audience inspect the evidence.
4. Use the HTML/SVG surface for exploration and sharing. Use the existing
   presentation or publication pipelines for editable PPTX and audited
   submission PDF/SVG; do not rasterize the only editable master.
5. Export PNG, PDF, TIFF, share cards, and optional WebM through the browser
   bridge when the required local runtime is available. Record missing optional
   exporters in the QA report instead of silently omitting requested formats.
6. Keep export names and metadata tied to the same IR id and revision so that
   HTML, SVG, PPTX, and publication assets can be compared and regenerated.

## Ground all outputs in evidence

1. Inventory every paper, note, dataset, code path, configuration, figure, and citation supplied by the user.
2. Build a claim-to-source ledger before outlining a deck or drawing a figure.
3. Separate verified evidence, inference, preliminary results, and proposed work.
4. Resolve source conflicts or surface them explicitly. Never invent results, dimensions, modules, connections, citations, institutions, or conclusions.
5. Preserve units, denominators, uncertainty, sample sizes, reference conditions, tensor dimensions, and variable semantics.
6. Keep working ledgers, prompts, and QA notes in the scratch workspace, not in visible slide or figure copy.

When source code is the evidence, trace the authoritative constructor, executed forward path, trainer, evaluator, and active configuration. Treat model names and old design documents as hypotheses, not architecture facts.

## Select a visual source

Apply the first matching route and do not mix unrelated systems:

1. A user-provided deck or figure template is the sole layout and style source.
2. Explicit visual direction or reference images define the visual grammar.
3. Create a concept board only when the user requests alternatives or selection is materially useful.
4. Otherwise infer a restrained academic treatment and continue.

For publication figures and technical roadmaps, a generated board may define component vocabulary, scientific-scene treatment, palette, line hierarchy, and depth. Its panel grid is not the final scientific topology. Never turn a 2x2 moodboard into four subfigures or route quadrants unless the evidence genuinely requires them.

## Author presentation mode

1. Build the evidence-led narrative described in the academic deck playbook.
2. Implement the deck through the `Presentations` skill.
3. Keep titles, body copy, citations, tables, charts, annotations, and simple diagrams editable.
4. Use raster imagery only where the source is inherently raster or native reconstruction would reduce scientific fidelity.
5. Preserve the input deck and export a new deliverable unless the user explicitly requests in-place editing.
6. Render every slide at full size, fix all unintended overlap and clipping, run the presentation overflow check, and run `scripts/audit_editability.py`.

## Author publication-figure mode

1. Establish the target venue, figure claim, caption role, final column width, maximum height, color mode, and accepted formats. Venue rules override defaults.
2. Choose a single integrated architecture for one end-to-end mechanism. Use a composite figure only when independent evidence types need different visual grammars.
3. Design at final physical size. Do not rely on later downscaling to repair oversized text or strokes.
4. Use one continuous reading path, compact labels, restrained color, redundant encodings, and minimal arrow crossings.
5. Keep formula source canonical and use the math-typesetting workflow. Setting `Cambria Math` on plain text does not create a mathematical equation. Label each formula as native Office Math, source-editable vector math with a `.tex` sidecar, or appearance-only; never claim that an embedded SVG is a native PowerPoint equation.
6. Prefer one shared scene or data model when emitting SVG, PPTX, and PDF so labels, coordinates, and dimensions cannot drift.
7. Keep the primary figure vector. Retain raster only for photographs, microscopy, original raster evidence, or a complex generated illustration that cannot be reconstructed faithfully.
8. Export the required source and submission assets, a caption text file, the evidence ledger, and a short QA report.

## Author technical-roadmap mode

1. Establish the audience, placement width, one route claim, scientific
   objective, question set, work packages, methods, outputs, validations,
   milestones, risks, and final contribution.
2. Build both an evidence ledger and the JSON contract described in
   `references/technical-roadmap.md`. Give every node and edge a source locator
   or explicit proposed status.
3. Select a topology from the research logic: staged, parallel-convergent,
   multiscale, experiment-method bridge, decision branch, or iterative loop.
   Do not choose topology from a generated style board.
4. Design at the final placement width. Use phase bands, swimlanes, distinct
   component silhouettes, connector corridors, milestones, decision gates, and
   embedded scientific scenes to produce a rich but readable single canvas.
5. Keep the dominant path continuous and route secondary evidence,
   uncertainty, and feedback with redundant line styles. Avoid node collisions,
   unexplained crossings, and decorative card grids.
6. Use one shared scene or data model for SVG, PPTX, PDF, and PNG. Keep text,
   equations, arrows, stage bands, and simple components native and editable.
7. Run `scripts/audit_technical_roadmap.py <contract.json> --strict`, then run
   the publication-figure and PPTX editability audits. Render the SVG, PDF, and
   PPTX independently at the final physical size.
8. Apply the acceptance rubric in the technical-roadmap reference. Do not
   approve a route below 85/100 or with an unresolved evidence, formula,
   clipping, connector, font, or vector failure.

## Use image generation within its boundary

When the user supplies a compatible endpoint or model, use the bundled `imagegen` CLI route described in the custom-image reference. Keep credentials process-local and inspect the returned MIME type, dimensions, and content.

When the user selects WisArt, use its documented OpenAI-compatible base URL
`https://wisart.kuaileshifu.com/v1` through
`scripts/run_wisart_image.ps1`, not the raw imagegen CLI. The launcher resolves
`WISART_API_KEY` from Process, User, or Machine scope at execution time and
temporarily sets the pinned OpenAI-compatible variables in the launcher and its
imagegen child, restoring prior values before exit. This works when an existing
Codex desktop process did not inherit a newly added user environment variable.
The launcher also resolves an optional `WISART_PYTHON` (then `PYTHON`) setting
from Process, User, or Machine scope so the selected interpreter can carry the
`openai` SDK across Codex sessions.
Keep `n=1` by default and never exceed WisArt's official limit of 5. Use a
CLI-compatible concrete size such as `3840x2160` for a fixed 16:9 4K board; do
not pass ratio strings or use browser cookies, browser automation, or
intercepted private endpoints. On Windows, use the bundled launcher through
PowerShell 7 or Windows PowerShell 5.1; it captures GNU-style arguments before
PowerShell's common parameter binder can reinterpret `--out`. Treat 503 as
maintenance and never resubmit automatically after an ambiguous timeout.

Treat generated output as raster unless it is valid SVG/XML with vector elements. A model alias containing `4k`, `svg`, or `ppt` does not guarantee that format or resolution.

Use generated raster output for style exploration, component design, scientific scene atoms, or a complex illustration. Do not use a full-slide or full-figure raster render as the editable final surface. For a roadmap, generate a component board and isolated scene vocabulary rather than asking the image model to invent the final topology. When the user asks to "generate with GPT-image-2 and convert to editable," follow the explicit raster-to-editable reconstruction contract in `references/raster-to-editable.md`; do not describe OCR, auto-tracing, or a renamed PNG as semantic editability.

## Convert GPT-image-2 references into editable artifacts

Treat GPT-image-2/WisArt output as a visual hypothesis, never as the authoritative
scientific source. The normal route is evidence-first, but when the user wants a
visual-first workflow, allow a provisional GPT-image-2 draft before inspecting
the code. In that route, the first image is explicitly marked
`provisional-visual-only`, contains no trusted claims, and is later reconciled
against the authoritative constructor, forward path, data, formulas, and
terminology. Use the generated image to extract palette, silhouettes, depth
cues, texture, and component vocabulary; independently rebuild topology,
labels, equations, charts, arrows, and connectors as native SVG/PPTX objects.
Permit one or more masked/local image-edit passes for appearance refinement, but
never use an edited raster as the semantic master. Mark every object or retained
raster region with its provenance and editability class (`semantic`,
`geometric`, or `raster-retained`). Read `references/raster-to-editable.md` for
the evidence-first and visual-first routes, their refinement loop, the minimum
IR fields, and the final QA gate.

## Verify publication figures and roadmaps

Run all three passes from the publication reference:

1. **Evidence QA:** trace every block, arrow, label, number, and formula to its source.
2. **Visual QA:** inspect at final physical size, at 100%, in grayscale, and after an independent render.
3. **Technical QA:** verify crop box, page count, dimensions, fonts, vectors, raster DPI, transparency, and missing glyphs.

Run:

```bash
python scripts/audit_publication_figure.py <figure-files...> --target-width-mm <width> --art-kind mixed
```

Also run `scripts/audit_editability.py` for every PPTX source. Investigate every warning; use `--strict` for the final technical gate. Re-render after each fix.

For a technical roadmap, also run:

```bash
python scripts/audit_technical_roadmap.py <roadmap-contract.json> --strict
```

Confirm objective-to-validation reachability, branch and merge semantics,
feedback or an explicit waiver, risk controls, milestone coverage, connector
crossings, node-edge collisions, stage backtracking, final-size typography, and
the one-canvas contract.

When the interactive delivery layer is enabled, also run:

```bash
node scripts/render_interactive_html.mjs --ir <visual-ir.json> --out <out-dir> --check
```

Then render the HTML at desktop and mobile widths, exercise search, focus,
zoom, reset, theme, and print controls, and independently inspect SVG/PDF/PNG
exports. The HTML preview is not a substitute for final-size publication QA.

## Deliver the correct artifact set

For a deck, deliver the verified `.pptx` and summarize evidence limitations and intentional non-editable elements.

For a paper figure, deliver:

- cropped one-page vector PDF for submission;
- editable SVG source;
- editable PPTX source when requested or useful;
- PNG preview at final aspect ratio;
- venue-required EPS or TIFF when applicable;
- caption, abbreviation list, evidence ledger, formula source, and QA report.

For a technical roadmap, deliver the same publication asset set plus the JSON
roadmap contract. Keep it as one integrated figure; a one-slide PPTX is an
authoring source, not four separate figures.

When requested, also deliver:

- self-contained interactive HTML companion;
- shared visual IR JSON;
- vector SVG exported from the same IR;
- PNG, PDF, TIFF, share card, or WebM exports that were actually generated;
- an export manifest listing successful and unavailable formats.

Do not claim that PPTX, SVG, PDF, EPS, TIFF, or raster output is publication-ready until the corresponding final artifact has been rendered and inspected.

## Reusable resources

- `references/academic-deck-playbook.md`: presentation evidence mapping and narrative design.
- `references/publication-main-figure.md`: integrated figure structure, final-size design, formats, and submission QA.
- `references/style-selection-and-qa.md`: visual-system selection and editable translation.
- `references/code-grounded-architecture.md`: implementation authority, execution tracing, inclusion, and exclusion.
- `references/technical-roadmap.md`: route topology, scientific component language, image-generation boundary, contract manifest, and acceptance rubric.
- `references/math-typesetting.md`: correct formula routing for PPTX, SVG, and PDF.
- `references/custom-image-api.md`: secure use of compatible image endpoints and raster-to-editable boundaries.
- `references/wisart-image-api.md`: official WisArt OpenAI-compatible endpoints, field mapping, CLI constraints, and credential handling.
- `references/raster-to-editable.md`: GPT-image-2/WisArt raster analysis, scene-IR reconstruction, editability classes, retained-raster disclosures, and QA.
- `scripts/audit_editability.py`: PPTX structure and editability audit.
- `scripts/audit_publication_figure.py`: SVG, PDF, PPTX, and raster publication-asset audit.
- `scripts/audit_technical_roadmap.py`: semantic closure, route topology, geometry, crossing, and typography audit for roadmap manifests.
- `scripts/render_math_svg.py`: vector math rendering with retained LaTeX source.
- `scripts/run_wisart_image.ps1`: resolves Windows-scoped WisArt credentials and launches the official OpenAI-compatible route without exposing the key.
- `references/interactive-html-and-export.md`: Archify-inspired shared IR, HTML interaction, and multi-format export contract.
- `scripts/render_interactive_html.mjs`: self-contained HTML/SVG renderer with optional Playwright and sharp exports.
