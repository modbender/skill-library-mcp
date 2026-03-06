/**
 * FFmpeg/FFprobe integration — probing, stitching, muxing, encoding.
 * Falls back to generating helper scripts when ffmpeg is not installed.
 */
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { join } from 'node:path';
import { writeFile } from 'node:fs/promises';
import chalk from 'chalk';
import { ensureDir, writeOutputFile } from './utils.js';

const exec = promisify(execFile);

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

export type SyncPolicy = 'shortest' | 'pad' | 'trim';

export interface MuxOptions {
  videoPath: string;
  audioPath: string;
  outputPath: string;
  syncPolicy: SyncPolicy;
}

export interface MuxResult {
  success: boolean;
  outputPath: string;
  videoDuration: number | null;
  audioDuration: number | null;
  syncPolicy: SyncPolicy;
  ffmpegCommand: string;
  error?: string;
}

export interface FfmpegAvailability {
  ffmpeg: boolean;
  ffprobe: boolean;
}

/* ------------------------------------------------------------------ */
/*  Availability check                                                 */
/* ------------------------------------------------------------------ */

export async function checkFfmpeg(): Promise<FfmpegAvailability> {
  const check = async (bin: string): Promise<boolean> => {
    try {
      await exec(bin, ['-version']);
      return true;
    } catch {
      return false;
    }
  };

  const [ffmpeg, ffprobe] = await Promise.all([check('ffmpeg'), check('ffprobe')]);
  return { ffmpeg, ffprobe };
}

/* ------------------------------------------------------------------ */
/*  Probe duration                                                     */
/* ------------------------------------------------------------------ */

export async function probeDuration(filePath: string): Promise<number | null> {
  try {
    const { stdout } = await exec('ffprobe', [
      '-v', 'quiet',
      '-print_format', 'json',
      '-show_format',
      filePath,
    ]);
    const data = JSON.parse(stdout);
    const dur = parseFloat(data?.format?.duration);
    return isNaN(dur) ? null : dur;
  } catch {
    return null;
  }
}

/* ------------------------------------------------------------------ */
/*  Stitch segments into master                                        */
/* ------------------------------------------------------------------ */

export async function stitchSegments(
  segmentPaths: string[],
  outputPath: string,
): Promise<boolean> {
  // Build concat file list
  const concatDir = join(outputPath, '..', '..');
  const concatFile = join(concatDir, 'tmp', 'concat.txt');
  await ensureDir(join(concatDir, 'tmp'));

  const concatContent = segmentPaths
    .map((p) => `file '${p.replace(/'/g, "'\\''")}'`)
    .join('\n');
  await writeFile(concatFile, concatContent);

  try {
    await exec('ffmpeg', [
      '-y',
      '-f', 'concat',
      '-safe', '0',
      '-i', concatFile,
      '-c', 'copy',
      outputPath,
    ]);
    return true;
  } catch (err) {
    console.error(chalk.yellow(`   ⚠ Stitch failed, trying re-encode…`));
    try {
      // Fallback: re-encode with consistent format
      await exec('ffmpeg', [
        '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', concatFile,
        '-ar', '22050',
        '-ac', '1',
        '-sample_fmt', 's16',
        outputPath,
      ]);
      return true;
    } catch {
      return false;
    }
  }
}

/* ------------------------------------------------------------------ */
/*  Encode to mp3                                                      */
/* ------------------------------------------------------------------ */

export async function encodeToMp3(inputPath: string, outputPath: string): Promise<boolean> {
  try {
    await exec('ffmpeg', ['-y', '-i', inputPath, '-codec:a', 'libmp3lame', '-q:a', '2', outputPath]);
    return true;
  } catch {
    return false;
  }
}

/* ------------------------------------------------------------------ */
/*  Simple loudness normalization                                      */
/* ------------------------------------------------------------------ */

export async function normalizeLoudness(inputPath: string, outputPath: string): Promise<boolean> {
  try {
    // Two-pass loudnorm (integrated -16 LUFS for YouTube/podcast)
    const { stdout: analysisJson } = await exec('ffmpeg', [
      '-y', '-i', inputPath,
      '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json',
      '-f', 'null', '-',
    ]);

    // Simple single-pass normalization (good enough for MVP)
    await exec('ffmpeg', [
      '-y', '-i', inputPath,
      '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
      outputPath,
    ]);
    return true;
  } catch {
    return false;
  }
}

/* ------------------------------------------------------------------ */
/*  Mux audio into video                                               */
/* ------------------------------------------------------------------ */

