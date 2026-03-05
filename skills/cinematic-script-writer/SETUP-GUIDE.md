# 📖 Complete Setup, Testing & Publishing Guide

This guide walks you through:
1. Creating a GitHub repository
2. Testing the skill
3. Publishing to ClawHub

---

## Step 1: Create GitHub Repository

### Option A: Using GitHub Website (Recommended)

1. **Go to GitHub**: https://github.com/new

2. **Create New Repository**:
   - Repository name: `Cinematic-Writer`
   - Description: `OpenClaw skill for cinematic script generation with consistency and storage`
   - Make it **Public** (or Private if you prefer)
   - **DON'T** initialize with README (we already have one)
   - Click "Create repository"

3. **Connect Local Repository**:
   ```bash
   # In your terminal (PowerShell/CMD), navigate to the project
   cd "D:\My Professional Projects\openclawskills"
   
   # Add the GitHub remote
   git remote add origin https://github.com/YOUR_USERNAME/openclaw-cinematic-writer.git
   
   # Rename branch to main
   git branch -M main
   
   # Push to GitHub
   git push -u origin main
   ```

4. **Verify**: Visit `https://github.com/YOUR_USERNAME/openclaw-cinematic-writer`

### Option B: Using GitHub CLI

```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Login to GitHub
gh auth login

# Create repository from current directory
gh repo create openclaw-cinematic-writer --public --source=. --push
```

---

## Step 2: Testing the Skill

### A. TypeScript Compilation Test

```bash
# Navigate to project
cd "D:\My Professional Projects\openclawskills"

# Install dependencies
npm install

# Build/compile TypeScript
npm run build

# Check for compilation errors
# Should create dist/ folder with compiled JS
```

### B. Lint Test

```bash
# Check code style
npm run lint

# Fix auto-fixable issues
npm run lint:fix
```

### C. Manual Testing Script

Create a test file `test-skill.ts`:

```typescript
import { CinematicScriptWriter } from './skills/cinematic-script-writer';

// Mock context for testing
const mockContext = {
  userId: 'test-user',
  memory: {
    get: async () => null,
    set: async () => {},
    delete: async () => {}
  },
  logger: {
    debug: console.log,
    info: console.log,
    warn: console.warn,
    error: console.error
  }
};

async function testSkill() {
  console.log('🧪 Testing Cinematic Script Writer Skill\n');
  
  const skill = new CinematicScriptWriter({}, mockContext);
  
  // Test 1: Cinematography Database
  console.log('✓ Testing Cinematography Database...');
  const angles = skill.getAllCameraAngles();
  console.log(`  - Found ${Object.keys(angles).length} camera angles`);
  
  const movements = skill.getAllCameraMovements();
  console.log(`  - Found ${Object.keys(movements).length} camera movements`);
  
  const shots = skill.getAllShotTypes();
  console.log(`  - Found ${Object.keys(shots).length} shot types`);
  
  // Test 2: Consistency System
  console.log('\n✓ Testing Consistency System...');
  const charRef = skill.createCharacterReference(
    'test-char',
    'Test Character',
    'Purple fur, golden eyes',
    'Ramayana Era',
    'pixar-3d'
  );
  console.log(`  - Created character reference: ${charRef.characterName}`);
  
  // Test 3: Environment Guide
  console.log('\n✓ Testing Environment Guide...');
  const envGuide = skill.createEnvironmentStyleGuide(
    'test-context',
    'Ramayana Era',
    'Treta Yuga',
    'Lanka',
    'pixar-3d'
  );
  console.log(`  - Created environment guide: ${envGuide.era}`);
  console.log(`  - Forbidden items: ${envGuide.eraSpecs.anachronismsForbidden.slice(0, 3).join(', ')}...`);
  
  // Test 4: Validation
  console.log('\n✓ Testing Anachronism Validation...');
  const badResult = skill.validatePrompt(
    'Character wearing sunglasses',
    ['test-char'],
    'test-context'
  );
  console.log(`  - Detected anachronism: ${!badResult.valid}`);
  console.log(`  - Errors: ${badResult.errors.join(', ')}`);
  
  // Test 5: Prompt Builder
  console.log('\n✓ Testing Prompt Builder...');
  const prompts = skill.buildConsistentPrompts({
    characterIds: ['test-char'],
    contextId: 'test-context',
    shotType: 'close-up',
    cameraAngle: 'eye-level',
    cameraMovement: 'static',
    lighting: 'golden-hour',
    mood: 'happy'
  });
  console.log(`  - Generated image prompt length: ${prompts.imagePrompt.length} chars`);
  console.log(`  - Generated negative prompt length: ${prompts.negativePrompt.length} chars`);
  
  console.log('\n✅ All tests passed!');
}

testSkill().catch(console.error);
```

Run the test:
```bash
npx ts-node test-skill.ts
```

### D. Testing Storage (Manual)

