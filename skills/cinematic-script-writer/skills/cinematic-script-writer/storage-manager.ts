/**
 * Storage Manager
 * Manages saving all generated content to storage (Google Drive, Local, etc.)
 */

import * as fs from 'fs';
import * as path from 'path';
import {
  StorageAdapter,
  StorageFactory,
  StorageConfig,
  StorageFolder,
  GoogleDriveAdapter
} from './storage-adapter';

export interface StoragePreferences {
  provider: 'google-drive' | 'local' | 'ask-every-time';
  defaultFolder?: string;
  autoSave: boolean;
  askBeforeSave: boolean;
}

export interface SaveOptions {
  title: string;
  contextId: string;
  scriptId?: string;
  includeScript?: boolean;
  includePrompts?: boolean;
  includeConsistency?: boolean;
  includeMetadata?: boolean;
  includeVoice?: boolean;
}

export interface SaveResult {
  success: boolean;
  folder: StorageFolder;
  files: SavedFile[];
  errors: string[];
  shareLink?: string;
}

export interface SavedFile {
  name: string;
  id: string;
  webViewLink?: string;
  type: 'script' | 'prompts' | 'consistency' | 'metadata' | 'voice' | 'master';
}

export interface StorageStatus {
  connected: boolean;
  provider?: string;
  basePath?: string;
  userInfo?: {
    email?: string;
    name?: string;
  };
  rootFolder?: string;
}

export class StorageManager {
  private adapter: StorageAdapter | null = null;
  private config: StorageConfig | null = null;
  private preferences: StoragePreferences = {
    provider: 'ask-every-time',
    autoSave: false,
    askBeforeSave: true
  };

  private static get configDir(): string {
    const home = process.env.HOME || process.env.USERPROFILE || '';
    return path.join(home, '.cinematic-script');
  }

  private static get configPath(): string {
    return path.join(StorageManager.configDir, 'config.json');
  }

  /**
   * Save current storage config to disk for persistence across sessions
   */
  private saveConfig(): void {
    try {
      fs.mkdirSync(StorageManager.configDir, { recursive: true });
      const data: Record<string, any> = { provider: this.config?.provider };
      if (this.config?.basePath) data.basePath = this.config.basePath;
      if (this.config?.folderId) data.folderId = this.config.folderId;
      fs.writeFileSync(StorageManager.configPath, JSON.stringify(data, null, 2), 'utf-8');
    } catch {
      // Silently ignore write errors (read-only fs, etc.)
    }
  }

  /**
   * Load persisted config and reconnect storage adapter automatically
   */
  async loadConfig(): Promise<boolean> {
    try {
      if (!fs.existsSync(StorageManager.configPath)) return false;
      const raw = JSON.parse(fs.readFileSync(StorageManager.configPath, 'utf-8'));
      if (raw.provider === 'local' && raw.basePath) {
        await this.connectLocal(raw.basePath);
        return true;
      }
    } catch {
      // Silently ignore read/parse errors
    }
    return false;
  }

  /**
   * Remove persisted config
   */
  private clearConfig(): void {
    try {
      if (fs.existsSync(StorageManager.configPath)) {
        fs.unlinkSync(StorageManager.configPath);
      }
    } catch {
      // Silently ignore
    }
  }

  /**
   * Check if storage is configured and connected
   */
  async getStatus(): Promise<StorageStatus> {
    if (!this.adapter || !this.config) {
      return { connected: false };
    }

    return {
      connected: this.adapter.isConnected(),
      provider: this.config.provider,
      basePath: this.config.basePath
    };
  }

  /**
   * Ask user where to store files
   */
  async askStorageLocation(): Promise<any> {
    // In a real implementation, this would show UI to user
    // For OpenClaw skill, this returns the question structure
    return {
      question: "Where would you like to store your generated files?",
      options: [
        {
          id: 'google-drive',
          label: '📁 Google Drive',
          description: 'Save to your Google Drive account'
        },
        {
          id: 'local',
          label: '💻 Local Download',
          description: 'Download files to your computer'
        },
        {
          id: 'ask-later',
          label: '❓ Ask me later',
          description: 'Decide when saving each time'
        }
      ]
    };
  }

