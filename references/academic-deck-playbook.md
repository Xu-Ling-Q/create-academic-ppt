# Academic Deck Playbook

Use this reference to turn papers, proposals, notes, datasets, or mixed research materials into a defensible group-meeting deck. Treat the 12-slide arc as a narrative default, not a fixed template.

## Build from evidence first

1. Define the audience, meeting purpose, time limit, and desired discussion outcome.
2. Inventory every available source. Prefer the paper, supplement, protocol, code, and data over summaries or commentary.
3. Create an evidence ledger before outlining slides. Record each candidate claim, its exact support, source location, confidence, allowed wording, and best visual form.
4. Write one sentence that states the research question, method, strongest supported finding or expected contribution, and boundary condition.
5. Arrange claims into a narrative spine: problem -> gap -> question -> approach -> evidence or analysis plan -> interpretation -> decision or discussion.
6. Draft slide headlines as complete takeaway sentences. Make the body prove the headline; remove any headline the evidence cannot support.
7. Choose visuals only after fixing the claim. Use one primary message per slide and move methodological depth, extra checks, and full references to an appendix.
8. Audit every number, citation, label, and causal verb against the evidence ledger before delivery.

## Adapt the default 12-slide arc

Use this order for a research group meeting, then merge or split slides according to complexity and speaking time.

| Slide | Purpose | Require |
|---|---|---|
| 1. Title and thesis | Orient the room immediately | State the topic, paper or project status, presenter, date, and one-sentence thesis. |
| 2. Why this problem matters | Establish stakes | Quantify the phenomenon or show a concrete case; avoid generic motivation. |
| 3. What is known and missing | Locate the gap | Synthesize the closest literature and name the unresolved contradiction, limitation, or missing mechanism. |
| 4. Research question and claims | Fix the target | State the question, hypotheses, or estimands; separate confirmatory from exploratory claims. |
| 5. Mechanism or conceptual model | Explain why the claim could hold | Map constructs, causal steps, moderators, and observable implications. |
| 6. Data, sample, or materials | Establish the evidence base | Report provenance, inclusion rules, sample size, timing, and important exclusions. |
| 7. Design and identification | Establish inferential logic | Show assignment, comparison, model, controls, assumptions, or counterfactual. |
| 8. Measures and analysis | Make execution inspectable | Define outcomes, predictors, coding, preprocessing, and primary analysis. |
| 9. Headline evidence | Answer the main question | Present the strongest result with effect size, uncertainty, units, and reference group. |
| 10. Robustness, heterogeneity, and limits | Test the answer | Show decisive checks or subgroups and state remaining threats without defensiveness. |
| 11. Interpretation and contribution | Explain what changes | Distinguish empirical result, mechanism interpretation, theoretical contribution, and practical implication. |
| 12. Discussion and next decision | Direct the meeting | End with two or three specific questions, decisions, or next steps rather than a generic “Questions?” slide. |

Treat this as a 12-slide core excluding appendix slides. Add an appendix for detailed models, variable definitions, full-size tables, alternate specifications, preregistration, and references. Compress slides 6–8 for a conceptual paper; expand them for a methods review. Replace slides 2–4 with a structured comparison when presenting several papers.

## Enforce source and claim discipline

- Mark working claims as **verified**, **inferred**, **preliminary**, or **proposed**. Remove the tags from polished prose only when the status remains unmistakable.
- Match verbs to evidence. Use “causes,” “mediates,” or “drives” only when the design supports that inference; otherwise use “is associated with,” “predicts,” or “is consistent with.”
- Preserve the denominator, unit, time window, baseline, reference group, sample size, and uncertainty for every quantitative claim.
- Cite the nearest primary source on the slide with a compact author–year plus page, section, figure, or table locator. Put the full reference, DOI, or stable URL in notes or the appendix.
- Attribute reused and adapted visuals. Label reconstructions, digitized values, and author calculations explicitly.
- Keep direct quotations short, visibly quoted, and page-located. Paraphrase only after checking that scope and modality remain intact.
- Surface conflicts among sources. Do not silently reconcile inconsistent sample sizes, dates, estimates, or definitions.
- State “not reported,” “not available,” or “cannot be verified from the supplied sources” instead of filling gaps.
- Keep slide-level claims no stronger than the paper. Separate the authors’ interpretation from the presenter’s critique or extension.

