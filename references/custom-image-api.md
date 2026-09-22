# Custom Image API Routing

Use this reference only when the user explicitly supplies or selects an OpenAI-compatible image API base URL, model, or credential. Load and follow the installed `imagegen` skill first.

## Contents

1. Provider selection
2. Credential handling
3. Compatible endpoint calls
4. Response verification
5. Editable-deliverable boundary
6. Publication-layout boundary
7. GPT-image-2 raster-to-editable reconstruction

If the user selects WisArt, read `references/wisart-image-api.md` for its
official field mappings and CLI constraints. WisArt is OpenAI-compatible and
uses the same bundled CLI route; never fall back to a browser-session workflow.

## Provider selection

Use this profile when the user asks this installed skill to generate academic visuals through its configured endpoint and does not override the provider:

- Base URL: `https://api.123nhh.com/v1`
- Model: `gpt-image-2-4k`
- Size: `auto`
- Quality: `high`
- Output: PNG for generated previews and complex illustrations

The user may override that profile with another OpenAI-compatible provider. A
second provider explicitly supplied during this task is:

- Base URL: `https://52ccl.net/v1`
- Model: `gpt-image-2`
- Size: `auto`
- Quality: `high`

The documented WisArt profile is:

- Base URL: `https://wisart.kuaileshifu.com/v1`
- Model: `gpt-image-2`
- Size: `auto` or a CLI-compatible concrete size
- Quality: `high` for final academic component boards
- Response: synchronous OpenAI-style `data[]`; use the default `b64_json`

Provider precedence is: an endpoint/model explicitly requested in the current
turn, then the process variables `ACADEMIC_PPT_IMAGE_BASE_URL` and
`ACADEMIC_PPT_IMAGE_MODEL`, then the default profile above. Do not infer that a
vendor supports every OpenAI parameter; if the CLI reports an unsupported
field, retry only with the documented compatible parameters and record the
response schema.

An explicit WisArt request selects the documented WisArt profile. All three
profiles use the bundled `imagegen` CLI, but provider-specific models, sizes,
and response constraints still apply.

For a temporary provider override in PowerShell, set only non-secret selection
variables before the generation subprocess:

```powershell
$env:ACADEMIC_PPT_IMAGE_BASE_URL = "https://52ccl.net/v1"
$env:ACADEMIC_PPT_IMAGE_MODEL = "gpt-image-2"
```

Read the credential from `WISART_API_KEY` for WisArt or
`ACADEMIC_PPT_IMAGE_API_KEY` for another configured provider. Copy the selected
value to `OPENAI_API_KEY` only for the child CLI process. If it is absent, ask
the user to set it locally; never add the value to this profile. Keep provider
overrides in process variables rather than command arguments.

For WisArt, use `scripts/run_wisart_image.ps1` instead of assigning environment
variables in a Codex terminal. It checks Process, User, and Machine scopes at
execution time, which avoids a stale Codex desktop process missing a user-level
variable added after application launch.

## Credential handling

- Send the credential only to the exact host the user authorized.
- Keep it in the generation process environment. Never write it into `SKILL.md`, scripts, prompt files, shell history, presentation notes, source notes, logs, ZIP packages, or final deliverables.
- Do not print, repeat, partially reveal, or validate a key by exposing it.
- Prefer a hidden interactive prompt or a preconfigured environment variable. Do not place the literal key in a command line.
- Treat a key pasted into chat as exposed and recommend rotation after the requested test.

## Compatible endpoint calls

1. Normalize the supplied HTTPS base URL and retain its `/v1` suffix when present.
2. Set `OPENAI_BASE_URL`, `OPENAI_API_KEY`, and the selected model only for the
   child process. Keep the base URL normalized and never persist the key.
3. Use the bundled CLI from the installed `imagegen` skill. Do not create a separate SDK client or modify the bundled CLI.
4. Run its `generate` command with the user-selected `gpt-image-*` model, a prompt file in the presentation scratch workspace, and a non-existing output path.
5. Use `--size auto` for vendor-specific model aliases such as a `*-4k` variant unless the provider documents a compatible explicit size. Use `--quality high` for an academic diagram or style board.
6. Keep prompt augmentation fields explicit: `--use-case scientific-educational` or `infographic-diagram`, intended slide use, composition, exact required labels, and constraints.

