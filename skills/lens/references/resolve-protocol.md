# Resolve Protocol

This protocol defines the logic for handling contradictions, privacy boundaries, and behavioral drift within the LENS.

## 1. Conflict Resolution (Truth Evolution)
- **Rule:** New interaction data takes precedence over existing Node data if a direct contradiction exists.
- **Action:** 
  - Update the Node with the new data.
  - **Archive:** Move the displaced data to a "Historical" or "Legacy" section within the AXIOM/ETHOS node. Never delete.
  - **Validation:** If the conflict is high-impact (e.g., a core philosophical shift), the `lens-interview` should be used to seek surgical clarification.

## 2. Privacy Redlines (Exfiltration Protection)
- **Rule:** AXIOM data is for internal calibration only unless explicitly cleared for public manifestation.
- **Redline Items:** Biometric data, specific geolocational addresses, private financial assets, and medical constraints must never be included in generated content (Posts/Replies).
- **Masking:** Use abstractions when these topics are relevant (e.g., "The Home" instead of the specific address).

## 3. Drift & Contextual Deviation
- **Rule:** Distinguish between "Core Identity" and "Contextual Noise."
- **Detection:** If the subject's linguistic style or decision-logic deviates significantly from MODUS/ETHOS, analyze the context (e.g., high-stress, humor, or roleplay).
- **Weighting:** Contextual noise should be recorded in daily memory but weighted lower during distillation. Only persistent deviations (patterns) trigger a Node update.

## 4. Structural Integrity (The Vault Rule)
- **Rule:** Refinement must never result in net information loss. 
- **Action:** Merging and rewriting for "Structural Peace" must preserve the underlying data points. Abstracted data is still data.