# 🎬 Example: Kutil's Cursed Adventure

Complete workflow example for creating a comic video about Kutil, the cursed rakshasa.

## 📖 Story Premise

**Kutil** - A cute rakshasa from Lanka in Ramayana era, cursed by a saint that whenever he does something wrong, it transforms into something good.

## 🚀 Step-by-Step Usage

### Step 1: Create the Context

```typescript
const skill = agent.tools['cinematic-script-writer'];

const kutilContext = await skill.createContext(
  "Kutil - The Cursed Rakshasa",
  "A lovable rakshasa's misadventures where every bad deed turns into accidental heroism",
  [
    {
      name: "Kutil",
      description: "A small, cute rakshasa with purple fur, tiny horns, and big innocent eyes. Tries his best to be scary and evil but fails adorably.",
      personality: "Mischievous, determined, secretly kind-hearted, frustrated by his curse, optimistic",
      appearance: "Purple fluffy fur, small curved horns, big expressive golden eyes, wears traditional rakshasa attire but looks cute in it, small fangs that show when he smiles",
      role: "protagonist",
      backstory: "Once a fearsome rakshasa warrior, cursed by Saint Vardhan during a failed raid. Now whenever he attempts evil, it transforms into good deeds.",
      specialTraits: ["Curse of unintended goodness", "Shape-shifting (limited)", "Super strength (can't use for evil)", "Loves sweets", "Terrified of his own cuteness"]
    },
    {
      name: "Saint Vardhan",
      description: "An ancient sage with immense spiritual power",
      personality: "Wise, patient, sees good in everyone, has a mischievous sense of humor",
      appearance: "Long white beard with flowers in it, saffron robes, peaceful glowing aura, kind twinkling eyes",
      role: "supporting",
      backstory: "The sage who cursed Kutil, but actually sees it as a blessing in disguise. Occasionally appears to offer cryptic advice."
    },
    {
      name: "Maya",
      description: "A clever village girl who befriends Kutil",
      personality: "Intelligent, brave, quick-witted, protective of her friends",
      appearance: "Young girl in simple village clothes, curious eyes, always carries a basket",
      role: "supporting",
      backstory: "First human to see through Kutil's 'evil' act and recognize his kind heart. Acts as his moral compass."
    }
  ],
  "Ramayana Era",
  "Ancient India - Treta Yuga",
  "Lanka and surrounding villages/forests",
  "short",
  "comedy",
  "All ages, especially young adults who enjoy anime-style content",
  "Stylized 3D animation blending Indian miniature painting aesthetics with modern Pixar-style character design. Vibrant colors, expressive characters, detailed environments.",
  "Focus on visual comedy and slapstick. Emphasize the contrast between Kutil's evil intentions and the cute/good outcomes. Use bright, warm color palette."
);

console.log("✅ Context created:", kutilContext.id);
```

### Step 2: List Available Contexts

```typescript
// When you want to select a context later
const contexts = await skill.listContexts();
console.log("Your contexts:");
contexts.forEach((ctx, i) => {
  console.log(`${i + 1}. ${ctx.name} (Created: ${new Date(ctx.createdAt).toLocaleDateString()})`);
});
```

**Output:**
```
Your contexts:
1. Kutil - The Cursed Rakshasa (Created: 2/10/2026)
2. Warriors of Ancient Bharat (Created: 2/8/2026)
```

### Step 3: Generate Story Ideas

```typescript
// Select the context (user picks #1)
const selectedContextId = contexts[0].id;

// Generate ideas for a Diwali-themed story
const ideas = await skill.generateStoryIdeas(
  selectedContextId,
  3,              // Generate 3 ideas
  "Diwali festival"  // Theme
);

// Display ideas to user
ideas.forEach((idea, i) => {
  console.log(`\n${i + 1}. ${idea.title}`);
  console.log(`   ${idea.summary}`);
  console.log(`   Genre: ${idea.genre} | Duration: ~${idea.estimatedDuration}s`);
  console.log(`   Hook: ${idea.hook}`);
});
```

**Example Output:**
```
1. Kutil Tries to Steal the Diwali Sweets
   Kutil plans to raid the village's Diwali sweet preparations, but his curse turns every attempt into helping make the sweets even more delicious.
   Genre: Comedy | Duration: ~60s
   Hook: What happens when a monster tries to ruin Diwali but can only make it better?

2. The Accidental Lantern Hero
   Kutil attempts to blow out all the diyas in the village, but his breath creates magical floating lanterns that save a lost child.
   Genre: Comedy-Drama | Duration: ~75s
   Hook: This Diwali, even darkness brings light!

3. Kutil vs. The Firecracker
   Trying to scare the village with a loud firecracker, Kutil accidentally creates the most spectacular firework display ever seen.
   Genre: Action-Comedy | Duration: ~60s
   Hook: The villain who became the celebration!
```

