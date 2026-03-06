const fs = require('fs');
const pdf = require('pdf-parse');

async function convertPdfToMd(filePath) {
  try {
    const dataBuffer = fs.readFileSync(filePath);
    const data = await pdf(dataBuffer);
    // pdf-parse returns raw text. We can try to do some basic formatting if needed, 
    // but usually it's just text. We can wrap pages or something?
    // For now, let's just return the text as is, maybe with page separators.
    
    // We can add page numbers
    const numPages = data.numpages;
    let text = data.text;
    
    // Simple cleanup: remove excessive newlines
    text = text.replace(/\n\s*\n/g, '\n\n');
    
    return text;
  } catch (error) {
    throw new Error(`Failed to convert PDF: ${error.message}`);
  }
}

module.exports = convertPdfToMd;
