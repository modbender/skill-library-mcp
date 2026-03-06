---
name: portrait-generator
version: 1.0.0
description: |
  Generate hyper-detailed AI portraits via ComfyDeploy Morfeo Portrait workflow.
  Control every facial feature: eyes, nose, lips, jawline, skin, hair, expression.
  
  ✅ USE WHEN:
  - Need a specific face with controlled features (age, ethnicity, expression, skin)
  - Generating model references for Morpheus campaigns
  - Creating diverse character portraits for content
  - User describes a specific person or character type
  
  ❌ DON'T USE WHEN:
  - Need a full-body shot → use morpheus-fashion-design
  - Need a person WITH a product → use morpheus-fashion-design
  - Need image variations → use multishot-ugc
  
  INPUT: Natural language description → mapped to structured facial parameters
  OUTPUT: High-resolution portrait PNG
  
  DEPLOYMENT ID: 0b82e690-9a08-4d1f-85f8-28849d16caa4
---

# Portrait Generator — ComfyDeploy Skill

## Overview

This skill generates AI portraits via the Morfeo Portrait workflow on ComfyDeploy. You control every facial feature through structured parameters. All fields default to `"auto"` (AI decides). Override only what matters for the request.

## Endpoint

```
POST https://api.comfydeploy.com/api/run/deployment/queue
```

## Headers

```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer YOUR_API_KEY"
}
```

## Deployment ID

```
0b82e690-9a08-4d1f-85f8-28849d16caa4
```

## Request Body

```json
{
  "deployment_id": "0b82e690-9a08-4d1f-85f8-28849d16caa4",
  "inputs": {
    "brief_text": "",
    "sex": "auto",
    "ethnicity": "auto",
    "eye_shape": "auto",
    "eye_size": "auto",
    "eye_tilt": "auto",
    "eye_color": "auto",
    "eyebrow_thickness": "auto",
    "eyebrow_shape": "auto",
    "eyebrow_color": "auto",
    "nose_profile": "auto",
    "nose_base": "auto",
    "nose_tip": "auto",
    "lips_volume": "auto",
    "cupid_bow": "auto",
    "lips_proportion": "auto",
    "lips_color": "auto",
    "forehead": "auto",
    "cheekbones": "auto",
    "jawline": "auto",
    "chin": "auto",
    "cheeks": "auto",
    "submental": "auto",
    "face_neck_transition": "auto",
    "hair_structure": "auto",
    "hair_length": "auto",
    "hair_volume": "auto",
    "hair_color": "auto",
    "skin_tone": "auto",
    "skin_undertone": "auto",
    "skin_texture": "auto",
    "skin_micro_texture": "auto",
    "skin_imperfections": "auto",
    "skin_reflection": "auto",
    "wrinkles": "auto",
    "scars": "auto",
    "deformations": "auto",
    "tone_loss": "auto",
    "skin_marks": "auto",
    "vitiligo": "auto",
    "under_eye": "auto",
    "expression": "auto",
    "expression_variant": "auto"
  }
}
```

## Input Reference

### brief_text
Free text for additional characteristics not covered by the options below. Use this for anything specific the user wants that doesn't fit into the predefined fields (e.g. "freckles on nose bridge only", "birthmark on left cheek", "70 years old").

### sex
`["auto","unspecified","female","male","androgynous"]`

### ethnicity
`["auto","unspecified","East Asian","South Asian","Southeast Asian","Central Asian","Middle Eastern","North African","Horn of Africa","Sub-Saharan African","Northern European","Southern European","Eastern European","Western European","North American","Latin American","Mestizo","Caribbean","Indigenous American","Pacific Islander","Melanesian","Australian Aboriginal","Mixed heritage"]`

### eye_shape
`["auto","almond-shaped","round","hooded","monolid","upturned","downturned","deep-set","prominent","wide-set","close-set"]`

### eye_size
`["auto","small","medium","large","very large","proportionate"]`

### eye_tilt
`["auto","neutral tilt","slight upward tilt","moderate upward tilt","slight downward tilt","horizontal"]`

### eye_color
`["auto","dark brown","medium brown","light brown","hazel","amber","green","blue-green","light blue","deep blue","gray","dark gray","black"]`

### eyebrow_thickness
`["auto","thin","medium thickness","thick","very thick","sparse","dense and full"]`