  /**
   * Connect to Google Drive with OAuth
   */
  /**
   * Load Google OAuth credentials from env vars.
   * Supports:
   *   GOOGLE_CLIENT_SECRET=/path/to/client_secret.json  (file path)
   *   or GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET as raw values
   */
  private loadGoogleCredentials(): { clientId: string; clientSecret: string } {
    const secretEnv = process.env.GOOGLE_CLIENT_SECRET || '';

    // If it looks like a file path, read and parse the JSON
    if (secretEnv.endsWith('.json') && fs.existsSync(secretEnv)) {
      const raw = JSON.parse(fs.readFileSync(secretEnv, 'utf-8'));
      // Google client secret JSON has credentials under "installed" or "web" key
      const creds = raw.installed || raw.web;
      if (creds) {
        return { clientId: creds.client_id, clientSecret: creds.client_secret };
      }
    }

    return {
      clientId: process.env.GOOGLE_CLIENT_ID || 'YOUR_CLIENT_ID',
      clientSecret: secretEnv || 'YOUR_CLIENT_SECRET',
    };
  }

  async connectGoogleDrive(authCode?: string): Promise<{
    success: boolean;
    authUrl?: string;
    needsAuth: boolean;
    message: string;
  }> {
    const { clientId, clientSecret } = this.loadGoogleCredentials();

    // If no auth code, provide the auth URL
    if (!authCode) {
      const redirectUri = 'urn:ietf:wg:oauth:2.0:oob'; // Out-of-band for CLI

      const authUrl = GoogleDriveAdapter.getAuthUrl(clientId, redirectUri, 'cinematic-writer');

      return {
        success: false,
        authUrl,
        needsAuth: true,
        message: `Please authorize access to your Google Drive:\n${authUrl}\n\nAfter authorization, paste the code here.`
      };
    }

    // Exchange code for tokens
    try {
      const redirectUri = 'urn:ietf:wg:oauth:2.0:oob';

      const tokens = await GoogleDriveAdapter.exchangeCode(
        authCode,
        clientId,
        clientSecret,
        redirectUri
      );

      // Connect with tokens
      this.config = {
        provider: 'google-drive',
        credentials: {
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token
        }
      };

      this.adapter = StorageFactory.createAdapter('google-drive');
      const connected = await this.adapter.connect(this.config);

      if (connected) {
        this.preferences.provider = 'google-drive';
        return {
          success: true,
          needsAuth: false,
          message: '✅ Successfully connected to Google Drive!'
        };
      }
    } catch (error) {
      return {
        success: false,
        needsAuth: true,
        message: `Failed to connect: ${error}`
      };
    }

    return {
      success: false,
      needsAuth: true,
      message: 'Unknown error connecting to Google Drive'
    };
  }

  /**
   * Connect to local storage (downloads)
   */
  async connectLocal(basePath?: string): Promise<{ success: boolean; message: string }> {
    const resolvedPath = basePath
      ? path.resolve(basePath)
      : path.resolve('./downloads');

    this.config = {
      provider: 'local',
      basePath: resolvedPath
    };

    this.adapter = StorageFactory.createAdapter('local');
    const connected = await this.adapter.connect(this.config);

    if (connected) {
      this.preferences.provider = 'local';
      this.saveConfig();
      return {
        success: true,
        message: `✅ Local storage configured. Files will be saved to ${resolvedPath}`
      };
    }

    return {
      success: false,
      message: 'Failed to configure local storage'
    };
  }

  /**
   * Disconnect from storage
   */
  async disconnect(): Promise<void> {
    if (this.adapter) {
      await this.adapter.disconnect();
      this.adapter = null;
      this.config = null;
      this.clearConfig();
    }
  }

