# 🎯 Character & Environment Consistency Example

This example shows how to use the consistency system to ensure your characters, voices, and environments stay consistent across all generated content.

## The Problem

Without consistency:
- ❌ Kutil looks different in every shot
- ❌ Characters wear modern clothes in Ramayana era
- ❌ Buildings look like modern architecture
- ❌ Characters sound different in each scene

With consistency:
- ✅ Kutil always has purple fur, small horns, golden eyes
- ✅ Everyone wears era-appropriate clothing (dhotis, sarees, no glasses!)
- ✅ Architecture is stone temples and mud huts
- ✅ Each character has a distinct, consistent voice

## Step-by-Step Setup

### Step 1: Create Context with Consistency

```typescript
const skill = agent.tools['cinematic-script-writer'];

// First, create your base context
const kutilContext = await skill.createContext(
  "Kutil - The Cursed Rakshasa",
  "A lovable rakshasa's misadventures",
  [
    {
      name: "Kutil",
      description: "A small, cute rakshasa with purple fur",
      personality: "Mischievous, determined, secretly kind",
      appearance: "Purple fluffy fur, small curved horns, big expressive golden eyes",
      role: "protagonist",
      backstory: "Cursed by Saint Vardhan - bad deeds become good",
      specialTraits: ["Curse of unintended goodness", "Loves sweets"]
    },
    {
      name: "Saint Vardhan",
      description: "An ancient wise sage",
      personality: "Wise, patient, mischievous sense of humor",
      appearance: "Long white beard with flowers, saffron robes, peaceful aura",
      role: "supporting"
    },
    {
      name: "Maya",
      description: "A clever village girl",
      personality: "Intelligent, brave, quick-witted",
      appearance: "Young girl in simple village cotton clothes, curious eyes",
      role: "supporting"
    }
  ],
  "Ramayana Era",
  "Ancient India - Treta Yuga",
  "Lanka and surrounding villages",
  "short",
  "comedy",
  "All ages",
  "Stylized 3D animation with Indian art influences"
);

// Now setup consistency guides
const { guides } = await skill.setupContextWithConsistency(
  kutilContext,
  {
    // Detailed visual descriptions for each character
    [kutilContext.characters[0].id]: `
      Kutil is a small cute rakshasa (mythical being) with:
      - Fluffy purple fur covering entire body
      - Two small curved horns on head (cream colored tips)
      - Large round golden eyes with black pupils
      - Small fangs visible when smiling
      - Pointed ears with pink insides
      - Short tail with purple fur
      - About 3 feet tall, chibi proportions
      - Expressive face showing emotions clearly
    `,
    [kutilContext.characters[1].id]: `
      Saint Vardhan is an elderly sage with:
      - Long flowing white beard with flowers woven in
      - Kind wrinkled face with twinkling blue eyes
      - Saffron/orange traditional robes
      - Wooden staff with carvings
      - Peaceful glowing aura
      - Barefoot
    `,
    [kutilContext.characters[2].id]: `
      Maya is a young village girl with:
      - Dark brown hair in simple braid
      - Brown eyes full of curiosity
      - Simple white cotton saree/dress
      - Barefoot
      - Carries a basket
      - Around 10 years old
    `
  }
);

console.log("✅ Consistency guides created!");
console.log("Character References:", Object.keys(guides.characters));
console.log("Voice Profiles:", Object.keys(guides.voices));
console.log("Environment Guide:", guides.environment.era);
```

### Step 2: View Consistency Guides

```typescript
// Get Kutil's character reference
const kutilRef = skill.getCharacterReference(kutilContext.characters[0].id);
console.log("Kutil's Reference Sheet:", {
  baseDescription: kutilRef.visual.baseDescription,
  signatureColor: kutilRef.visual.colorPalette.signature,
  keyFeatures: kutilRef.visual.features,
  wardrobe: kutilRef.wardrobe.defaultOutfit.description
});

// Get voice profile
const kutilVoice = skill.getVoiceProfile(kutilContext.characters[0].id);
console.log("Kutil's Voice:", {
  pitch: kutilVoice.speech.pitch,
  catchphrases: kutilVoice.language.catchphrases,
  examples: kutilVoice.examples
});

// Get environment guide
const envGuide = skill.getEnvironmentGuide(kutilContext.id);
console.log("Environment Rules:", {
  era: envGuide.eraSpecs.name,
  forbiddenItems: envGuide.eraSpecs.anachronismsForbidden.slice(0, 5),
  architecture: envGuide.architecture.buildingStyles.map(b => b.type),
  clothingMaterials: envGuide.clothing.materials
});
```

### Step 3: Build Consistent Image Prompts

