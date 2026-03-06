# 🎬 Cinematic Script Writer Skill v1.3

Create professional cinematic scripts for comic/animated videos with:
- ✅ **Google Drive Integration** - Save all content organized in folders
- ✅ **Character Consistency** - Same character appearance across all shots
- ✅ **Voice Consistency** - Distinct, consistent voice for each character  
- ✅ **Environment Consistency** - Era-appropriate architecture, clothing, props
- ✅ **Anachronism Detection** - No modern elements in historical settings
- ✅ **Comprehensive Cinematography** - 20+ camera angles, 30+ lighting, 25+ styles
- ✅ **YouTube Metadata** - Titles, descriptions, SEO tags

## ✨ What's New in v1.3

### Google Drive Storage

| Feature | Description |
|---------|-------------|
| **Ask Storage Location** | Choose where to save (Google Drive or Local) |
| **Organized Folders** | Story title as folder name with numbered files |
| **Complete Export** | Script, prompts, consistency guides, voice profiles, metadata |
| **One-Click Save** | Save everything with one method call |
| **Share Links** | Get shareable Google Drive links |

Generated folder structure:
```
📁 Story Title/
├── 00_INDEX.md (navigation)
├── 01_SCRIPT_README.md (human-readable script)
├── 02_IMAGE_PROMPTS.md (copy-paste AI prompts)
├── 03_CHARACTER_REFERENCES.md (design guides)
├── 04_VOICE_GUIDELINES.md (dialogue guides)
├── 05_YOUTUBE_METADATA.md (upload info)
└── 99_CONTEXT_INFO.md (background)
```

## ✨ What's New in v1.2

### Consistency System

| Feature | Description |
|---------|-------------|
| **Character Reference Sheets** | Detailed visual breakdowns for consistent character design |
| **Voice Profiles** | Pitch, vocabulary, catchphrases, emotional variations |
| **Environment Style Guides** | Era-appropriate architecture, clothing, props, forbidden items |
| **Prompt Builder** | Builds image/video prompts with full consistency |
| **Validation** | Detects anachronisms (glasses in Ramayana, smartphones in ancient times) |

### Cinematography Database

| Category | Count | Examples |
|----------|-------|----------|
| **Camera Angles** | 20+ | eye-level, low-angle, dutch-angle, bird-eye, POV, reflection |
| **Camera Movements** | 20+ | dolly, crane, gimbal, rack-focus, snorricam, whip-pan |
| **Shot Types** | 25+ | extreme-wide, medium-close-up, insert, silhouette, through-frame |
| **Lighting Techniques** | 30+ | three-point, chiaroscuro, god-rays, neon, volume-light |
| **Composition Rules** | 20+ | rule-of-thirds, golden-ratio, leading-lines, negative-space |
| **Color Grading** | 20+ | teal-orange, bleach-bypass, noir, dayglow, vintage |
| **Visual Aesthetics** | 25+ | Pixar-3D, anime, film-noir, indian-miniature, spider-verse |
| **Genre Cinematography** | 15+ | horror, comedy, action, romance, sci-fi, fantasy |

## 🚀 Quick Start

### 1. Create Your First Context

```typescript
const skill = agent.tools['cinematic-script-writer'];

const context = await skill.createContext(
  "Kutil's Adventures",
  "A cursed rakshasa's hilarious journey",
  [{
    name: "Kutil",
    description: "A cute rakshasa from Lanka",
    personality: "Mischievous, determined, secretly kind",
    appearance: "Purple fur, small horns, big golden eyes",
    role: "protagonist",
    backstory: "Cursed by a saint - bad deeds become good",
    specialTraits: ["Curse of unintended goodness", "Loves sweets"]
  }],
  "Ramayana Era",
  "Ancient India - Treta Yuga",
  "Lanka and surrounding forests",
  "short",
  "comedy",
  "All ages",
  "Stylized 3D animation with Indian art influences"
);
```

### 2. Explore Cinematography

```typescript
// Get all camera angles
const angles = skill.getAllCameraAngles();
// Returns: { 'eye-level': {...}, 'low-angle': {...}, 'dutch-angle': {...}, ... }

// Get angles by emotion
const powerAngles = skill.getAnglesByEmotion('power');
// Returns: low-angle, worm-eye, heroic shots

// Get recommended setup
const setup = skill.getRecommendedCameraSetup(
  'dialogue-intimate',  // scene type
  'emotional',          // mood
  'intermediate'        // skill level
);
// Returns: { angle, movement, shot, lighting, lens }

// Get lighting for scene
const lighting = skill.suggestLighting('interior-day', 'comedy');
// Returns: ['high-key', 'three-point', 'soft-key']

// Get color grading for genre
const grading = skill.suggestColorGrading('comedy');
// Returns: ['warm', 'high-saturation', 'natural']
```

