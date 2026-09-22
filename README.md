# create-academic-ppt

An evidence-grounded Codex skill for academic slide decks, publication-ready
paper figures, technical roadmaps, and graphical abstracts.

The skill combines:

- publication-figure and presentation routing;
- code-grounded architecture reconstruction;
- GPT-image-2/WisArt visual references with provenance-aware reconstruction;
- editable SVG/PPTX output contracts;
- mathematical typesetting guidance;
- publication, editability, and technical-roadmap audits;
- interactive HTML and multi-format export helpers.

## Repository Layout

```text
SKILL.md                         Skill entry point
agents/openai.yaml               Codex UI metadata
references/                      Mode-specific workflow references
scripts/                         Auditors and rendering helpers
examples/academic-visual-ir.json Minimal scene IR example
examples/a2g-case-study/         Sanitized end-to-end figure case study
```

## Install As A Codex Skill

Copy this directory into the local Codex skills directory:

```powershell
Copy-Item -Recurse . "$env:USERPROFILE\.codex\skills\create-academic-ppt"
```

If the destination already exists, replace it only after reviewing local
changes. The skill remains automatically discoverable through its frontmatter;
explicit invocation is also supported:

```text
$create-academic-ppt
```

## Typical Workflows

### Publication figure

1. Route the request as `publication-figure`.
2. Read `references/publication-main-figure.md`,
   `references/code-grounded-architecture.md`, and
   `references/math-typesetting.md` when applicable.
3. Build the topology from verified code, data, and claims.
4. Use GPT-image-2/WisArt only for visual vocabulary or bounded raster regions.
5. Export and audit SVG, PDF, PNG, and PPTX independently.

### Academic deck

Read `references/academic-deck-playbook.md` and use the presentation skill for
editable PPTX authoring. Keep slide narrative, evidence, and source notes
traceable.

### Visual-first reconstruction

Read `references/raster-to-editable.md`. A generated image is a visual prior,
not the semantic source. Rebuild meaningful text, equations, nodes, connectors,
charts, and data from the evidence ledger.

## Validation

Run the repository validator:

```powershell
python scripts/validate_repo.py
```

Audit the included publication figure:

```powershell
python scripts/audit_publication_figure.py `
  examples/a2g-case-study/A2G_current_best_main_figure_editable.svg `
  examples/a2g-case-study/A2G_current_best_main_figure_vector.pdf `
  --target-width-mm 360 --art-kind line --strict

python scripts/audit_editability.py `
  examples/a2g-case-study/A2G_current_best_main_figure_editable.pptx
```

## Credential Handling

The WisArt launcher reads `WISART_API_KEY` from the process, user, or machine
environment at runtime and passes it only to the image-generation child
process. Never commit API keys, personal access tokens, `.env` files, or
provider responses containing secrets.

## Evidence Boundary

The A2G case study is included as a figure-generation example. Its scientific
claims are deliberately bounded by the source session: fold 0, seed 42,
validation-only evidence, no test or window-test access, and no universal-SOTA,
five-fold, or multi-seed claim.

## License

MIT. See [LICENSE](LICENSE).