### Step 4: Create Cinematic Script

```typescript
// User selects idea #1: "Kutil Tries to Steal the Diwali Sweets"
const selectedIdea = ideas[0];

const script = await skill.createCinematicScript(
  selectedContextId,
  selectedIdea.id,
  selectedIdea
);

console.log("🎬 Script created:", script.title);
```

### Step 5: Review the Generated Script

The script will include:

#### Hook Script
```typescript
script.hook = {
  text: "What happens when a monster tries to ruin Diwali but can only make it better?",
  duration: 3,
  visualDescription: "Quick cuts: Kutil sneaking → Kutil accidentally decorating → Confused cute face. Fast-paced, festive music.",
  impact: "Creates immediate curiosity about the comedic premise"
}
```

#### Scenes with Detailed Shots

**Scene 1: The Setup**
```typescript
scene.shots = [
  {
    shotNumber: 1,
    type: "establishing",
    cameraAngle: "high-angle",
    cameraMovement: "static",
    duration: 3,
    description: "Wide shot of Lanka village preparing for Diwali, colorful decorations everywhere",
    impact: "Establishes festive atmosphere and setting",
    imagePrompt: "Epic wide establishing shot of ancient Indian village during Diwali preparations, vibrant colors, rangoli patterns, diyas glowing, traditional architecture, golden hour lighting, highly detailed, 8k, stylized 3D animation with Indian art influences",
    videoPrompt: "Wide establishing shot of ancient village during Diwali, gentle camera drift, hundreds of diyas twinkling, smoke from firecrackers, festive atmosphere, golden hour lighting, atmospheric particles, cinematic, 4k quality"
  },
  {
    shotNumber: 2,
    type: "close-up",
    cameraAngle: "low-angle",
    cameraMovement: "dolly",
    duration: 4,
    description: "Kutil emerging from shadows with 'evil' expression that just looks cute",
    impact: "Character introduction with comedic irony",
    imagePrompt: "Close-up low-angle shot of cute purple rakshasa Kutil with tiny horns and big golden eyes, trying to look evil but looking adorable, dramatic underlighting from diyas, stylized 3D animation, expressive face, purple fluffy fur, cinematic shadows, Indian festival background",
    videoPrompt: "Slow dolly in on Kutil's face, expression changing from trying-to-be-evil to confused, rack focus to colorful Diwali decorations behind, warm lighting, 24fps cinematic"
  }
  // ... more shots
];
```

#### Dialogue Example
```typescript
dialogues: [
  {
    character: "Kutil",
    text: "Tonight, I shall steal ALL the sweets! Muahaha!",
    tone: "determined-evil",
    delivery: "Attempting evil laugh but sounding cute"
  },
  {
    character: "Kutil",
    text: "Wait... why am I arranging them beautifully?",
    tone: "confused",
    delivery: "bewildered, looking at hands",
    isPunchline: true
  }
]
```

#### B-Roll Footage
```typescript
bRoll: [
  {
    timestamp: "0:05",
    description: "Close-up of hands making ladoo",
    purpose: "Show sweet-making process for transitions",
    imagePrompt: "Close-up of hands shaping colorful ladoos, vibrant Indian sweets, detailed textures, warm lighting, Diwali decorations in soft background blur, stylized 3D animation, mouth-watering detail",
    videoPrompt: "Macro shot of ladoo preparation in slow motion, hands shaping sweet, steam rising, warm golden lighting, 60fps"
  }
]
```

#### Sound Design
```typescript
soundDesign: {
  ambient: ["Village festival ambience", "Distant firecrackers", "Temple bells"],
  sfx: [
    { timestamp: "0:08", sound: "Comedic slide whistle", description: "Curse activating", intensity: "moderate" },
    { timestamp: "0:23", sound: "Magical sparkle chime", description: "Sweets transforming", intensity: "subtle" }
  ],
  music: [
    {
      timestamp: "0:00",
      type: "intro",
      genre: "fusion",
      mood: "festive-playful",
      tempo: "upbeat",
      instrumentation: ["tabla", "sitar", "modern beats", "festive bells"]
    }
  ]
}
```

### Step 6: Generate YouTube Metadata

```typescript
const metadata = await skill.generateYouTubeMetadata(script.id);

console.log("📺 YouTube Metadata:");
console.log("Title:", metadata.title);
console.log("Tags:", metadata.tags.join(", "));
console.log("\nDescription:\n", metadata.description);
```

