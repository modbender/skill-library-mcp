/**
 * `voiceai-vo replace-audio` — mux audio into an existing video.
 */
import { resolve, join, dirname } from 'node:path';
import chalk from 'chalk';
import {
  checkFfmpeg,
  muxAudioVideo,
  generateMuxScripts,
  type SyncPolicy,
} from '../ffmpeg.js';
import { fileExists, writeOutputFile, ensureDir } from '../utils.js';

/* ------------------------------------------------------------------ */
/*  Option types                                                       */
/* ------------------------------------------------------------------ */

export interface ReplaceAudioOptions {
  video: string;
  audio: string;
  out?: string;
  sync?: string;
}

/* ------------------------------------------------------------------ */
/*  Command handler                                                    */
/* ------------------------------------------------------------------ */

export async function replaceAudioCommand(opts: ReplaceAudioOptions): Promise<void> {
  // ── Validate inputs ────────────────────────────────────────────────
  if (!opts.video) {
    console.error(chalk.red('✗ --video is required. Pass the input video file.'));
    process.exit(1);
  }

  if (!opts.audio) {
    console.error(chalk.red('✗ --audio is required. Pass the audio file to mux in.'));
    process.exit(1);
  }

  const videoPath = resolve(opts.video);
  const audioPath = resolve(opts.audio);

  if (!(await fileExists(videoPath))) {
    console.error(chalk.red(`✗ Video not found: ${videoPath}`));
    process.exit(1);
  }

  if (!(await fileExists(audioPath))) {
    console.error(chalk.red(`✗ Audio not found: ${audioPath}`));
    process.exit(1);
  }

  const syncPolicy: SyncPolicy = (opts.sync as SyncPolicy) ?? 'shortest';
  if (!['shortest', 'pad', 'trim'].includes(syncPolicy)) {
    console.error(
      chalk.red(`✗ Invalid sync policy: "${syncPolicy}". Use: shortest, pad, or trim.`),
    );
    process.exit(1);
  }

  const outputPath = opts.out ? resolve(opts.out) : resolve(dirname(audioPath), 'muxed.mp4');
  await ensureDir(dirname(outputPath));

  // ── Check ffmpeg ──────────────────────────────────────────────────
  console.log(chalk.bold('\n╔══════════════════════════════════════════════════╗'));
  console.log(chalk.bold('║') + chalk.cyan.bold('   Voice.ai — Replace Audio                        ') + chalk.bold('║'));
  console.log(chalk.bold('╚══════════════════════════════════════════════════╝'));

  const ffAvail = await checkFfmpeg();

  if (ffAvail.ffmpeg) {
    const result = await muxAudioVideo({
      videoPath,
      audioPath,
      outputPath,
      syncPolicy,
    });

    // Save mux report next to output
    const reportPath = outputPath.replace(/\.[^.]+$/, '') + '_mux_report.json';
    await writeOutputFile(reportPath, JSON.stringify(result, null, 2));
    console.log(chalk.gray(`   Report:  ${reportPath}`));

    if (result.success) {
      console.log(
        chalk.bold('\n✅ Done!') + chalk.gray(` → ${result.outputPath}`),
      );
    } else {
      console.error(chalk.red('\n✗ Mux failed. Check the report for details.'));
      process.exit(1);
    }
  } else {
    console.log(
      chalk.yellow('\n⚠ ffmpeg not found — cannot mux directly.') +
        chalk.gray('\n   Generating helper scripts instead…'),
    );

    const scriptDir = dirname(outputPath);
    await generateMuxScripts(videoPath, audioPath, outputPath, syncPolicy, scriptDir);

    console.log(chalk.green('\n   ✅ Helper scripts generated:'));
    console.log(chalk.gray(`      ${join(scriptDir, 'ffmpeg', 'replace-audio.sh')}`));
    console.log(chalk.gray(`      ${join(scriptDir, 'ffmpeg', 'replace-audio.ps1')}`));
    console.log(
      chalk.gray(
        '\n   Install ffmpeg, then run the script for your platform.',
      ),
    );
  }
  console.log('');
}
