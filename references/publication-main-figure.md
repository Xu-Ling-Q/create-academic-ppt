# Publication Main Figure Workflow

Use this workflow for a paper main figure, `Figure 1`, journal method figure, model overview, or any requested single publication image. Venue author instructions override every default below.

## Establish the figure contract

Record before drawing:

- target venue and accepted file formats;
- the one claim the figure must communicate;
- figure number and caption role;
- final width: single, intermediate, or double column;
- maximum height and color-mode restrictions;
- editable source, vector submission, raster preview, and caption deliverables;
- authoritative papers, code, data, configurations, and existing visuals.

If the venue is unknown, use 180 mm double-column width, RGB, vector PDF, editable SVG, and PNG preview. State that these are defaults, not venue-specific compliance.

## Choose one integrated figure or a true composite

Use a **single integrated figure** when one end-to-end mechanism, architecture, or information flow is the contribution. Arrange the primary path left to right and embed a compact exploded detail only where it clarifies a mechanism.

Use a **composite multi-panel figure** only when architecture, experimental evidence, qualitative examples, or results require genuinely different visual grammars. Give every panel one scientific job and order panels in reading sequence.

Do not confuse these cases:

- one PPT slide can still contain four separate subfigures;
- a 2x2 image-generation board is a visual reference, not a scientific panel plan;
- stages in a model pipeline do not automatically become `(a)`, `(b)`, `(c)`, and `(d)`;
- a paper caption belongs outside the artwork unless the venue explicitly requires otherwise.

For a single architecture figure, remove slide titles, page headers, footers, page numbers, presentation legends, production notes, and decorative section separators.

## Build an evidence ledger

For each block, arrow, label, formula, number, and visual encoding, record:

| Element | Meaning | Authoritative source | Status |
|---|---|---|---|
| Block | Executed component or reported construct | code symbol or paper section | verified/inferred |
| Arrow | Data, control, or causal relationship | call path or method text | direct/inferred |
| Number | Parameter, result, or dimension | config, table, log, or data | verified/digitized |
| Formula | Transformation or objective | source equation or implementation | exact/adapted |

Never invent a module, dependency, tensor dimension, causal claim, metric, or formula. Keep an explicit exclusion list for retired, proposed, disabled, and compatibility-only mechanisms.

## Design at final physical size

Use venue dimensions when known. Otherwise:

| Layout | Width |
|---|---:|
| Single column | 85-90 mm |
| Intermediate | 120-140 mm |
| Double column | 175-185 mm |

At final size:

- body labels: 7-9 pt, never below the venue minimum;
- panel labels: 9-11 pt;
- main strokes: 0.6-1.0 pt;
- internal grids and secondary edges: 0.35-0.6 pt;
- one sans-serif label family plus a tested math family;
- compact margins and a crop box tight to the artwork.

Create directly at the final aspect ratio. Check the smallest label after scaling to final millimeters; a readable 16:9 slide preview is not evidence of readable publication typography.

## Apply a publication visual system

- Use restrained, colorblind-safe colors and redundant encodings such as shape or line style.
- Ensure the figure remains understandable in grayscale.
- Use alignment, proximity, and whitespace to express hierarchy.
- Keep arrows directional, route them behind nodes, and minimize crossings.
- Use manuscript terminology exactly and define each abbreviation once.
- Keep legends adjacent to the evidence they decode.
- Avoid gradients, shadows, 3D effects, decorative UI cards, and unsupported emphasis.
- Use generated imagery for component language or inherently raster scientific content, not for the final figure topology.

## Typeset mathematics correctly

Read `references/math-typesetting.md`. Do not display literal `_` or `^` as substitutes for subscripts and superscripts. Do not assume that changing a textbox to `Cambria Math` creates an equation.

## Export the artifact set

- **Primary submission:** cropped, one-page vector PDF with embedded fonts or verified outlined glyphs.
- **Editable vector source:** SVG with a valid `viewBox`, no unexpected raster `<image>`, and retained formula source.
- **Editable author source:** one-page PPTX when useful; do not treat it as the submission master unless the venue requests PPTX.
- **Preview:** PNG at 2x or at the venue-specified DPI.
- **Raster submission:** TIFF only when required; use lossless compression.
- **Legacy vector:** EPS only when required and after independent rendering.

Avoid JPEG for diagrams, plots, and text. Do not rasterize the whole figure merely to simplify export.

## Run final QA

### Evidence QA

- Trace every object and formula to the ledger.
- Recompute plotted values where possible.
- Verify terminology, units, dimensions, conditions, and reading order against the manuscript.

### Visual QA

- Render and inspect at actual publication size and at 100%.
- Check smallest text, line contrast, arrow direction, whitespace, clipping, and legend ambiguity.
- Inspect a grayscale render and a common color-vision-deficiency simulation.
- Confirm that the caption explains the same reading order as the artwork.

### Technical QA

- Verify page count, physical dimensions, crop box, font embedding, transparency, and missing glyphs.
- Zoom into the PDF to confirm that text and line art remain vector.
- Verify raster pixel dimensions and effective DPI at final width.
- Reopen PDF, SVG, PPTX, and raster deliverables in independent viewers.
- Run `scripts/audit_publication_figure.py` with the intended final width and run `scripts/audit_editability.py` for PPTX.

Acceptance requires factual traceability, final-size legibility, technical compliance, editability, reproducibility, and a figure that can be understood without relying on presentation chrome.
