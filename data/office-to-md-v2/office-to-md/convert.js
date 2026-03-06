const fs = require('fs');
const path = require('path');
const pdfConverter = require('./utils/pdfConverter');
const wordConverter = require('./utils/wordConverter');
const docConverter = require('./utils/docConverter');
const pptConverter = require('./utils/pptConverter');

async function main() {
  const filePath = process.argv[2];
  if (!filePath) {
    console.error('Please provide a file path.');
    process.exit(1);
  }

  const absolutePath = path.resolve(filePath);
  if (!fs.existsSync(absolutePath)) {
    console.error('File not found:', absolutePath);
    process.exit(1);
  }

  const ext = path.extname(absolutePath).toLowerCase();
  const outputPath = absolutePath.replace(ext, '.md');

  console.log(`Converting ${absolutePath} to Markdown...`);

  let markdown = '';

  try {
    switch (ext) {
      case '.pdf':
        markdown = await pdfConverter(absolutePath);
        break;
      case '.docx':
        markdown = await wordConverter(absolutePath);
        break;
      case '.doc':
        markdown = await docConverter(absolutePath);
        break;
      case '.pptx':
        markdown = await pptConverter(absolutePath);
        break;
      default:
        console.error('Unsupported file type:', ext);
        process.exit(1);
    }

    fs.writeFileSync(outputPath, markdown);
    console.log(`Conversion successful! Output saved to: ${outputPath}`);
  } catch (error) {
    console.error('Conversion failed:', error.message);
    process.exit(1);
  }
}

main();
