# A2G current-best figure QA report

## Evidence QA

- Claim boundary is explicit in the artwork and caption: fold0/seed42/validation-only, test/window-test false, quality_freeze=false.
- Full accounting is shown as `6/8`; the two fail markers are A12 and Statics.
- Selective-SSM is shown as the only strict matched `5/5` contribution.
- Train-only item residual dropout is dashed and labeled `0.4`; it is not connected to inference-only claims.
- Retired/failed candidates and the boundary-complete memory API are excluded from the main contribution path.

## Visual QA

- SVG, PPTX, and PDF independently rendered after the final copy-fit pass.
- One continuous left-to-right reading path with side channels for prior/statistic logits.
- Grayscale simulation preserves hierarchy through text, border, line style, and shape redundancy.
- Protanopia simulation preserves the distinction between the proven SSM, amber evidence paths, and coral train-only/statistic paths through border and dash redundancy.
- No gradients, shadows, raster screenshots, decorative blobs, or four-panel topology were used.

## Technical QA

- `audit_publication_figure.py --strict --target-width-mm 360 --art-kind line`: PASS for SVG and PDF.
- SVG: viewBox `0 0 3840 2160`, 168 vector elements, 60 text elements, 0 image elements, 0 gradients, minimum font 8.61 pt, minimum stroke 0.638 pt at 360 mm.
- PDF: 1 page, 359.833 x 202.523 mm crop, 5 embedded font resources, 0 image XObjects.
- PPTX editability audit: PASS; 1 slide, 62 text shapes, 103 non-text/connectors in the audit summary, 0 pictures/tables/charts. ZIP inspection reports 151 `<p:sp>` shapes and 14 `<p:cxnSp>` connectors.
- PPTX overflow test: completed with no reported overflow output.
- PNG: 3840 x 2160 RGB. It is a 4K preview; the vector PDF is the publication master.

## Formula QA

- Canonical source: `A2G_current_best_formula_sources.tex`.
- The visible SSM shorthand is implementation-equivalent and uses `rho`, `h(prev)`, `tanh`, and explicit multiplication; no literal `_` or `^` fake math remains in the SVG.
- Formula status: editable text in PPTX/SVG plus retained `.tex` semantic source; not native Office Math.

## WisArt provenance

- Official route: `https://wisart.kuaileshifu.com/v1` via `run_wisart_image.ps1`, `gpt-image-2`, `3840x2160`, `quality=high`, `n=1`.
- The fresh 2026-08-24 call returned HTTP 500 token-unavailable error and was not retried.
- The delivered board is a previously generated official WisArt 4K board from the user-specified Codex session. It was used only for palette/component vocabulary; all scientific topology, labels, arrows, and formulas were rebuilt as editable SVG/PPTX.

## Residual risk

The main scientific risk is not rendering: it is that the current evidence is still single-fold/single-seed validation supporting evidence. Any paper claim should preserve that boundary until a new authorized protocol supplies stronger evidence.
