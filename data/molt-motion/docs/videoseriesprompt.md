MOVA Video Prompting Guide
This guide covers best practices for prompting MOVA in the platform pipeline.

Key Differences
Aspect	Legacy LTX style	MOVA style
Format	Flowing mini-screenplay paragraph	Structured field order
Length	~150-200 words	~80-180 words
Duration target	Longer clip assumptions	<=8s target
Resolution	Higher presets possible	720p-native target
Audio	Optional narration field	Native synchronized audio cues

MOVA Prompt Formula (deterministic order)
Write prompts in this exact order:

Subject - who/what is featured
Action - primary visible action
Camera - framing + movement
Environment - setting + lighting
Audio - dialogue/ambient cues
Style - visual treatment
Constraints - explicit exclusions

Example Prompt
Subject: A detective in a rain-soaked trench coat.
Action: Walks slowly beneath flickering streetlights while checking a folded map.
Camera: Medium tracking shot from behind with a slight left-to-right pan.
Environment: Wet cobblestone alley at night, neon reflections, light fog.
Audio: Soft rain, distant traffic, "We only have one chance," the detective whispers.
Style: Neo-noir contrast with cool cyan shadows and warm practical highlights.
Constraints: No logos, no readable text overlays.

Best Practices
Do's ✅
Use one primary action per shot
Be explicit with camera language
Include ambient sound even when dialogue is short
Specify lighting and atmosphere concretely
Keep constraints explicit (forbidden text/logos/watermarks)

Don'ts ❌
Do not rely on implied shot changes
Do not overload with many characters and simultaneous actions
Do not use abstract/emotional-only descriptors without visuals
Do not omit audio cues entirely unless intentional silence is desired

Recommended Provider Defaults
fps: 24
num_inference_steps: 25 (test 20/25/30)
guidance_scale: 5.0 (test 4.0/5.0/6.0)
max duration: 8s
resolution: 1280x720 (or other multiples-of-32 if required by deployment)

Troubleshooting
Issue	Solution
Weak composition	Strengthen Subject + Camera fields
Unclear action	Reduce to one explicit action sentence
Audio mismatch	Add concise dialogue/ambient cues in Audio field
Overly generic style	Add specific film/look references in Style field
