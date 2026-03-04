#!/usr/bin/env node

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import os from 'os';

// Extract video ID from URL
function extractVideoId(url) {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&?\s]+)/,
    /^([a-zA-Z0-9_-]{11})$/
  ];
  
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) return match[1];
  }
  return null;
}

// Format seconds to MM:SS
function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Get video info via yt-dlp
function getVideoInfo(url) {
  try {
    const output = execSync(`yt-dlp --dump-json --no-download "${url}"`, {
      encoding: 'utf-8',
      timeout: 30000,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    return JSON.parse(output);
  } catch {
    return null;
  }
}

// Get transcript via yt-dlp
function getTranscript(url) {
  const tmpDir = os.tmpdir();
  const tmpFile = path.join(tmpDir, `yt-transcript-${Date.now()}`);
  
  try {
    // Try auto-generated first, then manual subs
    execSync(`yt-dlp --write-auto-sub --sub-lang en --skip-download --sub-format vtt -o "${tmpFile}" "${url}"`, {
      encoding: 'utf-8',
      timeout: 30000,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    // Find the subtitle file
    const files = fs.readdirSync(tmpDir).filter(f => f.startsWith(path.basename(tmpFile)) && f.endsWith('.vtt'));
    if (files.length === 0) {
      throw new Error('No subtitles found');
    }
    
    const vttContent = fs.readFileSync(path.join(tmpDir, files[0]), 'utf-8');
    
    // Clean up
    files.forEach(f => fs.unlinkSync(path.join(tmpDir, f)));
    
    return parseVTT(vttContent);
  } catch (err) {
    // Clean up any partial files
    try {
      const files = fs.readdirSync(tmpDir).filter(f => f.startsWith(path.basename(tmpFile)));
      files.forEach(f => fs.unlinkSync(path.join(tmpDir, f)));
    } catch {}
    
    throw new Error(`Could not fetch transcript: ${err.message}`);
  }
}

// Parse VTT format
function parseVTT(vtt) {
  const lines = vtt.split('\n');
  const segments = [];
  let currentTime = 0;
  let currentText = '';
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // Time line: 00:00:05.000 --> 00:00:08.000
    const timeMatch = line.match(/(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*-->/);
    if (timeMatch) {
      const hours = parseInt(timeMatch[1]);
      const mins = parseInt(timeMatch[2]);
      const secs = parseInt(timeMatch[3]);
      currentTime = hours * 3600 + mins * 60 + secs;
      continue;
    }
    
    // Text line
    if (line && !line.startsWith('WEBVTT') && !line.includes('-->') && !/^\d+$/.test(line)) {
      // Remove VTT tags
      const cleanText = line.replace(/<[^>]+>/g, '').trim();
      if (cleanText && cleanText !== currentText) {
        segments.push({ time: currentTime, text: cleanText });
        currentText = cleanText;
      }
    }
  }
  
  // Dedupe consecutive identical lines
  return segments.filter((seg, i, arr) => i === 0 || seg.text !== arr[i-1].text);
}

// Extract chapters from transcript
function extractChapters(transcript, count = 6) {
  if (!transcript || transcript.length === 0) return [];
  
  const totalDuration = transcript[transcript.length - 1].time;
  const interval = totalDuration / count;
  
  const chapters = [];
  for (let i = 0; i < count; i++) {
    const targetTime = i * interval;
    const segment = transcript.find(t => t.time >= targetTime) || transcript[0];
    chapters.push({
      time: formatTime(segment.time),
      text: segment.text.slice(0, 60) + (segment.text.length > 60 ? '...' : '')
    });
  }
  
  return chapters;
}

// Commands
async function cmdTranscript(url, options = {}) {
  const videoId = extractVideoId(url);
  if (!videoId) {
    console.error('❌ Invalid YouTube URL');
    return;
  }
  
  console.log('📥 Fetching transcript...\n');
  
  const info = getVideoInfo(url);
  if (info) {
    console.log(`📺 ${info.title}`);
    console.log(`👤 ${info.uploader}\n`);
  }
  
  const transcript = getTranscript(url);
  
  const limit = options.limit || Infinity;
  let charCount = 0;
  
  for (const segment of transcript) {
    if (charCount >= limit) break;
    
    const time = formatTime(segment.time);
    console.log(`[${time}] ${segment.text}`);
    charCount += segment.text.length;
  }
  
  if (charCount >= limit) {
    console.log(`\n... (truncated at ${limit} chars)`);
  }
}

async function cmdSummary(url) {
  const videoId = extractVideoId(url);
  if (!videoId) {
    console.error('❌ Invalid YouTube URL');
    return;
  }
  
  console.log('📥 Fetching video info...\n');
  
  const info = getVideoInfo(url);
  const transcript = getTranscript(url);
  
  const fullText = transcript.map(t => t.text).join(' ');
  const duration = info?.duration || transcript[transcript.length - 1]?.time || 0;
  
  console.log(`📺 **${info?.title || 'Video'}**`);
  console.log(`👤 ${info?.uploader || 'Unknown'}`);
  console.log(`⏱️ ${formatTime(duration)}\n`);
  
  console.log(`## Transcript Preview\n`);
  console.log(fullText.slice(0, 2000) + (fullText.length > 2000 ? '...' : ''));
  
  console.log(`\n---`);
  console.log(`📝 Full transcript: ${fullText.length} chars, ~${fullText.split(/\s+/).length} words`);
}

async function cmdChapters(url) {
  const videoId = extractVideoId(url);
  if (!videoId) {
    console.error('❌ Invalid YouTube URL');
    return;
  }
  
  console.log('📥 Extracting chapters...\n');
  
  const info = getVideoInfo(url);
  
  // Check if video has chapters in description
  if (info?.chapters && info.chapters.length > 0) {
    console.log(`📺 ${info.title}\n`);
    console.log(`## Chapters (from video)\n`);
    for (const ch of info.chapters) {
      console.log(`- **${formatTime(ch.start_time)}** ${ch.title}`);
    }
    return;
  }
  
  // Generate from transcript
  const transcript = getTranscript(url);
  
  console.log(`📺 ${info?.title || 'Video'}\n`);
  console.log(`## Key Moments (auto-generated)\n`);
  
  const chapters = extractChapters(transcript, 8);
  for (const ch of chapters) {
    console.log(`- **${ch.time}** ${ch.text}`);
  }
}

async function cmdAnalyze(url) {
  const videoId = extractVideoId(url);
  if (!videoId) {
    console.error('❌ Invalid YouTube URL');
    return;
  }
  
  console.log('📥 Analyzing video...\n');
  
  const info = getVideoInfo(url);
  const transcript = getTranscript(url);
  
  const fullText = transcript.map(t => t.text).join(' ');
  const duration = info?.duration || transcript[transcript.length - 1]?.time || 0;
  
  console.log(`# YouTube Video Analysis\n`);
  console.log(`📺 **${info?.title || 'Video'}**`);
  console.log(`👤 Channel: ${info?.uploader || 'Unknown'}`);
  console.log(`⏱️ Duration: ${formatTime(duration)}`);
  console.log(`🔗 https://youtube.com/watch?v=${videoId}\n`);
  
  // Chapters
  if (info?.chapters && info.chapters.length > 0) {
    console.log(`## Chapters\n`);
    for (const ch of info.chapters) {
      console.log(`- **${formatTime(ch.start_time)}** ${ch.title}`);
    }
  } else {
    console.log(`## Key Moments\n`);
    const chapters = extractChapters(transcript, 6);
    for (const ch of chapters) {
      console.log(`- **${ch.time}** ${ch.text}`);
    }
  }
  
  console.log(`\n## Transcript Stats\n`);
  console.log(`- Words: ~${fullText.split(/\s+/).length}`);
  console.log(`- Characters: ${fullText.length}`);
  console.log(`- Segments: ${transcript.length}\n`);
  
  console.log(`## Transcript Preview\n`);
  console.log(fullText.slice(0, 1500) + (fullText.length > 1500 ? '...' : ''));
}

// Check for yt-dlp
function checkDependencies() {
  try {
    execSync('which yt-dlp', { stdio: 'pipe' });
  } catch {
    console.error('❌ yt-dlp is required. Install with: brew install yt-dlp');
    process.exit(1);
  }
}

// Main CLI
async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];
  const url = args[1];
  
  if (!cmd || !url) {
    console.log(`
yt-digest - Extract summaries and transcripts from YouTube videos

Commands:
  transcript <url>    Get full transcript with timestamps
  summary <url>       Get video info and transcript preview
  chapters <url>      Extract chapters or key moments
  analyze <url>       Full analysis (info + chapters + transcript)

Options:
  --limit <n>         Limit transcript output to n characters

Examples:
  yt-digest transcript "https://youtube.com/watch?v=abc123"
  yt-digest analyze "https://youtu.be/abc123"

Requires: yt-dlp (brew install yt-dlp)
    `);
    return;
  }
  
  checkDependencies();
  
  const limitIdx = args.indexOf('--limit');
  const options = {
    limit: limitIdx > -1 ? parseInt(args[limitIdx + 1]) : Infinity
  };
  
  try {
    switch (cmd) {
      case 'transcript':
        await cmdTranscript(url, options);
        break;
      case 'summary':
        await cmdSummary(url);
        break;
      case 'chapters':
        await cmdChapters(url);
        break;
      case 'analyze':
        await cmdAnalyze(url);
        break;
      default:
        console.error(`Unknown command: ${cmd}`);
    }
  } catch (err) {
    console.error(`❌ Error: ${err.message}`);
    process.exit(1);
  }
}

main();
