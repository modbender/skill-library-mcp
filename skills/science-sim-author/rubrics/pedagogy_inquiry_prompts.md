# Pedagogy Inquiry Prompts

Generate inquiry prompts that lead to a prediction, a controlled test, and an explanation tied to the observed output.

## Required structure

Always generate:

- 3 `predict` prompts
- 2 `test` prompts
- 2 `explain` prompts
- 2 `misconceptions` prompts

Do not leave any category empty. Do not use generic filler such as "What do you notice?".

## Authoring rules

- Change one parameter at a time unless the prompt explicitly asks for a comparison.
- Tie every prompt to a visible observable: trajectory, displacement, voltage, time constant, or plotted curve.
- Prefer prompts that can be answered from evidence gathered in the sim instead of prior memorization.
- Keep prompt wording concise and student-facing.
- Use prompts that support a `Predict -> Test -> Explain` sequence.

## Mechanics prompts

Use mechanics prompts for projectile and spring-mass-damper systems.

- Predict how changing one parameter alters range, peak height, oscillation period, damping envelope, or equilibrium crossing.
- Test prompts should instruct learners to hold other variables fixed and compare two or three runs.
- Explain prompts should connect forces, acceleration, energy loss, or restoring effects to the observed graph and motion.
- Misconception checks should challenge beliefs such as "heavier always moves faster" or "damping changes equilibrium position by itself."

### Mechanics examples

- Predict: "If you increase drag while keeping launch speed fixed, how should the range change?"
- Predict: "If you double the spring constant and keep mass fixed, what happens to the oscillation period?"
- Test: "Run the simulation twice with the same initial displacement and compare the peak heights for low and high damping."
- Explain: "Explain why the object crosses equilibrium more slowly after damping increases."
- Misconception: "Does a larger launch speed always increase peak height by the same amount when drag is present?"

## Electromagnetism prompts

Use electromagnetism prompts for RC charging and discharging systems.

- Predict how changing resistance, capacitance, or source voltage alters the charging rate or final voltage.
- Test prompts should compare curves using a single parameter change and reference the plot.
- Explain prompts should tie observations to the time constant and asymptotic behavior.
- Misconception checks should challenge ideas such as "higher resistance means higher final voltage" or "capacitors charge linearly over time."

### Electromagnetism examples

- Predict: "If resistance increases while capacitance stays fixed, how should the time to reach 63% of the final voltage change?"
- Predict: "If the source voltage doubles, what changes in the plot and what stays the same?"
- Test: "Keep capacitance fixed and compare two runs with different resistances using the voltage-time plot."
- Explain: "Explain why the curve flattens as the capacitor voltage approaches the source voltage."
- Misconception: "Does increasing capacitance change the final voltage, or only how quickly the capacitor gets there?"
