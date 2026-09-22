# Code-Grounded Architecture Diagrams

Use this workflow whenever a slide, paper figure, SVG, PDF, or PPT diagram must represent an implementation rather than a conceptual proposal.

## Lock the authoritative code

1. Resolve the exact repository, Codex task, checkout, remote path, or archive named by the user.
2. Identify the production entrypoint, model class, trainer, evaluation path, and configuration actually used for the referenced result.
3. Record the absolute path, commit or file hash, class name, run configuration, and date in scratch notes.
4. Distinguish these states explicitly:
   - formal or deployed entrypoint;
   - latest accepted implementation;
   - experimental candidate;
   - rejected or retired code;
   - compatibility-only or disabled code.
5. Ask only when two live implementations are materially different and the user's pointer does not resolve the choice. Otherwise select the most authoritative target and state it.

Never let an older design document override a newer executed implementation. Never infer active modules from the model name alone.

## Trace the executed graph

Read the complete relevant constructor and forward path, then inspect the trainer and evaluator.

Map:

- raw inputs, padding, shifted sequences, masks, and labels;
- target-time inputs versus strictly historical inputs;
- embeddings, learned parameters, fixed priors, and derived statistics;
- concatenations, residuals, gates, recurrences, masks, and branch merges;
- active module order and repetition count;
- tensor shapes and dimensions from the actual run configuration, not constructor defaults;
- direct residual logits and other paths that bypass the learned head;
- prediction semantics, loss, auxiliary outputs, and evaluation slicing;
- training-only behavior versus deterministic inference behavior.

Follow inheritance, wrappers, feature flags, and module replacement after initialization. Treat a created-then-deleted module, zeroed channel, folded parameter, disabled flag, or compatibility shim according to its runtime effect.

## Build an inclusion and exclusion ledger

For every proposed diagram node, record its code anchor and status. Include only executed or intentionally depicted training-only paths.

Create a negative list from:

- rejected experiments;
- retired branches still present in old files;
- unused inputs;
- no-op compatibility objects;
- proposed mechanisms absent from the selected code;
- implicit zero channels that preserve normalization but are not real feature branches.

Do not draw a graph module because the model name contains “Graph.” Do not draw a router because the training API returns a placeholder route tensor. Do not draw a position encoder when it is instantiated only for seed compatibility and immediately deleted.

## Translate code into the visual

1. Reduce the executed graph to a readable main pipeline.
2. For a publication main figure, keep that pipeline semantically continuous. Model stages are not separate `(a)` through `(d)` panels unless they are scientifically independent views.
3. Show evidence or calibration branches only when they affect the output.
4. Separate training-only mechanisms with a dashed boundary and label them `training only`.
5. Label repeated blocks with the configured count and note any asymmetric final block.
6. Show dimensions only when verified from the selected run.
7. Keep equations compact and faithful to the implementation, and follow the math-typesetting reference.
8. Keep the selected hash or commit in the evidence ledger or caption provenance. Put it inside the artwork only when the venue or user requires it.

If using image generation for a style proof, build the prompt from the inclusion ledger and add the negative list as explicit constraints. Treat the generated raster only as a visual reference. Reconstruct the final SVG or PPT with native editable text, shapes, and connectors.

## Validate the finished diagram

- Match every node and edge against the execution ledger.
- Verify tensor dimensions arithmetically at concatenations and projections.
- Confirm that target labels or future responses do not appear as model inputs when the code uses them only for loss.
- Confirm that rejected, retired, and inactive modules are absent.
- Confirm that training-only paths cannot be mistaken for inference paths.
- Render and inspect every slide at full size.
- Run the editability audit for PPTX output.
- For a publication figure, inspect the PDF and SVG at final physical size and run the publication-figure audit.
- Preserve earlier conceptual versions and use a distinct `from-code` filename.
