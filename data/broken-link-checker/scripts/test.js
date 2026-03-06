const { checkUrl } = require('../index.js');

async function run() {
  console.log('Testing broken-link-checker...');
  
  // Test valid URL
  const valid = await checkUrl('https://www.google.com');
  if (!valid.valid) {
    console.error('Failed to validate google.com', valid);
    process.exit(1);
  }

  // Test invalid URL (force 404)
  const invalid = await checkUrl('https://www.google.com/this-does-not-exist-12345');
  if (invalid.valid && invalid.status === 200) {
     console.warn('Warning: google returned 200 for missing page? Skipping strict check for now.');
  } else if (invalid.valid) {
     console.error('Failed to detect broken link', invalid);
     process.exit(1);
  }

  console.log('Tests passed!');
}

run();