  /**
   * Save all generated content
   */
  async saveAll(
    options: SaveOptions,
    content: {
      script?: any;
      prompts?: any;
      consistency?: any;
      metadata?: any;
      voice?: any;
      storyIdea?: any;
      context?: any;
    }
  ): Promise<SaveResult> {
    if (!this.adapter || !this.adapter.isConnected()) {
      // Try to connect based on preferences
      if (this.preferences.provider === 'google-drive') {
        const result = await this.connectGoogleDrive();
        if (!result.success) {
          return {
            success: false,
            folder: { id: '', name: '', path: '' },
            files: [],
            errors: ['Not connected to storage. Please connect first.']
          };
        }
      }
    }

    if (!this.adapter) {
      return {
        success: false,
        folder: { id: '', name: '', path: '' },
        files: [],
        errors: ['No storage adapter configured']
      };
    }

    const result: SaveResult = {
      success: false,
      folder: { id: '', name: '', path: '' },
      files: [],
      errors: []
    };

    try {
      // 1. Create folder with title
      const folderName = this.sanitizeFolderName(options.title);
      const folder = await this.adapter.createFolder(folderName);
      result.folder = folder;

      // 2. Save master index file
      const indexFile = this.createIndexFile(options, content);
      const savedIndex = await this.adapter.createFile(folder.id, {
        name: '00_INDEX.md',
        content: indexFile,
        mimeType: 'text/markdown'
      });
      result.files.push({
        name: '00_INDEX.md',
        id: savedIndex.id,
        webViewLink: savedIndex.webViewLink,
        type: 'master'
      });

      // 3. Save script
      if (options.includeScript !== false && content.script) {
        const scriptContent = JSON.stringify(content.script, null, 2);
        const savedScript = await this.adapter.createFile(folder.id, {
          name: '01_SCRIPT.json',
          content: scriptContent,
          mimeType: 'application/json'
        });
        result.files.push({
          name: '01_SCRIPT.json',
          id: savedScript.id,
          webViewLink: savedScript.webViewLink,
          type: 'script'
        });

        // Also save human-readable version
        const scriptMd = this.formatScriptAsMarkdown(content.script);
        const savedScriptMd = await this.adapter.createFile(folder.id, {
          name: '01_SCRIPT_README.md',
          content: scriptMd,
          mimeType: 'text/markdown'
        });
        result.files.push({
          name: '01_SCRIPT_README.md',
          id: savedScriptMd.id,
          webViewLink: savedScriptMd.webViewLink,
          type: 'script'
        });
      }

      // 4. Save prompts
      if (options.includePrompts !== false && content.prompts) {
        const promptsContent = JSON.stringify(content.prompts, null, 2);
        const savedPrompts = await this.adapter.createFile(folder.id, {
          name: '02_PROMPTS.json',
          content: promptsContent,
          mimeType: 'application/json'
        });
        result.files.push({
          name: '02_PROMPTS.json',
          id: savedPrompts.id,
          webViewLink: savedPrompts.webViewLink,
          type: 'prompts'
        });

        // Save image prompts separately for easy copy
        const imagePromptsMd = this.formatImagePrompts(content.prompts);
        const savedImagePrompts = await this.adapter.createFile(folder.id, {
          name: '02_IMAGE_PROMPTS.md',
          content: imagePromptsMd,
          mimeType: 'text/markdown'
        });
        result.files.push({
          name: '02_IMAGE_PROMPTS.md',
          id: savedImagePrompts.id,
          webViewLink: savedImagePrompts.webViewLink,
          type: 'prompts'
        });
      }

      // 5. Save consistency guides
      if (options.includeConsistency !== false && content.consistency) {
        const consistencyContent = JSON.stringify(content.consistency, null, 2);
        const savedConsistency = await this.adapter.createFile(folder.id, {
          name: '03_CONSISTENCY.json',
          content: consistencyContent,
          mimeType: 'application/json'
        });
        result.files.push({
          name: '03_CONSISTENCY.json',
          id: savedConsistency.id,
          webViewLink: savedConsistency.webViewLink,
          type: 'consistency'
        });

        // Save character reference sheets
        if (content.consistency.characters) {
          const charRefsMd = this.formatCharacterReferences(content.consistency.characters);
          const savedCharRefs = await this.adapter.createFile(folder.id, {
            name: '03_CHARACTER_REFERENCES.md',
            content: charRefsMd,
            mimeType: 'text/markdown'
          });
          result.files.push({
            name: '03_CHARACTER_REFERENCES.md',
            id: savedCharRefs.id,
            webViewLink: savedCharRefs.webViewLink,
            type: 'consistency'
          });
        }

        // Save environment guide
        if (content.consistency.environment) {
          const envGuideMd = this.formatEnvironmentGuide(content.consistency.environment);
          const savedEnvGuide = await this.adapter.createFile(folder.id, {
            name: '03_ENVIRONMENT_GUIDE.md',
            content: envGuideMd,
            mimeType: 'text/markdown'
          });
          result.files.push({
            name: '03_ENVIRONMENT_GUIDE.md',
            id: savedEnvGuide.id,
            webViewLink: savedEnvGuide.webViewLink,
            type: 'consistency'
          });
        }
      }

      // 6. Save voice profiles
      if (options.includeVoice !== false && content.voice) {
        const voiceContent = JSON.stringify(content.voice, null, 2);
        const savedVoice = await this.adapter.createFile(folder.id, {
          name: '04_VOICE_PROFILES.json',
          content: voiceContent,
          mimeType: 'application/json'
        });
        result.files.push({
          name: '04_VOICE_PROFILES.json',
          id: savedVoice.id,
          webViewLink: savedVoice.webViewLink,
          type: 'voice'
        });

        const voiceMd = this.formatVoiceProfiles(content.voice);
        const savedVoiceMd = await this.adapter.createFile(folder.id, {
          name: '04_VOICE_GUIDELINES.md',
          content: voiceMd,
          mimeType: 'text/markdown'
        });
        result.files.push({
          name: '04_VOICE_GUIDELINES.md',
          id: savedVoiceMd.id,
          webViewLink: savedVoiceMd.webViewLink,
          type: 'voice'
        });
      }

      // 7. Save metadata
      if (options.includeMetadata !== false && content.metadata) {
        const metadataContent = JSON.stringify(content.metadata, null, 2);
        const savedMetadata = await this.adapter.createFile(folder.id, {
          name: '05_YOUTUBE_METADATA.json',
          content: metadataContent,
          mimeType: 'application/json'
        });
        result.files.push({
          name: '05_YOUTUBE_METADATA.json',
          id: savedMetadata.id,
          webViewLink: savedMetadata.webViewLink,
          type: 'metadata'
        });

        const metadataMd = this.formatMetadata(content.metadata);
        const savedMetadataMd = await this.adapter.createFile(folder.id, {
          name: '05_YOUTUBE_METADATA.md',
          content: metadataMd,
          mimeType: 'text/markdown'
        });
        result.files.push({
          name: '05_YOUTUBE_METADATA.md',
          id: savedMetadataMd.id,
          webViewLink: savedMetadataMd.webViewLink,
          type: 'metadata'
        });
      }

      // 8. Save context info
      if (content.context) {
        const contextMd = this.formatContextInfo(content.context, content.storyIdea);
        const savedContext = await this.adapter.createFile(folder.id, {
          name: '99_CONTEXT_INFO.md',
          content: contextMd,
          mimeType: 'text/markdown'
        });
        result.files.push({
          name: '99_CONTEXT_INFO.md',
          id: savedContext.id,
          webViewLink: savedContext.webViewLink,
          type: 'master'
        });
      }

      result.success = true;
      result.shareLink = folder.webViewLink;

    } catch (error) {
      result.errors.push(`Save failed: ${error}`);
    }

    return result;
  }

