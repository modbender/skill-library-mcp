#!/usr/bin/env node
import { Innertube } from 'youtubei.js';

const url = process.argv[2];
if (!url) {
  console.error('Usage: transcript.mjs <youtube-url-or-id>');
  process.exit(1);
}

// Extract video ID from URL or use as-is
const videoId = url.includes('youtube.com') || url.includes('youtu.be')
  ? url.match(/(?:v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/)?.[1]
  : url;

if (!videoId) {
  console.error('Could not extract video ID from URL');
  process.exit(1);
}

async function getTranscript() {
  try {
    const yt = await Innertube.create();
    const info = await yt.getInfo(videoId);
    
    // Get video title
    console.log('TITLE:', info.basic_info.title);
    console.log('AUTHOR:', info.basic_info.author);
    console.log('DURATION:', Math.floor(info.basic_info.duration / 60) + ':' + (info.basic_info.duration % 60).toString().padStart(2, '0'));
    console.log('---');
    
    // Get transcript
    const transcriptInfo = await info.getTranscript();
    if (!transcriptInfo?.transcript?.content?.body?.initial_segments) {
      console.error('No transcript available for this video');
      process.exit(1);
    }
    
    const segments = transcriptInfo.transcript.content.body.initial_segments;
    segments.forEach(seg => {
      if (seg.snippet?.text) {
        const startMs = parseInt(seg.start_ms) || 0;
        const mins = Math.floor(startMs / 60000);
        const secs = Math.floor((startMs % 60000) / 1000);
        const timestamp = `[${mins}:${secs.toString().padStart(2, '0')}]`;
        console.log(`${timestamp} ${seg.snippet.text}`);
      }
    });
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

getTranscript();
