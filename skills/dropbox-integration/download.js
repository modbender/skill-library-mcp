#!/usr/bin/env node

/**
 * Download a file from Dropbox with auto-refresh
 */

const { getDropboxClient } = require('./dropbox-helper');
const fs = require('fs').promises;
const path = require('path');

async function downloadFile(dropboxPath, localPath) {
  try {
    console.log(`📥 Downloading: ${dropboxPath}`);
    
    // Get auto-refreshing client
    const dbx = await getDropboxClient();
    
    const response = await dbx.filesDownload({ path: dropboxPath });
    const buffer = response.result.fileBinary;
    
    // Create directory if needed
    const dir = path.dirname(localPath);
    await fs.mkdir(dir, { recursive: true });
    
    await fs.writeFile(localPath, buffer);
    console.log(`✅ Saved to: ${localPath} (${formatBytes(buffer.length)})\n`);
    
  } catch (error) {
    console.error(`❌ Error downloading ${dropboxPath}:`, error.message);
    if (error.error) {
      console.error(JSON.stringify(error.error, null, 2));
    }
    process.exit(1);
  }
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
}

// Usage: node download.js "/path/in/dropbox" "./local/path"
const dropboxPath = process.argv[2];
const localPath = process.argv[3];

if (!dropboxPath || !localPath) {
  console.error('Usage: node download.js "/path/in/dropbox" "./local/path"');
  process.exit(1);
}

downloadFile(dropboxPath, localPath);
