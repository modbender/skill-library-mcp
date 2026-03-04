#!/usr/bin/env node

/**
 * OpenClaw Visual - Image Generation Script
 *
 * Supports two rendering engines:
 * 1. node-html-to-image (default) - Lightweight, fast
 * 2. playwright (advanced) - Better CSS support for complex designs
 *
 * Usage:
 *   node generate-image.js --template quote-card --content '{"QUOTE":"Hello"}' --output ./image.png
 *   node generate-image.js --template quote-card --content '{"QUOTE":"Hello"}' --renderer playwright --output ./image.png
 */

const fs = require('fs');
const path = require('path');

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    template: 'quote-card',
    content: '{}',
    output: './output.png',
    renderer: 'auto', // auto | nodejs | playwright
    width: null,  // null means use template-specific defaults
    height: null  // null means use template-specific defaults
  };

  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace('--', '');
    const value = args[i + 1];
    if (key === 'width' || key === 'height') {
      options[key] = parseInt(value, 10);
    } else {
      options[key] = value;
    }
  }

  return options;
}

// Read template file
function readTemplate(templateName) {
  const templatePath = path.join(__dirname, '..', 'assets', 'templates', `${templateName}.html`);
  if (!fs.existsSync(templatePath)) {
    throw new Error(`Template not found: ${templateName}`);
  }
  return fs.readFileSync(templatePath, 'utf-8');
}

// Read CSS file
function readCSS() {
  const cssPath = path.join(__dirname, '..', 'assets', 'css', 'base-styles.css');
  if (!fs.existsSync(cssPath)) {
    return '';
  }
  return fs.readFileSync(cssPath, 'utf-8');
}