### 3. Generate Story & Script

```typescript
// Generate story ideas
const ideas = await skill.generateStoryIdeas(context.id, 3, "Diwali festival");

// Create cinematic script
const script = await skill.createCinematicScript(context.id, ideas[0].id, ideas[0]);

// Get YouTube metadata
const metadata = await skill.generateYouTubeMetadata(script.id);
```

### 4. Save to Google Drive 🆕

```typescript
// Ask where to store
const location = await skill.askStorageLocation();

// Connect to Google Drive (first time)
const auth = await skill.connectGoogleDrive();
if (auth.needsAuth) {
  console.log("Visit:", auth.authUrl);
  const code = await getCodeFromUser(); // User provides auth code
  await skill.connectGoogleDrive(code);
}

// Save everything!
const result = await skill.saveScriptToStorage(
  ideas[0].title,  // Folder name = story title
  context.id,
  script.id,
  {
    includeScript: true,
    includePrompts: true,
    includeConsistency: true,
    includeVoice: true,
    includeMetadata: true
  }
);

console.log("Saved to:", result.shareLink);
// https://drive.google.com/drive/folders/...
```

## 📚 Complete API Reference

### Context Management

| Method | Returns | Description |
|--------|---------|-------------|
| `createContext(...)` | `StoryContext` | Create new story world |
| `listContexts()` | `ContextSummary[]` | List all contexts |
| `listContextsDetailed()` | `StoryContext[]` | List with full details |
| `getContext(id)` | `StoryContext \| null` | Get specific context |
| `deleteContext(id)` | `boolean` | Delete context |

### Story & Script Generation

| Method | Returns | Description |
|--------|---------|-------------|
| `generateStoryIdeas(contextId, count?, theme?)` | `StoryIdea[]` | Generate story ideas |
| `createCinematicScript(contextId, ideaId, idea)` | `CinematicScript` | Create full script |
| `generateYouTubeMetadata(scriptId)` | `YouTubeMetadata` | Generate YouTube data |
| `exportScript(scriptId, format)` | `string` | Export as JSON/text/markdown |

### 💾 Storage (Google Drive)

| Method | Returns | Description |
|--------|---------|-------------|
| `askStorageLocation()` | `StorageOptions` | Ask user where to store files |
| `connectGoogleDrive(authCode?)` | `AuthResult` | Connect to Google Drive |
| `connectLocalStorage()` | `ConnectionResult` | Use local downloads |
| `getStorageStatus()` | `StorageStatus` | Check connection status |
| `saveScriptToStorage(title, contextId, scriptId, options?)` | `SaveResult` | Save complete project |
| `disconnectStorage()` | `void` | Disconnect from storage |

### 🎥 Camera Techniques (20+ Angles, 25+ Shots)

#### Camera Angles

```typescript
// Get all angles
skill.getAllCameraAngles()

// Get specific angle
skill.getCameraAngle('dutch-angle')
// Returns: {
//   description: 'Tilted camera, horizon not level',
//   emotionalImpact: 'Unease, disorientation, tension',
//   bestFor: 'Chaos, dreams, insanity, danger',
//   commonUses: ['Nightmares', 'Villain lairs', 'Horror'],
//   difficulty: 'intermediate'
// }

// Find angles by emotion
skill.getAnglesByEmotion('power')
// Returns: low-angle, worm-eye, heroic shots
```

**Available Angles (20+):**
- Standard: `eye-level`, `low-angle`, `high-angle`
- Dramatic: `dutch-angle`, `dutch-angle` (canted)
- Extreme: `bird-eye`, `worm-eye`, `overhead`
- POV: `pov`, `over-shoulder`, `profile`
- Special: `reflection`, `aerial`, `crane-shot`, `three-quarter`

#### Camera Movements

```typescript
// Get all movements
skill.getAllCameraMovements()

// Get specific movement
skill.getCameraMovement('rack-focus')
// Returns: {
//   description: 'Shifting focus from one plane to another',
//   emotionalImpact: 'Connection, choice, revelation',
//   speed: 'smooth transition',
//   difficulty: 'advanced'
// }
```

