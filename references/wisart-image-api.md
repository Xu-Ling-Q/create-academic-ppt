# WisArt Official Image API

Use this provider profile when the user explicitly selects WisArt. WisArt
publishes an OpenAI-compatible HTTPS API, so use the installed `imagegen`
skill's bundled `scripts/image_gen.py` CLI. Do not use browser cookies, browser
automation, intercepted requests, or the website origin as a private API.

## Contents

1. Official contract
2. Credential handling
3. Generation mapping
4. Editing mapping
5. Response and failure handling
6. Academic-artifact boundary
7. Provenance

## 1. Official contract

- Base URL: `https://wisart.kuaileshifu.com/v1`
- Authentication: `Authorization: Bearer <API key>`
- Models: `GET /v1/models`
- Generate: `POST /v1/images/generations`
- Edit: `POST /v1/images/edits`
- Default model: `gpt-image-2`, subject to the live models response
- Generation is synchronous and returns OpenAI-style `created` plus `data[]`
- The service returns HTTP 503 during maintenance

Generation fields:

| Field | Rule |
| --- | --- |
| `model` | Optional; use a value returned by `/v1/models` |
| `prompt` | Required and non-empty |
| `size` | `auto`, a documented ratio, or arbitrary `WIDTHxHEIGHT` / `WIDTH*HEIGHT` |
| `quality` | `auto`, `low`, `medium`, `high`, or `hd` |
| `n` | 1 through 5 |
| `response_format` | `b64_json` or `url` |

WisArt maps a concrete size to the closest aspect ratio and derives the
resolution tier from area. When size is absent, `auto`, or a ratio, `medium`
maps to 2K, `high`/`hd` maps to 4K, and other values map to 1K.

WisArt accepts compatibility fields including `background`, `moderation`,
`output_format`, `output_compression`, and `user`, but the current generation
channel may safely ignore unsupported values. Do not infer transparency or
output encoding from these accepted fields.

## 2. Credential handling

Use `scripts/run_wisart_image.ps1` for every WisArt invocation. It resolves
`WISART_API_KEY` in this order: Process, User, then Machine environment scope.
It sets `OPENAI_API_KEY` and the pinned `OPENAI_BASE_URL` only inside the
launcher process and its imagegen child. This makes the provider available in
other Codex sessions even when the already-running desktop application did not
inherit a user-level variable. Never provide a `--api-key` argument or write the
key to the skill, prompt, command history, logs, presentation notes, manifests,
or ZIP.

Treat a key pasted into chat as exposed and require rotation before a live
production run. Send the key only to `wisart.kuaileshifu.com`.

## 3. Generation mapping

The bundled CLI only accepts `auto` or `WIDTHxHEIGHT` for `gpt-image-2`, and it
requires both dimensions to be multiples of 16. Do not pass WisArt ratio strings
or the documentation example `1200x675` through this CLI. Use a compatible
concrete size instead:

| Placement | CLI size |
| --- | --- |
| 1:1 high-resolution board | `2880x2880` |
| 4:3 landscape | `3072x2304` |
| 16:9 landscape | `3840x2160` |
| 9:16 portrait | `2160x3840` |
| Provider-selected composition | `auto` |

Use `quality=high` rather than the WisArt alias `hd`; the bundled CLI accepts
`low`, `medium`, `high`, and `auto`. Keep `n=1` unless the user explicitly asks
for variants, and never exceed WisArt's limit of 5.
The launcher rejects `generate-batch` because its per-job JSONL `n` values are
not safely bounded by the wrapper; issue separate `generate` calls instead.

The bundled CLI expects `data[].b64_json`. Omit `response_format` so WisArt's
documented `gpt-image-*` generation default remains `b64_json`; do not request
`url` through this route.

Check local configuration without exposing the key:

```powershell
& "$env:USERPROFILE\.codex\skills\create-academic-ppt\scripts\run_wisart_image.ps1" -Check
```

Use the launcher for a generation child process:

```powershell
& "$env:USERPROFILE\.codex\skills\create-academic-ppt\scripts\run_wisart_image.ps1" generate `
  --model gpt-image-2 `
  --prompt-file "<prompt.txt>" `
  --size 3840x2160 `
  --quality high `
  --n 1 `
  --out "<non-existing-output.png>"
```

The launcher restores any pre-existing `OPENAI_API_KEY` and `OPENAI_BASE_URL`
values before it exits. It also supports direct `-File` invocation from Windows
PowerShell 5.1: it captures imagegen arguments before PowerShell's own common
parameter binder can mistake `--out` for `OutVariable`/`OutBuffer`.

`-Check` also reports whether the selected Python interpreter can import the
`openai` package. The launcher resolves `WISART_PYTHON` first, then `PYTHON`,
from Process, User, then Machine scope, so an already-running Codex desktop
process can use a user-level interpreter setting without changing the system's
general Python default. A real (non-`--dry-run`) invocation stops before sending
a request if that import is unavailable; install the package in that interpreter
with the project's normal environment manager (for example, `uv pip install
openai`) or set `WISART_PYTHON` to an interpreter that already contains it.

## 4. Editing mapping

The official endpoint accepts multipart `image` fields or a JSON `images`
array. Multipart inputs may be JPEG, PNG, WebP, or GIF, with up to 16 images.
`prompt` is required; `model`, `size`, `n`, and `response_format` are optional.
The documented `mask` field is accepted for compatibility but currently does
not participate in generation, so never promise mask-bounded edits.

The bundled CLI's `edit` command uses multipart upload and is structurally
compatible. However, it only decodes `b64_json` and does not expose
`response_format`. Use it for WisArt only after a live one-image test confirms
that the edit endpoint defaults to `b64_json`. Until then, treat generation as
the verified production route and describe editing as documented but not yet
live-verified in this skill.

## 5. Response and failure handling

- Confirm the actual file signature, byte size, pixel dimensions, and aspect
  ratio. Provider-side format fields may be ignored.
- If the file signature disagrees with the requested extension, rename the file
  to the MIME-correct extension before use.
- Treat HTTP 503 as maintenance. Stop and report it; do not change providers or
  submit repeated production requests automatically.
- After a connection loss or timeout, do not immediately resubmit a synchronous
  request because the first request may have completed. Check WisArt history or
  ask the user before spending again.
- Never log the Authorization header, full API key, or unpublished prompt.

## 6. Academic-artifact boundary

Treat every WisArt result as raster unless it is verified SVG/XML with real
vector elements. Use generated output for component-language boards,
scientific scene atoms, or complex illustrations. Rebuild final topology,
labels, arrows, equations, charts, legends, and evidence claims as editable SVG
or PowerPoint objects. Run the publication and editability audits before
delivery.

## 7. Provenance

Source: `https://wisart.kuaileshifu.com/#/member/api-docs`, transcribed from the
official API documentation supplied by the user and verified on 2026-07-27.
