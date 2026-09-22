# GPT-image-2 Raster-to-Editable Reconstruction

Use this reference whenever GPT-image-2 (including the official WisArt route)
creates a board, style reference, component sheet, scene atom, or draft
architecture image that must become an editable SVG or PPTX. The generated
image is a visual prior. The evidence ledger, source code, data, formulas, and
scene IR remain authoritative after reconciliation.

## Contents

1. Non-negotiable contract
2. Choose the generation order
3. Required pipeline
4. Prompt contract for GPT-image-2
5. Editability classes and disclosure
6. QA gate
7. Common failure modes

## Non-negotiable contract

- Do not claim that a PNG, JPEG, WebP, screenshot, OCR result, or renamed file is
  an editable scientific figure.
- Do not let generated wording, numbers, equations, arrows, or topology override
  verified source evidence. Raster-model text is a spelling/layout hint only.
- Recreate scientific labels, formulas, tables, charts, nodes, arrows, and
  connectors natively whenever they carry meaning.
- Preserve a generated raster region only when it is inherently illustrative or
  cannot be reconstructed without losing important appearance. Record its
  bounding box, source image, reason, and editability class in the manifest.
- If only appearance-preserving tracing is possible, call the result
  `geometric`/`appearance-preserving`, not semantically editable.

## Choose the generation order

Select one order explicitly in the manifest:

### Evidence-first (default for a scientific architecture)

Use the code, data, formulas, and claim ledger to define the topology, then use
GPT-image-2 to explore palette, component silhouettes, depth, and scene language.
This is the safest route when the image contains many modules, tensor shapes,
ablation labels, or numerical results.

### Visual-first iterative refinement (allowed when the user requests it)

Use GPT-image-2 first to create a provisional visual draft. This is useful when
the visual composition is unclear or the user wants to discover a stronger
journal-style treatment before committing to layout. The draft must be labeled
`provisional-visual-only` and must not be treated as evidence. Then run the
following loop:

```text
GPT-image-2 draft
  -> visual token extraction and rough geometry
  -> optional masked/local image edit for style cleanup
  -> code/evidence reconciliation and discrepancy matrix
  -> corrected scene IR
  -> native editable SVG/PPTX render
  -> side-by-side visual comparison
  -> style-only refinement (repeat if needed)
```

The first pass may be generated without source code, but the final pass may not
be approved until every scientific object is mapped to a source locator or
explicitly marked `inferred`/`proposed`. A later image-edit pass may improve
spacing, color, glow, texture, or silhouette; it may not decide module
existence, edge direction, tensor dimensions, formula content, stage order, or
result values.

## Required pipeline

1. **Declare the generation order.** Record `evidence-first` or
   `visual-first` in the manifest. If visual-first is selected, create a
   provisional-only record before source inspection and keep all generated
   claims untrusted.
2. **Freeze or open the source contract.** For evidence-first, inventory the
   authoritative constructor, executed forward path, data values, equations,
   terminology, and target publication size before prompting. For visual-first,
   inventory those same sources immediately after the draft and before any
   semantic reconstruction. Create the claim-to-source ledger before approval.
3. **Generate a visual reference.** Use the official WisArt launcher for
   WisArt, `gpt-image-2`, `quality=high`, `n=1`, and a concrete `3840x2160`
   canvas for a fixed 16:9 4K board. Ask for component vocabulary or scene
   atoms, not the final scientific topology. Keep exact claims, long labels,
   equations, and fine-grained stage order out of the prompt unless they are
   explicitly treated as placeholders. Save the prompt, model, endpoint profile,
   output path, MIME type, dimensions, and generation timestamp in scratch
   metadata without storing credentials.
4. **Optionally refine the raster appearance.** If the provider supports image
   edits, use masked/local passes for style-only changes such as palette,
   spacing, stroke visibility, background cleanup, or component silhouette.
   Keep each revision and mask in the manifest. Never use these edits to add or
   remove scientific modules or to repair factual labels.
5. **Verify the raster.** Confirm the file signature, byte size, dimensions,
   color mode, and visible content. Inspect spelling, unwanted watermarks,
   impossible geometry, accidental extra modules, and visual artifacts. Treat
   every label or number as untrusted until checked against the ledger.
6. **Extract visual tokens.** Record palette roles, background treatment, stroke
   hierarchy, corner radii, shadows, gradients, depth cues, icon silhouettes,
   component proportions, spacing rhythm, and annotation style. Do not copy the
   board's quadrant layout as the figure topology.
7. **Build the canonical scene IR.** Project verified evidence into typed
   `group`, `node`, `edge`, `text`, `formula`, `chart`, `image`, and `raster`
   records. Keep geometry separate from claims and attach provenance to every
   node and edge. A minimal record is:

   ```json
   {
     "id": "selective_ssm",
     "kind": "node",
     "bbox": [x, y, width, height],
     "role": "model_block",
     "source": "a2g_mambakt_final.py:...",
     "editable": "semantic",
     "text": "Selective-SSM",
     "status": "verified"
   }
   ```

   Required fields are `id`, `kind`, geometry, `source` (or an explicit
   `proposed`/`inferred` status), and `editable`. Edges additionally carry
   `from`, `to`, direction, and edge provenance. Raster records additionally
   carry `asset`, `bbox`, `reason`, and `editable: "raster-retained"`.