**Available Movements (20+):**
- Basic: `static`, `pan`, `tilt`
- Dolly: `dolly-in`, `dolly-out`, `dolly-zoom`
- Complex: `crane`, `jib`, `steadicam`, `gimbal`, `drone`
- Effects: `zoom-in`, `zoom-out`, `rack-focus`, `whip-pan`
- Special: `orbit`, `snorricam`, `follow-focus`

#### Shot Types

```typescript
// Get all shot types
skill.getAllShotTypes()

// Get specific shot
skill.getShotType('extreme-close-up')
// Returns: {
//   description: 'Detail only - eyes, mouth, hands',
//   emotionalImpact: 'Intense emotion, symbolism, detail importance',
//   framing: 'Fills frame with detail',
//   lens: 'Macro or 100mm+'
// }
```

**Available Shots (25+):**
- Distance: `extreme-wide`, `wide`, `medium-wide`, `medium`, `medium-close-up`, `close-up`, `extreme-close-up`
- Special: `establishing`, `master`, `two-shot`, `three-shot`, `group-shot`
- Creative: `over-shoulder`, `pov`, `reaction-shot`, `insert`, `cutaway`
- Artistic: `silhouette`, `shadow-shot`, `mirror-shot`, `through-frame`, `dirty-single`

#### Camera Recommendations

```typescript
// Get complete setup recommendation
skill.getRecommendedCameraSetup(
  'hero-entrance',      // sceneType
  'epic',               // mood
  'intermediate'        // skillLevel
)
// Returns: {
//   angle: 'low-angle',
//   movement: 'crane-down',
//   shot: 'wide',
//   lighting: 'rim-light',
//   lens: '24mm'
// }

// Suggest techniques for purpose
skill.suggestCameraTechnique('intimacy', 'beginner')
// Returns: { angles, movements, shots } for intimacy scenes
```

### 💡 Lighting Techniques (30+ Methods)

```typescript
// Get all techniques
skill.getAllLightingTechniques()

// Get specific technique
skill.getLightingTechnique('chiaroscuro')
// Returns: {
//   description: 'Extreme contrast between light and dark',
//   emotionalImpact: 'Dramatic, intense, artistic',
//   bestFor: 'Drama, art films, noir',
//   difficulty: 'advanced'
// }

// Suggest lighting for scene
skill.suggestLighting('interior-night', 'horror')
// Returns: ['practical-lighting', 'moonlight', 'low-key']
```

**Lighting Categories:**
- Three-Point: `three-point`, `key-light-only`, `high-key`, `low-key`
- Natural: `golden-hour`, `blue-hour`, `daylight`, `overcast`
- Dramatic: `chiaroscuro`, `silhouette`, `rim-light`, `single-source`
- Practical: `motivated-lighting`, `practical-lighting`, `candlelight`, `firelight`
- Modern: `neon`, `fluorescent`, `tungsten`, `strobe`
- Atmospheric: `god-rays`, `volume-light`, `lens-flare`

### 📐 Composition Rules (20+ Guidelines)

```typescript
// Get all composition rules
skill.getAllCompositionRules()

// Get specific rule
skill.getCompositionRule('rule-of-thirds')
// Returns: {
//   description: 'Divide frame into 3x3 grid',
//   purpose: 'Balanced, visually pleasing',
//   whenToUse: 'Almost all compositions',
//   whenToBreak: 'For symmetry, tension'
// }
```

**Available Rules:**
- Classic: `rule-of-thirds`, `golden-ratio`, `symmetry`, `asymmetry`
- Lines: `leading-lines`, `diagonals`, `s-curve`, `triangles`
- Space: `negative-space`, `fill-frame`, `depth-layers`, `frame-within-frame`
- Balance: `visual-weight`, `rule-of-odds`, `headroom`, `nose-room`
- Patterns: `patterns-textures`, `center-composition`

### 🎨 Color Grading (20+ Styles)

```typescript
// Get all styles
skill.getAllColorGradingStyles()

// Get specific style
skill.getColorGradingStyle('teal-orange')
// Returns: {
//   description: 'Teal shadows, orange highlights',
//   emotionalImpact: 'Cinematic, modern, commercial',
//   bestFor: 'Action, blockbusters',
//   examples: ['Transformers', 'Mad Max: Fury Road']
// }

// Suggest for genre
skill.suggestColorGrading('sci-fi')
// Returns: ['teal-orange', 'cool', 'matrix-green', 'dayglow']
```

