# 💾 Storage & Google Drive Integration Example

This example shows how to save all your generated content to Google Drive with organized folders.

## Quick Start: Save to Google Drive

### Step 1: Ask Where to Store

```typescript
const skill = agent.tools['cinematic-script-writer'];

// Ask user where to store files
const locationQuestion = await skill.askStorageLocation();
console.log(locationQuestion.question);
// "Where would you like to store your generated files?"
//
// Options:
// 1. 📁 Google Drive - Save to your Google Drive account
// 2. 💻 Local Download - Download files to your computer
// 3. ❓ Ask me later - Decide when saving each time
```

### Step 2: Connect to Google Drive

```typescript
// User selects Google Drive
// Get auth URL
const authResult = await skill.connectGoogleDrive();

if (authResult.needsAuth) {
  console.log(authResult.message);
  // Please authorize access to your Google Drive:
  // https://accounts.google.com/o/oauth2/v2/auth?...
  //
  // After authorization, paste the code here.
  
  // User pastes auth code from Google
  const userAuthCode = '4/0Adeu...'; // User provides this
  
  const connectResult = await skill.connectGoogleDrive(userAuthCode);
  console.log(connectResult.message);
  // ✅ Successfully connected to Google Drive!
}
```

### Step 3: Create Your Story

```typescript
// Create context
const kutilContext = await skill.createContext(
  "Kutil - The Cursed Rakshasa",
  "A lovable rakshasa's misadventures",
  [/* characters */],
  "Ramayana Era",
  "Ancient India - Treta Yuga",
  "Lanka",
  "short",
  "comedy",
  "All ages",
  "Stylized 3D animation"
);

// Setup consistency
const { guides } = await skill.setupContextWithConsistency(
  kutilContext,
  { /* character visuals */ }
);

// Generate story
const ideas = await skill.generateStoryIdeas(kutilContext.id, 3);
const script = await skill.createCinematicScript(
  kutilContext.id,
  ideas[0].id,
  ideas[0]
);

// Generate metadata
const metadata = await skill.generateYouTubeMetadata(script.id);
```

### Step 4: Save Everything to Google Drive

```typescript
// Save all content to Google Drive
const saveResult = await skill.saveScriptToStorage(
  "Kutil's Diwali Disaster",  // Folder name (title)
  kutilContext.id,            // Context ID
  script.id,                  // Script ID
  {
    includeScript: true,      // Save 01_SCRIPT.json
    includePrompts: true,     // Save 02_PROMPTS.json
    includeConsistency: true, // Save 03_CONSISTENCY.json
    includeVoice: true,       // Save 04_VOICE_PROFILES.json
    includeMetadata: true     // Save 05_YOUTUBE_METADATA.json
  }
);

console.log(saveResult);
// {
//   success: true,
//   folder: {
//     id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
//     name: "Kutil's Diwali Disaster",
//     path: "/Kutil's Diwali Disaster",
//     webViewLink: "https://drive.google.com/drive/folders/..."
//   },
//   files: [
//     { name: "00_INDEX.md", type: "master", ... },
//     { name: "01_SCRIPT.json", type: "script", ... },
//     { name: "01_SCRIPT_README.md", type: "script", ... },
//     { name: "02_PROMPTS.json", type: "prompts", ... },
//     { name: "02_IMAGE_PROMPTS.md", type: "prompts", ... },
//     { name: "03_CONSISTENCY.json", type: "consistency", ... },
//     { name: "03_CHARACTER_REFERENCES.md", type: "consistency", ... },
//     { name: "03_ENVIRONMENT_GUIDE.md", type: "consistency", ... },
//     { name: "04_VOICE_PROFILES.json", type: "voice", ... },
//     { name: "04_VOICE_GUIDELINES.md", type: "voice", ... },
//     { name: "05_YOUTUBE_METADATA.json", type: "metadata", ... },
//     { name: "05_YOUTUBE_METADATA.md", type: "metadata", ... },
//     { name: "99_CONTEXT_INFO.md", type: "master", ... }
//   ],
//   shareLink: "https://drive.google.com/drive/folders/...",
//   errors: []
// }
```

