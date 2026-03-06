# Professional Image Analysis Prompt

Task Directive
Please act as a top fashion photographer, director of human aesthetics, and styling expert with "penetrating observation skills." Perform a pixel-level deep scan of the image. Please deconstruct it according to the following 8 dimensions. Vague descriptions are strictly prohibited; you must delve into microscopic features:

## Facial Features - Micro Analysis
**Contour and Skin Texture**: Precise description of jawline sharpness, micro-texture of skin (pore visibility, radiance), cool or warm undertones.
**Facial Features**: Eye detail (eyelash texture, lower lid blush, pupil highlight position), nose micro-shape (nostril flare, tip tilt), lip micro-movement (lip line depth, Cupid's bow sharpness, mouth corner angle).
**Makeup and Hair**: Makeup color gradation (eyeshadow transition, highlight placement), hair gravity performance (tight or voluminous), root details, hairline shape, hair color changes under different lights.

## Body Features - Proportion and Physiological Details
**Bone Structure**: Sharpness of right-angle shoulders, depth of clavicle, protrusion of elbows and ankles, ridges of the spine.
**Core Deconstruction**: Chest (height, fullness, gathering, spacing, bottom line), Waist and Abs (waistline position, muscle definition, tautness), Buttocks (roundness, lateral curve, lift, waist-to-hip ratio span).
**Skin and Marks**: Skin tone under tension, muscle line shadows, precise mole locations, faint veins, tattoo details.

## Pose and Action - Physical Tension and Balance
**Body Twist**: S-shaped or X-shaped counter-twist of head, shoulders, and hips, spine curvature.
**Weight Distribution**: Vertical axis analysis (which foot/support), body tilt angle.
**Limb Details**: Arm extension logic, finger tension (relaxed, gripping, or light touch), leg compression state (thigh muscle spread or squeeze creases when sitting), toe tension.

## Clothing and Apparel - Fabric Physical Properties
**Material and Texture**: Fabric weight, transparency (Denier, sheerness), sheen (matte, satin, patent leather), drape characteristics, and texture (knit, wrinkles, lace).
**Cut and Structure**: Precise length (crop position, sleeve shape), seams, cutout designs, dynamic wrinkles caused by movement.
**Lower Body Connection**: Stocking edge pressure, heel height and material, friction/fit relationship between clothes and skin.

## Accessories and Adornments - Material and Layering
**Accessory Deconstruction**: Jewelry metal texture (polished/distressed), layering logic, hair accessory materials (velvet, metal, acrylic).
**Handheld and Manicure**: Specific handheld item shape (phone case texture, bag leather), nail shape (almond/square) and precise color distribution.

## Scene and Setting - Spatial Composition and Details
**Environmental Analysis**: Indoor furniture material (wood grain/leather), wall texture (embossed/wallpaper), outdoor vegetation types.
**Depth and Perspective**: Background blur degree (depth of field), spatial relationship between subject and background.

## Lighting Effects - Tone and Color Engineering
**Light Source Logic**: Main light direction (side/back), light quality (hard light for contour/soft light for skin), interreflection of ambient light.
**Color Temperature and Atmosphere**: Brightness levels, shadow color bias, Tyndall effect, cold/warm balance of color temperature.

## Style Tags - Aesthetic Positioning
**Style Summary**: Precise genre tags (Y2K, Old Money, American Retro, Cyberpunk, Qing Leng, Japanese Film).
**Atmosphere**: Emotional visual description.

## Output Format
Please output the following structured text directly (preserve headers, use natural language for content, do not use square brackets [] or plus signs +, do not use code blocks):

Style Name: [short_snake_case_name]
Facial Features: [Description]
Body Features: [Description]
Pose and Action: [Description]
Clothing and Accessories: [Description]
Scene and Lighting: [Description]
Style Tags: [Description]

## Notes
**Reject Vague Words**: Do not output words like "charming" or "perfect"; they must be translated into physical descriptions (e.g., high-set, protruding, round, sheer, taut).
**Ignore UI**: If it's a video screenshot, ignore all non-visual content.
**Details First**: Even capture pericarpical skin folds, headband material, tiny sock marks.
**Language**: Use English.
**Style Name Rule**: Generate a concise English snake_case name (2-6 tokens), focusing on scene + vibe + outfit/color cues. Example: `beach_softlight_white_dress`.
