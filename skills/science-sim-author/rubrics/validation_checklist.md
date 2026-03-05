# Validation Checklist

Use this checklist before returning a generated simulation.

- [ ] Output contains exactly one file named `index.html`.
- [ ] The file runs by double-clicking in a browser; no local server is required.
- [ ] No external dependencies are referenced: no CDN scripts, web fonts, remote images, or runtime fetch calls.
- [ ] The HTML includes the required DOM ids: `simCanvas`, `plotCanvas`, `runToggle`, `stepBtn`, `resetBtn`, `dtSlider`, `paramControls`, `readouts`, `statusBanner`, `worksheet`, `copyJsonBtn`, `downloadCsvBtn`.
- [ ] Core controls are present and wired: start/pause, reset, single-step, dt slider, and 2-6 parameter sliders.
- [ ] The model equations in the script match the normalized SimSpec equations.
- [ ] The simulation uses fixed-step physics and renders with `requestAnimationFrame`.
- [ ] RK4 is the default integrator and Euler fallback exists.
- [ ] Dt is clamped to the configured range.
- [ ] NaN/Inf detection auto-pauses the simulation and shows a visible warning.
- [ ] Trail history is capped and old points are discarded.
- [ ] Plot history is capped and the plotted series updates while the simulation runs.
- [ ] Readouts include time plus all state variables in state order.
- [ ] The worksheet accordion is present and every section is non-empty.
- [ ] The output includes Predict, Test, Explain, and Misconceptions prompts.
- [ ] JSON snapshot export works with a clipboard API path and a `file://` fallback path.
- [ ] CSV download works fully client-side and includes headers plus time-series rows.
- [ ] The generated file does not ask the user to run shell commands, install packages, provide secrets, or download assets.
- [ ] The generated file remains readable and inspectable plain HTML/CSS/JS.
