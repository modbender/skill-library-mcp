#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const args = process.argv.slice(2);
const folderPath = args[0];

let threshold = 90;
let lang = 'General Backend';
let yoe = 'Any';

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--threshold') threshold = parseInt(args[i+1]);
  if (args[i] === '--lang') lang = args[i+1];
  if (args[i] === '--yoe') yoe = args[i+1];
}

if (!folderPath || !fs.existsSync(folderPath)) {
  console.error('Usage: node batch_screen.js <folder_path> [--threshold 90] [--lang <lang>] [--yoe <yoe>]');
  process.exit(1);
}

const files = fs.readdirSync(folderPath).filter(f => f.endsWith('.txt') || f.endsWith('.md') || f.endsWith('.pdf'));

console.log('--- BATCH SCREENING START ---');
console.log('Folder: ' + folderPath);
console.log('Threshold: ' + threshold);
console.log('Target: ' + lang + ' (' + yoe + ' YOE)');
console.log('Files found: ' + files.length + '\n');

files.forEach(file => {
  const filePath = path.join(folderPath, file);
  console.log('Processing ' + file + '...');
  
  try {
    let processPath = filePath;
    let isTemp = false;

    // Handle PDF conversion
    if (file.toLowerCase().endsWith('.pdf')) {
      const tempTxt = path.join('/tmp', file + '.txt');
      execSync('pdftotext "' + filePath + '" "' + tempTxt + '"');
      processPath = tempTxt;
      isTemp = true;
    }

    const output = execSync('node ' + path.join(__dirname, 'screen_resume.js') + ' "' + processPath + '" --lang "' + lang + '" --yoe "' + yoe + '"', { encoding: 'utf8' });
    
    console.log('[FILE_CONTENT_FOR_AGENT]: ' + file);
    console.log(output);
    console.log('--- END_OF_FILE: ' + file + ' ---\n');

    if (isTemp && fs.existsSync(processPath)) {
      fs.unlinkSync(processPath);
    }
  } catch (e) {
    console.error('Error processing ' + file + ': ' + e.message);
  }
});

console.log('--- BATCH SCREENING COMPLETE ---');
