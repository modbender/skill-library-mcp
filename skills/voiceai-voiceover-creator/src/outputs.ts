/**
 * Output file generators — manifest, timeline, review page, chapters, captions, description.
 */
import { join } from 'node:path';
import { type Segment } from './chunking.js';
import { type RenderResult } from './render.js';
import { type MuxResult } from './ffmpeg.js';
import {
  writeOutputFile,
  youtubeTimestamp,
  srtTimestamp,
  formatDuration,
} from './utils.js';

/* ------------------------------------------------------------------ */
/*  Manifest                                                           */
/* ------------------------------------------------------------------ */

export interface ManifestData {
  title: string;
  voice_id: string;
  voice_name?: string;
  template?: string;
  language: string;
  mock: boolean;
  segments: {
    index: number;
    title: string;
    source_text: string;
    text_hash: string;
    file_path: string;
    duration_seconds: number;
  }[];
  created_at: string;
  total_duration_seconds: number;
}

export function buildManifest(
  title: string,
  voiceId: string,
  voiceName: string | undefined,
  template: string | undefined,
  language: string,
  mock: boolean,
  results: RenderResult[],
): ManifestData {
  const totalDuration = results.reduce((s, r) => s + r.duration, 0);
  return {
    title,
    voice_id: voiceId,
    voice_name: voiceName,
    template,
    language,
    mock,
    segments: results.map((r) => ({
      index: r.segment.index,
      title: r.segment.title,
      source_text: r.segment.text,
      text_hash: r.segment.hash,
      file_path: r.fileName,
      duration_seconds: r.duration,
    })),
    created_at: new Date().toISOString(),
    total_duration_seconds: totalDuration,
  };
}

/* ------------------------------------------------------------------ */
/*  Timeline                                                           */
/* ------------------------------------------------------------------ */

export interface TimelineEntry {
  index: number;
  title: string;
  start_seconds: number;
  duration_seconds: number;
  end_seconds: number;
}

export interface TimelineData {
  segments: TimelineEntry[];
  total_duration_seconds: number;
  has_durations: boolean;
}

export function buildTimeline(results: RenderResult[]): TimelineData {
  const hasDurations = results.every((r) => r.duration > 0);
  let cursor = 0;
  const segments: TimelineEntry[] = results.map((r) => {
    const entry: TimelineEntry = {
      index: r.segment.index,
      title: r.segment.title,
      start_seconds: cursor,
      duration_seconds: r.duration,
      end_seconds: cursor + r.duration,
    };
    cursor += r.duration;
    return entry;
  });

  return {
    segments,
    total_duration_seconds: cursor,
    has_durations: hasDurations,
  };
}

/* ------------------------------------------------------------------ */
/*  Chapters (YouTube-friendly)                                        */
/* ------------------------------------------------------------------ */

export function buildChapters(timeline: TimelineData): string | null {
  if (!timeline.has_durations) return null;

  const lines = timeline.segments.map(
    (s) => `${youtubeTimestamp(s.start_seconds)} ${s.title}`,
  );
  return lines.join('\n');
}

/* ------------------------------------------------------------------ */
/*  Captions (SRT)                                                     */
/* ------------------------------------------------------------------ */

export function buildCaptionsSrt(
  timeline: TimelineData,
  segments: Segment[],
): string | null {
  if (!timeline.has_durations) return null;

  const blocks = timeline.segments.map((t, i) => {
    const segText = segments[i]?.text ?? '';
    // Truncate very long segments to a summary line for caption blocks
    const captionText =
      segText.length > 200 ? segText.slice(0, 197) + '...' : segText;
    return `${i + 1}\n${srtTimestamp(t.start_seconds)} --> ${srtTimestamp(t.end_seconds)}\n${captionText}`;
  });

  return blocks.join('\n\n');
}

/* ------------------------------------------------------------------ */
/*  Description (YouTube/podcast)                                      */
/* ------------------------------------------------------------------ */

export function buildDescription(
  title: string,
  chapters: string | null,
): string {
  let desc = `${title}\n${'='.repeat(title.length)}\n\n`;

  if (chapters) {
    desc += `Chapters:\n${chapters}\n\n`;
  }

  desc += `---\nVoiceover generated with Voice.ai — https://voice.ai\n`;
  return desc;
}

/* ------------------------------------------------------------------ */
/*  Review HTML (the "wow" deliverable)                                */
/* ------------------------------------------------------------------ */