## 📁 Generated Folder Structure

When you save, it creates this organized folder:

```
📁 Kutil's Diwali Disaster (Google Drive Folder)
│
├── 📄 00_INDEX.md                    ← Start here! Overview of all files
│
├── 📄 01_SCRIPT.json                 ← Full script data (JSON)
├── 📄 01_SCRIPT_README.md            ← Human-readable script
│
├── 📄 02_PROMPTS.json                ← All prompts data
├── 📄 02_IMAGE_PROMPTS.md            ← Copy-paste prompts for Midjourney/SD
│
├── 📄 03_CONSISTENCY.json            ← Consistency data
├── 📄 03_CHARACTER_REFERENCES.md     ← Character design guides
├── 📄 03_ENVIRONMENT_GUIDE.md        ← Era/style guides
│
├── 📄 04_VOICE_PROFILES.json         ← Voice data
├── 📄 04_VOICE_GUIDELINES.md         ← Dialogue writing guide
│
├── 📄 05_YOUTUBE_METADATA.json       ← YouTube data
├── 📄 05_YOUTUBE_METADATA.md         ← Title/description/tags
│
└── 📄 99_CONTEXT_INFO.md             ← Story background
```

## 📄 What's in Each File?

### 00_INDEX.md
Navigation hub showing all files and their purposes.

```markdown
# Kutil's Diwali Disaster

Generated by Cinematic Script Writer
Date: 2/10/2026, 10:30:15 AM

## 📁 Contents

| File | Description |
|------|-------------|
| 00_INDEX.md | This file - overview of all content |
| 01_SCRIPT.json | Full script data (JSON) |
| 01_SCRIPT_README.md | Human-readable script |
| 02_PROMPTS.json | All prompts data (JSON) |
| 02_IMAGE_PROMPTS.md | Copy-paste image prompts |
| 03_CONSISTENCY.json | Consistency data (JSON) |
| 03_CHARACTER_REFERENCES.md | Character design references |
| 03_ENVIRONMENT_GUIDE.md | Era/style environment guide |
| 04_VOICE_PROFILES.json | Voice data (JSON) |
| 04_VOICE_GUIDELINES.md | Voice/dialogue guidelines |
| 05_YOUTUBE_METADATA.json | YouTube metadata (JSON) |
| 05_YOUTUBE_METADATA.md | YouTube title/description/tags |
| 99_CONTEXT_INFO.md | Story context and background |

## 🎬 Quick Start

1. **Script**: Read `01_SCRIPT_README.md` for the full story
2. **Images**: Copy prompts from `02_IMAGE_PROMPTS.md` to Midjourney/Stable Diffusion
3. **Consistency**: Check `03_CHARACTER_REFERENCES.md` to keep characters consistent
4. **Voice**: Use `04_VOICE_GUIDELINES.md` for dialogue writing
5. **YouTube**: Use `05_YOUTUBE_METADATA.md` for upload
```

### 01_SCRIPT_README.md
Human-readable script with all scenes, shots, and dialogue.

```markdown
# Kutil's Diwali Disaster

## 🪝 Hook

What happens when a monster tries to ruin Diwali but can only make it better?

**Duration:** 3s

---

## 🎬 Scene 1: The Setup

**Duration:** 15s | **Location:** Lanka marketplace

### Synopsis
Introduce protagonist and the curse dynamics

### 📷 Shots

**Shot 1** - establishing | high-angle | 3s

Description: Wide shot of Lanka, establishing the setting

**Image Prompt:**
```
Epic wide establishing shot of ancient Lanka marketplace during Diwali preparations, 
vibrant colors, rangoli patterns, diyas glowing, traditional architecture, 
golden hour lighting, highly detailed, 8k, stylized 3D animation with Indian art influences
```

**Video Prompt:**
```
Wide establishing shot of ancient marketplace during Diwali, gentle camera drift, 
hundreds of diyas twinkling, smoke from firecrackers, festive atmosphere, 
golden hour lighting, atmospheric particles, cinematic, 4k quality
```

### 💬 Dialogue

**Kutil:** Today, I shall steal ALL the sweets! Muahaha!
*(determined-evil, confident, evil laugh)*

**Kutil:** Wait... why am I arranging them beautifully?
*(confused, bewildered, high pitch)* 💥
```

