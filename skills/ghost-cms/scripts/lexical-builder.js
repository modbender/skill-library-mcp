#!/usr/bin/env node

/**
 * Lexical Content Builder for Ghost CMS
 * Converts structured content to Ghost's Lexical format
 */

/**
 * Create a text node
 */
function createTextNode(text, format = 0) {
  return {
    detail: 0,
    format,
    mode: "normal",
    style: "",
    text,
    type: "extended-text",
    version: 1
  };
}

/**
 * Create a paragraph
 */
function createParagraph(text, format = 0) {
  return {
    children: [createTextNode(text, format)],
    direction: "ltr",
    format: "",
    indent: 0,
    type: "paragraph",
    version: 1
  };
}

/**
 * Create a heading
 */
function createHeading(text, level = 2, format = 1) {
  return {
    children: [createTextNode(text, format)],
    direction: "ltr",
    format: "",
    indent: 0,
    type: "heading",
    version: 1,
    tag: `h${level}`
  };
}

/**
 * Build complete Lexical document
 */
function buildLexical(children) {
  return {
    root: {
      children,
      direction: "ltr",
      format: "",
      indent: 0,
      type: "root",
      version: 1
    }
  };
}

/**
 * Convert simple text to Lexical (paragraphs separated by double newlines)
 */
function textToLexical(text) {
  const paragraphs = text.split('\n\n').filter(p => p.trim());
  const children = paragraphs.map(para => createParagraph(para.trim()));
  return buildLexical(children);
}

/**
 * Convert structured content to Lexical
 * 
 * @param {Array} content - Array of content blocks
 * @returns {Object} Lexical document
 * 
 * Example:
 * [
 *   { type: 'h2', text: 'Main Heading' },
 *   { type: 'p', text: 'First paragraph' },
 *   { type: 'h3', text: 'Subheading' },
 *   { type: 'p', text: 'Second paragraph', bold: true }
 * ]
 */
function structuredToLexical(content) {
  const children = content.map(block => {
    const format = block.bold && block.italic ? 3 : block.bold ? 1 : block.italic ? 2 : 0;
    
    if (block.type === 'p') {
      return createParagraph(block.text, format);
    } else if (block.type.startsWith('h')) {
      const level = parseInt(block.type.substring(1));
      return createHeading(block.text, level, format);
    } else {
      // Default to paragraph
      return createParagraph(block.text, format);
    }
  });
  
  return buildLexical(children);
}

/**
 * Stringify Lexical for Ghost API
 */
function stringifyLexical(lexicalDoc) {
  return JSON.stringify(lexicalDoc);
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const mode = process.argv[2] || 'text';
  
  if (mode === 'text') {
    // Simple text mode
    const text = process.argv.slice(3).join(' ');
    if (!text) {
      console.error('Usage: lexical-builder.js text "Your text here"');
      process.exit(1);
    }
    const lexical = textToLexical(text);
    console.log(stringifyLexical(lexical));
  } else if (mode === 'structured') {
    // Structured mode - expects JSON input
    const jsonInput = process.argv.slice(3).join(' ');
    if (!jsonInput) {
      console.error('Usage: lexical-builder.js structured \'[{"type":"h2","text":"Title"},{"type":"p","text":"Content"}]\'');
      process.exit(1);
    }
    try {
      const content = JSON.parse(jsonInput);
      const lexical = structuredToLexical(content);
      console.log(stringifyLexical(lexical));
    } catch (e) {
      console.error('Invalid JSON:', e.message);
      process.exit(1);
    }
  } else if (mode === 'example') {
    // Show example
    const example = [
      { type: 'h2', text: 'Main Heading' },
      { type: 'p', text: 'This is a normal paragraph.' },
      { type: 'h3', text: 'Subheading' },
      { type: 'p', text: 'This is bold text.', bold: true },
      { type: 'p', text: 'This is italic text.', italic: true },
      { type: 'p', text: 'This is bold and italic.', bold: true, italic: true }
    ];
    const lexical = structuredToLexical(example);
    console.log('Example structured content:');
    console.log(JSON.stringify(example, null, 2));
    console.log('\nResulting Lexical:');
    console.log(JSON.stringify(lexical, null, 2));
  } else {
    console.error('Unknown mode. Use: text, structured, or example');
    process.exit(1);
  }
}

