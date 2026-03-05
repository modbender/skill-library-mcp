const WordExtractor = require("word-extractor");

async function convertDocToMd(filePath) {
  try {
    const extractor = new WordExtractor();
    const extracted = await extractor.extract(filePath);
    const text = extracted.getBody();
    
    // word-extractor returns raw text.
    // We can strip extra whitespace if needed.
    return text.replace(/\n\s*\n/g, '\n\n');
  } catch (error) {
    throw new Error(`Failed to convert DOC: ${error.message}`);
  }
}

module.exports = convertDocToMd;