For WisArt, keep `n=1`, omit `response_format`, and use `3840x2160` for a fixed
16:9 4K component board. The bundled CLI does not accept ratio strings,
`1200x675`, or `quality=hd`; use the mappings in the WisArt reference.

For `gpt-image-2` scene atoms that need a cutout, request a perfectly flat
chroma-key background and run the installed `remove_chroma_key.py` helper;
`gpt-image-2` does not provide native `background=transparent`. Ask before
switching to CLI `gpt-image-1.5` for true transparency, especially for glass,
smoke, liquids, hair, or other soft/reflective edges.

The OpenAI SDK reads these process variables, so a compatible base URL can be used without changing the bundled CLI. The compatible generation endpoint is normally `POST /v1/images/generations`.

For the official WisArt route, `run_wisart_image.ps1` resolves an optional
`WISART_PYTHON` interpreter setting from Windows environment scopes before
falling back to `PYTHON` and then `python`. This allows an existing Codex
desktop process to use a user-scoped interpreter that already has the `openai`
package installed.

## Response verification

- Confirm that the command produced a file and record its MIME signature, byte size, and pixel dimensions.
- Treat PNG, JPEG, or WebP as raster even when the model name contains `4k`, `svg`, or `ppt`.
- Treat a file as SVG only when the response is valid SVG/XML containing vector elements. A renamed PNG is not SVG.
- The bundled CLI expects `data[].b64_json`. If the provider returns only a URL or a non-compatible schema, report the incompatibility. Do not silently create an unreviewed client.
- Inspect the result visually for scientific plausibility, label spelling, hierarchy, unwanted text, and watermarking before using it.

## Editable-deliverable boundary

Use generated raster output for style exploration, decorative support, or a complex scientific illustration. Do not use it as a full-slide replacement.

When GPT-image-2 output is requested as the starting point for an editable
figure, follow [raster-to-editable.md](raster-to-editable.md). That workflow
separates visual analysis from scientific reconstruction and requires an
editability class and provenance record for every object or retained raster
region.

For a final editable PPT:

- rebuild titles, body text, captions, citations, tables, charts, arrows, and simple diagram nodes as native PowerPoint objects;
- retain an image only for the portion that is inherently raster or too complex to reconstruct faithfully;
- run the editability audit before delivery.

For a final editable SVG, reconstruct the diagram from verified structure and labels or use an explicitly authorized vector-conversion workflow. Image tracing may create vector paths, but it does not recover semantic nodes, editable text, chart data, or connector logic.

## Publication-layout boundary

A generated 2x2 component board or style board is not a paper figure plan. Extract its palette, component silhouettes, line hierarchy, annotation treatment, and depth cues, then rebuild the evidence-led topology independently.

For a requested single paper architecture figure:

- default to one continuous end-to-end reading path;
- do not preserve generated panel letters or board quadrants;
- do not include slide titles, page chrome, or production footers;
- use correctly typeset mathematical labels rather than raster text from the generated image;
- export and inspect vector PDF and SVG separately from the generated raster reference.

For a technical roadmap or graphical abstract, split generation into a
text-light component board and isolated scientific scene atoms. Ask for
phase-ribbon silhouettes, mechanism insets, apparatus or field scenes,
validation badges, and connector/depth language. Do not ask the image model to
invent the research route, exact labels, equations, stage order, branch logic,
or evidence claims. Reconstruct those elements natively from the roadmap
contract and evidence ledger, then keep the raster only where the scene itself
is inherently illustrative.

If a credential was pasted into chat, treat it as exposed and rotate it. Use a
fresh `ACADEMIC_PPT_IMAGE_API_KEY` environment variable for subsequent runs;
never copy the pasted value into a prompt, command, log, skill file, or ZIP.
