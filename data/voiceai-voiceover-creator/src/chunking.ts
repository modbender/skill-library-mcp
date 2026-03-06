/**
 * Script ingestion and chunking — turns raw scripts into numbered segments.
 * Supports markdown heading mode and auto-chunking for plain text.
 */
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { slugify, contentHash, fileExists } from './utils.js';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

export interface Segment {
  index: number;
  title: string;
  slug: string;
  text: string;
  source: 'heading' | 'auto' | 'template';
  hash: string;
}

export type ChunkMode = 'headings' | 'auto';
export type TemplateName = 'youtube' | 'podcast' | 'shortform';

export interface ChunkOptions {
  mode: ChunkMode;
  maxChars: number;
  language?: string;
  template?: TemplateName;
  templateDir: string;
  voiceId: string;
}

/* ------------------------------------------------------------------ */
/*  Markdown heading parser                                            */
/* ------------------------------------------------------------------ */

/** Split markdown by ## headings into segments. */
export function parseMarkdownHeadings(content: string): { title: string; text: string }[] {
  const lines = content.split('\n');
  const sections: { title: string; text: string }[] = [];
  let currentTitle = '';
  let currentLines: string[] = [];
  let h1Title = ''; // Track H1 for preamble naming

  for (const line of lines) {
    const h2Match = line.match(/^##\s+(.+)$/);
    const h1Match = line.match(/^#\s+(.+)$/);

    if (h2Match) {
      // Save previous section if it has content
      if (currentTitle || currentLines.some((l) => l.trim())) {
        const fallbackTitle = h1Title || 'Preamble';
        sections.push({
          title: currentTitle || fallbackTitle,
          text: currentLines.join('\n').trim(),
        });
      }
      currentTitle = h2Match[1].trim();
      currentLines = [];
    } else if (h1Match && !currentTitle && sections.length === 0) {
      // Capture H1 as the preamble title (don't add H1 text to body)
      h1Title = h1Match[1].trim();
    } else {
      currentLines.push(line);
    }
  }

  // Push final section
  if (currentTitle || currentLines.some((l) => l.trim())) {
    const fallbackTitle = h1Title || 'Preamble';
    sections.push({
      title: currentTitle || fallbackTitle,
      text: currentLines.join('\n').trim(),
    });
  }

  // Filter out empty sections
  return sections.filter((s) => s.text.length > 0);
}

/* ------------------------------------------------------------------ */
/*  Auto-chunking by sentence boundaries                               */
/* ------------------------------------------------------------------ */

/** Split text into chunks of ~maxChars, respecting sentence boundaries. */
export function autoChunk(content: string, maxChars: number): { title: string; text: string }[] {
  const text = content.trim();
  if (text.length <= maxChars) {
    return [{ title: 'Segment 1', text }];
  }

  // Split on sentence endings
  const sentences = text.match(/[^.!?]+[.!?]+[\s]*/g) ?? [text];
  const chunks: { title: string; text: string }[] = [];
  let current = '';
  let chunkNum = 1;

  for (const sentence of sentences) {
    if (current.length + sentence.length > maxChars && current.length > 0) {
      chunks.push({ title: `Segment ${chunkNum}`, text: current.trim() });
      chunkNum++;
      current = '';
    }
    current += sentence;
  }

  if (current.trim()) {
    chunks.push({ title: `Segment ${chunkNum}`, text: current.trim() });
  }

  return chunks;
}

/* ------------------------------------------------------------------ */
/*  Template loading                                                   */
/* ------------------------------------------------------------------ */

const TEMPLATE_MAP: Record<TemplateName, { intro?: string; outro?: string }> = {
  youtube: { intro: 'youtube_intro.txt', outro: 'youtube_outro.txt' },
  podcast: { intro: 'podcast_intro.txt' },
  shortform: { intro: 'shortform_hook.txt' },
};

async function loadTemplate(
  templateDir: string,
  filename: string,
): Promise<string | null> {
  const filePath = join(templateDir, filename);
  if (await fileExists(filePath)) {
    const content = await readFile(filePath, 'utf-8');
    return content.trim();
  }
  return null;
}

/* ------------------------------------------------------------------ */
/*  Main chunking pipeline                                             */
/* ------------------------------------------------------------------ */

/** Full chunking pipeline: parse → chunk → apply templates → number & hash. */
export async function chunkScript(content: string, options: ChunkOptions): Promise<Segment[]> {
  // 1. Parse into raw sections
  let rawSections: { title: string; text: string; source: 'heading' | 'auto' | 'template' }[];

  if (options.mode === 'headings') {
    const headingSections = parseMarkdownHeadings(content);
    const hasRealHeadings = headingSections.some(
      (s) => s.title !== 'Preamble' && s.title !== 'Untitled Section',
    );

    if (hasRealHeadings && headingSections.length > 0) {
      rawSections = headingSections.map((s) => ({ ...s, source: 'heading' as const }));
    } else {
      // Fallback to auto if no real ## headings found
      rawSections = autoChunk(content, options.maxChars).map((s) => ({
        ...s,
        source: 'auto' as const,
      }));
    }
  } else {
    rawSections = autoChunk(content, options.maxChars).map((s) => ({
      ...s,
      source: 'auto' as const,
    }));
  }

  // 2. Apply template intro/outro
  if (options.template && TEMPLATE_MAP[options.template]) {
    const tmpl = TEMPLATE_MAP[options.template];
    if (tmpl.intro) {
      const introText = await loadTemplate(options.templateDir, tmpl.intro);
      if (introText) {
        rawSections.unshift({ title: 'Intro', text: introText, source: 'template' });
      }
    }
    if (tmpl.outro) {
      const outroText = await loadTemplate(options.templateDir, tmpl.outro);
      if (outroText) {
        rawSections.push({ title: 'Outro', text: outroText, source: 'template' });
      }
    }
  }

  // 3. Number, slug, and hash each segment
  const segments: Segment[] = rawSections.map((section, i) => {
    const index = i + 1;
    const slug = slugify(section.title);
    const hash = contentHash(section.text, options.voiceId, options.language ?? 'en');
    return {
      index,
      title: section.title,
      slug,
      text: section.text,
      source: section.source,
      hash,
    };
  });

  return segments;
}
