#!/usr/bin/env node
/**
 * voiceai-vo — Voice.ai Creator Voiceover Pipeline
 * Turn scripts into publishable voiceovers with one command.
 */
import { config } from 'dotenv';
import { Command } from 'commander';
import { buildCommand } from './commands/build.js';
import { replaceAudioCommand } from './commands/replace-audio.js';
import { voicesCommand } from './commands/voices.js';

// Load .env from project root
config();

const program = new Command();

program
  .name('voiceai-vo')
  .description('Voice.ai Creator Voiceover Pipeline — script → segments → master → video')
  .version('0.1.0');

/* ------------------------------------------------------------------ */
/*  build                                                              */
/* ------------------------------------------------------------------ */

program
  .command('build')
  .description('Build a voiceover from a script file')
  .requiredOption('-i, --input <path>', 'Path to script file (.txt or .md)')
  .requiredOption('-v, --voice <id>', 'Voice ID (run `voices` to discover)')
  .option('-t, --title <title>', 'Project title (defaults to filename)')
  .option('--template <name>', 'Template: youtube, podcast, or shortform')
  .option('--mode <mode>', 'Chunk mode: headings or auto (default: headings for .md)')
  .option('--max-chars <n>', 'Max characters per auto-chunk (default: 1500)')
  .option('--language <code>', 'Language code (default: en)')
  .option('--video <path>', 'Input video file for muxing')
  .option('--mux', 'Enable video muxing (requires --video)')
  .option('--sync <policy>', 'Sync policy: shortest, pad, trim (default: shortest)')
  .option('--force', 'Force re-render all segments (ignore cache)')
  .option('--mock', 'Run in mock mode (no real API calls)')
  .option('-o, --out <dir>', 'Custom output directory')
  .action(buildCommand);

/* ------------------------------------------------------------------ */
/*  replace-audio                                                      */
/* ------------------------------------------------------------------ */

program
  .command('replace-audio')
  .description('Replace the audio track of a video with a voiceover')
  .requiredOption('--video <path>', 'Input video file')
  .requiredOption('--audio <path>', 'Audio file to mux in (e.g. master.wav)')
  .option('--out <path>', 'Output video path (default: muxed.mp4 next to audio)')
  .option('--sync <policy>', 'Sync policy: shortest, pad, trim (default: shortest)')
  .action(replaceAudioCommand);

/* ------------------------------------------------------------------ */
/*  voices                                                             */
/* ------------------------------------------------------------------ */

program
  .command('voices')
  .description('List available Voice.ai voices')
  .option('-l, --limit <n>', 'Max voices to show (default: 20)')
  .option('-q, --query <term>', 'Search voices by name or description')
  .option('--mock', 'Use mock voice catalog')
  .action(voicesCommand);

/* ------------------------------------------------------------------ */
/*  Parse + run                                                        */
/* ------------------------------------------------------------------ */

program.parse();