```typescript
// Test storage connection
async function testStorage() {
  const skill = new CinematicScriptWriter({}, mockContext);
  
  // Check status
  const status = await skill.getStorageStatus();
  console.log('Storage status:', status);
  
  // Test Google Drive connection (requires auth)
  // const result = await skill.connectGoogleDrive();
  // console.log('Auth URL:', result.authUrl);
}
```

---

## Step 3: Publishing to ClawHub

### Prerequisites

1. ✅ GitHub repository created
2. ✅ All code committed
3. ✅ README.md is complete
4. ✅ skill.json is properly configured
5. ✅ Tests pass

### ClawHub Submission Process

#### Option 1: Web Interface (Recommended for first time)

1. **Visit ClawHub**: https://clawhub.ai/publish

2. **Fill in the form**:

   ```yaml
   # Basic Information
   Skill Name: cinematic-script-writer
   Version: 1.3.0
   Description: Professional cinematic script generation with character consistency, 
                comprehensive cinematography (175+ techniques), and Google Drive storage.
   
   # Repository
   GitHub URL: https://github.com/YOUR_USERNAME/openclaw-cinematic-writer
   License: MIT
   
   # Entry Point
   Main File: skills/cinematic-script-writer/index.ts
   
   # Configuration
   Config Schema: skills/cinematic-script-writer/schema.json
   
   # Permissions Required
   Permissions:
     - memory:read    (Store/retrieve contexts, scripts)
     - memory:write   (Save generated content)
     - http:request   (Google Drive API)
   
   # Tags
   Tags:
     - creative
     - video
     - script
     - cinematography
     - consistency
     - character-design
     - voice
     - storage
     - google-drive
     - youtube
   
   # Documentation
   README: https://github.com/YOUR_USERNAME/openclaw-cinematic-writer/blob/main/README.md
   Examples: 
     - https://github.com/YOUR_USERNAME/openclaw-cinematic-writer/blob/main/skills/cinematic-script-writer/EXAMPLE-KUTIL.md
   ```

3. **Upload or Provide**:
   - Screenshot/demo GIF (optional but recommended)
   - Video tutorial link (optional)

4. **Submit** and wait for review (usually 1-3 days)

#### Option 2: ClawHub CLI (When Available)

```bash
# Install ClawHub CLI
npm install -g @clawhub/cli

# Login
clawhub login

# Publish from repository
clawhub publish

# Or specify directory
clawhub publish ./skills/cinematic-script-writer
```

#### Option 3: API Submission (Advanced)

```bash
# Create skill bundle
cd skills/cinematic-script-writer
tar -czvf cinematic-script-writer-v1.3.0.tar.gz .

# Submit via API (requires API key from ClawHub)
curl -X POST https://api.clawhub.ai/v1/skills \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F "name=cinematic-script-writer" \
  -F "version=1.3.0" \
  -F "bundle=@cinematic-script-writer-v1.3.0.tar.gz" \
  -F "repository=https://github.com/YOUR_USERNAME/openclaw-cinematic-writer"
```

---

## Step 4: Post-Publication

### Create GitHub Release

1. Go to GitHub → Releases → "Draft a new release"
2. Choose tag: `v1.3.0`
3. Title: `v1.3.0 - Cinematic Script Writer`
4. Description:
   ```markdown
   ## What's New
   - Google Drive storage integration
   - Character/voice/environment consistency
   - 175+ cinematography techniques
   - Anachronism detection
   - YouTube metadata generation
   
   ## Installation
   ```bash
   npx clawhub@latest install cinematic-script-writer
   ```
   ```
5. Publish release

### Announce

- Share on Twitter/X with #OpenClaw hashtag
- Post in OpenClaw Discord/community
- Write a blog post about your skill

---

## Troubleshooting

### Git Push Issues

```bash
# If you get "fatal: unable to access"
# Make sure you're using HTTPS URL
git remote set-url origin https://github.com/YOUR_USERNAME/openclaw-cinematic-writer.git

# Or use SSH
git remote set-url origin git@github.com:YOUR_USERNAME/openclaw-cinematic-writer.git
```

### Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check TypeScript version
npx tsc --version  # Should be 5.0+
```

### ClawHub Rejection

Common reasons and fixes:

| Issue | Fix |
|-------|-----|
| Missing documentation | Add more examples in README |
| Tests fail | Fix errors and add more tests |
| Security concerns | Review and limit permissions |
| Code quality | Run linter, add comments |
| Duplicate skill | Ensure unique functionality |

---

## Quick Reference

```bash
# Full workflow
npm install          # Install dependencies
npm run build        # Compile TypeScript
npm run lint         # Check code style
npm test             # Run tests
git add .            # Stage changes
git commit -m "..."  # Commit
git push origin main # Push to GitHub

# ClawHub commands
clawhub validate     # Validate skill before publishing
clawhub publish      # Publish to ClawHub
clawhub update       # Update published skill
```

---

## Need Help?

- **ClawHub Docs**: https://clawhub.ai/docs
- **OpenClaw Community**: [Discord](https://discord.gg/openclaw)
- **GitHub Issues**: Create issue in your repo

Good luck! 🚀