### 02_IMAGE_PROMPTS.md
Ready-to-copy prompts for AI image generation.

```markdown
# Image & Video Generation Prompts

Copy these prompts into your AI image/video generation tool:

---

## Shot 1: establishing - Wide shot of Lanka marketplace...

### Image Prompt (Midjourney/Stable Diffusion)
```
close-up shot, low-angle camera angle, Kutil is a small cute rakshasa with 
fluffy purple fur covering entire body, two small curved horns on head cream 
colored tips, large round golden eyes with black pupils, wearing simple 
traditional cotton dhoti, Ramayana Era setting, Lanka marketplace, stone 
temple architecture, golden-hour lighting, mischievous mood, pixar-3d style, 
consistent character design, same character across frames, highly detailed, 8k
```

### Video Prompt (Veo/Sora/Runway)
```
close-up shot, static camera movement, low-angle angle, Kutil: small cute 
rakshasa with purple fur, trying to look evil but looking cute, Ramayana Era 
setting, golden-hour lighting, mischievous atmosphere, smooth motion, 
24fps cinematic, high quality
```

### Negative Prompt
```
inconsistent character design, different character in each frame, changing 
features, wrong eye color, wrong hair color, modern clothing, glasses, 
watches, plastic, synthetic fabrics, blurry, low quality, deformed
```

---
```

### 03_CHARACTER_REFERENCES.md
Visual reference guides for consistency.

```markdown
# Character Reference Sheets

Use these references to keep characters consistent across all images:

---

# Kutil

## Visual Description
Kutil is a small cute rakshasa (mythical being) with:
- Fluffy purple fur covering entire body
- Two small curved horns on head (cream colored tips)
- Large round golden eyes with black pupils
- Small fangs visible when smiling
- Pointed ears with pink insides
- Short tail with purple fur
- About 3 feet tall, chibi proportions

## Color Palette
- **Signature:** purple, golden
- **Primary:** purple, cream
- **Hair:** purple
- **Eyes:** golden

## Default Outfit
Simple traditional cotton dhoti in earthy colors

## Consistency Keywords
Always include these in prompts:
- consistent character design
- same character across frames
- character continuity

## Negative Prompts
Always exclude these:
- modern clothing
- anachronistic elements
- inconsistent features
```

### 04_VOICE_GUIDELINES.md
Voice profiles for consistent dialogue.

```markdown
# Voice Guidelines

Use these guidelines for consistent character dialogue:

---

# Kutil

## Speech Characteristics
- **Pitch:** high
- **Speed:** fast
- **Volume:** normal
- **Clarity:** clear

## Language
- **Vocabulary:** simple
- **Formality:** casual

## Catchphrases
- "I am evil!"
- "Curse you, Saint Vardhan!"
- "Muahaha!"

## Speech Examples
- **Greeting:** "Tremble before me!"
- **Question:** "What do you mean I'm helping?"
- **Exclamation:** "No, not again!"
```

### 05_YOUTUBE_METADATA.md
Ready-to-use YouTube upload info.

