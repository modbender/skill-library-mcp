#!/usr/bin/env node
const { getSubtitles } = require('youtube-captions-scraper');

const url = process.argv[2];
const lang = process.argv[3] || 'en';

if (!url) {
  console.error('Usage: transcript.js <youtube-url-or-id> [language]');
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

getSubtitles({ videoID: videoId, lang: lang })
  .then(captions => {
    if (!captions || captions.length === 0) {
      console.error('No captions available for this video');
      process.exit(1);
    }
    
    captions.forEach(item => {
      const startSec = parseFloat(item.start);
      const mins = Math.floor(startSec / 60);
      const secs = Math.floor(startSec % 60);
      const timestamp = `[${mins}:${secs.toString().padStart(2, '0')}]`;
      console.log(`${timestamp} ${item.text}`);
    });
  })
  .catch(err => {
    console.error('Error fetching transcript:', err.message);
    process.exit(1);
  });