```typescript
// Build prompts with full consistency
const prompts = skill.buildConsistentPrompts({
  characterIds: [kutilContext.characters[0].id],  // Kutil
  contextId: kutilContext.id,
  shotType: 'close-up',
  cameraAngle: 'low-angle',
  cameraMovement: 'static',
  lighting: 'golden-hour',
  mood: 'determined',
  action: 'trying to look evil but looking cute',
  timeOfDay: 'afternoon',
  includeEnvironment: true
});

console.log("=== IMAGE PROMPT ===");
console.log(prompts.imagePrompt);
// Output: close-up shot, low-angle camera angle, Kutil is a small cute rakshasa with purple fluffy fur, 
// small curved horns, large round golden eyes, purple, golden, fluffy, wearing simple traditional dhoti, 
// Ramayana Era setting, Lanka and surrounding villages, stone temple architecture, golden-hour lighting, 
// afternoon light, determined mood, Stylized 3D animation with Indian art influences, 
// consistent character design, same character across frames, highly detailed, 8k, cinematic composition

console.log("\n=== NEGATIVE PROMPT ===");
console.log(prompts.negativePrompt);
// Output: inconsistent character design, different character in each frame, changing features, 
// wrong eye color, wrong hair color, modern clothing, glasses, watches, plastic, synthetic fabrics, 
// modern furniture, blurry, low quality, deformed...

console.log("\n=== CONSISTENCY NOTES ===");
console.log(prompts.consistencyNotes);

console.log("\n=== VALIDATION WARNINGS ===");
console.log(prompts.validationWarnings);
```

### Step 4: Generate Multiple Shots with Consistency

```typescript
// Generate a series of shots for the same scene
const shots = [
  {
    type: 'close-up',
    angle: 'low-angle',
    action: 'evil grin attempt',
    mood: 'mischievous'
  },
  {
    type: 'medium',
    angle: 'eye-level', 
    action: 'confused expression',
    mood: 'confused'
  },
  {
    type: 'wide',
    angle: 'high-angle',
    action: 'accidentally helping villagers',
    mood: 'heroic-irony'
  }
];

const shotPrompts = shots.map(shot => {
  return skill.buildConsistentPrompts({
    characterIds: [kutilContext.characters[0].id],
    contextId: kutilContext.id,
    shotType: shot.type,
    cameraAngle: shot.angle,
    cameraMovement: 'static',
    lighting: 'golden-hour',
    mood: shot.mood,
    action: shot.action
  });
});

// All prompts will have the SAME character description!
// Kutil will look consistent across all shots
```

### Step 5: Voice Consistency in Dialogue

```typescript
// Get voice guidelines for writing dialogue
const kutilVoiceGuide = skill.generateVoiceGuidelines(kutilContext.characters[0].id);
console.log(kutilVoiceGuide);

// Output:
// Voice Profile for Kutil:
// - Pitch: high, Speed: fast, Volume: normal
// - Vocabulary: simple, Formality: casual
// - Catchphrases: "I am evil!", "Curse you!"
// - Speech Examples:
//   - Greeting: "Tremble before me!"
//   - Question: "What do you mean I'm helping?"
//   - Exclamation: "No, not again!"

// Use this to write consistent dialogue
const dialogue = {
  kutil: [
    {
      text: "Today I shall steal all the sweets! Muahaha!",
      tone: "trying-to-be-evil",
      notes: "High pitch, fast speech, overconfident"
    },
    {
      text: "Wait... why am I arranging them beautifully?",
      tone: "confused",
      notes: "Speed slows down, pitch raises"
    },
    {
      text: "Curse you, Saint Vardhan!",
      tone: "frustrated",
      notes: "Use catchphrase"
    }
  ]
};
```

### Step 6: Validate for Anachronisms

```typescript
// Test a prompt that might have issues
const badPrompt = "Kutil wearing sunglasses and holding a smartphone in a stone temple";

const validation = skill.validatePrompt(
  badPrompt,
  [kutilContext.characters[0].id],
  kutilContext.id
);

console.log(validation);
// Output:
// {
//   valid: false,
//   errors: [
//     'Anachronism detected: "glasses" does not belong in Ramayana Era',
//     'Anachronism detected: "smartphone" does not belong in Ramayana Era'
//   ],
//   warnings: [...],
//   suggestions: [
//     'Consider using era-appropriate material: cotton',
//     'Consider using era-appropriate material: silk'
//   ]
// }

// Fix the prompt
const goodPrompt = "Kutil in traditional dhoti holding a clay pot in a stone temple";
const goodValidation = skill.validatePrompt(
  goodPrompt,
  [kutilContext.characters[0].id],
  kutilContext.id
);
console.log(goodValidation.valid); // true
```

### Step 7: Complete Workflow

