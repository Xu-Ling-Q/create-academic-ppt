# Technical Roadmap and Research Route Workflow

Use this workflow for a research technical route, grant or proposal route map,
multi-stage method overview, graphical abstract with an explicit process, or a
paper figure that must explain how a project moves from a scientific question to
validated evidence. The route map is one integrated scientific canvas, not a
decorative flowchart and not a four-panel moodboard.

## Contents

1. Figure contract
2. Evidence and topology
3. Composition system
4. Component vocabulary
5. Scientific scene and image generation
6. Mathematics and editable sources
7. Export and QA
8. Acceptance rubric
9. Contract manifest
10. Provenance

## 1. Figure contract

Record these fields before drawing:

- audience and placement: paper, proposal, defense, review, or public summary;
- one sentence describing the research route and the intended reader takeaway;
- target physical width, maximum height, color mode, and accepted formats;
- research objective, scientific questions, hypotheses, work packages, methods,
  outputs, validation checks, risks, milestones, and final contribution;
- authoritative papers, protocols, code, data, configurations, and citations;
- whether the work is verified, inferred, preliminary, or proposed.

If the placement is unknown, use a single integrated canvas at 180 mm width and
design the height from the content. Keep the final figure height below the
venue limit rather than shrinking the whole route after export. For a proposal
page, use the actual document column width when it is supplied.

Deliver one route map. A PPTX source may contain one slide with that route, but
the route itself must remain one reading surface. A 2x2 style board is a
reference asset only; it is never silently promoted to four scientific panels.

## 2. Evidence and topology

Build an evidence ledger before making visual decisions. Every node, connector,
formula, number, icon, and scientific scene must have a source locator or an
explicit `proposed` status. Keep an exclusion list for retired, disabled,
compatibility-only, and merely plausible mechanisms.

The minimum semantic chain is:

```text
objective -> scientific question -> work package -> method or experiment
          -> output or evidence -> validation -> contribution
```

Extend the chain when the research needs it:

- `data` before a method when provenance or preprocessing affects validity;
- `mechanism` between question and method when a causal or physical explanation
  is central;
- `decision` after validation when a gate determines the next work package;
- `risk-control` beside a work package when a threat has a concrete mitigation;
- `uncertainty` on an output when confidence, error propagation, or sensitivity
  is part of the claim;
- `feedback` from validation or decision back to a prior work package for an
  iterative design, calibration, or active-learning loop.

Choose topology from the evidence, not from a fashionable visual template:

| Research logic | Suitable topology |
| --- | --- |
| staged protocol | horizontal phase bands with milestones |
| several methods answering one question | parallel work-package lanes that merge at evidence |
| multiscale mechanism | nested macro scene, meso process, and micro detail |
| model plus experiment | data and method lanes with an evidence bridge |
| optimization or calibration | closed loop with a visible decision gate |
| alternative hypotheses | explicit branch, separate outcomes, and a merge rule |
| uncertainty propagation | solid forward path plus dotted uncertainty path |

Do not draw a branch, feedback loop, or causal arrow merely to make the figure
look complex. Each nontrivial connector must state whether it carries data,
control, evidence, uncertainty, or a hypothesis. Use line style and a small
legend in addition to color.

For code-grounded diagrams, follow `references/code-grounded-architecture.md`.
For a publication main figure, also follow
`references/publication-main-figure.md`; the route map adds semantic stages but
does not relax final-size, vector, or provenance requirements.

## 3. Composition system

Use a small, repeatable grid with a clear reading order:

1. Put the objective and scientific question in a compact north-star band.
2. Divide the body into two to five phase bands or swimlanes. Name each band
   with a verb-led stage and a milestone, not a generic number.
3. Place work packages in the bands. Keep the primary path left to right or
   top to bottom, and reserve a separate lane for data, mechanism, experiment,
   or validation only when it clarifies responsibility.
4. Put outputs and validation on a visually continuous lower or right-hand
   evidence track. Connect them to the work package that produced them.
5. End with the contribution or decision that the evidence supports. A final
   arrow that simply says `results` is not a contribution.

Use a 3-level hierarchy:

- level 1: objective, phase names, and final contribution;
- level 2: work packages, methods, datasets, experiments, and validation gates;
- level 3: parameters, equations, evidence markers, risks, and local detail.

Use whitespace between stages, not large empty margins around every node. A
route should feel information-rich without becoming a wall of equal boxes. As
a starting heuristic, let the artwork occupy about 45-75 percent of the canvas
area, use no more than four accent colors, and keep one dominant path visibly
stronger than secondary evidence and feedback paths.