  /**
   * Sanitize folder name
   */
  private sanitizeFolderName(title: string): string {
    // Remove special characters, limit length
    return title
      .replace(/[<>:"/\\|?*]/g, '_')
      .substring(0, 100)
      .trim() || 'Untitled_Project';
  }

  /**
   * Create master index file
   */
  private createIndexFile(options: SaveOptions, content: any): string {
    const lines = [
      `# ${options.title}`,
      '',
      'Generated by Cinematic Script Writer',
      `Date: ${new Date().toLocaleString()}`,
      '',
      '## 📁 Contents',
      '',
      '| File | Description |',
      '|------|-------------|',
      '| 00_INDEX.md | This file - overview of all content |',
    ];

    if (options.includeScript !== false) {
      lines.push('| 01_SCRIPT.json | Full script data (JSON) |');
      lines.push('| 01_SCRIPT_README.md | Human-readable script |');
    }

    if (options.includePrompts !== false) {
      lines.push('| 02_PROMPTS.json | All prompts data (JSON) |');
      lines.push('| 02_IMAGE_PROMPTS.md | Copy-paste image prompts |');
    }

    if (options.includeConsistency !== false) {
      lines.push('| 03_CONSISTENCY.json | Consistency data (JSON) |');
      lines.push('| 03_CHARACTER_REFERENCES.md | Character design references |');
      lines.push('| 03_ENVIRONMENT_GUIDE.md | Era/style environment guide |');
    }

    if (options.includeVoice !== false) {
      lines.push('| 04_VOICE_PROFILES.json | Voice data (JSON) |');
      lines.push('| 04_VOICE_GUIDELINES.md | Voice/dialogue guidelines |');
    }

    if (options.includeMetadata !== false) {
      lines.push('| 05_YOUTUBE_METADATA.json | YouTube metadata (JSON) |');
      lines.push('| 05_YOUTUBE_METADATA.md | YouTube title/description/tags |');
    }

    lines.push('| 99_CONTEXT_INFO.md | Story context and background |');
    lines.push('');
    lines.push('## 🎬 Quick Start');
    lines.push('');
    lines.push('1. **Script**: Read `01_SCRIPT_README.md` for the full story');
    lines.push('2. **Images**: Copy prompts from `02_IMAGE_PROMPTS.md` to Midjourney/Stable Diffusion');
    lines.push('3. **Consistency**: Check `03_CHARACTER_REFERENCES.md` to keep characters consistent');
    lines.push('4. **Voice**: Use `04_VOICE_GUIDELINES.md` for dialogue writing');
    lines.push('5. **YouTube**: Use `05_YOUTUBE_METADATA.md` for upload');
    lines.push('');

    return lines.join('\n');
  }

  /**
   * Format script as markdown
   */
  private formatScriptAsMarkdown(script: any): string {
    const lines = [
      `# ${script.title}`,
      '',
      '## 🪝 Hook',
      '',
      script.hook?.text || '',
      '',
      `**Duration:** ${script.hook?.duration}s`,
      '',
      '---',
      ''
    ];

    // Add scenes
    if (script.scenes) {
      script.scenes.forEach((scene: any, i: number) => {
        lines.push(`## 🎬 Scene ${scene.number}: ${scene.title}`);
        lines.push('');
        lines.push(`**Duration:** ${scene.duration}s | **Location:** ${scene.location}`);
        lines.push('');
        lines.push('### Synopsis');
        lines.push(scene.synopsis);
        lines.push('');

        // Shots
        if (scene.shots) {
          lines.push('### 📷 Shots');
          lines.push('');
          scene.shots.forEach((shot: any) => {
            lines.push(`**Shot ${shot.shotNumber}** - ${shot.type} | ${shot.cameraAngle} | ${shot.duration}s`);
            lines.push('');
            lines.push(`Description: ${shot.description}`);
            lines.push('');
            lines.push('**Image Prompt:**');
            lines.push('```');
            lines.push(shot.imagePrompt);
            lines.push('```');
            lines.push('');
            lines.push('**Video Prompt:**');
            lines.push('```');
            lines.push(shot.videoPrompt);
            lines.push('```');
            lines.push('');
          });
        }

        // Dialogues
        if (scene.dialogues) {
          lines.push('### 💬 Dialogue');
          lines.push('');
          scene.dialogues.forEach((dialogue: any) => {
            const punchline = dialogue.isPunchline ? ' 💥' : '';
            lines.push(`**${dialogue.character}:** ${dialogue.text}${punchline}`);
            lines.push(`*(${dialogue.tone}, ${dialogue.delivery})*`);
            lines.push('');
          });
        }

        lines.push('---');
        lines.push('');
      });
    }

    return lines.join('\n');
  }

  /**
   * Format image prompts
   */
  private formatImagePrompts(prompts: any): string {
    const lines = [
      '# Image & Video Generation Prompts',
      '',
      'Copy these prompts into your AI image/video generation tool:',
      '',
      '---',
      ''
    ];

    if (prompts.shots) {
      prompts.shots.forEach((shot: any, i: number) => {
        lines.push(`## Shot ${i + 1}: ${shot.type} - ${shot.description?.substring(0, 50)}...`);
        lines.push('');
        lines.push('### Image Prompt (Midjourney/Stable Diffusion)');
        lines.push('```');
        lines.push(shot.imagePrompt || 'N/A');
        lines.push('```');
        lines.push('');
        lines.push('### Video Prompt (Veo/Sora/Runway)');
        lines.push('```');
        lines.push(shot.videoPrompt || 'N/A');
        lines.push('```');
        lines.push('');
        lines.push('### Negative Prompt');
        lines.push('```');
        lines.push(prompts.negativePrompt || '');
        lines.push('```');
        lines.push('');
        lines.push('---');
        lines.push('');
      });
    }

    return lines.join('\n');
  }

  /**
   * Format character references
   */
  private formatCharacterReferences(characters: any): string {
    const lines = [
      '# Character Reference Sheets',
      '',
      'Use these references to keep characters consistent across all images:',
      '',
      '---',
      ''
    ];

    Object.entries(characters).forEach(([id, char]: [string, any]) => {
      lines.push(`# ${char.characterName}`);
      lines.push('');
      lines.push('## Visual Description');
      lines.push(char.visual?.baseDescription || '');
      lines.push('');

      if (char.visual?.colorPalette) {
        lines.push('## Color Palette');
        lines.push(`- **Signature:** ${char.visual.colorPalette.signature}`);
        lines.push(`- **Primary:** ${char.visual.colorPalette.primary?.join(', ')}`);
        lines.push(`- **Hair:** ${char.visual.colorPalette.hair}`);
        lines.push(`- **Eyes:** ${char.visual.colorPalette.eyes}`);
        lines.push('');
      }

      if (char.wardrobe?.defaultOutfit) {
        lines.push('## Default Outfit');
        lines.push(char.wardrobe.defaultOutfit.description);
        lines.push('');
      }

      if (char.style?.consistencyKeywords) {
        lines.push('## Consistency Keywords');
        lines.push('Always include these in prompts:');
        char.style.consistencyKeywords.forEach((kw: string) => {
          lines.push(`- ${kw}`);
        });
        lines.push('');
      }

      if (char.style?.negativePrompts) {
        lines.push('## Negative Prompts');
        lines.push('Always exclude these:');
        char.style.negativePrompts.forEach((np: string) => {
          lines.push(`- ${np}`);
        });
        lines.push('');
      }

      lines.push('---');
      lines.push('');
    });

    return lines.join('\n');
  }

  /**
   * Format environment guide
   */
  private formatEnvironmentGuide(env: any): string {
    const lines = [
      '# Environment Style Guide',
      '',
      `## ${env.era} | ${env.location}`,
      '',
      '## Architecture',
      ''
    ];

    if (env.architecture?.buildingStyles) {
      env.architecture.buildingStyles.forEach((style: any) => {
        lines.push(`### ${style.type}`);
        lines.push(style.description);
        lines.push(`- **Materials:** ${style.materials?.join(', ')}`);
        lines.push(`- **Features:** ${style.features?.join(', ')}`);
        lines.push('');
      });
    }

    lines.push('## Clothing Materials');
    lines.push(env.clothing?.materials?.join(', ') || 'N/A');
    lines.push('');

    lines.push('## Forbidden Elements (Anachronisms)');
    lines.push('NEVER include these:');
    env.eraSpecs?.anachronismsForbidden?.forEach((item: string) => {
      lines.push(`- ❌ ${item}`);
    });
    lines.push('');

    return lines.join('\n');
  }

  /**
   * Format voice profiles
   */
  private formatVoiceProfiles(voices: any): string {
    const lines = [
      '# Voice Guidelines',
      '',
      'Use these guidelines for consistent character dialogue:',
      '',
      '---',
      ''
    ];

    Object.entries(voices).forEach(([id, voice]: [string, any]) => {
      lines.push(`# ${voice.characterName}`);
      lines.push('');

      if (voice.speech) {
        lines.push('## Speech Characteristics');
        lines.push(`- **Pitch:** ${voice.speech.pitch}`);
        lines.push(`- **Speed:** ${voice.speech.speed}`);
        lines.push(`- **Volume:** ${voice.speech.volume}`);
        lines.push(`- **Clarity:** ${voice.speech.clarity}`);
        lines.push('');
      }

      if (voice.language) {
        lines.push('## Language');
        lines.push(`- **Vocabulary:** ${voice.language.vocabularyLevel}`);
        lines.push(`- **Formality:** ${voice.language.formality}`);
        lines.push('');

        if (voice.language.catchphrases?.length > 0) {
          lines.push('## Catchphrases');
          voice.language.catchphrases.forEach((phrase: string) => {
            lines.push(`- "${phrase}"`);
          });
          lines.push('');
        }
      }

      if (voice.examples) {
        lines.push('## Speech Examples');
        lines.push(`- **Greeting:** "${voice.examples.greeting}"`);
        lines.push(`- **Question:** "${voice.examples.question}"`);
        lines.push(`- **Exclamation:** "${voice.examples.exclamation}"`);
        lines.push('');
      }

      lines.push('---');
      lines.push('');
    });

    return lines.join('\n');
  }

  /**
   * Format metadata
   */
  private formatMetadata(metadata: any): string {
    return [
      '# YouTube Metadata',
      '',
      '## Title',
      '',
      metadata.title || '',
      '',
      '## Description',
      '',
      '```',
      metadata.description || '',
      '```',
      '',
      '## Tags',
      '',
      metadata.tags?.join(', ') || '',
      '',
      '## Category',
      '',
      metadata.category || 'Film & Animation',
      '',
      '## Thumbnail Idea',
      '',
      metadata.thumbnailIdea || '',
      ''
    ].join('\n');
  }

  /**
   * Format context info
   */
  private formatContextInfo(context: any, storyIdea?: any): string {
    const lines = [
      '# Context Information',
      '',
      '## Story',
      '',
      `**Title:** ${storyIdea?.title || context.name || 'Untitled'}`,
      `**Era:** ${context.era}`,
      `**Period:** ${context.period}`,
      `**Location:** ${context.location}`,
      `**Tone:** ${context.tone}`,
      `**Type:** ${context.videoType}`,
      '',
      '## Synopsis',
      '',
      context.description || '',
      '',
      '## Characters',
      ''
    ];

    if (context.characters) {
      context.characters.forEach((char: any) => {
        lines.push(`### ${char.name} (${char.role})`);
        lines.push(char.description);
        lines.push(`**Personality:** ${char.personality}`);
        lines.push(`**Appearance:** ${char.appearance}`);
        if (char.backstory) {
          lines.push(`**Backstory:** ${char.backstory}`);
        }
        lines.push('');
      });
    }

    lines.push('## Visual Style');
    lines.push(context.visualStyle || '');
    lines.push('');

    return lines.join('\n');
  }
}

export default StorageManager;