```markdown
# YouTube Metadata

## Title

Kutil's Diwali Disaster 😂 | Cute Rakshasa Cursed to Be Good

## Description

🎬 Welcome to an epic tale of Kutil, a lovable rakshasa from ancient Lanka!

When a mischievous curse turns every bad deed into accidental good, 
chaos and comedy ensue! Watch as Kutil tries to steal Diwali sweets 
but ends up making them even more delicious!

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

## Tags

animated short, comedy animation, diwali animation, ai animation, 
funny videos, short film, cinematic, comedy, storytelling, 
character animation, lanka, indie animation, viral video, 
entertainment, web series, cartoon, mythology, ramayana, 
kutil, curse comedy, wholesome, feel good

## Category

Film & Animation

## Thumbnail Idea

Epic thumbnail: Kutil holding a ladoo with confused expression, 
surrounded by magical sparkles and Diwali decorations, 
bold text "SWEET DISASTER! 🪔", warm orange and gold colors
```

## Complete Workflow Example

```typescript
async function createAndSaveStory() {
  const skill = agent.tools['cinematic-script-writer'];
  
  // 1. Connect to Google Drive (first time only)
  const status = await skill.getStorageStatus();
  if (!status.connected) {
    const auth = await skill.connectGoogleDrive();
    if (auth.needsAuth) {
      console.log("Please visit this URL and paste the code:");
      console.log(auth.authUrl);
      // User visits URL, authorizes, gets code
      const userCode = await askUserForCode(); // Get from user
      await skill.connectGoogleDrive(userCode);
    }
  }
  
  // 2. Create context
  const context = await skill.createContext(
    "Kutil's Adventure",
    "Diwali comedy story",
    [/* characters */],
    "Ramayana Era",
    "Treta Yuga",
    "Lanka",
    "short",
    "comedy",
    "All ages",
    "Pixar 3D style"
  );
  
  // 3. Setup consistency
  await skill.setupContextWithConsistency(context, {
    [context.characters[0].id]: "Purple fur, small horns, golden eyes..."
  });
  
  // 4. Generate story
  const ideas = await skill.generateStoryIdeas(context.id, 3);
  const selectedIdea = ideas[0];
  
  // 5. Create script
  const script = await skill.createCinematicScript(
    context.id,
    selectedIdea.id,
    selectedIdea
  );
  
  // 6. Generate metadata
  const metadata = await skill.generateYouTubeMetadata(script.id);
  
  // 7. Save everything to Google Drive!
  const saveResult = await skill.saveScriptToStorage(
    selectedIdea.title,  // Uses story title as folder name
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
  
  if (saveResult.success) {
    console.log("✅ Saved to Google Drive!");
    console.log("Folder:", saveResult.folder.name);
    console.log("Link:", saveResult.shareLink);
    console.log("Files:", saveResult.files.map(f => f.name).join(', '));
  } else {
    console.error("Save failed:", saveResult.errors);
  }
  
  return saveResult;
}
```

## Local Storage (Download)

If user doesn't want Google Drive:

```typescript
// Connect to local storage
await skill.connectLocalStorage();

// Save will download files
const result = await skill.saveScriptToStorage(
  "Kutil's Story",
  context.id,
  script.id
);
// Files will download to browser/computer
```

## Check Storage Status

```typescript
const status = await skill.getStorageStatus();
console.log(status);
// {
//   connected: true,
//   provider: 'google-drive'
// }
```

## Disconnect

```typescript
await skill.disconnectStorage();
console.log("Disconnected from storage");
```

## Tips

1. **First Time Setup**: Only need to connect Google Drive once
2. **Folder Names**: Uses your story title as the folder name
3. **Re-save**: Can re-save to update files
4. **Share**: Use `shareLink` to share folder with collaborators
5. **Backup**: Everything is saved - script, prompts, consistency guides, metadata

## File Summary

| File | When to Use |
|------|-------------|
| `00_INDEX.md` | Start here - see what's available |
| `01_SCRIPT_README.md` | Read the full story |
| `02_IMAGE_PROMPTS.md` | Copy prompts to Midjourney/Stable Diffusion |
| `03_CHARACTER_REFERENCES.md` | Check when generating character images |
| `04_VOICE_GUIDELINES.md` | Use when writing dialogue |
| `05_YOUTUBE_METADATA.md` | Copy when uploading to YouTube |

All files are organized in a Google Drive folder named after your story title! 🎬
