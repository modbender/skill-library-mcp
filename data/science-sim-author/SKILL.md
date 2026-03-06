---
name: science-sim-author
description: Generate self-contained interactive science simulations as a single index.html from a SimSpec YAML or JSON. Use when the user asks for physics, chemistry, biology, STEM, science education, classroom demos, virtual labs, PhET-style activities, mechanics simulations, circuit simulations, parameter sliders, plots, inquiry worksheets, or offline canvas-based teaching tools.
metadata: {"openclaw":{"emoji":"🧪","requires":{"bins":[],"env":[],"config":[]},"os":["darwin","linux","win32"]}}
---

# Science Simulation Author

## Core promise

Generate one self-contained `index.html` that runs offline, renders a STEM simulation on a 2D canvas, exposes model parameters as sliders, plots a time series, and includes an inquiry worksheet.

## Inputs

Accept a SimSpec in YAML or JSON with:

- `id`, `title`, `domain`
- `state`, `params`, `initial`, `equations`, `outputs`
- optional `level`, `dt`, `worksheet`, `success_criteria`

Validate against [templates/sim_spec_schema.json](templates/sim_spec_schema.json) before generating anything.

## Output contract

- Produce exactly one file named `index.html`.
- Keep all CSS in `<style>` and all JS in `<script>`.
- Do not use bundlers, package managers, CDNs, external fonts, or runtime network access.
- Include these DOM ids: `simCanvas`, `plotCanvas`, `runToggle`, `stepBtn`, `resetBtn`, `dtSlider`, `paramControls`, `readouts`, `statusBanner`, `worksheet`, `copyJsonBtn`, `downloadCsvBtn`.
- Include controls, readouts, one time-series plot, local JSON snapshot export, local CSV download, and a non-empty worksheet.

## Workflow

1. Validate the incoming SimSpec against [templates/sim_spec_schema.json](templates/sim_spec_schema.json).
2. Normalize the spec:
   - If `dt` is missing, use `default=0.01`, `min=0.001`, `max=0.05`.
   - If a parameter omits `step`, derive `step=(max-min)/100` with sensible rounding.
   - Normalize derivative aliases such as `dx`, `dy`, `dvx`, `dvy`, `dq`, `dvc` to canonical `d<stateName>` keys before generating JS.
   - Default readouts to `t` plus every state variable in state order.
3. Choose the renderer:
   - `mechanics` + state includes `x` and `y` -> `trajectory2d`
   - `mechanics` + state includes `x` and `v` -> `oscillator1d`
   - `electromagnetism` + state includes `q` or `vc` -> `circuit_rc`
   - Otherwise stop and ask the user for a clearer SimSpec instead of guessing.
4. Populate [templates/sim_single_file_html_template.html](templates/sim_single_file_html_template.html) with pre-normalized values.
5. Run [rubrics/validation_checklist.md](rubrics/validation_checklist.md) before returning the final `index.html`.

## Template placeholders

Populate these mustache variables:

- `sim_id`, `sim_title`, `domain`, `level`, `renderer_kind`
- `state_json`, `params_json`, `initial_json`, `equations_json`, `outputs_json`
- `worksheet_json`, `success_criteria_json`, `readout_fields_json`
- `dt_default`, `dt_min`, `dt_max`
- `model_step_logic_js`, `scene_draw_js`, `readout_map_js`

Expectations:

- JSON placeholders must be serialized before insertion.
- String placeholders used in data attributes should be plain strings.
- `model_step_logic_js` must return a derivative object without using `eval` or `Function`.
- `scene_draw_js` and `readout_map_js` may be no-ops; use `return [];` for an empty readout override.

## Rendering and model rules

- Use the shared RK4 and Euler integrators already present in the template.
- Keep physics fixed-step and rendering on `requestAnimationFrame`.
- Auto-pause if any state becomes `NaN` or `Infinity`.
- Cap trail history and plot history.
- Prefer one clear plot target from `outputs`; if multiple plots are supplied, use the first one for the visible plot and keep the rest only as metadata.

## Worksheet rules

- If the SimSpec provides a worksheet, keep it unless it is incomplete.
- If any worksheet category is missing, synthesize it using [rubrics/pedagogy_inquiry_prompts.md](rubrics/pedagogy_inquiry_prompts.md).
- Always return:
  - 3 Predict prompts
  - 2 Test prompts
  - 2 Explain prompts
  - 2 Misconceptions prompts

## Safety rules

Apply [rubrics/security_notes.md](rubrics/security_notes.md) strictly.

- Do not tell the user to run shell commands.
- Do not request secrets or API keys.
- Do not fetch remote assets or scripts.
- Do not add hidden telemetry or analytics.
- Do not produce multiple files.

## Templates and references

- Template: [templates/sim_single_file_html_template.html](templates/sim_single_file_html_template.html)
- Schema: [templates/sim_spec_schema.json](templates/sim_spec_schema.json)
- Validation checklist: [rubrics/validation_checklist.md](rubrics/validation_checklist.md)
- Pedagogy prompts: [rubrics/pedagogy_inquiry_prompts.md](rubrics/pedagogy_inquiry_prompts.md)
- Security notes: [rubrics/security_notes.md](rubrics/security_notes.md)

## Examples

- [examples/projectile_drag.yml](examples/projectile_drag.yml)
- [examples/spring_mass.yml](examples/spring_mass.yml)
- [examples/rc_circuit.yml](examples/rc_circuit.yml)
