const mammoth = require('mammoth');
const TurndownService = require('turndown');

const turndownService = new TurndownService();

async function convertDocxToMd(filePath) {
  try {
    const result = await mammoth.convertToHtml({ path: filePath });
    const html = result.value; // The generated HTML
    const messages = result.messages; // Any messages, such as warnings during conversion
    
    if (messages.length > 0) {
      console.warn('Mammoth messages:', messages);
    }
    
    const markdown = turndownService.turndown(html);
    return markdown;
  } catch (error) {
    throw new Error(`Failed to convert DOCX: ${error.message}`);
  }
}

module.exports = convertDocxToMd;