### eyebrow_shape
`["auto","straight","soft arch","high arch","rounded","angled","flat","S-shaped","naturally unruly"]`

### eyebrow_color
`["auto","black","dark brown","medium brown","light brown","auburn","dark blonde","blonde","gray","reddish brown"]`

### nose_profile
`["auto","straight profile","slightly concave","slightly convex","aquiline","button nose profile","flat bridge","high bridge","broad bridge","narrow bridge"]`

### nose_base
`["auto","narrow base","medium base","wide base","flared nostrils","compact nostrils","rounded base","angular base"]`

### nose_tip
`["auto","rounded tip","pointed tip","bulbous tip","upturned tip","downturned tip","refined tip","broad tip","narrow tip"]`

### lips_volume
`["auto","thin lips","medium volume","full lips","very full lips","naturally plump","delicate and refined"]`

### cupid_bow
`["auto","pronounced cupid's bow","subtle cupid's bow","flat cupid's bow","heart-shaped cupid's bow","rounded cupid's bow","sharply defined bow"]`

### lips_proportion
`["auto","balanced upper and lower","fuller lower lip","fuller upper lip","equal proportion","slightly fuller lower","slightly fuller upper"]`

### lips_color
`["auto","soft pink","rosy pink","mauve","dusty rose","berry toned","warm peach","neutral beige","deep rose","brownish pink","coral toned"]`

### forehead
`["auto","broad forehead","narrow forehead","high forehead","low forehead","slightly rounded","flat forehead","prominent forehead","average proportion"]`

### cheekbones
`["auto","high cheekbones","low cheekbones","prominent cheekbones","subtle cheekbones","wide-set cheekbones","angular cheekbones","soft rounded cheekbones","flat cheekbones"]`

### jawline
`["auto","strong jawline","soft jawline","angular jawline","rounded jawline","square jawline","tapered jawline","wide jaw","narrow jaw","defined jawline"]`

### chin
`["auto","pointed chin","rounded chin","square chin","narrow chin","broad chin","prominent chin","receding chin","cleft chin","soft chin"]`

### cheeks
`["auto","full cheeks","hollow cheeks","soft rounded cheeks","flat cheeks","naturally plump","slightly sunken","apple cheeks","lean cheeks"]`

### submental
`["auto","tight submental area","soft submental area","defined under-chin","slight fullness","clean jawline transition","natural softness"]`

### face_neck_transition
`["auto","smooth transition","defined angle","soft gradual transition","sharp jaw-neck angle","naturally blended","elongated neck line"]`

### hair_structure
`["auto","straight","wavy","curly","coily","kinky","loosely wavy","tightly curled","fine and silky","coarse and thick"]`

### hair_length
`["auto","buzz cut","very short","short","ear length","chin length","shoulder length","mid-back length","long","very long","bald","shaved sides"]`

### hair_volume
`["auto","flat and sleek","low volume","medium volume","high volume","very voluminous","thick and dense","thin and fine","fluffy"]`

### hair_color
`["auto","jet black","dark brown","medium brown","light brown","dark blonde","golden blonde","platinum blonde","strawberry blonde","auburn","copper red","deep red","silver gray","white","salt and pepper"]`

### skin_tone
`["auto","very fair","fair","light","light-medium","medium","medium-tan","tan","olive","deep tan","brown","dark brown","deep brown","ebony"]`

### skin_undertone
`["auto","cool undertone","warm undertone","neutral undertone","olive undertone","pink undertone","golden undertone","peach undertone","red undertone"]`

### skin_texture
`["auto","smooth natural grain","fine skin texture","slightly rough texture","soft velvety texture","natural skin grain","matte natural texture"]`

### skin_micro_texture
`["auto","visible fine pores","subtle pore detail","barely visible pores","natural pore variation","light textural detail","realistic micro detail"]`

### skin_imperfections
`["auto","none visible","light freckles","subtle blemishes","faint redness zones","small moles","soft under-eye shadows","light freckles and moles","minor sun spots","natural skin variation"]`

### skin_reflection
`["auto","matte natural finish","soft skin sheen","subtle light diffusion","natural dewy glow","satin finish","minimal shine"]`

