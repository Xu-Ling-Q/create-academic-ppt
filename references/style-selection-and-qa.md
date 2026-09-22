# Academic Style Selection and QA

Use this reference to turn a visual preference into a consistent academic deck, paper figure, or technical roadmap. Keep style subordinate to evidence and readability.

## Separate visual grammar from scientific structure

In presentation mode, a concept board may explore complete slide systems. In publication-figure mode, it may explore component vocabulary, palette, line hierarchy, annotation style, and depth only. In technical-roadmap mode, it may additionally explore phase ribbons, swimlane headers, milestone and decision-gate silhouettes, scientific scene atoms, evidence badges, uncertainty paths, and feedback treatment.

Do not transfer a concept board's 2x2 grid, panel count, title band, footer, or slide aspect ratio into a paper figure unless the evidence independently requires that structure. A request for one model architecture defaults to one continuous scientific reading path, even when the style reference contains several panels.

Read `references/publication-main-figure.md` before translating a style into a submission figure. Read `references/technical-roadmap.md` before translating a style into a research route.

## Choose one visual route

Apply the first matching route and do not mix visual systems:

1. Use a user-provided PPTX or template skill as the sole style source. Preserve its typography, palette, grid, spacing, placeholders, footer treatment, and page markers through the template workflow in the `Presentations` skill.
2. Follow explicit visual direction or reference images from scratch. Extract the visual grammar; do not copy scientific claims or unrelated branding from a reference image.
3. Create four style concepts only when the user asks to compare styles, requests the three-stage workflow, or says they want to choose before authoring.
4. When no direction or comparison request exists, use the default composition route required by the `Presentations` skill and continue without a style-selection pause.

Treat a style choice as material only when it changes palette, typography, composition, image treatment, or the implied tone. Do not pause to ask about minor decoration. If the user delegates the choice or requests one-shot delivery, select the strongest fit and state the assumption in the handoff.

## Build a useful four-concept board

Generate a single moodboard containing a 2x2 grid of four 16:9 miniature slide systems. Keep the concepts academically credible and genuinely distinct.

Vary all of these dimensions across the four concepts:

- palette and contrast;
- type personality and title scale;
- grid, margins, and dominant composition;
- information density and whitespace;
- chart and table treatment;
- treatment of photography, microscopy, paper figures, or scientific illustration;
- rules for dividers, citations, annotations, and highlights.

Avoid four superficial recolors of the same layout. Give each concept a short neutral label and a clear best-fit use case, such as quantitative results, clinical research, methods-heavy engineering, or conceptual review. Use generic sample content and minimal text; do not invent findings for the user's project. Keep any generated text nonessential because raster image models can misspell labels.

Present the board with a compact comparison of palette, typography, composition, visual vocabulary, and tradeoff. Ask the user to choose one concept only when selection is required. Once selected, stop generating additional alternatives and convert that concept into a design system.

If image generation is unavailable, provide four concise written style specifications and continue with the same selection rule.

For a technical roadmap, do not ask the model for four finished route maps.
Generate a component-language board with text-light phase bands, scientific
scene atoms, method and evidence components, connector styles, and depth cues.
Extract those tokens, then build the one-canvas topology from the evidence
ledger and roadmap contract. A board quadrant is not a route stage.

## Convert the choice into design tokens

Record the selected concept as a small implementation specification in the presentation scratch workspace:

- slide size and safe margins;
- background, primary text, secondary text, accent, and data-series colors;
- Latin and CJK font families with fallbacks;
- deck-title, slide-title, subheading, body, caption, and citation sizes;
- spacing rhythm, corner treatment, line weights, and image crop rules;
- chart axes, gridlines, labels, uncertainty, and highlight conventions;
- citation and page-number placement.

For a technical roadmap, also record:

- final physical width, maximum height, and minimum figure font size;
- phase-band, swimlane, work-package, decision-gate, milestone, output, and
  validation component silhouettes;
- primary flow, evidence, uncertainty, feedback, and proposed-link line styles;
- connector corridors, branch and merge spacing, and inset depth treatment;
- scene-atom crop, masking, native-label overlay, and grayscale rules;
- maximum node and connector density before detail moves to an inset or appendix.