export function buildReviewHtml(
  title: string,
  results: RenderResult[],
  timeline: TimelineData,
  hasMaster: boolean,
  voiceId: string,
  mock: boolean,
): string {
  const segmentCards = results
    .map((r) => {
      const t = timeline.segments.find((s) => s.index === r.segment.index);
      const dur = t ? formatDuration(t.duration_seconds) : '—';
      return `
      <div class="segment-card">
        <div class="segment-header">
          <span class="segment-num">${String(r.segment.index).padStart(2, '0')}</span>
          <h3>${escapeHtml(r.segment.title)}</h3>
          <span class="segment-dur">${dur}</span>
        </div>
        <audio controls preload="metadata" src="segments/${escapeHtml(r.fileName)}"></audio>
        <details>
          <summary>View script text</summary>
          <p class="segment-text">${escapeHtml(r.segment.text)}</p>
        </details>
        <code class="regen-hint">voiceai-vo build --input &lt;script&gt; --voice ${escapeHtml(voiceId)} --force</code>
      </div>`;
    })
    .join('\n');

  const masterSection = hasMaster
    ? `
    <section class="master-section">
      <h2>🎧 Master Audio</h2>
      <audio controls preload="metadata" src="master.wav" style="width:100%"></audio>
    </section>`
    : '';

  const totalDur = formatDuration(timeline.total_duration_seconds);
  const mockBadge = mock
    ? '<span class="badge badge-mock">MOCK MODE</span>'
    : '';

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(title)} — Voiceover Review</title>
  <style>
    :root {
      --bg: #0f0f13;
      --surface: #1a1a24;
      --border: #2a2a3a;
      --text: #e8e8f0;
      --text-dim: #8888a0;
      --accent: #6c5ce7;
      --accent-glow: #7c6cf7;
      --success: #00d2a0;
      --radius: 12px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 2rem 1rem;
    }
    .container { max-width: 800px; margin: 0 auto; }
    header {
      text-align: center;
      margin-bottom: 2.5rem;
      padding: 2rem 1rem;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      border-radius: var(--radius);
      border: 1px solid var(--border);
    }
    header h1 {
      font-size: 1.8rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      background: linear-gradient(135deg, var(--accent-glow), var(--success));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    header .meta {
      color: var(--text-dim);
      font-size: 0.9rem;
    }
    .badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-left: 0.5rem;
    }
    .badge-mock { background: #ff9f43; color: #000; }
    .master-section {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.5rem;
      margin-bottom: 2rem;
    }
    .master-section h2 { margin-bottom: 1rem; font-size: 1.2rem; }
    .segment-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.25rem;
      margin-bottom: 1rem;
      transition: border-color 0.2s;
    }
    .segment-card:hover { border-color: var(--accent); }
    .segment-header {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 0.75rem;
    }
    .segment-num {
      background: var(--accent);
      color: #fff;
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.8rem;
      font-weight: 700;
      flex-shrink: 0;
    }
    .segment-header h3 { flex: 1; font-size: 1rem; font-weight: 600; }
    .segment-dur { color: var(--text-dim); font-size: 0.85rem; }
    audio {
      width: 100%;
      height: 36px;
      margin-bottom: 0.5rem;
      border-radius: 6px;
    }
    details { margin-top: 0.5rem; }
    details summary {
      cursor: pointer;
      color: var(--text-dim);
      font-size: 0.85rem;
      user-select: none;
    }
    details summary:hover { color: var(--text); }
    .segment-text {
      margin-top: 0.75rem;
      padding: 1rem;
      background: var(--bg);
      border-radius: 8px;
      font-size: 0.9rem;
      line-height: 1.7;
      white-space: pre-wrap;
    }
    .regen-hint {
      display: block;
      margin-top: 0.5rem;
      padding: 0.5rem 0.75rem;
      background: var(--bg);
      border-radius: 6px;
      font-size: 0.75rem;
      color: var(--text-dim);
      overflow-x: auto;
    }
    footer {
      text-align: center;
      margin-top: 3rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--border);
      color: var(--text-dim);
      font-size: 0.85rem;
    }
    footer a { color: var(--accent-glow); text-decoration: none; }
    footer a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>${escapeHtml(title)}</h1>
      <p class="meta">
        ${results.length} segments · ${totalDur} total · voice: <code>${escapeHtml(voiceId)}</code>
        ${mockBadge}
      </p>
    </header>

    ${masterSection}

    <section>
      <h2 style="margin-bottom: 1rem; font-size: 1.2rem;">📝 Segments</h2>
      ${segmentCards}
    </section>

    <footer>
      <p>Generated by <a href="https://voice.ai">Voice.ai</a> Creator Voiceover Pipeline</p>
    </footer>
  </div>
</body>
</html>`;
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ------------------------------------------------------------------ */
/*  Write all output files                                             */
/* ------------------------------------------------------------------ */

export interface WriteOutputsOptions {
  outputDir: string;
  title: string;
  voiceId: string;
  voiceName?: string;
  template?: string;
  language: string;
  mock: boolean;
  results: RenderResult[];
  segments: Segment[];
  hasMaster: boolean;
  muxResult?: MuxResult;
}

export async function writeAllOutputs(opts: WriteOutputsOptions): Promise<void> {
  const {
    outputDir,
    title,
    voiceId,
    voiceName,
    template,
    language,
    mock,
    results,
    segments,
    hasMaster,
    muxResult,
  } = opts;

  // Manifest
  const manifest = buildManifest(title, voiceId, voiceName, template, language, mock, results);
  await writeOutputFile(join(outputDir, 'manifest.json'), JSON.stringify(manifest, null, 2));

  // Timeline
  const timeline = buildTimeline(results);
  await writeOutputFile(join(outputDir, 'timeline.json'), JSON.stringify(timeline, null, 2));

  // Chapters
  const chapters = buildChapters(timeline);
  if (chapters) {
    await writeOutputFile(join(outputDir, 'chapters.txt'), chapters);
  }

  // Captions (SRT)
  const captions = buildCaptionsSrt(timeline, segments);
  if (captions) {
    await writeOutputFile(join(outputDir, 'captions.srt'), captions);
  }

  // Description
  const description = buildDescription(title, chapters);
  await writeOutputFile(join(outputDir, 'description.txt'), description);

  // Review HTML
  const reviewHtml = buildReviewHtml(title, results, timeline, hasMaster, voiceId, mock);
  await writeOutputFile(join(outputDir, 'review.html'), reviewHtml);

  // Mux report (if applicable)
  if (muxResult) {
    await writeOutputFile(join(outputDir, 'mux_report.json'), JSON.stringify(muxResult, null, 2));
  }
}
