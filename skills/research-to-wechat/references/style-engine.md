# Style Engine

Resolve writing style in this order:
1. explicit user instruction
2. preset mode
3. author mode
4. custom brief

## Preset Catalog

- `deep-analysis`
  use: technology shifts, industry structure, business models, policy effects
  avoid: low-evidence opinion pieces
  frame: question, mechanism map, evidence, tensions, synthesis

- `explainer`
  use: concept unpacking, framework teaching, complex topics for broad readers
  avoid: insider shorthand and unexplained jargon
  frame: definition, why it matters, core parts, example, takeaway

- `tutorial`
  use: tools, workflows, operations, playbooks
  avoid: abstract discussion with no actionable path
  frame: goal, prerequisites, steps, pitfalls, checklist

- `case-study`
  use: launches, campaigns, company stories, growth moves, failures
  avoid: evidence fragments without chronology
  frame: background, problem, options, action, result, lessons

- `commentary`
  use: reactions, critiques, strategic judgments, trend takes
  avoid: fence-sitting and unsupported rhetoric
  frame: thesis, support, counterpoint, judgment

- `narrative`
  use: 人物、品牌、经历、历史转折
  avoid: report-style dumping
  frame: opening scene, conflict, development, insight, return

- `trend-report`
  use: market scans, sector outlooks, platform change, AI tracking
  avoid: presenting weak signals as settled facts
  frame: current state, fresh signals, scenarios, implications

- `founder-letter`
  use: strategic updates, principle statements, roadmap framing, culture writing
  avoid: generic PR polish
  frame: why now, what changed, decisions, principles, next move

- `newsletter`
  use: weekly roundups, curated briefs, multi-topic updates
  avoid: overlong transitions and one-thread essays
  frame: top line, short sections, quick takeaways, links or actions

## Author Mode

When the user names a writer, build an author card from 1 to 3 representative pieces.

Extract and store:
- `voice`
- `reader_distance`
- `paragraph_cadence`
- `opening_pattern`
- `argument_pattern`
- `evidence_habit`
- `signature_devices`
- `taboos`
- `safe_boundary`

Apply the author card with these rules:
- keep the cadence, lens, and evidence preference
- soften highly distinctive metaphors and sentence signatures
- inject the user's topic, reader, and required depth
- verify the result feels inspired, not impersonated

## Custom Brief

If the style is user-defined, ask for:
- target reader
- tone
- structural preference
- evidence density
- banned expressions

Compress the answer into a short internal brief before drafting.