function buildMuxArgs(opts: MuxOptions): string[] {
  const args = ['-y', '-i', opts.videoPath, '-i', opts.audioPath];

  switch (opts.syncPolicy) {
    case 'shortest':
      args.push('-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-map', '0:v:0', '-map', '1:a:0', '-shortest');
      break;
    case 'pad':
      // Pad audio with silence to match video — we add an apad filter
      args.push('-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-map', '0:v:0', '-map', '1:a:0', '-af', 'apad', '-shortest');
      break;
    case 'trim':
      // Trim audio to video duration — shortest does this naturally
      args.push('-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-map', '0:v:0', '-map', '1:a:0', '-shortest');
      break;
  }

  args.push(opts.outputPath);
  return args;
}

export async function muxAudioVideo(opts: MuxOptions): Promise<MuxResult> {
  const ffmpegArgs = buildMuxArgs(opts);
  const command = `ffmpeg ${ffmpegArgs.map((a) => (a.includes(' ') ? `"${a}"` : a)).join(' ')}`;

  const videoDuration = await probeDuration(opts.videoPath);
  const audioDuration = await probeDuration(opts.audioPath);

  console.log(chalk.cyan('\n🎬 Muxing audio into video…'));
  console.log(chalk.gray(`   Video: ${opts.videoPath} (${videoDuration?.toFixed(1) ?? '?'}s)`));
  console.log(chalk.gray(`   Audio: ${opts.audioPath} (${audioDuration?.toFixed(1) ?? '?'}s)`));
  console.log(chalk.gray(`   Sync:  ${opts.syncPolicy}`));

  try {
    await exec('ffmpeg', ffmpegArgs);
    console.log(chalk.green(`   ✅ Muxed → ${opts.outputPath}`));
    return {
      success: true,
      outputPath: opts.outputPath,
      videoDuration,
      audioDuration,
      syncPolicy: opts.syncPolicy,
      ffmpegCommand: command,
    };
  } catch (err) {
    const errMsg = err instanceof Error ? err.message : String(err);
    console.error(chalk.red(`   ✗ Mux failed: ${errMsg}`));
    return {
      success: false,
      outputPath: opts.outputPath,
      videoDuration,
      audioDuration,
      syncPolicy: opts.syncPolicy,
      ffmpegCommand: command,
      error: errMsg,
    };
  }
}

/* ------------------------------------------------------------------ */
/*  Fallback helper scripts (when ffmpeg not installed)                 */
/* ------------------------------------------------------------------ */

export async function generateMuxScripts(
  videoPath: string,
  audioPath: string,
  outputPath: string,
  syncPolicy: SyncPolicy,
  outDir: string,
): Promise<void> {
  const ffmpegDir = join(outDir, 'ffmpeg');
  await ensureDir(ffmpegDir);

  const args = buildMuxArgs({ videoPath, audioPath, outputPath, syncPolicy });
  const cmdString = `ffmpeg ${args.map((a) => (a.includes(' ') ? `"${a}"` : a)).join(' ')}`;

  // Bash script
  const bash = `#!/usr/bin/env bash
# Replace Audio — generated by voiceai-creator-voiceover-pipeline
# Sync policy: ${syncPolicy}
#
# Prerequisites: Install ffmpeg (https://ffmpeg.org/download.html)
#   macOS:   brew install ffmpeg
#   Ubuntu:  sudo apt install ffmpeg
#   Windows: choco install ffmpeg  OR  download from https://ffmpeg.org
#
# Usage: bash replace-audio.sh

set -euo pipefail

VIDEO_INPUT="${videoPath}"
AUDIO_INPUT="${audioPath}"
OUTPUT="${outputPath}"

echo "🎬 Muxing audio into video…"
echo "   Video: \$VIDEO_INPUT"
echo "   Audio: \$AUDIO_INPUT"
echo "   Sync:  ${syncPolicy}"
echo ""

${cmdString}

echo ""
echo "✅ Done → \$OUTPUT"
`;

  // PowerShell script
  const ps1 = `# Replace Audio — generated by voiceai-creator-voiceover-pipeline
# Sync policy: ${syncPolicy}
#
# Prerequisites: Install ffmpeg (https://ffmpeg.org/download.html)
#   Windows: choco install ffmpeg  OR  winget install ffmpeg
#
# Usage: .\\replace-audio.ps1

$ErrorActionPreference = "Stop"

$VideoInput = "${videoPath.replace(/\\/g, '\\\\')}"
$AudioInput = "${audioPath.replace(/\\/g, '\\\\')}"
$Output = "${outputPath.replace(/\\/g, '\\\\')}"

Write-Host "🎬 Muxing audio into video…"
Write-Host "   Video: $VideoInput"
Write-Host "   Audio: $AudioInput"
Write-Host "   Sync:  ${syncPolicy}"
Write-Host ""

${cmdString}

Write-Host ""
Write-Host "✅ Done → $Output"
`;

  await writeOutputFile(join(ffmpegDir, 'replace-audio.sh'), bash);
  await writeOutputFile(join(ffmpegDir, 'replace-audio.ps1'), ps1);
}
