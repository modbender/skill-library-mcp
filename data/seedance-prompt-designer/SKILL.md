---
name: seedance-prompt-designer
description: Intelligently analyzes user-provided multimodal assets and creative intent to generate optimal, structured video generation prompts for the Seedance 2.0 model.
version: 2.0.0
author: wells1137
tags: [video, generation, prompt, seedance, multimodal]
---

# Seedance Prompt Designer Skill

This skill transforms a user's scattered multimodal assets (images, videos, audio) and ambiguous creative intent into a structured, executable prompt for the Seedance 2.0 video generation model. It acts as an expert prompt engineer, ensuring the highest quality output from the underlying model.

## Core Workflow

This skill follows a strict three-phase workflow. The output of each phase is the input for the next.

| Phase | Goal | Key Actions | Output |
| :--- | :--- | :--- | :--- |
| **1. Recognition** | Understand user input | Parse intent, analyze assets, tag with atomic roles | `recognition_output.json` |
| **2. Mapping & Strategy** | Design an executable reference strategy | Determine optimal reference method (Text, Asset, Hybrid) | `strategy_output.json` |
| **3. Construction & Assembly** | Generate the final, complete prompt | Assemble text, append @-syntax, consult templates | `final_prompt.json` |

## Usage Example

**User Request:** "Make the Mona Lisa drink a Coke. I want it to feel cinematic, like a close-up shot."
*User uploads `monalisa.png` and `coke.png`*

**Agent's Internal Process:**
1.  **Recognition**: Identifies `action_intent` ("drink a Coke"), `style_intent` ("cinematic, close-up"), and tags `monalisa.png` as `Subject Identity` and `coke.png` as `Subject Identity-Object`.
2.  **Mapping & Strategy**: Decides to use `@monalisa` and `@coke` as asset references and the rest as text prompts.
3.  **Construction & Assembly**: Assembles the final prompt.

**Final Output:**
```json
{
  "final_prompt": "A cinematic close-up shot of a woman picking up a bottle of Coke and taking a sip. The scene is lit with dramatic, high-contrast lighting. Use @monalisa as the subject reference, and the object appearing in the video is @coke.",
  "recommended_parameters": {
    "duration": 8,
    "aspect_ratio": "16:9"
  }
}
```

## Knowledge Base

This skill relies on an internal knowledge base to make informed decisions. The agent MUST consult these files during execution.

- **`/references/atomic_element_mapping.md`**: **Core Knowledge**. Contains the "Asset Type -> Atomic Element" and "Atomic Element -> Optimal Reference Method" mapping tables. **Must be consulted** during Phase 1 and Phase 2.
- **`/references/seedance_syntax_guide.md`**: Seedance 2.0 "@asset_name" syntax reference. **Must be consulted** during Phase 3 to ensure correct syntax generation.
- **`/references/prompt_templates.md`**: Advanced prompt templates for different genres (e.g., Cinematic, Product Showcase, Narrative). Optional consultation during Phase 3 for stylistic enhancement.