**Available Styles:**
- Modern: `teal-orange`, `desaturated`, `high-saturation`
- Classic: `noir`, `sepia`, `vintage`, `bleach-bypass`
- Creative: `dayglow`, `cross-process`, `duotone`, `matrix-green`
- Temperature: `warm`, `cool`, `golden`, `natural`

### 🎭 Visual Aesthetics (25+ Styles)

```typescript
// Get all aesthetics
skill.getAllVisualAesthetics()

// Get specific aesthetic
skill.getVisualAesthetic('spider-verse')
// Returns: {
//   description: 'Comic book come to life',
//   characteristics: { frameRate, style, rendering },
//   emotionalQuality: 'Energetic, youthful',
//   examples: ['Spider-Verse', 'Arcane']
// }

// Get by type
skill.getAestheticsByType('animation')
// Returns: [pixar-3d, disney-classic, anime, spider-verse, ...]
```

**Animation Styles:**
- 3D: `pixar-3d`, `low-poly`, `voxel`
- 2D: `disney-classic`, `anime`, `spider-verse`
- Stop Motion: `stop-motion`, `claymation`, `cut-out`
- Motion: `motion-graphics`

**Live-Action Styles:**
- Documentary: `documentary`, `cinema-verite`, `found-footage`, `mockumentary`
- Commercial: `commercial`, `music-video`

**Artistic Styles:**
- Classic: `film-noir`, `german-expressionism`, `french-new-wave`
- Genre: `horror`, `sci-fi`, `fantasy`, `western`, `war`, `romance`, `comedy`
- Indian: `indian-miniature`, `indian-classical-art`

### 🎬 Genre Cinematography (15+ Genres)

```typescript
// Get all genre conventions
skill.getAllGenreCinematography()

// Get specific genre
skill.getGenreCinematography('horror')
// Returns: {
//   cameraMovement: ['slow-push', 'handheld', 'static-tension'],
//   shotTypes: ['close-up', 'POV', 'wide-empty'],
//   angles: ['dutch', 'low', 'high', 'unusual'],
//   lighting: 'Low-key, shadows, practical sources',
//   colorGrading: 'Desaturated, cool tones'
// }
```

**Available Genres:**
`action`, `comedy`, `drama`, `horror`, `romance`, `sci-fi`, `fantasy`, `thriller`, `documentary`, `musical`, `western`, `war`, `period-drama`, `noir`, `animation-comedy`

### 🇮🇳 Indian Cinematography

```typescript
// Get all Indian styles
skill.getIndianCinematography()

// Get specific style
skill.getIndianCinematography('bollywood-masala')
// Returns: {
//   songs: 'Vibrant colors, multiple locations...',
//   drama: 'Emotional close-ups, dramatic lighting',
//   characteristics: 'High saturation, vibrant costumes'
// }
```

**Indian Styles:**
- `bollywood-masala` - Classic commercial Bollywood
- `bollywood-contemporary` - Modern urban Bollywood
- `art-house-indian` - Parallel cinema
- `mythological-epic` - Devotional epics
- `period-historical-indian` - Historical dramas

### 🎯 Complete Scene Packages

```typescript
// Get everything for a scene
skill.getSceneCinematographyPackage(
  'comedy',           // genre
  'chaotic',          // mood
  'comedic-fall',     // sceneType
  'intermediate'      // skillLevel
)
// Returns: {
//   genreConventions: { ... },
//   camera: { angle, movement, shot, lighting, lens },
//   lighting: [...],
//   colorGrading: [...],
//   completeSetup: { ... }
// }

// Generate prompt for AI image generation
skill.generateCinematicPrompt(
  "Kutil the cute rakshasa",
  "low-angle",
  "medium",
  "golden-hour",
  "pixar-3d"
)
// Returns: "Medium shot, Camera below subject looking up..."

// Search everything
skill.searchCinematography('dramatic')
// Returns: { angles, movements, shots, lighting } matching "dramatic"
```

## 📖 Example: Complete Workflow with Cinematography

