#!/usr/bin/env node
/**
 * YouTube Music - Direct Play Helper
 * Gets video ID instantly and plays without search results
 * 
 * Usage: node direct-play.js "Dildara Ra One"
 */

const { execSync } = require('child_process');

const YOUTUBE_MUSIC_BASE = 'https://music.youtube.com';

/**
 * Fast search - returns first result URL directly
 */
async function getFirstResultUrl(query) {
  const encoded = encodeURIComponent(query);
  const searchUrl = `${YOUTUBE_MUSIC_BASE}/search?q=${encoded}`;
  
  console.log(`🎵 Searching: ${query}`);
  console.log(`🔗 URL: ${searchUrl}`);
  
  return searchUrl;
}

/**
 * Direct play - opens and auto-clicks first result
 */
async function directPlay(query) {
  try {
    const url = await getFirstResultUrl(query);
    
    // Open browser directly
    execSync(`openclaw browser open --targetUrl="${url}"`, {
      stdio: 'ignore'
    });
    
    console.log('✅ Playing now!');
    console.log('💡 Tip: Song will auto-play from search results');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Main
const query = process.argv.slice(2).join(' ');
if (!query) {
  console.log('Usage: node direct-play.js "<song name>"');
  console.log('Example: node direct-play.js "Dildara Ra One"');
  process.exit(0);
}

directPlay(query);