/**
 * Create a button card
 * @param {string} buttonText - Button label
 * @param {string} buttonUrl - Link destination
 * @param {string} alignment - "left" or "center" (default: "center")
 */
function createButtonCard(buttonText, buttonUrl, alignment = "center") {
  return {
    type: "button",
    version: 1,
    buttonText,
    alignment,
    buttonUrl
  };
}

/**
 * Create a toggle (collapsible) card
 * @param {string} heading - Toggle header/title
 * @param {string} content - Collapsible content (HTML)
 */
function createToggleCard(heading, content) {
  return {
    type: "toggle",
    version: 1,
    heading: `<span style="white-space: pre-wrap;">${heading}</span>`,
    content: `<p dir="ltr"><span style="white-space: pre-wrap;">${content}</span></p>`
  };
}

/**
 * Create a video card
 * @param {string} src - Video file URL
 * @param {object} options - Optional settings
 */
function createVideoCard(src, options = {}) {
  return {
    type: "video",
    version: 1,
    src,
    caption: options.caption ? `<p dir="ltr"><span style="white-space: pre-wrap;">${options.caption}</span></p>` : "",
    fileName: options.fileName || "",
    mimeType: options.mimeType || "",
    width: options.width || null,
    height: options.height || null,
    duration: options.duration || 0,
    thumbnailSrc: options.thumbnailSrc || "",
    customThumbnailSrc: options.customThumbnailSrc || "",
    thumbnailWidth: options.thumbnailWidth || null,
    thumbnailHeight: options.thumbnailHeight || null,
    cardWidth: options.cardWidth || "regular",
    loop: options.loop || false
  };
}

/**
 * Create an audio card
 * @param {string} src - Audio file URL
 * @param {string} title - Audio title
 * @param {object} options - Optional settings
 */
function createAudioCard(src, title, options = {}) {
  return {
    type: "audio",
    version: 1,
    duration: options.duration || 0,
    mimeType: options.mimeType || "audio/mpeg",
    src,
    title,
    thumbnailSrc: options.thumbnailSrc || ""
  };
}

/**
 * Create a file download card
 * @param {string} src - File URL
 * @param {string} fileTitle - Display title
 * @param {object} options - Optional settings
 */
function createFileCard(src, fileTitle, options = {}) {
  return {
    type: "file",
    src,
    fileTitle,
    fileCaption: options.fileCaption || "",
    fileName: options.fileName || "",
    fileSize: options.fileSize || 0
  };
}

/**
 * Create a product card
 * @param {string} title - Product name
 * @param {string} description - Product description
 * @param {object} options - Optional settings
 */
function createProductCard(title, description, options = {}) {
  return {
    type: "product",
    version: 1,
    productImageSrc: options.imageSrc || "",
    productImageWidth: options.imageWidth || null,
    productImageHeight: options.imageHeight || null,
    productTitle: `<span style="white-space: pre-wrap;">${title}</span>`,
    productDescription: `<p dir="ltr"><span style="white-space: pre-wrap;">${description}</span></p>`,
    productRatingEnabled: options.ratingEnabled || false,
    productStarRating: options.starRating || 5,
    productButtonEnabled: options.buttonEnabled || false,
    productButton: options.buttonText || "",
    productUrl: options.productUrl || ""
  };
}

/**
 * Create a paywall divider
 */
function createPaywallCard() {
  return {
    type: "paywall",
    version: 1
  };
}