Route connectors before placing labels and nodes. Use orthogonal or gently
curved paths, keep arrows behind nodes, bundle parallel edges, and reserve a
dedicated corridor for feedback. No connector may pass through a node, formula,
or milestone label. Crossing is acceptable only when the crossing is
unambiguous, visually separated, and documented; reroute it whenever possible.

## 4. Component vocabulary

Use components with different silhouettes so a reader can scan roles without
depending on color alone:

- phase ribbon: a long, low band with a stage verb and time or milestone;
- objective marker: a restrained target or statement block, not a giant title;
- question or hypothesis node: a compact outlined capsule or diamond;
- work-package island: a grouped region containing method, data, and output;
- data object: a file, sample, cohort, field, or sensor glyph with provenance;
- method object: an editable process shape with a short operation label;
- mechanism inset: a local cross-section, interaction, or multiscale detail;
- experiment or simulation object: a setup scene plus a measurable readout;
- validation gate: a check, benchmark, ablation, calibration, or external test;
- decision gate: a diamond with explicit pass, revise, or branch outcomes;
- uncertainty ribbon: a dotted or translucent route that carries error or risk;
- milestone badge: a date, deliverable, or release condition tied to evidence;
- contribution endpoint: a concise claim with its supported boundary condition.

Group a scene, its local labels, and its evidence marker as one editable or
clearly bounded unit. Avoid nested decorative cards. Use framed regions only
for genuinely distinct work packages, experiments, or insets.

Use an academic palette with a neutral base, one primary path color, one
secondary method color, one evidence/validation color, and one warning color.
Check the route in grayscale and under a common color-vision-deficiency
simulation. Encode status with shape, line style, or labels as well as hue.
Prefer flat fills, subtle outlines, and restrained depth cues. Do not use a
single hue family, gratuitous gradients, glossy UI panels, or 3D effects that
hide the evidence structure.

## 5. Scientific scene and image generation

Use the user-specified compatible image endpoint only when the user explicitly
selects it, and follow `references/custom-image-api.md` plus the installed
`imagegen` skill. When the user selects WisArt, also read
`references/wisart-image-api.md` and use its official OpenAI-compatible base
URL with `gpt-image-2`, `n=1`, and a CLI-compatible concrete size such as
`3840x2160` for a 16:9 4K board. Regardless of provider, generated output is a
raster reference or complex illustration, never an unverified editable
diagram.

Generate in three bounded passes when a route benefits from richer visual
language:

1. **Component board:** request a text-light board of scene silhouettes,
   scientific instruments, mechanism insets, evidence badges, line hierarchy,
   and palette. Ask for multiple component families, not a final 2x2 figure.
2. **Scene atoms:** request individual or small groups of microscope, field,
   apparatus, tissue, molecule, sensor, or simulation scenes. Keep labels and
   formulas out of the raster whenever possible so they can be typeset natively.
3. **Native reconstruction:** use the board only for palette, silhouette,
   depth, and annotation language. Rebuild topology, arrows, labels, formulas,
   stage bands, and evidence markers from the ledger in editable SVG/PPTX.

Use a prompt structure of `scene -> subject -> scientific details -> desired
composition -> constraints`. Require: no watermark, no invented numbers, no
fake citations, no panel letters unless explicitly requested, no full-slide
text, and no arrows that claim a relationship not present in the ledger. Treat
all model output as raster unless the response is verified XML/SVG with real
vector elements. A model name containing `4k`, `svg`, or `ppt` is not proof of
format or editability.

## 6. Mathematics and editable sources

Read `references/math-typesetting.md` whenever formulas, tensor dimensions,
Greek symbols, or probability expressions appear. Keep one canonical `.tex`
source and reuse it for SVG, PPTX, PDF, and the caption. Never leave visible
fake notation such as `x_t`, `R^256`, or `P(r_t=1)` when scripts are intended.

For an editable PPTX, use native Office Math only when the authoring route has
been tested. Otherwise embed a tested vector formula SVG and ship the `.tex`
sidecar. For SVG, preserve text and vector paths, a valid `viewBox`, and the
formula source. Inspect the rendered result at the final physical width; a
correct LaTeX string is not proof of a correct exported formula.

Keep the evidence ledger, roadmap contract, prompt files, and QA report in the
scratch workspace. Do not put API keys, hidden credentials, or internal notes
into a slide, SVG, PDF, ZIP, or prompt artifact.

## 7. Export and QA

Deliver the following unless the venue specifies another set:

- one-page cropped vector PDF for submission;
- editable SVG with native labels and connectors;
- one-slide editable PPTX source when useful or requested;
- PNG preview at the final aspect ratio and an appropriate DPI;
- caption, abbreviation list, evidence ledger, formula sources, and QA report;
- the roadmap contract manifest used by the semantic audit.

