# Cinematic Script Writer

Create professional cinematic scripts for AI video generation with character consistency, comprehensive cinematography knowledge, and Google Drive storage integration.

## Description

This skill helps you create complete cinematic scripts for animated/comic videos. It includes:

- **Story Generation**: Create contexts, characters, and generate story ideas
- **Cinematic Scripts**: Full scripts with camera angles, shots, lighting, and dialogue
- **Character Consistency**: Ensures characters look the same across all shots
- **Voice Consistency**: Maintains consistent speech patterns for each character
- **Environment Consistency**: Era-appropriate architecture, clothing, and props
- **Anachronism Detection**: Prevents modern items in historical settings
- **Google Drive Storage**: Auto-saves all content to organized folders
- **YouTube Metadata**: Generates titles, descriptions, and tags

## Features

### Cinematography Database (175+ Techniques)
- 20+ Camera Angles (eye-level, low-angle, dutch-angle, bird-eye, POV)
- 20+ Camera Movements (dolly, crane, gimbal, rack-focus, snorricam)
- 25+ Shot Types (extreme-wide, close-up, insert, silhouette)
- 30+ Lighting Techniques (three-point, chiaroscuro, god-rays, neon)
- 20+ Composition Rules (rule-of-thirds, golden-ratio, leading-lines)
- 20+ Color Grading Styles (teal-orange, noir, vintage, dayglow)
- 25+ Visual Aesthetics (Pixar-3D, anime, film-noir, indian-miniature)
- 15+ Genre Cinematography Guides

### Consistency System
- Character reference sheets with visual details
- Voice profiles with pitch, vocabulary, catchphrases
- Environment style guides for era accuracy
- Prompt builder with consistency enforcement
- Anachronism validation

### Storage Integration
- Google Drive OAuth connection
- Local storage (downloads)
- Organized folder structure
- Complete project export

## Usage Examples

### Basic Story Creation

```javascript
// Create a story context
const context = await skill.createContext(
  "Kutil's Adventure",
  "A cursed rakshasa's journey",
  [{
    name: "Kutil",
    description: "Cute purple rakshasa",
    personality: "Mischievous, kind",
    appearance: "Purple fur, golden eyes",
    role: "protagonist"
  }],
  "Ramayana Era",
  "Ancient India",
  "Lanka",
  "short",
  "comedy",
  "All ages",
  "Pixar 3D style"
);

// Generate story ideas
const ideas = await skill.generateStoryIdeas(context.id, 3);

// Create script
const script = await skill.createCinematicScript(
  context.id,
  ideas[0].id,
  ideas[0]
);
```

### Using Cinematography

```javascript
// Get camera techniques
const angles = skill.getAllCameraAngles();
const lighting = skill.suggestLighting('interior-day', 'comedy');
const grading = skill.suggestColorGrading('comedy');

// Get complete setup
const setup = skill.getRecommendedCameraSetup(
  'dialogue-intimate',
  'emotional',
  'intermediate'
);
```

### Character Consistency

```javascript
// Create character reference
const ref = skill.createCharacterReference(
  "char-123",
  "Kutil",
  "Purple fur, small horns, golden eyes",
  "Ramayana Era",
  "pixar-3d"
);

// Generate consistent prompts
const prompt = skill.generateCharacterConsistencyPrompt("char-123");

// Validate for anachronisms
const result = skill.validatePrompt(
  "Kutil wearing sunglasses",
  ["char-123"],
  context.id
);
// Returns error: glasses don't belong in Ramayana Era
```

### Save to Google Drive

```javascript
// Connect Google Drive
const auth = await skill.connectGoogleDrive();
// Visit auth.authUrl, authorize, paste code
await skill.connectGoogleDrive(userAuthCode);

// Save everything
const result = await skill.saveScriptToStorage(
  "Story Title",
  context.id,
  script.id
);
console.log(result.shareLink);
```

## Tools

### Context Management
- `createContext()` - Create story world
- `listContexts()` - List all contexts
- `getContext()` - Get specific context
- `deleteContext()` - Delete context

### Story Generation
- `generateStoryIdeas()` - Generate story ideas
- `createCinematicScript()` - Create full script
- `generateYouTubeMetadata()` - Generate YouTube data

### Consistency
- `createCharacterReference()` - Character visual reference
- `createVoiceProfile()` - Voice consistency profile
- `createEnvironmentStyleGuide()` - Era-appropriate guide
- `buildConsistentPrompts()` - Build consistent prompts
- `validatePrompt()` - Check for anachronisms

### Cinematography
- `getAllCameraAngles()` - All camera angles
- `getAllCameraMovements()` - All movements
- `getAllShotTypes()` - All shot types
- `getAllLightingTechniques()` - All lighting
- `suggestCameraTechnique()` - Suggest techniques
- `suggestLighting()` - Suggest lighting
- `suggestColorGrading()` - Suggest grading

### Storage
- `connectGoogleDrive()` - Connect Google Drive
- `connectLocalStorage()` - Use local storage
- `saveScriptToStorage()` - Save to storage
- `getStorageStatus()` - Check connection

## File Structure

When saved to Google Drive, creates:

```
📁 Story Title/
├── 00_INDEX.md                    # Navigation
├── 01_SCRIPT_README.md            # Human-readable script
├── 02_IMAGE_PROMPTS.md            # AI generation prompts
├── 03_CHARACTER_REFERENCES.md     # Design guides
├── 04_VOICE_GUIDELINES.md         # Dialogue guides
├── 05_YOUTUBE_METADATA.md         # Upload info
└── 99_CONTEXT_INFO.md             # Background
```

## Requirements

- Node.js 18+
- OpenClaw Agent with memory permissions
- Google Drive API (optional, for storage)

## Tags

creative, video, script, cinematography, consistency, character-design, voice, storage, google-drive, youtube

## Version

1.3.0

## Author

Praveen Kumar

## License

MIT
