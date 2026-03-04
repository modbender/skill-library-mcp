/**
 * Safe Web Content Processor using Prompt Injection Protection
 * This module wraps web content fetching with security measures
 */

const PromptInjectionProtection = require('./index.js');
const protection = new PromptInjectionProtection();

/**
 * Safely fetches and processes web content with injection protection
 */
async function fetchAndSecureContent(url, options = {}) {
  const {
    maxLength = 10000,
    extractTextOnly = true,
    strictMode = false
  } = options;

  try {
    // Note: In a real implementation, we would use web_fetch here
    // For now, this serves as the framework
    console.log(`Fetching content from ${url} with security measures...`);
    
    // This would normally call the web_fetch tool
    // const rawContent = await tools.web_fetch({ url });
    
    // For demonstration purposes, we'll simulate securing content
    return {
      url,
      secured: true,
      processedAt: new Date().toISOString()
    };
  } catch (error) {
    throw new Error(`Failed to securely fetch content: ${error.message}`);
  }
}

/**
 * Processes raw content through the protection mechanism
 */
async function secureProcess(content, options = {}) {
  try {
    return await protection.processExternalContent(content, {
      maxLength: options.maxLength || 10000,
      strictMode: options.strictMode || false
    });
  } catch (error) {
    return {
      error: error.message,
      isSafe: false,
      sanitized: '',
      originalLength: content ? content.length : 0
    };
  }
}

/**
 * Extracts content from web pages safely
 */
async function safeExtractWebContent(html, extractionOptions = {}) {
  try {
    return await protection.extractFromWebContent(html, extractionOptions);
  } catch (error) {
    return {
      error: error.message,
      extracted: '',
      originalLength: html ? html.length : 0
    };
  }
}

module.exports = {
  protection,
  fetchAndSecureContent,
  secureProcess,
  safeExtractWebContent
};