```typescript
async function createConsistentScene(contextId: string, sceneNumber: number) {
  const skill = agent.tools['cinematic-script-writer'];
  const context = await skill.getContext(contextId);
  
  // Get all consistency data
  const characterRefs = {};
  const voiceProfiles = {};
  
  for (const char of context.characters) {
    characterRefs[char.id] = skill.getCharacterReference(char.id);
    voiceProfiles[char.id] = skill.getVoiceProfile(char.id);
  }
  
  const envGuide = skill.getEnvironmentGuide(contextId);
  
  // Define shots for the scene
  const shots = [
    {
      number: 1,
      description: "Kutil plans mischief",
      type: "close-up",
      angle: "low-angle",
      characters: [context.characters[0].id],
      action: "evil plotting expression",
      lighting: "dramatic-shadows"
    },
    {
      number: 2,
      description: "Curse activates",
      type: "wide",
      angle: "high-angle",
      characters: [context.characters[0].id],
      action: "magical transformation",
      lighting: "golden-magic-light"
    },
    {
      number: 3,
      description: "Villagers celebrate",
      type: "medium",
      angle: "eye-level",
      characters: context.characters.map(c => c.id),
      action: "celebration scene",
      lighting: "warm-sunlight"
    }
  ];
  
  // Generate consistent prompts for all shots
  const shotPrompts = shots.map(shot => {
    return {
      ...shot,
      prompts: skill.buildConsistentPrompts({
        characterIds: shot.characters,
        contextId,
        shotType: shot.type,
        cameraAngle: shot.angle,
        cameraMovement: 'static',
        lighting: shot.lighting,
        mood: 'comedy',
        action: shot.action
      })
    };
  });
  
  return {
    scene: sceneNumber,
    context,
    characterRefs,
    voiceProfiles,
    environment: envGuide,
    shots: shotPrompts
  };
}

// Use it
const scene1 = await createConsistentScene(kutilContext.id, 1);

// scene1 now contains:
// - Character references ensuring visual consistency
// - Voice profiles ensuring dialogue consistency  
// - Environment guide ensuring era-appropriate elements
// - Shot prompts with consistency built-in
```

## Consistency Features Summary

### Character Consistency
- ✅ Reference sheets with detailed visual breakdown
- ✅ Color palette enforcement
- ✅ Wardrobe variations for different situations
- ✅ Key features tracking (eyes, hair, build)
- ✅ Style keywords for AI generation

### Voice Consistency  
- ✅ Pitch, speed, volume profiles
- ✅ Vocabulary and formality levels
- ✅ Catchphrases and recurring phrases
- ✅ Emotional variations
- ✅ Speech examples

### Environment Consistency
- ✅ Era-appropriate architecture
- ✅ Period-accurate clothing materials
- ✅ Forbidden anachronism detection
- ✅ Props and objects validation
- ✅ Society and customs guidelines

### Validation
- ✅ Anachronism detection
- ✅ Era-accurate material suggestions
- ✅ Consistency warnings
- ✅ Prompt corrections

## Example Output

```typescript
// Generated prompt for Kutil
{
  imagePrompt: "close-up shot, low-angle camera angle, Kutil is a small cute rakshasa with fluffy purple fur covering entire body, two small curved horns on head cream colored tips, large round golden eyes with black pupils, small fangs visible when smiling, pointed ears with pink insides, short tail with purple fur, about 3 feet tall chibi proportions, expressive face, purple golden fluffy, wearing simple traditional cotton dhoti, Ramayana Era setting, Lanka and surrounding villages, stone temple architecture with intricate carvings, mud huts with thatched roofs, golden-hour lighting, afternoon light, mischievous mood, Stylized 3D animation with Indian art influences, consistent character design, same character across frames, highly detailed, 8k, cinematic composition",
  
  negativePrompt: "inconsistent character design, different character in each frame, changing features, wrong eye color, wrong hair color, anatomical errors, modern clothing, glasses, watches, plastic, synthetic fabrics, modern furniture, modern buildings, electric lights, metal utensils, blurry, low quality, deformed, mutated, extra limbs, missing limbs, bad anatomy",
  
  consistencyNotes: "=== CHARACTER CONSISTENCY ===\nKutil:\n  Base: Kutil is a small cute rakshasa...\n  Signature Colors: purple, golden\n  Key Features: golden eyes, purple fluffy hair, small build\n  Wardrobe: Simple cotton dhoti...\n\n=== ENVIRONMENT CONSISTENCY ===\nEra: Ramayana Era\nLocation: Lanka and surrounding villages\nArchitecture: Temple, Palace, Hut, Market\nForbidden Elements: glasses, watches, plastic, synthetic fabrics...",
  
  validationWarnings: []
}
```

This ensures Kutil looks the same in every shot, wears appropriate clothing, and stays true to the Ramayana era setting! 🎬