/**
 * Create an embed card
 * @param {string} url - URL to embed (YouTube, Spotify, Twitter, etc.)
 * 
 * Note: Ghost will automatically fetch oEmbed metadata when the post is created.
 * This creates a minimal structure that Ghost will populate.
 */
function createEmbedCard(url) {
  return {
    type: "embed",
    version: 1,
    url,
    embedType: "",  // Ghost will populate this
    html: "",        // Ghost will populate this
    metadata: {},    // Ghost will populate this
    caption: ""
  };
}

/**
 * Load and inject a snippet into Lexical content
 * @param {string} snippetName - Name of snippet from library
 * @param {Object} lexicalDoc - Existing Lexical document
 * @param {string} position - 'start', 'end', or number
 * @returns {Object} Updated Lexical document
 */
async function injectSnippetFromLibrary(snippetName, lexicalDoc, position = 'end') {
  // Dynamic import of snippet manager
  const { loadSnippet, injectSnippet } = await import('../snippets/ghost-snippet.js');
  
  const snippet = loadSnippet(snippetName);
  return injectSnippet(snippet, lexicalDoc, position);
}

/**
 * Build Lexical document with snippet at end
 * @param {Array} content - Main content cards
 * @param {string} snippetName - Snippet to append
 * @returns {Object} Complete Lexical document
 */
async function buildLexicalWithSnippet(content, snippetName) {
  const lexical = buildLexical(content);
  return await injectSnippetFromLibrary(snippetName, lexical, 'end');
}

// Update exports
export {
  // Basic content
  createTextNode,
  createParagraph,
  createHeading,
  
  // Build utilities
  buildLexical,
  textToLexical,
  structuredToLexical,
  stringifyLexical,
  
  // Media cards
  createImageCard,
  createGalleryCard,
  createBookmarkCard,
  
  // Layout cards
  createCalloutCard,
  createHorizontalRule,
  
  // Interactive cards
  createButtonCard,
  createToggleCard,
  
  // Upload cards
  createVideoCard,
  createAudioCard,
  createFileCard,
  
  // Newsletter/CTA cards
  createSignupCard,
  createHeaderCard,
  createCallToActionCard,
  
  // Advanced cards
  createProductCard,
  createPaywallCard,
  createEmbedCard,
  createHTMLCard,
  createMarkdownCard,
  
  // Snippet integration
  injectSnippetFromLibrary,
  buildLexicalWithSnippet
};
/**
 * Create an image card with caption and alt text
 * @param {string} src - Image URL
 * @param {Object} options - Optional settings
 * @param {string} options.alt - Alt text for accessibility
 * @param {string} options.caption - Image caption
 * @param {number} options.width - Image width
 * @param {number} options.height - Image height
 * @param {string} options.cardWidth - 'regular', 'wide', or 'full'
 * @param {string} options.href - Link URL
 * @param {string} options.title - Image title
 * @returns {Object} Image card
 */
function createImageCard(src, options = {}) {
  return {
    type: "image",
    version: 1,
    src,
    width: options.width || 1024,
    height: options.height || 768,
    title: options.title || "",
    alt: options.alt || "",
    caption: options.caption || "",
    cardWidth: options.cardWidth || "regular",
    href: options.href || ""
  };
}

/**
 * Create a gallery card with multiple images
 * @param {Array<Object>} images - Array of image objects
 *   Each image: { src, width, height, fileName, row }
 * @param {string} caption - Gallery caption (optional)
 * @returns {Object} Gallery card
 */
function createGalleryCard(images, caption = "") {
  const formattedImages = images.map((img, index) => ({
    row: img.row !== undefined ? img.row : Math.floor(index / 3),
    src: img.src,
    width: img.width || 1024,
    height: img.height || 768,
    fileName: img.fileName || `image${index + 1}.jpg`
  }));
  
  return {
    type: "gallery",
    version: 1,
    images: formattedImages,
    caption
  };
}

/**
 * Create a bookmark card (link preview)
 * @param {string} url - URL to bookmark
 * @param {Object} metadata - Optional metadata (Ghost fetches if empty)
 * @param {string} caption - Optional caption
 * @returns {Object} Bookmark card
 */
