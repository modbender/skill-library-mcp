#!/usr/bin/env node
/**
 * YouTube upload wrapper for MV pipeline.
 * Thin CLI around youtube-studio/scripts/video-uploader.js
 *
 * Usage:
 *   node youtube-upload.js --file output.mp4 --title "Song [Official MV]" \
 *     --description "..." --tags "AI,MV" --privacy public
 */

const path = require('path');

// Resolve the shared youtube-studio scripts
const ytScriptsDir = path.resolve(__dirname, '../../youtube-studio/scripts');

// Dynamically require from the shared skill
const { uploadVideo } = require(path.join(ytScriptsDir, 'video-uploader'));

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (!args.file || !args.title) {
    console.log('Usage: youtube-upload.js --file <path> --title <title> [--description <desc>] [--tags <csv>] [--privacy public|unlisted|private] [--thumbnail <path>] [--playlist <name>]');
    process.exit(1);
  }

  const metadata = {
    title: args.title,
    description: args.description || '',
    tags: args.tags ? args.tags.split(',').map(t => t.trim()) : [],
    privacyStatus: args.privacy || 'unlisted',
    categoryId: '10', // Music
  };

  const options = {};
  if (args.thumbnail) options.thumbnail = args.thumbnail;
  if (args.playlist) options.playlist = args.playlist;

  try {
    const result = await uploadVideo(args.file, metadata, options);
    console.log('\n✅ Upload complete!');
    console.log(`   Video ID: ${result.videoId}`);
    console.log(`   URL: ${result.url}`);
    console.log(`   Status: ${result.status}`);
  } catch (err) {
    console.error('❌ Upload failed:', err.message);
    process.exit(1);
  }
}

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--') && i + 1 < argv.length) {
      args[argv[i].slice(2)] = argv[i + 1];
      i++;
    }
  }
  return args;
}

main();
