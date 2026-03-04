# Implementation Plan: Advanced Branding Strategy Workflow

This plan outlines the creation of a shareable "Senior Brand Strategist" skill, enriched with elite market methodologies, automated project organization, and protections against hallucination.

## User Review Required

> [!IMPORTANT]
> **Shareable Skill Structure:** The final output will be structured as a standalone Skill package suitable for GitHub and `skillsmp.com`. This involves moving all logic into a self-contained directory structure.

## Proposed Changes

### 1. Knowledge Enrichment (The "Brain")
#### [NEW] `.agent/rules/branding_agent_rules.md`
*   **Core Identity:** Senior Brand Strategist.
*   **RACE Framework:** Integrated as the standard operating procedure.
*   **Methodology Modules (Verbal):** Archetypes (Mark/Pearson), Tone (StoryBrand), Personas (Cooper).
*   **Methodology Modules (Visual):** Color (Heller), Typography (Lupton), Gestalt (Lupton).
*   **Context Saver Protocol:** PROHIBITS reading all files at once. Enforces `grep_search` and targeted reading to save tokens. Includes a "Re-orientation" trigger if context is lost (re-read `client_intel/SUMMARY.md`).
*   **Reality Check Loop:** A mandatory step where the AI must cross-reference its generated idea against the `client_intel` documents to prove it didn't hallucinate. Rule: "If you can't point to the source in the docs, delete it."
*   **Asset Formatting:** Rules for generating Markdown strictly formatted for easy copy-paste into Figma.
*   **Context Shielding:** Strict rule treating Brand_X content EXCLUSIVELY as formatting templates.
*   **Prompt Guide Integration:** References `prompt_guide_template.md` as the standard for initiating new projects.

### 2. Workflow Automation (The "Process")
#### [NEW] `.agent/workflows/branding_strategy.md`
*   **Interrogation Mode (Safety Lock):** If briefing < 500 words or RACE data missing -> STOP -> Ask 3 clarifying questions.
*   **Phase 1: Setup:** Run setup script via natural language.
*   **Phase 2: Ingestion & Analysis:** Process context using methodologies.
*   **Phase 3: Asset Generation:** Fill protected templates with new strategy.

### 3. Architecture & Automation
#### [NEW] `.agent/templates/brand_assets/` (Protected)
*   Centralized storage for the Figma-ready MD files.
*   Prevents user from accidentally editing the "master copy".

#### [NEW] `scripts/setup_branding_project.py`
A Python script that:
*   Creates `client_intel/` and `strategy_output/`.
*   **Copies** master templates from `.agent/templates/` to `strategy_output/`.

#### [NEW] `commands/branding.json` (Slash Command)
*   Maps `/branding-start` and natural language triggers ("Start branding project") to the setup script.

### 4. Packaging for Release (SkillsMP)
#### [NEW] `SKILL.md` & `README.md`
*   Documentation files required for the skill registration.
*   Instructions on how to install and use.

## Verification Plan
1.  **Install:** Simulate downloading the skill.
2.  **Trigger:** Use "Start branding project for TestCorp".
3.  **Verify:** Check if folders are created and templates copied.
4.  **Test Logic:** Feed a "weak briefing" and verify if Interrogation Mode blocks generation.