function createBookmarkCard(url, metadata = {}, caption = "") {
  return {
    type: "bookmark",
    version: 1,
    url,
    metadata: {
      icon: metadata.icon || "",
      title: metadata.title || "",
      description: metadata.description || "",
      author: metadata.author || "",
      publisher: metadata.publisher || "",
      thumbnail: metadata.thumbnail || ""
    },
    caption
  };
}

/**
 * Create a callout/info box with emoji and background color
 * @param {string} text - Callout text (HTML allowed)
 * @param {Object} options - Optional settings
 * @param {string} options.emoji - Emoji icon (default: 💡)
 * @param {string} options.backgroundColor - Color: blue, green, yellow, red, pink, purple, white, grey, accent
 * @returns {Object} Callout card
 */
function createCalloutCard(text, options = {}) {
  const formattedText = text.includes('<p>') 
    ? text 
    : `<p><span style="white-space: pre-wrap;">${text}</span></p>`;
  
  return {
    type: "callout",
    version: 1,
    calloutText: formattedText,
    calloutEmoji: options.emoji || "💡",
    backgroundColor: options.backgroundColor || "blue"
  };
}

/**
 * Create a horizontal rule (divider line)
 * @returns {Object} Horizontal rule card
 */
function createHorizontalRule() {
  return {
    type: "horizontalrule",
    version: 1
  };
}

/**
 * Create a signup card (newsletter CTA)
 * @param {Object} options - Signup card settings
 * @param {string} options.header - Main heading
 * @param {string} options.subheader - Subtitle
 * @param {string} options.buttonText - Button text (default: 'Subscribe')
 * @param {string} options.disclaimer - Disclaimer text
 * @param {string} options.alignment - 'left', 'center', 'right'
 * @param {string} options.layout - 'wide', 'full'
 * @param {string} options.backgroundColor - Background color (hex or color name)
 * @param {string} options.buttonColor - Button color
 * @returns {Object} Signup card
 */
function createSignupCard(options = {}) {
  return {
    type: "signup",
    version: 1,
    alignment: options.alignment || "left",
    backgroundColor: options.backgroundColor || "#F0F0F0",
    backgroundImageSrc: options.backgroundImageSrc || "",
    backgroundSize: options.backgroundSize || "cover",
    textColor: options.textColor || "#000000",
    buttonColor: options.buttonColor || "accent",
    buttonTextColor: options.buttonTextColor || "#FFFFFF",
    buttonText: options.buttonText || "Subscribe",
    disclaimer: options.disclaimer 
      ? `<span style="white-space: pre-wrap;">${options.disclaimer}</span>`
      : "<span style=\"white-space: pre-wrap;\">No spam. Unsubscribe anytime.</span>",
    header: options.header 
      ? `<span style="white-space: pre-wrap;">${options.header}</span>`
      : "<span style=\"white-space: pre-wrap;\">Sign up for Newsletter</span>",
    labels: options.labels || [],
    layout: options.layout || "wide",
    subheader: options.subheader 
      ? `<span style="white-space: pre-wrap;">${options.subheader}</span>`
      : "<span style=\"white-space: pre-wrap;\">Get updates delivered to your inbox.</span>",
    successMessage: options.successMessage || "Email sent! Check your inbox to complete your signup.",
    swapped: options.swapped || false
  };
}

/**
 * Create a header card (section header with background)
 * @param {string} header - Main heading text
 * @param {Object} options - Header card settings
 * @param {string} options.subheader - Subtitle
 * @param {string} options.size - 'small', 'medium', 'large'
 * @param {string} options.style - 'dark', 'light', 'accent'
 * @param {boolean} options.buttonEnabled - Show button
 * @param {string} options.buttonText - Button text
 * @param {string} options.buttonUrl - Button URL
 * @param {string} options.backgroundImageSrc - Background image URL
 * @param {string} options.backgroundColor - Background color (hex)
 * @param {string} options.alignment - 'left', 'center'
 * @param {string} options.layout - 'wide', 'full', 'split'
 * @returns {Object} Header card
 */