## Write bilingual copy deliberately

- Choose one primary presentation language from the audience context. Use the second language for concise support, not automatic line-by-line duplication.
- Keep the primary-language headline dominant. Place a short translation beneath it only when both audiences need independent access.
- Define each technical term once as `Primary term（对应术语，ACRONYM）`, then reuse one stable term and acronym throughout.
- Preserve equations, variable names, citations, proper nouns, and official scale names. Keep an original paper title and add a translated title in brackets only when useful.
- Translate meaning and argumentative force rather than syntax. Check hedges such as “may,” “suggests,” “初步表明,” and “与…一致” carefully.
- Use parallel hierarchy, numbering, color meaning, decimal precision, and units across languages.
- Shorten copy before reducing type size. Allow extra width for English and extra line height for Chinese; use fonts with reliable Latin and CJK coverage.
- Run a terminology pass at the end and resolve every competing translation.

## Select the right evidence visual

### Charts

- Use a chart to show magnitude, distribution, trend, or relationship. Make the chart title state the finding.
- Plot effect sizes with confidence or credible intervals when inference matters. Show raw distributions or sample counts when aggregation could conceal instability.
- Label axes, units, groups, and reference conditions. Use a zero baseline when magnitude comparisons require it; disclose any truncated axis.
- Recreate a chart only from recoverable data. Label approximate values and avoid false precision when digitizing a published figure.
- Avoid 3D effects, ornamental encodings, and dual axes unless the second scale is essential and unambiguous.

### Tables

- Use a table for exact values or structured comparisons, not for a visual trend.
- Retain only columns needed for the slide claim. Align decimals, standardize precision, define symbols, and highlight the decisive cells sparingly.
- Split dense regression output across a main-message slide and an appendix; never shrink a full paper table until it becomes unreadable.

### Mechanism diagrams

- Use a mechanism diagram to explain how constructs, interventions, or states connect.
- Arrange the primary path left to right. Label arrows with the proposed process and distinguish causal, correlational, and speculative links by line style plus a legend.
- Separate mediator, moderator, confounder, measurement, and outcome roles. Attach observable implications or evidence markers to each important link.
- Keep the diagram consistent with the identification strategy. Do not let an arrow imply causality the analysis cannot establish.

## Handle incomplete or absent results

- Label status prominently: **proposal**, **preregistered**, **data collection**, **analysis in progress**, or **preliminary**.
- Preserve slides 1–8, then replace the results sequence instead of inventing a conclusion.
- For incomplete results, present only validated outputs on slide 9, show missing analyses and blocking issues on slide 10, and state what remains provisional on slide 11.
- For no results, replace slide 9 with the planned estimands and output shells, slide 10 with assumptions, diagnostics, falsification tests, and decision thresholds, and slide 11 with expected contribution under multiple plausible outcomes.
- Use outcome-contingency framing: state what a positive, null, mixed, or contradictory result would imply and what it would not imply.
- Show simulated data only to explain the analysis or visual format. Watermark it **simulated / illustrative** and never mix it with observed values.
- Ask the group to decide something actionable: refine a hypothesis, approve an exclusion rule, select a specification, diagnose a threat, or prioritize the next data collection step.
- Treat null or inconclusive evidence as a result only after reporting uncertainty, power or precision, data quality, and design limitations.

## Run the final narrative audit

- Read only the slide headlines and confirm that they form a complete, non-contradictory argument.
- Verify that every slide answers “why is this here now?” and that every visual proves the headline.
- Remove repetition, unsupported novelty claims, decorative data, and conclusions that appear before their evidence.
- Confirm that limitations qualify the relevant claim rather than appearing as an isolated disclaimer.
- End with the exact discussion questions or decisions the meeting should resolve.

## Provenance

Use the user-supplied [Feishu page](https://wievf29s6ca.feishu.cn/wiki/L8mOwmm0KiApwZkfy8JcN7tonHg?from=from_copylink) as workflow inspiration. Treat this playbook as an original synthesis rather than a transcription of that page.