8. **Reconstruct the strict editable layer.** Use the IR as the only layout
   authority. Render text and captions as native SVG text/PPTX text boxes;
   render nodes, stage bands, arrows, and connectors as vector shapes; render
   charts from source values; and route equations through the math-typesetting
   workflow with a retained LaTeX/source sidecar. Use the `Presentations` skill
   and `@oai/artifact-tool` for PPTX; never use `python-pptx`.
9. **Handle visual-only regions explicitly.** Choose one of these routes:

   | Route | What remains editable | Allowed retained raster | Required wording |
   | --- | --- | --- | --- |
   | Strict scientific reconstruction | All meaningful text, formulas, topology, nodes, edges, and charts | Only inherently raster scientific imagery | "Semantically editable SVG/PPTX; raster regions listed in manifest." |
   | Hybrid editable reconstruction | All labels, formulas, arrows, simple components, and overlays | A bounded complex illustration or texture | "Hybrid: listed raster regions are not semantically editable." |
   | Appearance-preserving trace | Vector paths and styling geometry | None required, but source semantics are not recovered | "Geometrically editable trace; text, data, and connector logic were reconstructed only where verified." |

   Never silently rasterize the whole figure to make the output look closer to
   the reference. If a region cannot be reconstructed faithfully, retain it as
   a bounded image and disclose the limitation rather than inventing semantics.
10. **Cross-check and export.** Render SVG, PDF, PNG, and PPTX independently from
   the same IR. Compare the editable reconstruction with the raster reference
   for palette and visual grammar, then compare it with the evidence ledger for
   scientific truth. For visual-first work, include a discrepancy matrix with
   each draft object, its reconciled source locator, the correction applied, and
   the final disposition (`kept`, `corrected`, `removed`, or `retained-raster`).
   Keep a manifest that lists source assets, IR revision, generated reference,
   image-edit revisions/masks, retained raster regions, formula source, and
   output hashes.

## Prompt contract for GPT-image-2

Build the prompt from the visual-token needs and the inclusion/exclusion ledger.
Use wording such as:

- “academic component design board / isolated scene atoms / text-light”;
- “restrained journal palette, explicit stroke hierarchy, clean connector
  corridors, no decorative claims”;
- “leave labels as short placeholders; do not invent data, equations, module
  names, or results”;
- “show separate reusable silhouettes rather than a final four-panel paper
  figure.”

Add negative constraints for watermarks, logos, photorealistic people,
illegible microtext, extra modules, unsupported arrows, and panel letters.
After generation, replace every placeholder with verified native text. Do not
use the image model to decide stage order, branch logic, tensor dimensions,
ablation claims, or numerical results.

For a visual-first draft, make the prompt deliberately text-light. Ask for
neutral placeholders such as `INPUT`, `BLOCK`, `MERGE`, and `OUTPUT`; add
`provisional concept only — no scientific claims or numbers`. This makes the
draft useful for composition while keeping later reconciliation auditable.

## Editability classes and disclosure

Use the following classes consistently in the IR, export manifest, and handoff:

- `semantic`: the object can be edited while preserving its scientific role
  (for example, a named node, connector, chart datum, or formula source).
- `geometric`: paths, fills, and styling can be edited, but semantic text/data or
  connector relationships were not recovered.
- `raster-retained`: the object is an image region; it can be cropped or moved
  but not edited as native scientific content.

The final QA report must list counts and bounding boxes for each non-semantic
object. A statement such as “0 image elements” is valid only after inspecting
the SVG XML and PPTX package, not from the file extension or a visual glance.
For visual-first work, also report the number of draft objects that were
corrected or removed during reconciliation and link each to the discrepancy
matrix.

## QA gate

Run the normal publication and presentation audits after reconstruction:

```bash
python scripts/audit_publication_figure.py <svg-or-pdf-or-png> --target-width-mm <width> --art-kind mixed
python scripts/audit_editability.py <pptx>
```

For a roadmap, also run:

```bash
python scripts/audit_technical_roadmap.py <contract.json> --strict
```

Inspect at final physical size, at 100%, in grayscale, and after an
independent render. Test that a reviewer can select, move, rename, and delete a
label, connector, and module without changing unrelated objects. Verify that
formula source, chart data, image regions, and evidence locators are present.
If any of these checks fail, downgrade the deliverable to a visual reference or
hybrid reconstruction and say so plainly.

## Common failure modes

- **OCR-first conversion:** fixes spelling but loses grouping, data semantics,
  connector direction, and formula structure. Rebuild from the ledger and IR.
- **One-click vector tracing:** creates many paths but no semantic nodes or
  editable text. Use only for appearance-preserving geometry.
- **Full-image embedding:** looks faithful but fails editability and publication
  QA. Crop and disclose only bounded inherently raster regions.
- **Board-as-topology:** turns a moodboard into arbitrary panels or stages.
  Extract visual grammar, then design topology from the evidence.
- **Unverified generated claims:** imports plausible but false numbers or module
  names. Treat all generated content as untrusted until source-checked.
