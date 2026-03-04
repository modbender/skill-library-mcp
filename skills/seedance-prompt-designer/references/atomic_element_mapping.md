# Atomic Element Mapping Knowledge Base

This document provides the core logic for the Seedance Prompt Designer skill. It contains two critical mapping tables.

## Table 1: Asset Type -> Potential Atomic Elements

This table maps the type of user-uploaded asset to the most likely atomic element roles it can play in video generation. The skill should use this table in **Phase 1** to analyze uploaded assets.

| Asset Type (Heuristic) | Potential Atomic Element(s) |
| :--- | :--- |
| Image with a clear human/character face | `主体身份` (Subject Identity), `美学风格` (Aesthetic Style) |
| Image of an object/product | `主体身份-物体` (Subject Identity - Object) |
| Image of a landscape/environment | `场景环境` (Scene Environment), `美学风格` (Aesthetic Style) |
| Image with strong artistic style (e.g., painting, sketch) | `美学风格` (Aesthetic Style) |
| Image with clear compositional structure | `构图布局` (Composition/Layout) |
| Video with a character performing an action | `主体运动` (Subject Motion), `主体身份` (Subject Identity) |
| Video with significant camera movement | `镜头语言` (Camera Language) |
| Video with prominent visual effects | `视觉特效` (Visual Effects) |
| Audio file with speech | `语音 (音色)` (Voice - Timbre) |
| Audio file with music | `非语音 (音乐)` (Non-speech - Music) |
| Audio file with sound effects | `非语音 (音效)` (Non-speech - Sound Effect) |

## Table 2: Atomic Element -> Optimal Reference Method

This table defines the best way to reference each atomic element when constructing the prompt. The skill must use this table in **Phase 2** to design the reference strategy.

| Atomic Element | Optimal Method | Rationale |
| :--- | :--- | :--- |
| **主体身份** (Subject Identity) | **Asset** | High information density. Must use a reference image. |
| **场景环境** (Scene Environment) | **Hybrid** | Use an asset for the base, and text to modify details (e.g., weather). |
| **美学风格** (Aesthetic Style) | **Hybrid** | Use an asset to define the style, and text to specify its application. |
| **构图布局** (Composition/Layout) | **Asset** | Purely visual. Must be controlled by a keyframe image. |
| **主体运动** (Subject Motion) | **Hybrid** | Simple, describable actions use text. Complex, unique motions require a reference video. |
| **镜头语言** (Camera Language) | **Text** | Standardized cinematic language. Text is clearer and more direct. |
| **视觉特效** (Visual Effects) | **Text** | Most effects are describable. Only very unique effects need a reference video. |
| **语音 (音色)** (Voice - Timbre) | **Asset** | Unique biometric signature. Must use an audio sample. |
| **语音 (表演)** (Voice - Performance) | **Text** | Performance details (speed, tone, emotion) are best controlled by text/SSML. |
| **非语音 (音效/音乐)** (Non-speech) | **Asset** | Unique sounds/melodies must be provided as an asset. |
| **多镜头组合** (Multi-shot) | **Text** | Structural information is best defined by structured text (e.g., `multi_prompt`). |
| **节奏** (Pacing) | **Text** | Temporal control is best defined by text parameters. |
| **故事逻辑** (Story Logic) | **Text** | Abstract concepts can only be guided by text prompts. |