Run the semantic audit first:

```bash
python scripts/audit_technical_roadmap.py roadmap-contract.json --strict
```

Then run the existing technical and editability audits:

```bash
python scripts/audit_publication_figure.py figure.svg figure.pdf figure.pptx \
  --target-width-mm 180 --art-kind mixed --strict
python scripts/audit_editability.py figure.pptx
```

For a final PDF, load the installed `PDF` skill and render every page with
Poppler. For a PPTX, load the installed `Presentations` skill, use
`@oai/artifact-tool`, render the slide at full size, and inspect connectors,
wrapping, clipping, and image-only exceptions. For a generated scene, load the
installed `imagegen` skill and inspect MIME type, dimensions, spelling,
watermarks, and scientific plausibility.

### Evidence gate

- every node and edge has a ledger entry and source status;
- every objective reaches a question, work package, method, output, and
  validation;
- each work package has a measurable output and a validation or an explicit
  `proposed`/`not yet available` boundary;
- branches, merges, feedback, uncertainty, and risk controls are either
  evidenced or explicitly waived with a reason;
- no retired or disabled mechanism appears in the route.

### Visual gate

- the primary reading path is obvious in three seconds;
- phase bands, swimlanes, milestones, and decision gates have distinct roles;
- no unexplained connector crossing, node collision, clipping, or orphan label;
- final-size body text is at least 7 pt unless the venue requires larger type;
- the route remains legible in grayscale and with color removed;
- scientific scenes add meaning rather than decorative density;
- the route is one integrated canvas, not four unrelated mini-figures.

### Technical gate

- PDF has one page and a tight crop box at the target width;
- SVG has a valid `viewBox`, native text, no accidental full-slide raster, and
  retained formula sources;
- PPTX has one route slide with editable text, shapes, and connectors;
- raster previews meet the required effective DPI;
- fonts, glyphs, transparency, and line weights survive an independent render.

## 8. Acceptance rubric

Score the route before delivery. A passing route needs at least 85/100 and no
critical failure in the evidence or technical gate:

| Criterion | Points |
| --- | ---: |
| Evidence traceability and scientific correctness | 30 |
| Objective-to-validation closure and topology | 20 |
| Stage, lane, milestone, branch, and feedback clarity | 15 |
| Scientific scene richness without decorative overload | 10 |
| Final-size legibility and visual hierarchy | 15 |
| Vector, font, formula, and editability compliance | 10 |

Do not increase the score by adding boxes. If a route fails, first remove
unsupported claims and reroute the evidence path, then refine component detail.

## 9. Contract manifest

Create a JSON manifest for the audit script. The required top-level fields are
`canvas`, `stages`, `lanes`, `nodes`, and `edges`:

```json
{
  "canvas": {"width_mm": 180, "height_mm": 110, "min_font_pt": 7},
  "stages": [{"id": "s1", "label": "Prepare", "order": 1}],
  "lanes": [{"id": "method", "label": "Method"}],
  "nodes": [
    {"id": "goal", "kind": "goal", "stage": "s1", "lane": "method",
     "label": "Research objective", "source": "paper:sec.1",
     "bbox": [5, 5, 35, 14], "font_pt": 10}
  ],
  "edges": [
    {"source": "goal", "target": "question", "kind": "flow",
     "points": [[40, 12], [55, 12]]}
  ],
  "waivers": []
}
```

Allowed node kinds are `goal`, `question`, `hypothesis`, `work-package`,
`data`, `method`, `experiment`, `mechanism`, `decision`, `output`,
`validation`, `risk-control`, `milestone`, `contribution`, `uncertainty`,
`scene`, and `annotation`. Allowed edge kinds are `flow`, `dependency`,
`evidence`, `validation`, `feedback`, `uncertainty`, and `decision`.

Use `waivers` only for a real absence in the research plan. Each waiver must
name a rule such as `feedback_loop`, `branch`, `risk_control`, or `merge` and
include a non-empty reason. Coordinates are in millimetres. Set
`allow_overlap: true` only for an intentional inset or scene overlay.

## 10. Provenance

This workflow incorporates general visual principles from the user-supplied
references on technical-route figures and academic diagram construction:

- https://blog.csdn.net/qazplm12_3/article/details/145818705
- https://zhuanlan.zhihu.com/p/693834430

Those references inform component richness, stage organization, annotation,
color discipline, and review practice. They do not supply scientific claims,
topology, data, or venue rules. The research evidence remains authoritative.
