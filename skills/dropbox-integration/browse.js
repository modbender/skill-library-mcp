#!/usr/bin/env node

/**
 * Browse Dropbox folders with auto-refresh
 */

const { getDropboxClient } = require('./dropbox-helper');

async function main() {
  const folderPath = process.argv[2] || '';
  console.log(`\n📁 Listing: ${folderPath || '(root)'}\n`);
  
  try {
    // Get auto-refreshing client
    const dbx = await getDropboxClient();
    
    const response = await dbx.filesListFolder({
      path: folderPath,
      recursive: false,
      include_deleted: false,
      limit: 2000,
    });
    
    const entries = response.result.entries;
    
    entries.forEach(entry => {
      const icon = entry['.tag'] === 'folder' ? '📁' : '📄';
      const size = entry.size ? ` (${formatBytes(entry.size)})` : '';
      const modified = entry.server_modified ? ` - ${entry.server_modified.split('T')[0]}` : '';
      console.log(`${icon} ${entry.name}${size}${modified}`);
    });
    
    console.log(`\nTotal: ${entries.length} items\n`);
    
  } catch (error) {
    console.error('Error:', error.message);
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

main();