**Output:**
```
📺 YouTube Metadata:

Title: Kutil's Diwali Disaster 😂 | Cute Rakshasa Cursed to Be Good

Tags: animated short, comedy animation, diwali animation, ai animation, funny videos, short film, cinematic, comedy, storytelling, character animation, lanka, indie animation, viral video, entertainment, web series, cartoon, mythology, ramayana, kutil, curse comedy, wholesome, feel good, indian animation, festival special, rakshasa

Description:
🎬 Welcome to an epic tale of Kutil, a lovable rakshasa from ancient Lanka!

When a mischievous curse turns every bad deed into accidental good, chaos and comedy ensue! Watch as Kutil tries to steal Diwali sweets but ends up making them even more delicious!

🎨 Created with love using AI-powered storytelling
📍 Setting: Ancient Lanka during Diwali
⏱️ Duration: ~1 minute
🪔 Happy Diwali!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 CHARACTERS:
• Kutil - Protagonist (The cursed cute rakshasa)
• Saint Vardhan - Supporting
• Maya - Supporting

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎵 MUSIC & SFX:
Traditional Ancient Indian instrumentation meets modern cinematic scoring

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 FOLLOW FOR MORE:
New animated shorts every week!

#Diwali #Animation #Comedy #ShortFilm #Kutil

Thumbnail Idea: Epic thumbnail: Kutil holding a ladoo with confused expression, surrounded by magical sparkles and Diwali decorations, bold text "SWEET DISASTER! 🪔", warm orange and gold colors, cute character design, clickbait style but artistic
```

### Step 7: Export Script for Production

```typescript
// Export as different formats

// JSON (for programmatic use)
const jsonScript = await skill.exportScript(script.id, 'json');
await fs.writeFile('kutil-script.json', jsonScript);

// Markdown (for reading)
const mdScript = await skill.exportScript(script.id, 'markdown');
await fs.writeFile('kutil-script.md', mdScript);

// Text (simple)
const textScript = await skill.exportScript(script.id, 'text');
await fs.writeFile('kutil-script.txt', textScript);
```

## 🎨 Camera Angle Examples for Kutil

### Low Angle Shot - Making Kutil Look Heroic
```typescript
const lowAngle = skill.getCameraTechnique('angle', 'low-angle');
// Use when Kutil accidentally does something impressive
// Impact: Power, heroism, dominance
```

### Dutch Angle - Comedic Chaos
```typescript
const dutchAngle = skill.getCameraTechnique('angle', 'dutch-angle');
// Use when curse activates unexpectedly
// Impact: Unease, disorientation, comedy
```

### Extreme Close-up - Emotional Moments
```typescript
const ecu = skill.getCameraTechnique('shot', 'extreme-close-up');
// Use for Kutil's eye twitch when curse activates
// Impact: Intense emotion, comedy
```

## 📋 Full Workflow Summary

```typescript
// Complete workflow in one go
async function createKutilVideo(theme = "Diwali festival") {
  const skill = agent.tools['cinematic-script-writer'];
  
  // 1. Get or create context
  let contexts = await skill.listContexts();
  let context = contexts.find(c => c.name.includes("Kutil"));
  
  if (!context) {
    context = await skill.createContext(/* Kutil details */);
  }
  
  // 2. Generate ideas
  const ideas = await skill.generateStoryIdeas(context.id, 3, theme);
  
  // 3. User selects idea (in real app, show UI)
  const selectedIdea = ideas[0]; // or user selection
  
  // 4. Create script
  const script = await skill.createCinematicScript(
    context.id, 
    selectedIdea.id, 
    selectedIdea
  );
  
  // 5. Get YouTube metadata
  const metadata = await skill.generateYouTubeMetadata(script.id);
  
  return {
    context,
    idea: selectedIdea,
    script,
    metadata
  };
}

// Run it
const videoProject = await createKutilVideo("Diwali festival");
console.log("🎬 Ready to produce:", videoProject.metadata.title);
```

## 🎯 Production Tips

### Image Generation (Midjourney/Stable Diffusion)
- Use the `imagePrompt` fields directly
- Add `--ar 16:9` for video aspect ratio
- Add `--style raw` or `--niji 5` for anime style

### Video Generation (Veo 3/Sora 2)
- Use the `videoPrompt` fields
- Specify camera movements clearly
- Include lighting and atmosphere details

### Editing
- Follow the shot durations for timing
- Use the B-roll for transitions
- Layer sound design as specified

## 📂 File Structure After Creation

```
my-kutil-project/
├── script.json              # Full script data
├── script.md                # Readable markdown
├── prompts/
│   ├── scene1-shots.md      # All image/video prompts for scene 1
│   ├── scene2-shots.md
│   └── b-roll.md
├── audio/
│   ├── music-cues.md
│   └── sfx-list.md
└── youtube/
    ├── title.txt
    ├── description.txt
    └── tags.txt
```

---

🎬 **Happy Creating!** May your Kutil videos bring joy and laughter! 🦞