```typescript
const skill = agent.tools['cinematic-script-writer'];

// 1. Create context
const context = await skill.createContext(
  "Kutil - The Cursed Rakshasa",
  "A lovable rakshasa's misadventures",
  [{
    name: "Kutil",
    description: "Cute purple rakshasa with a curse",
    personality: "Tries to be evil, fails adorably",
    appearance: "Purple fur, big eyes, small horns",
    role: "protagonist",
    backstory: "Cursed - bad deeds become good"
  }],
  "Ramayana Era",
  "Ancient India",
  "Lanka",
  "short",
  "comedy",
  "All ages",
  "Stylized 3D animation with Indian art style"
);

// 2. Explore cinematography options
const powerAngles = skill.getAnglesByEmotion('power');
const comedyLighting = skill.suggestLighting('interior-day', 'comedy');
const comedyGrading = skill.suggestColorGrading('comedy');

// 3. Get complete setup for a scene
const setup = skill.getSceneCinematographyPackage(
  'comedy',
  'slapstick',
  'comedic-fall',
  'intermediate'
);

// 4. Generate story
const ideas = await skill.generateStoryIdeas(context.id, 3);

// 5. Create script with cinematography
const script = await skill.createCinematicScript(
  context.id,
  ideas[0].id,
  ideas[0]
);

// 6. Generate enhanced image prompt
const prompt = skill.generateCinematicPrompt(
  "Kutil trying to look evil",
  "low-angle",
  "close-up",
  "golden-hour",
  "pixar-3d"
);
// Use this prompt in Midjourney, Stable Diffusion, etc.

// 7. Get YouTube metadata
const metadata = await skill.generateYouTubeMetadata(script.id);
```

## 🎨 Camera Angle Reference

| Angle | Impact | Best For |
|-------|--------|----------|
| `eye-level` | Connection, equality | Dialogue, intimacy |
| `low-angle` | Power, heroism | Hero entrances, villains |
| `high-angle` | Vulnerability | Defeat, isolation |
| `dutch-angle` | Unease, chaos | Horror, disorientation |
| `bird-eye` | Insignificance, scale | Epic, lost in crowd |
| `worm-eye` | Overwhelming | Monuments, giants |
| `pov` | Immersion | First-person, horror |
| `over-shoulder` | Conversation intimacy | Dialogue scenes |
| `reflection` | Introspection | Mirrors, self-examination |

## 💡 Lighting Quick Reference

| Technique | Mood | Best For |
|-----------|------|----------|
| `three-point` | Professional, flattering | Standard coverage |
| `golden-hour` | Romantic, magical | Beauty shots, endings |
| `chiaroscuro` | Dramatic, intense | Drama, noir, horror |
| `high-key` | Happy, light | Comedy, commercials |
| `low-key` | Mysterious, suspenseful | Thriller, noir |
| `god-rays` | Divine, spiritual | Fantasy, forests |
| `neon` | Urban, cyberpunk | City nights, sci-fi |
| `practical` | Realistic, natural | Documentary, realism |

## 🎨 Color Grading Reference

| Style | Mood | Genre |
|-------|------|-------|
| `teal-orange` | Cinematic, modern | Action, blockbusters |
| `bleach-bypass` | Gritty, harsh | War, action |
| `noir` | Mysterious, stylish | Crime, noir |
| `sepia` | Nostalgic, historical | Period pieces, flashbacks |
| `desaturated` | Bleak, realistic | Drama, war |
| `dayglow` | Futuristic, energetic | Sci-fi, cyberpunk |
| `warm` | Cozy, romantic | Romance, feel-good |
| `cool` | Clinical, isolated | Horror, isolation |

## 📁 File Structure

```
cinematic-script-writer/
├── index.ts                      # Main skill implementation
├── cinematography-api.ts         # Unified API for all techniques
├── cinematography-db.ts          # 20+ angles, 20+ movements, 25+ shots
├── lighting-db.ts                # 30+ lighting, 20+ composition, 20+ grading
├── visual-styles-db.ts           # 25+ aesthetics, 15+ genres, Indian styles
├── consistency-system.ts         # Character/voice/environment consistency
├── prompt-builder.ts             # Consistent prompt generation
├── storage-adapter.ts            # Google Drive & local storage adapters
├── storage-manager.ts            # Save organization & file creation
├── skill.json                    # Skill manifest
├── schema.json                   # Configuration schema
├── README.md                     # This file
├── EXAMPLE-KUTIL.md              # Complete Kutil example
├── EXAMPLE-CONSISTENCY.md        # Consistency system example
└── EXAMPLE-STORAGE.md            # Google Drive storage example
```

## 🔧 Configuration

```json
{
  "llmProvider": "anthropic",
  "apiKey": "your-api-key",
  "model": "claude-3-opus",
  "defaultVideoDuration": 60,
  "cameraStyle": "cinematic"
}
```

## 📝 Notes

- All cinematography data is embedded - no internet required
- Techniques include difficulty levels (beginner/intermediate/advanced)
- Each technique includes emotional impact and best use cases
- Indian cinematography styles included for cultural content
- Search function finds techniques across all categories

## 📄 License

MIT
