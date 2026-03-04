#!/usr/bin/env node
/**
 * OpenClaw Skill Wrapper for Office to Markdown Converter (v2 with .doc support)
 * 
 * This wrapper allows the converter to be used as an OpenClaw skill.
 * It can be called via exec tool from OpenClaw.
 */

const fs = require('fs');
const path = require('path');
const pdfConverter = require('./utils/pdfConverter');
const wordConverter = require('./utils/wordConverter');
const pptConverter = require('./utils/pptConverter');
const docConverter = require('./utils/docConverter');

/**
 * Main function for OpenClaw integration
 * @param {string} filePath - Path to the file to convert
 * @returns {Promise<{success: boolean, outputPath?: string, error?: string, markdown?: string, preview?: string, message?: string}>}
 */
async function convertOfficeToMarkdown(filePath) {
  try {
    // Validate input
    if (!filePath) {
      return {
        success: false,
        error: 'No file path provided. Usage: convertOfficeToMarkdown <file-path>'
      };
    }

    const absolutePath = path.resolve(filePath);
    
    // Check if file exists
    if (!fs.existsSync(absolutePath)) {
      return {
        success: false,
        error: `File not found: ${absolutePath}`
      };
    }

    // Check file extension
    const ext = path.extname(absolutePath).toLowerCase();
    const supportedExtensions = ['.pdf', '.doc', '.docx', '.pptx'];
    
    if (!supportedExtensions.includes(ext)) {
      return {
        success: false,
        error: `Unsupported file type: ${ext}. Supported types: ${supportedExtensions.join(', ')}`
      };
    }

    // Generate output path
    const outputPath = absolutePath.replace(ext, '.md');
    
    console.log(`[Office-to-MD v2] Converting ${absolutePath} to Markdown...`);

    let markdown = '';

    // Convert based on file type
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
    }

    // Write output file
    fs.writeFileSync(outputPath, markdown);
    
    // Return success with output path and preview
    const preview = markdown.length > 500 
      ? markdown.substring(0, 500) + '...' 
      : markdown;

    return {
      success: true,
      outputPath: outputPath,
      markdown: markdown,
      preview: preview,
      fileType: ext,
      message: `Successfully converted ${ext} file to: ${outputPath}`,
      stats: {
        lines: markdown.split('\n').length,
        characters: markdown.length,
        words: markdown.split(/\s+/).length
      }
    };

  } catch (error) {
    return {
      success: false,
      error: `Conversion failed: ${error.message}`,
      stack: error.stack
    };
  }
}

/**
 * CLI interface for direct testing
 */
if (require.main === module) {
  const filePath = process.argv[2];
  
  if (!filePath) {
    console.error('Usage: node openclaw-skill.js <file-path>');
    console.error('Example: node openclaw-skill.js ./document.doc');
    console.error('Supported formats: .pdf, .doc, .docx, .pptx');
    process.exit(1);
  }

  convertOfficeToMarkdown(filePath)
    .then(result => {
      if (result.success) {
        console.log('✅ Conversion successful!');
        console.log(`📁 Output: ${result.outputPath}`);
        console.log(`📄 File type: ${result.fileType}`);
        console.log(`📊 Stats: ${result.stats.lines} lines, ${result.stats.words} words, ${result.stats.characters} chars`);
        console.log(`📝 Preview:\n${result.preview}`);
      } else {
        console.error('❌ Conversion failed:');
        console.error(result.error);
        if (result.stack) {
          console.error('Stack trace:', result.stack);
        }
        process.exit(1);
      }
    })
    .catch(error => {
      console.error('❌ Unexpected error:', error);
      process.exit(1);
    });
}

// Export for OpenClaw integration
module.exports = { convertOfficeToMarkdown };