Follow the minimum font sizes and equal-margin guidance in the `Presentations` skill. Shorten wording or change layout before shrinking type. Keep a single-line title on one line.

Define a small layout family rather than repeating one silhouette:

- minimal cover;
- section or thesis statement;
- text plus evidence figure;
- full-width chart or table;
- study design or methods flow;
- comparison or synthesis;
- mechanism or conceptual model;
- conclusion and discussion prompt.

For technical-roadmap mode, use one integrated route layout rather than this
slide family. Vary hierarchy inside the route with phase bands, lanes, local
scene insets, output tracks, milestones, and validation gates.

Use only the layouts the story needs.

## Preserve editability

- Rebuild titles, body copy, citations, captions, legends, annotations, tables, charts, and simple diagrams as native editable objects.
- Never use a full-slide concept render or screenshot as the finished slide surface.
- Keep photos, microscopy, original paper figures, and complex generated scientific illustrations as images only when reconstruction would reduce fidelity or scientific meaning.
- Place editable labels and citations over or beside a retained image instead of baking new explanatory text into it.
- Use native PowerPoint shapes only for simple diagrams that materially improve understanding. Follow the connector-ordering and diagram-routing rules in the `Presentations` skill.
- Use a native chart only when verified values exist. Match labels, units, denominators, uncertainty, and reference groups to the source.
- Avoid rasterized tables and charts when source values can be represented faithfully as editable objects.
- Use grouped editable scripts for simple mathematical labels and vector formula SVG with retained LaTeX source for complex equations. A math typeface on plain ASCII text is not mathematical typesetting.

Treat editability as a functional requirement, not a visual approximation. Preserve source files and make the exported PPTX the authoritative editable deliverable.

## Handle academic typography and visuals

- Choose fonts with dependable Chinese and Latin glyph coverage. Avoid mixing fonts that disagree strongly in x-height or stroke weight.
- Use one primary presentation language. Add the second language only where the audience benefits; avoid automatic line-by-line duplication.
- Keep equations, gene and protein symbols, variable names, and official scale names exact.
- Use color to encode a stable meaning across slides. Never rely on color alone for experimental groups or causal status.
- Keep citations readable but visually secondary. Use one consistent locator format.
- Prefer a single strong evidence visual over decorative image collections.
- Use a mechanism diagram only when it clarifies a causal or conceptual relationship that prose cannot convey as quickly.
- Do not reuse the same non-background image on multiple slides unless the repeated reference is analytically necessary.

## Run visual and structural QA

Inspect the final deck in this order:

1. Read only the headlines and confirm that they form a coherent argument.
2. Render every slide and inspect each one individually at full size.
3. Check one-line titles, CJK and Latin wrapping, punctuation, equations, citations, axis labels, legends, units, and page markers.
4. Resolve every unintended overlap, clipping, overflow, broken connector, placeholder, and low-contrast element.
5. Compare every chart and table against the verified source values.
6. Inspect a montage for rhythm, layout variety, palette consistency, and abrupt density changes.
7. Run the overflow test required by the `Presentations` skill.
8. Run `<this-skill-directory>/scripts/audit_editability.py <final.pptx>` and investigate every flagged image-only slide. Allow an intentional exception only with `--allow-image-only` and record the reason.
9. Re-render and repeat the relevant checks after each fix.

For publication figures, additionally inspect at final physical width, render the SVG and PDF independently, search for literal `_` and `^` fake math, verify vector preservation and font embedding, and run `scripts/audit_publication_figure.py`.

For technical roadmaps, also verify objective-to-validation closure, work-package
outputs, branches, merges, feedback or explicit waivers, risk controls,
milestones, stage order, connector crossings, node-edge collisions, scientific
scene relevance, and one-canvas delivery. Run
`scripts/audit_technical_roadmap.py <contract.json> --strict` before the final
publication and editability audits.

Do not deliver from a contact sheet alone. Do not ignore programmatic overlap warnings without inspecting the affected slide.
