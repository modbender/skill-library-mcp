#!/usr/bin/env node

/**
 * Cinematic Script Writer CLI
 * Thin wrapper around the CinematicScriptWriter class for shell usage.
 */

import { CinematicScriptWriter, SkillConfig, SkillContext } from '../skills/cinematic-script-writer/index';

// ---------------------------------------------------------------------------
// Minimal in-memory implementations of MemoryStore and Logger
// ---------------------------------------------------------------------------

const memoryData = new Map<string, any>();

const memory = {
  async get(key: string) { return memoryData.get(key) ?? null; },
  async set(key: string, value: any) { memoryData.set(key, value); },
  async delete(key: string) { memoryData.delete(key); },
};

const logger = {
  debug(msg: string) { if (process.env.DEBUG) console.error('[debug]', msg); },
  info(msg: string) { console.error('[info]', msg); },
  warn(msg: string) { console.error('[warn]', msg); },
  error(msg: string) { console.error('[error]', msg); },
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function createSkill(): CinematicScriptWriter {
  const config: SkillConfig = {};
  const context: SkillContext = { userId: 'cli-user', memory, logger };
  return new CinematicScriptWriter(config, context);
}

function printJson(data: any): void {
  console.log(JSON.stringify(data, null, 2));
}

function requiredArg(args: string[], flag: string): string {
  const idx = args.indexOf(flag);
  if (idx === -1 || idx + 1 >= args.length) {
    console.error(`Missing required argument: ${flag}`);
    process.exit(1);
  }
  return args[idx + 1];
}

function optionalArg(args: string[], flag: string, fallback: string): string {
  const idx = args.indexOf(flag);
  if (idx === -1 || idx + 1 >= args.length) return fallback;
  return args[idx + 1];
}

// ---------------------------------------------------------------------------
// Command handlers
// ---------------------------------------------------------------------------

const commands: Record<string, (skill: CinematicScriptWriter, args: string[]) => Promise<void>> = {

  // -- Context Management ---------------------------------------------------

  'create-context': async (skill, args) => {
    const name = requiredArg(args, '--name');
    const description = optionalArg(args, '--description', '');
    const period = optionalArg(args, '--period', 'Modern');
    const era = optionalArg(args, '--era', 'Contemporary');
    const location = optionalArg(args, '--location', 'City');
    const videoType = optionalArg(args, '--video-type', 'short') as any;
    const tone = optionalArg(args, '--tone', 'comedy') as any;
    const audience = optionalArg(args, '--audience', 'General');
    const style = optionalArg(args, '--style', 'cinematic');

    const ctx = await skill.createContext(
      name, description, [], period, era, location, videoType, tone, audience, style,
    );
    printJson(ctx);
  },

  'list-contexts': async (skill) => {
    printJson(await skill.listContexts());
  },

  'get-context': async (skill, args) => {
    const id = requiredArg(args, '--id');
    const ctx = await skill.getContext(id);
    if (!ctx) { console.error('Context not found'); process.exit(1); }
    printJson(ctx);
  },

  'delete-context': async (skill, args) => {
    const id = requiredArg(args, '--id');
    await skill.deleteContext(id);
    console.log('Deleted.');
  },

  // -- Story Generation -----------------------------------------------------

  'generate-ideas': async (skill, args) => {
    const contextId = requiredArg(args, '--context-id');
    const count = parseInt(optionalArg(args, '--count', '3'), 10);
    printJson(await skill.generateStoryIdeas(contextId, count));
  },

  'create-script': async (skill, args) => {
    const contextId = requiredArg(args, '--context-id');
    const ideaId = requiredArg(args, '--idea-id');
    // Load saved ideas to find the matching one
    const ideas = await (skill as any).context.memory.get(
      (skill as any).getStorageKey('ideas', contextId),
    );
    const idea = ideas?.find((i: any) => i.id === ideaId);
    if (!idea) { console.error('Idea not found. Run generate-ideas first.'); process.exit(1); }
    printJson(await skill.createCinematicScript(contextId, ideaId, idea));
  },

  'generate-metadata': async (skill, args) => {
    const scriptId = requiredArg(args, '--script-id');
    printJson(await skill.generateYouTubeMetadata(scriptId));
  },

  // -- Cinematography -------------------------------------------------------

  'list-angles': async (skill) => { printJson(skill.getAllCameraAngles()); },
  'list-movements': async (skill) => { printJson(skill.getAllCameraMovements()); },
  'list-shots': async (skill) => { printJson(skill.getAllShotTypes()); },

  'suggest-camera': async (skill, args) => {
    const sceneType = requiredArg(args, '--scene-type');
    const mood = requiredArg(args, '--mood');
    const level = optionalArg(args, '--level', 'intermediate') as any;
    printJson(skill.getRecommendedCameraSetup(sceneType, mood, level));
  },

  'suggest-lighting': async (skill, args) => {
    const sceneType = requiredArg(args, '--scene-type');
    const mood = requiredArg(args, '--mood');
    printJson(skill.suggestLighting(sceneType, mood));
  },

  'suggest-grading': async (skill, args) => {
    const genre = requiredArg(args, '--genre');
    printJson(skill.suggestColorGrading(genre));
  },

  'search': async (skill, args) => {
    const query = requiredArg(args, '--query');
    printJson(skill.searchCinematography(query));
  },

  // -- Consistency ----------------------------------------------------------

  'create-character-ref': async (skill, args) => {
    const characterId = requiredArg(args, '--character-id');
    const name = requiredArg(args, '--name');
    const visual = requiredArg(args, '--visual');
    const era = requiredArg(args, '--era');
    const style = requiredArg(args, '--style');
    printJson(skill.createCharacterReference(characterId, name, visual, era, style));
  },

  'create-voice': async (skill, args) => {
    const characterId = requiredArg(args, '--character-id');
    const name = requiredArg(args, '--name');
    const personality = requiredArg(args, '--personality');
    const age = optionalArg(args, '--age', 'adult');
    const role = optionalArg(args, '--role', 'supporting');
    printJson(skill.createVoiceProfile(characterId, name, personality, age, role));
  },

  'validate-prompt': async (skill, args) => {
    const prompt = requiredArg(args, '--prompt');
    const charIds = requiredArg(args, '--character-ids').split(',');
    const contextId = requiredArg(args, '--context-id');
    printJson(skill.validatePrompt(prompt, charIds, contextId));
  },

  // -- Storage --------------------------------------------------------------

  'connect-drive': async (skill) => {
    printJson(await skill.connectGoogleDrive());
  },

  'connect-local': async (skill) => {
    printJson(await skill.connectLocalStorage());
  },

  'storage-status': async (skill) => {
    printJson(await skill.getStorageStatus());
  },

  'save': async (skill, args) => {
    const title = requiredArg(args, '--title');
    const contextId = requiredArg(args, '--context-id');
    const scriptId = optionalArg(args, '--script-id', '');
    printJson(await skill.saveScriptToStorage(title, contextId, scriptId));
  },

  // -- Export ---------------------------------------------------------------

  'export': async (skill, args) => {
    const scriptId = requiredArg(args, '--script-id');
    const format = optionalArg(args, '--format', 'markdown') as 'json' | 'text' | 'markdown';
    console.log(await skill.exportScript(scriptId, format));
  },
};

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === '--help' || command === '-h') {
    console.log(`
Cinematic Script Writer CLI

Usage: cinematic-script <command> [options]

Commands:
  Context:
    create-context      Create a new story context
    list-contexts       List all contexts
    get-context         Get a specific context
    delete-context      Delete a context

  Story:
    generate-ideas      Generate story ideas for a context
    create-script       Create a cinematic script from an idea
    generate-metadata   Generate YouTube metadata for a script

  Cinematography:
    list-angles         List all camera angles
    list-movements      List all camera movements
    list-shots          List all shot types
    suggest-camera      Get camera setup recommendation
    suggest-lighting    Get lighting suggestions
    suggest-grading     Get color grading suggestions
    search              Search cinematography database

  Consistency:
    create-character-ref  Create a character reference sheet
    create-voice          Create a voice profile
    validate-prompt       Validate a prompt for anachronisms

  Storage:
    connect-drive       Connect Google Drive
    connect-local       Connect local storage
    storage-status      Check storage connection
    save                Save project to storage

  Export:
    export              Export a script (json, text, markdown)

Run "cinematic-script <command> --help" for command-specific options.
    `.trim());
    process.exit(0);
  }

  const handler = commands[command];
  if (!handler) {
    console.error(`Unknown command: ${command}`);
    console.error('Run "cinematic-script --help" for available commands.');
    process.exit(1);
  }

  const skill = createSkill();
  await handler(skill, args.slice(1));
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
