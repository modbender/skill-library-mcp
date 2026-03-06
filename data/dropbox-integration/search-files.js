#!/usr/bin/env node

const { getDropboxClient } = require('./dropbox-helper');

const searchTerm = process.argv[2];

if (!searchTerm) {
  console.error('Usage: node search-files.js <search-term>');
  console.error('Example: node search-files.js "Emma Butin"');
  process.exit(1);
}

(async () => {
  try {
    console.log(`🔍 Searching for: "${searchTerm}"\n`);
    
    // Get auto-refreshing Dropbox client
    const dbx = await getDropboxClient();
    
    const response = await dbx.filesSearchV2({
      query: searchTerm,
      options: {
        max_results: 100,
      }
    });
    
    if (response.result.matches.length === 0) {
      console.log('❌ No matches found');
      return;
    }
    
    console.log(`✅ Found ${response.result.matches.length} matches:\n`);
    
    for (const match of response.result.matches) {
      const metadata = match.metadata.metadata;
      const icon = metadata['.tag'] === 'folder' ? '📁' : '📄';
      console.log(`${icon} ${metadata.path_display}`);
      if (metadata['.tag'] === 'file') {
        const sizeKB = (metadata.size / 1024).toFixed(1);
        console.log(`   Size: ${sizeKB} KB`);
        console.log(`   Modified: ${metadata.client_modified}`);
      }
      console.log('');
    }
    
  } catch (error) {
    console.error('❌ Search failed:', error.message);
    if (error.error) {
      console.error(JSON.stringify(error.error, null, 2));
    }
    process.exit(1);
  }
})();