// Simple Mustache-style template rendering with array and inverted conditional support
function renderTemplate(template, data) {
  let result = template;

  // Process blocks recursively until no more changes
  let changed;
  do {
    changed = false;

    // Handle {{^key}}...{{/key}} blocks (inverted conditionals - show if falsy or empty array)
    result = result.replace(/\{\{\^([\w.]+)\}\}([\s\S]*?)\{\{\/\1\}\}/g, (match, key, content) => {
      const value = data[key];
      const shouldShow = !value || (Array.isArray(value) && value.length === 0);
      if (shouldShow) {
        changed = true;
        // Process nested blocks in the content
        return renderTemplate(content, data);
      } else {
        changed = true;
        return '';
      }
    });

    // Handle {{#key}}...{{/key}} blocks (conditionals and arrays)
    result = result.replace(/\{\{#([\w.]+)\}\}([\s\S]*?)\{\{\/\1\}\}/g, (match, key, content) => {
      const value = data[key];

      // If value doesn't exist, return empty
      if (!value) return '';

      changed = true;

      // If value is an array, iterate over it
      if (Array.isArray(value)) {
        return value.map(item => {
          if (typeof item === 'object' && item !== null) {
            // For object arrays, render with object properties
            return renderTemplate(content, item);
          } else {
            // For primitive arrays, replace {{.}} with the item
            return renderTemplate(content, { '.': item, ...data });
          }
        }).join('');
      }

      // For boolean/objects, just render the content once
      if (typeof value === 'object' && value !== null) {
        return renderTemplate(content, value);
      }

      // For truthy primitives, render content
      return renderTemplate(content, data);
    });
  } while (changed);

  // Handle {{key}} and {{.}} variables
  result = result.replace(/\{\{([\w.]+)\}\}/g, (match, key) => {
    return data[key] !== undefined ? data[key] : '';
  });

  return result;
}

// Build full HTML document
function buildHTML(bodyContent, css) {
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    ${css}
    body { margin: 0; }
  </style>
</head>
<body>
  ${bodyContent}
</body>
</html>`;
}

// Generate image using node-html-to-image
async function generateWithNodeHtmlToImage(html, outputPath, width, height) {
  const isAutoHeight = height === 'auto' || height === null || height === undefined;

  // Adaptive height requires Playwright (node-html-to-image doesn't support fullPage)
  if (isAutoHeight) {
    console.error('Adaptive height detected, switching to Playwright renderer...');
    return generateWithPlaywright(html, outputPath, width, height);
  }

  const nodeHtmlToImage = require('node-html-to-image');

  await nodeHtmlToImage({
    output: outputPath,
    html: html,
    puppeteerArgs: {
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      defaultViewport: {
        width,
        height,
        deviceScaleFactor: 2 // Retina quality
      }
    }
  });

  return outputPath;
}

// Generate image using Playwright
async function generateWithPlaywright(html, outputPath, width, height) {
  const { chromium } = require('playwright');

  const browser = await chromium.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();

    // Check if adaptive height is needed
    const isAutoHeight = height === 'auto' || height === null || height === undefined;

    // Set viewport - use a large height for auto mode to ensure content renders
    await page.setViewportSize({
      width,
      height: isAutoHeight ? 2000 : height
    });

    await page.setContent(html, { waitUntil: 'networkidle' });

    // Wait for fonts to load
    await page.waitForTimeout(500);

    const screenshotOptions = {
      path: outputPath,
      type: 'png',
      scale: 'device'
    };
    if (isAutoHeight) {
      const card = await page.$('.card');
      if (card) {
        await card.screenshot(screenshotOptions);
      } else {
        console.warn('Card element not found; falling back to viewport screenshot.');
        await page.screenshot(screenshotOptions);
      }
    } else {
      await page.screenshot(screenshotOptions);
    }

    return outputPath;
  } finally {
    await browser.close();
  }
}

// Determine which renderer to use
function selectRenderer(requestedRenderer, userIntent) {
  // If explicitly specified, use that
  if (requestedRenderer === 'nodejs') return 'nodejs';
  if (requestedRenderer === 'playwright') return 'playwright';

  // Auto-detect based on user intent
  if (userIntent) {
    const keywords = ['精美', '复杂', '高级', '动画', '特效', 'beautiful', 'complex', 'advanced', 'animation'];
    const intent = JSON.stringify(userIntent).toLowerCase();
    if (keywords.some(k => intent.includes(k))) {
      return 'playwright';
    }
  }

  // Default to nodejs for speed
  return 'nodejs';
}

// Get template dimensions
function getTemplateDimensions(templateName) {
  const dimensions = {
    'quote-card': { width: 800, height: 800 },
    'moment-card': { width: 800, height: 1000 },
    'daily-journal': { width: 800, height: 1200 },
    'social-share': { width: 1200, height: 630 },
    'dashboard': { width: 1200, height: 800 },
    'article-long': { width: 800, height: 'auto' }  // Adaptive height for long articles
  };
  return dimensions[templateName] || { width: 800, height: 800 };
}

// Main function
async function main() {
  try {
    const options = parseArgs();
    console.error('Options:', JSON.stringify(options, null, 2));

    // Parse content JSON
    let contentData;
    try {
      contentData = JSON.parse(options.content);
    } catch (e) {
      console.error('Error parsing content JSON:', e.message);
      contentData = {};
    }

    // Read template and CSS
    const templateBody = readTemplate(options.template);
    const css = readCSS();

    // Render template with data
    const renderedBody = renderTemplate(templateBody, contentData);
    const fullHTML = buildHTML(renderedBody, css);

    // Determine renderer
    const renderer = selectRenderer(options.renderer, contentData);
    console.error(`Using renderer: ${renderer}`);

    // Get dimensions
    const dims = getTemplateDimensions(options.template);
    const width = options.width || dims.width;
    const height = options.height || dims.height;

    // Generate image
    let outputPath;
    if (renderer === 'playwright') {
      outputPath = await generateWithPlaywright(fullHTML, options.output, width, height);
    } else {
      outputPath = await generateWithNodeHtmlToImage(fullHTML, options.output, width, height);
    }

    // Output result as JSON for OpenClaw to parse
    const result = {
      success: true,
      outputPath: path.resolve(outputPath),
      renderer: renderer,
      template: options.template,
      dimensions: { width, height }
    };

    console.log(JSON.stringify(result, null, 2));
    process.exit(0);

  } catch (error) {
    const result = {
      success: false,
      error: error.message,
      stack: error.stack
    };
    console.error(JSON.stringify(result, null, 2));
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

// Export for use as module
module.exports = {
  generateWithNodeHtmlToImage,
  generateWithPlaywright,
  renderTemplate,
  buildHTML
};