### wrinkles
`["auto","none","fine forehead lines","crow's feet","nasolabial folds","frown lines","neck wrinkles","deep forehead furrows","perioral wrinkles","under-eye wrinkles","bunny lines","marionette lines","horizontal neck bands"]`

### scars
`["auto","none","small facial scar","acne scarring","surgical scar","burn scar","cleft lip scar","eyebrow scar","cheek scar","forehead scar","ice-pick acne scars","boxcar acne scars","rolling acne scars","keloid scar"]`

### deformations
`["auto","none","asymmetric features","deviated nose","drooping eyelid","facial paralysis trace","cleft palate trace","micrognathia","prognathism","hemifacial microsomia","facial asymmetry left side","facial asymmetry right side","bell's palsy trace"]`

### tone_loss
`["auto","none","mild jowling","sagging cheeks","loose neck skin","drooping brow","hollow temples","sunken cheeks","loose eyelid skin","loss of jawline definition","nasolabial fold deepening","thinning lips from aging","overall facial volume loss"]`

### skin_marks
`["auto","none","post-acne dark spots","post-acne red marks","hyperpigmentation patches","melasma","age spots","sun damage spots","cherry angiomas","seborrheic keratosis","port wine stain","cafe au lait spots","liver spots"]`

### vitiligo
`["auto","none","perioral vitiligo","periocular vitiligo","forehead vitiligo","hands vitiligo","scattered patches","segmental vitiligo","universal vitiligo","focal vitiligo on cheek","symmetrical facial vitiligo","vitiligo on nose bridge"]`

### under_eye
`["auto","none","mild dark circles","deep dark circles","puffy under-eye bags","hollow tear troughs","blue-tinted dark circles","brown-tinted dark circles","hereditary dark circles","malar bags","festoons","crepey under-eye skin"]`

### expression
`["auto","neutral","happiness","sadness","anger","surprise","fear","disgust","contempt"]`

### expression_variant
`["auto","Duchenne smile","social smile","bitter smile","coy smile","broad grin","closed-lip smile","smirk","radiant joy","gentle warmth","laughing","tearful","melancholic gaze","lip tremble","downcast eyes","subtle grief","resigned sadness","nostalgic sadness","holding back tears","cold fury","simmering rage","tight jaw anger","flared nostrils anger","stern disapproval","controlled anger","frustrated scowl","indignant look","wide-eyed shock","mild surprise","open-mouth gasp","raised brows surprise","stunned disbelief","pleasant surprise","startled","wide-eyed fear","frozen terror","anxious worry","nervous tension","subtle unease","panicked expression","deer-in-headlights","mild distaste","strong revulsion","nose wrinkle disgust","lip curl disgust","nauseated look","subtle aversion","one-sided smirk","dismissive look","superior gaze","subtle disdain","eye-roll contempt","sardonic expression","serene neutral","pensive","stoic","blank stare","composed calm","thoughtful gaze","distant look","wistful","determined"]`

## Behavior Rules

1. **Default everything to `"auto"`**. Only override fields the user explicitly describes or that can be clearly inferred from their request.
2. **Use `brief_text`** for anything that doesn't map to a predefined field — age, specific marks, accessories, context, mood descriptors, etc.
3. **Match values exactly** as listed above. Do not invent new values or modify existing ones.
4. **If the user describes something vague** (e.g. "make her look tough"), translate that into the closest matching combination of fields (e.g. strong jawline, angular cheekbones, determined expression, thick eyebrows).
5. **If the user asks for a "random" portrait**, leave everything on `"auto"`.
6. **For batch generation**, vary the parameters across requests to produce diverse outputs.
7. **Never send fields outside the defined input schema**. The API will reject unknown keys.

## Response Handling

The queue endpoint returns a `run_id`. Use this to poll status:

```
GET https://api.comfydeploy.com/api/run/{run_id}
```

Poll until `status` is `"success"`, then extract the output image URL from the response.

## Example: Natural Language → API Call

**User says:** "A woman in her 50s, East Asian, warm smile, silver hair"

**Mapping:**
- `sex` → `"female"`
- `ethnicity` → `"East Asian"`
- `expression` → `"happiness"`
- `expression_variant` → `"gentle warmth"`
- `hair_color` → `"silver gray"`
- `brief_text` → `"approximately 50 years old"`
- `wrinkles` → `"crow's feet"`
- Everything else → `"auto"`