function createHeaderCard(header, options = {}) {
  return {
    type: "header",
    version: 2,
    size: options.size || "small",
    style: options.style || "dark",
    buttonEnabled: options.buttonEnabled || false,
    buttonUrl: options.buttonUrl || "",
    buttonText: options.buttonText || "",
    header: `<span style="white-space: pre-wrap;">${header}</span>`,
    subheader: options.subheader 
      ? `<span style="white-space: pre-wrap;">${options.subheader}</span>`
      : "",
    backgroundImageSrc: options.backgroundImageSrc || "",
    accentColor: options.accentColor || "#15171A",
    alignment: options.alignment || "center",
    backgroundColor: options.backgroundColor || "#000000",
    backgroundImageWidth: options.backgroundImageWidth || 1920,
    backgroundImageHeight: options.backgroundImageHeight || 1080,
    backgroundSize: options.backgroundSize || "cover",
    textColor: options.textColor || "#FFFFFF",
    buttonColor: options.buttonColor || "#ffffff",
    buttonTextColor: options.buttonTextColor || "#000000",
    layout: options.layout || "full",
    swapped: options.swapped || false
  };
}

/**
 * Create a call-to-action card
 * @param {Object} options - CTA card settings
 * @param {string} options.buttonText - Button text
 * @param {string} options.buttonUrl - Button URL
 * @param {string} options.layout - 'minimal', 'default'
 * @param {string} options.alignment - 'left', 'center'
 * @param {boolean} options.showButton - Display button
 * @param {boolean} options.showDividers - Show divider lines
 * @param {boolean} options.hasSponsorLabel - Show sponsor tag
 * @param {string} options.imageUrl - CTA image URL
 * @param {string} options.backgroundColor - Background color
 * @returns {Object} Call-to-action card
 */
function createCallToActionCard(options = {}) {
  return {
    type: "call-to-action",
    version: 1,
    layout: options.layout || "minimal",
    alignment: options.alignment || "left",
    textValue: options.textValue || null,
    showButton: options.showButton !== false,
    showDividers: options.showDividers !== false,
    buttonText: options.buttonText || "Learn more",
    buttonUrl: options.buttonUrl || "",
    buttonColor: options.buttonColor || "#000000",
    buttonTextColor: options.buttonTextColor || "#ffffff",
    hasSponsorLabel: options.hasSponsorLabel || false,
    sponsorLabel: options.sponsorLabel 
      ? `<p><span style="white-space: pre-wrap;">${options.sponsorLabel}</span></p>`
      : "<p><span style=\"white-space: pre-wrap;\">SPONSORED</span></p>",
    backgroundColor: options.backgroundColor || "grey",
    linkColor: options.linkColor || "text",
    imageUrl: options.imageUrl || "",
    imageWidth: options.imageWidth || 600,
    imageHeight: options.imageHeight || 400,
    visibility: options.visibility || {
      web: {
        nonMember: true,
        memberSegment: "status:free,status:-free"
      },
      email: {
        memberSegment: "status:free,status:-free"
      }
    }
  };
}

/**
 * Create an HTML card with custom HTML content
 * @param {string} html - Custom HTML content
 * @param {Object} visibility - Member visibility settings (optional)
 * @returns {Object} HTML card
 */
function createHTMLCard(html, visibility = null) {
  const card = {
    type: "html",
    version: 1,
    html
  };
  
  if (visibility) {
    card.visibility = visibility;
  }
  
  return card;
}

/**
 * Create a markdown card
 * @param {string} markdown - Markdown content
 * @returns {Object} Markdown card
 */
function createMarkdownCard(markdown) {
  return {
    type: "markdown",
    version: 1,
    markdown
  };
}
