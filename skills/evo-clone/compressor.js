const fs = require('fs');
const path = require('path');

const KNOWLEDGE_DIR = path.resolve(__dirname, '../../knowledge');
const OUTPUT_FILE = path.join(KNOWLEDGE_DIR, 'TAGS.min.json');

function compress() {
  const tags = {};
  
  if (!fs.existsSync(KNOWLEDGE_DIR)) {
    console.error('Knowledge dir not found');
    return;
  }

  const files = fs.readdirSync(KNOWLEDGE_DIR).filter(f => f.endsWith('.md'));
  
  files.forEach(file => {
    const content = fs.readFileSync(path.join(KNOWLEDGE_DIR, file), 'utf8');
    // Extract @TAG patterns
    const regex = /@([A-Z0-9_-]+)(?:\s*[:(]|\s+)(.+)/g;
    let match;
    while ((match = regex.exec(content)) !== null) {
      const key = match[1];
      const val = match[2].trim().substring(0, 100); // Limit length
      tags[key] = val;
    }
  });

  // Inject File Map
  tags['_FILES'] = files.reduce((acc, f) => {
    acc[f.replace('.md', '').toUpperCase()] = f;
    return acc;
  }, {});

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(tags, null, 0));
  console.log(`Compressed ${Object.keys(tags).length} tags to ${OUTPUT_FILE}`);
}

compress();
