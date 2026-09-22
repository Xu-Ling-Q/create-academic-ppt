# Mathematical Typesetting for Academic Figures and Slides

Use this reference whenever visible content contains equations, variable subscripts, superscripts, Greek symbols, matrices, probability expressions, norms, or tensor dimensions.

## Keep a canonical formula source

Store every nontrivial formula in a UTF-8 `.tex` or structured source file. Copy formulas from the authoritative paper, code, or derivation and preserve a source locator. Do not repair an uncertain formula by visual guesswork.

Use the same canonical source for PPTX, SVG, PDF, and caption notation. Record intentional notation changes in the evidence ledger.

Classify formula editability explicitly in the QA report:

- `native-editable`: a verified Office Math/OMML equation that PowerPoint can
  edit as mathematics;
- `source-editable`: a vector SVG generated from a retained `.tex` source;
  scalable and reproducible, but not a native PowerPoint equation object;
- `appearance-only`: rasterized or outlined math with no semantic source;
  unacceptable for a primary formula unless the source format forces it.

Never describe a vector formula with a `.tex` sidecar as natively editable in
PowerPoint. State the actual boundary in the handoff.

## Route formulas by complexity

### Simple inline identifiers

Examples include a variable with one subscript, a tensor dimension, or a short probability label.

For editable PPTX, build these from rich-text runs or grouped text objects:

- italicize scalar and variable symbols;
- keep operators, function names, digits, and descriptive subscripts upright;
- set subscript or superscript text to roughly 65-75% of the base size;
- shift the baseline consistently instead of shrinking the whole expression;
- group the parts so the label moves as one component.

For editable SVG, use `<tspan>` with an explicit smaller font size and baseline shift, or use a tested vector math renderer.

Never leave visible ASCII notation such as `x_t`, `R^256`, `H_<t`, or `P(r_t=1)` when the intended output is typeset mathematics.

### Full equations and complex notation

Use native Office Math only when the authoring route is tested and the exported PPTX preserves it. Do not claim that a normal textbox is an equation object.

Otherwise:

1. Keep the LaTeX source.
2. Render it to vector SVG with `scripts/render_math_svg.py` or another verified MathJax, KaTeX, or TeX route.
3. Embed the SVG as a scalable vector asset in PPTX and the final figure.
4. Keep the `.tex` sidecar as the editable semantic source.
5. Inspect the SVG and every exported PDF/PPTX render.

This route is visually scalable but the embedded PPT object is not a native editable equation. State that boundary clearly.

If native Office Math is required, verify the generated PPTX contains `m:oMath`
or `m:oMathPara` elements and reopen the equation in PowerPoint. A normal text
box set in Cambria Math does not satisfy this requirement.

## Use mathematical typography, not just a math font

Changing a textbox typeface to `Cambria Math`, STIX, or Latin Modern does not create fraction layout, scripts, limits, matrices, or operator spacing.

Prefer:

- STIX Two Math, Cambria Math, or Latin Modern Math for formula rendering;
- the manuscript's exact symbols and conventions;
- proper mathematical minus, multiplication, inequalities, and delimiters from the renderer;
- upright roman text for operators such as `softplus`, `sigmoid`, `exp`, and `log`;
- consistent bold treatment for vectors and matrices.

Avoid mixed Unicode approximations, manual spaces, fake superscript characters, and line breaks inserted solely to force a formula into a box.

## Fit formulas to diagrams

- Shorten by defining a symbol once instead of shrinking below the figure's minimum font size.
- Put derivations in the caption, methods, or supplement; show only the transformation needed to understand the figure.
- Align repeated equations on the equals sign or a shared baseline.
- Keep equations clear of arrows, borders, masks, and node labels.
- Preserve enough surrounding whitespace for subscripts, superscripts, accents, and tall delimiters.

## Render vector formula SVG

Use:

```bash
python scripts/render_math_svg.py \
  --formula "P(r_t=1\\mid q_t,c_t,H_{<t})" \
  --output formula.svg \
  --font-size 10 \
  --fontset stix
```

The script writes an SVG and a sibling `.tex` source file. It uses Matplotlib MathText and therefore supports a LaTeX subset. For unsupported commands, use a full TeX, MathJax, or KaTeX workflow and record that dependency.

## Formula QA

For every output format:

- compare the rendered formula character by character with the canonical source;
- verify scripts, accents, Greek letters, relation symbols, brackets, and operator spacing;
- check baseline alignment with adjacent prose and diagram nodes;
- verify the smallest formula at final physical size;
- inspect in PowerPoint or LibreOffice, an SVG browser, and the final PDF renderer;
- check for missing glyph boxes, substituted fonts, clipped ascenders/descenders, and rasterized formulas;
- search visible PPTX and SVG text for suspicious literal `_` and `^` notation.
- record each formula as `native-editable`, `source-editable`, or
  `appearance-only` and verify that the delivered source matches the label.

Do not approve a figure because the LaTeX source is correct; approve the actual rendered artifacts.
