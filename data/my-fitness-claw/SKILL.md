---
name: my-fitness-claw
version: 1.7.0
description: Your personal nutrition sidekick. Log meals in plain natural language, track macros (P/C/F) automatically, and visualize your progress on a beautiful real-time dashboard. Version 1.7 adds automatic micronutrient tracking based on general 32-year-old male recommended daily intakes. Includes AI-driven health insights, common food memory, and daily progress tracking—all controlled via chat.
requires:
  tools: [canvas, read, write, edit]
  paths: [nutrition/, canvas/, memory/]
---

# MyFitnessClaw

This skill manages your nutritional data and provides a visual dashboard for tracking macros and micronutrients using OpenClaw's native tools.

## Core Files (Skill Assets)

- `assets/nutrition/daily_macros.json`: The structured log of daily intake.
- `assets/nutrition/targets.json`: Daily nutritional goals (calories, protein, carbs, fats, and 10 essential micronutrients).
- `assets/nutrition/insights.json`: AI-generated tips based on current progress.
- `assets/nutrition/foods/common.md`: A reference list of frequently eaten foods and their macros/micros.
- `assets/canvas/index.html`: The visual dashboard for the OpenClaw Canvas.

## Workflow: Logging Food

When the user mentions eating something:
1. **Estimate Macros & Micros**: If the user doesn't provide them, estimate:
   - Macros: Calories, protein, carbs, fats.
   - Micros: Vitamin D3, Magnesium, Potassium, Zinc, Vitamin B6, Vitamin B12, Selenium, Vitamin C, Vitamin A, Vitamin E.
   Check `assets/nutrition/foods/common.md` first.
2. **Update Daily Log (Canonical)**: Update `assets/nutrition/daily_macros.json`. Include the `micros` object for both individual meals and the daily total.
3. **Update Offline Mirror**: Update `assets/canvas/offline_data.js` with the same data, ensuring micronutrients are included.
   - Overwrite the file with: `window.__OFFLINE_DAILY_MACROS = [...]; window.__OFFLINE_TARGETS = {...}; window.__OFFLINE_INSIGHTS = {...};`
   - This ensures the dashboard works when opened via `file://` (offline/browser-first).
4. **Update Memory**: Log the meal in the agent's current daily memory file (e.g., `memory/YYYY-MM-DD.md`).
5. **Show Dashboard**: Use `canvas(action=present, url='skills/my-fitness-claw/assets/canvas/index.html')` to show the updated dashboard inside OpenClaw.
6. **Provide Browser Access**: After every log, provide the following message:
   > 📊 **View in your browser:**
   > - **Quick:** Open `skills/my-fitness-claw/assets/canvas/index.html` in your browser (uses offline mirror).
   > - **Full:** Run `python -m http.server 8000` from the workspace root and visit `http://localhost:8000/skills/my-fitness-claw/assets/canvas/index.html`.
7. **Generate Insights**: Analyze progress against goals in `assets/nutrition/targets.json` and update `assets/nutrition/insights.json`.

**Persistence Rules**:
- `assets/nutrition/*.json`: Canonical storage.
- `assets/canvas/offline_data.js`: Mirror for `file://` viewing only.
- **Do not** modify `assets/canvas/index.html` during routine logging.

## Publishing Checklist (Public Safety)

Before publishing or sharing this skill:
1. **Sanitize Data**: Clear `nutrition/daily_macros.json` by setting it to `[]`.
2. **Sanitize Mirror**: Clear `canvas/offline_data.js` to match the empty state: `window.__OFFLINE_DAILY_MACROS = [];`.
3. **Check Insights**: Clear `nutrition/insights.json` or reset to template tips.
4. **Remove Personal Notes**: Scrub `nutrition/targets.json` and `memory/` of any sensitive info.
5. **Verify Assets**: Ensure no private images or documents are in the `assets/` folder.
