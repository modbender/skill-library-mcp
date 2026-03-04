/**
 * Content Extractor - Phase 3.2 Implementation
 *
 * Converts raw HTML into clean, searchable text content.
 * Implements full pipeline: type detection, boilerplate removal, title extraction,
 * content extraction with code preservation, excerpt generation, quality validation.
 */

const { JSDOM } = require('jsdom');
const { marked } = require('marked');

class ContentExtractor {
  constructor(config) {
    this.config = config;
    this.minContentLength = config.content?.min_content_length || 500;
    this.maxContentLength = config.content?.max_content_length || 50000;
  }

  // ============================================================================
  // MAIN ENTRY POINT
  // ============================================================================

  /**
   * Extract content from HTML
   * @param {string} html - Raw HTML
   * @param {string} url - Source URL
   * @returns {Object} { title, content, excerpt, quality, type, issues }
   */
  async extract(html, url) {
    const dom = new JSDOM(html, { url });
    const doc = dom.window.document;

    // 1. Detect content type
    const type = this.detectContentType(doc, url);

    // 2. Remove boilerplate (clone to avoid mutating original)
    const cleanedDoc = this.removeBoilerplate(doc.cloneNode(true));

    // 3. Extract title with priority
    const title = this.extractTitle(cleanedDoc, url);

    // 4. Extract main content based on type
    let content = await this.extractContent(cleanedDoc, type, url);

    if (!content || content.length < 100) {
      // Fallback: body with boilerplate removal
      content = this.extractBodyFallback(cleanedDoc);
    }

    // 5. Normalize content (whitespace, code preservation)
    content = this.normalizeContent(content);

    // 6. Truncate if too long (reserve space for ellipsis)
    if (content.length > this.maxContentLength) {
      const ellipsis = '...';
      const max = this.maxContentLength;
      // Ensure we leave room for ellipsis
      const truncateLen = Math.max(max - ellipsis.length, 0);
      content = content.substring(0, truncateLen).trim() + ellipsis;
    }

    // 7. Generate excerpt (without code blocks)
    const excerpt = this.generateExcerpt(content);

    // 8. Quality validation
    const validation = this.validateQuality(content, title, url);

    return {
      title,
      content,
      excerpt,
      quality: validation.quality,
      type,
      issues: validation.issues,
      url
    };
  }

  // ============================================================================
  // 1. CONTENT TYPE DETECTION
  // ============================================================================

  detectContentType(doc, url) {
    try {
      const urlObj = new URL(url);
      const hostname = urlObj.hostname;

      // Order matters: check special hosts first
      if (hostname === 'raw.githubusercontent.com') {
        return 'github_markdown';
      }

      if (hostname === 'stackprinter.appspot.com') {
        return 'stackprinter';
      }

      // Site-specific map
      const siteMap = {
        'developer.mozilla.org': 'mdn',
        'docs.python.org': 'python_docs',
        'nodejs.org': 'node_docs',
        'en.wikipedia.org': 'wikipedia',
        'github.com': 'github_html',
        'stackoverflow.com': 'stackoverflow',
        'man7.org': 'manpage',
        'linux.die.net': 'manpage',
        'docs.openclaw.ai': 'generic'
      };

      return siteMap[hostname] || 'generic';
    } catch (e) {
      return 'generic';
    }
  }

  // ============================================================================
  // 2. BOILERPLATE REMOVAL
  // ============================================================================

  removeBoilerplate(element) {
    // Elements that should always be removed
    const selectors = [
      // Navigation
      'nav', 'header', 'footer',
      '[role="navigation"]', '[role="banner"]', '[role="contentinfo"]',
      '.navbar', '.nav', '.menu', '.breadcrumb', '.breadcrumbs',
      // Sidebars
      'aside', '.sidebar', '.side-bar', '[role="complementary"]',
      // Ads & promos
      '.ad', '.advertisement', '.ads', '.advert',
      '[class*="advert"]', '[id*="ad"]',
      // UI elements
      '.cookie-banner', '.cookie-consent', '.gdpr',
      '.newsletter-signup', '.subscribe',
      '.social-share', '.share-buttons',
      '.comment-form', '#comments', '.discussion',
      // Metadata areas
      '.meta', '.metadata', '.byline',
      '.author-info', '.post-meta',
      '.published-date', '.modified-date',
      // Related content (often duplicate)
      '.related-articles', '.read-more', '.see-also',
      '.similar-pages', '.recommended', '.popular-posts',
      // Scripts, styles, media
      'script', 'style', 'noscript',
      'iframe', 'object', 'embed', 'video', 'audio',
      // Hidden
      '[hidden]',
      '[style*="display: none"]',
      '[style*="visibility: hidden"]',
      '[aria-hidden="true"]'
    ];

    selectors.forEach(selector => {
      try {
        element.querySelectorAll(selector).forEach(el => el.remove());
      } catch (e) {
        // ignore invalid selectors
      }
    });

    return element;
  }

  // ============================================================================
  // 3. TITLE EXTRACTION (Priority Order)
  // ============================================================================

  extractTitle(doc, url) {
    const hostname = new URL(url).hostname;

    // 1. <title> tag
    let title = doc.querySelector('title')?.textContent.trim() || '';

    // 2. <h1> if exactly one
    if (!title) {
      const h1s = doc.querySelectorAll('h1');
      if (h1s.length === 1) {
        title = h1s[0].textContent.trim();
      }
    }

    // 3. OpenGraph meta
    if (!title) {
      const og = doc.querySelector('meta[property="og:title"]');
      if (og) title = og.getAttribute('content')?.trim() || '';
    }

    // 4. Twitter meta
    if (!title) {
      const tw = doc.querySelector('meta[name="twitter:title"]');
      if (tw) title = tw.getAttribute('content')?.trim() || '';
    }

    // 5. First <h2>
    if (!title) {
      const h2 = doc.querySelector('h2');
      if (h2) title = h2.textContent.trim();
    }

    // 6. First sentence of content (fallback)
    if (!title) {
      const bodyText = doc.body?.textContent.trim() || '';
      // Special case for raw GitHub markdown: use first line as title (before newline)
      if (hostname.includes('raw.githubusercontent.com')) {
        // Take first non-empty line; if it starts with '#', strip only the leading '#'
        const lines = bodyText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        const firstLine = lines[0] || '';
        // Only strip leading '#', preserve rest (e.g., "Node.js")
        title = firstLine.replace(/^#+\s*/, '').trim();
      } else {
        const firstSentence = bodyText.split(/[.!?]/)[0];
        title = firstSentence.substring(0, 150);
      }
    }

    // Clean title: remove site suffixes
    title = this.cleanTitle(title, hostname);

    // Length limit
    if (title.length > 150) {
      title = title.substring(0, 147) + '...';
    }

    return title.trim();
  }

  cleanTitle(title, hostname) {
    if (!title) return '';

    // Site-specific suffix patterns
    const suffixPatterns = [
      new RegExp(` - ${hostname}$`, 'i'),
      new RegExp(` \\| ${hostname}$`, 'i'),
      new RegExp(` — ${hostname}$`, 'i'),
      new RegExp(` :: ${hostname}$`, 'i'),
      / - Documentation$/i,
      / - MDN$/i,
      / - Wikipedia$/i,
      / · GitHub$/i,
      / \| Docs$/i
    ];

    for (const pattern of suffixPatterns) {
      title = title.replace(pattern, '');
    }

    return title.trim();
  }

  // ============================================================================
  // 4. CONTENT EXTRACTION BY TYPE
  // ============================================================================

  async extractContent(doc, type, url) {
    switch (type) {
      case 'mdn':
        return this.extractMDN(doc);
      case 'python_docs':
        return this.extractPythonDocs(doc);
      case 'wikipedia':
        return this.extractWikipedia(doc);
      case 'github_html':
        return this.extractGitHubHTML(doc);
      case 'github_markdown':
        return this.extractGitHubMarkdown(doc, url);
      case 'stackprinter':
        return this.extractStackPrinter(doc);
      case 'manpage':
        return this.extractManPage(doc);
      case 'generic':
      default:
        return this.extractGeneric(doc);
    }
  }

  extractMDN(doc) {
    const selectors = [
      'article.main-page-content',
      '#content article',
      'article'
    ];

    const el = this.selectFirst(doc, selectors);
    if (!el) return null;

    // MDN-specific cleanup
    el.querySelectorAll('aside.interactive, .document-toc').forEach(e => e.remove());

    return this.elementToText(el);
  }

  extractPythonDocs(doc) {
    const selectors = [
      '.body',
      'div.document',
      'div.bodywrapper > div.body',
      '[role="main"]'
    ];
    const el = this.selectFirst(doc, selectors);
    return el ? this.elementToText(el) : null;
  }

  extractWikipedia(doc) {
    const selectors = [
      '#mw-content-text',
      '.mw-parser-output'
    ];
    const el = this.selectFirst(doc, selectors);
    if (!el) return null;

    // Remove infobox, navbox, See also
    el.querySelectorAll('.infobox, .navbox, #See_also').forEach(e => {
      const section = e.closest('div, section');
      if (section) section.remove();
      else e.remove();
    });

    return this.elementToText(el);
  }

  extractGitHubHTML(doc) {
    const selectors = [
      '.markdown-body',
      '.repository-content .Box'
    ];
    const el = this.selectFirst(doc, selectors);
    return el ? this.elementToText(el) : null;
  }

  extractGitHubMarkdown(doc, url) {
    // Raw markdown from raw.githubusercontent.com: keep as plain text to preserve code fences
    const markdown = doc.body?.textContent.trim() || '';
    return markdown || null;
  }

  extractStackPrinter(doc) {
    // StackPrinter pages: entire body is Q&A text
    const body = doc.body?.textContent.trim() || '';
    // Could parse into separate docs, but for now return whole body
    return body;
  }

  extractManPage(doc) {
    // Find <pre> with man page content
    const pre = doc.querySelector('pre.manpage, pre.man-text, pre');
    if (!pre) return null;

    let text = pre.textContent;

    // Strip headers/footers
    text = text.replace(/^Manual page.*$/gm, '');
    text = text.replace(/^Linux man-pages.*$/gm, '');
    text = text.replace(/^\s*Page \d+.*$/gm, '');

    // Extract title from NAME section
    const nameMatch = text.match(/NAME\s+(.+?)\s+-\s+(.+)/s);
    if (nameMatch) {
      // Title will be set separately; content includes full man page
    }

    return text.trim();
  }

  extractGeneric(doc) {
    const selectors = [
      'article',
      'main',
      '[role="main"]',
      '.content',
      '.main-content',
      '#content',
      '.documentation',
      'section',
      '.body',
      '.post-content',
      'div.content-wrapper',
      'div.container > div.row'
    ];

    const el = this.selectFirst(doc, selectors);
    if (el && el.textContent.length > 500) {
      return this.elementToText(el);
    }

    // Fallback: text density scoring
    return this.extractByTextDensity(doc);
  }

  selectFirst(doc, selectors) {
    for (const selector of selectors) {
      const el = doc.querySelector(selector);
      if (el && el.textContent.trim().length > 500) {
        return el;
      }
    }
    return null;
  }

  extractByTextDensity(doc) {
    const candidates = doc.querySelectorAll('div, article, section');
    let bestElement = null;
    let bestScore = -Infinity;

    for (const element of candidates) {
      const score = this.scoreElement(element);
      if (score > bestScore) {
        bestScore = score;
        bestElement = element;
      }
    }

    if (bestElement && bestScore > 0.5) {
      return this.elementToText(bestElement);
    }

    return null;
  }

  scoreElement(element) {
    const text = element.textContent.trim();
    const textLength = text.length;

    // Count child elements (excluding script/style)
    const tags = element.querySelectorAll('*:not(script):not(style):not(svg)');
    const tagCount = tags.length;

    // Link density
    const links = element.querySelectorAll('a');
    const linkCount = links.length;
    const linkDensity = linkCount / (textLength / 100 + 1);

    // Score: more text, fewer tags, lower link density
    return textLength / (tagCount + linkDensity * 20 + 1);
  }

  extractBodyFallback(doc) {
    const body = doc.body?.cloneNode(true) || doc.documentElement.cloneNode(true);

    // Remove obvious boilerplate
    const removals = ['nav', 'header', 'footer', 'aside', '.sidebar', 'script', 'style', '.ad'];
    removals.forEach(sel => {
      try {
        body.querySelectorAll(sel).forEach(el => el.remove());
      } catch (e) {}
    });

    return body.textContent.trim().replace(/\s+/g, ' ');
  }

  // ============================================================================
  // 5. TEXT NORMALIZATION & CODE PRESERVATION
  // ============================================================================

  normalizeContent(content) {
    if (!content) return '';

    // We need to preserve code blocks. Assuming content may already have
    // ``` markers from elementToText, we only collapse whitespace outside code.
    // Split by code blocks, normalize text parts, reassemble.

    const parts = content.split(/(```[\s\S]*?```)/g);

    return parts.map(part => {
      if (part.startsWith('```') && part.endsWith('```')) {
        return part; // Leave code blocks untouched
      }
      // Normalize whitespace in text
      return part
        .replace(/\s+/g, ' ')           // Collapse whitespace
        .replace(/\n\s*\n/g, '\n')      // Preserve paragraph breaks
        .replace(/[\u200B-\u200D\uFEFF]/g, ''); // Remove zero-width spaces
    }).join('').trim();
  }

  elementToText(element) {
    let content = '';

    function traverse(node) {
      if (node.nodeType === 3) {
        // Text node
        content += node.textContent;
      } else if (node.nodeType === 1) {
        // Element node
        const tag = node.tagName.toLowerCase();

        if (tag === 'pre') {
          // Code block
          const code = node.textContent;
          content += '\n```\n' + code.trim() + '\n```\n';
        } else if (tag === 'code') {
          // Inline code (if not inside pre)
          const parent = node.parentElement?.tagName.toLowerCase();
          if (parent !== 'pre') {
            content += '`' + node.textContent.trim() + '`';
          }
        } else if (tag === 'br') {
          content += '\n';
        } else {
          // Recurse
          node.childNodes.forEach(traverse);
        }
      }
    }

    traverse(element);
    return content.trim();
  }

  // ============================================================================
  // 6. EXCERPT GENERATION
  // ============================================================================

  generateExcerpt(content, maxLength = 200) {
    if (!content) return '';

    // Remove code blocks for excerpt
    const textOnly = content.replace(/```[\s\S]*?```/g, '');

    if (textOnly.length <= maxLength) {
      return textOnly;
    }

    // Truncate to maxLength
    let truncated = textOnly.substring(0, maxLength);

    // Find last sentence boundary
    const lastPeriod = truncated.lastIndexOf('. ');
    const lastQuestion = truncated.lastIndexOf('? ');
    const lastExclamation = truncated.lastIndexOf('! ');

    const cutoff = Math.max(lastPeriod, lastQuestion, lastExclamation);

    if (cutoff > maxLength * 0.5) {
      return truncated.substring(0, cutoff + 1) + '...';
    }

    // Otherwise cut at word boundary
    const lastSpace = truncated.lastIndexOf(' ');
    if (lastSpace > maxLength * 0.7) {
      return truncated.substring(0, lastSpace) + '...';
    }

    return truncated + '...';
  }

  // ============================================================================
  // 7. QUALITY VALIDATION
  // ============================================================================

  validateQuality(content, title, url) {
    const issues = [];
    const contentLower = (content + ' ' + title).toLowerCase();

    // Length check
    if (content.length < this.minContentLength) {
      issues.push({
        level: 'warn',
        code: 'content_too_short',
        length: content.length,
        message: `Content too short (${content.length} < ${this.minContentLength})`
      });
    }

    // Error page detection
    const ERROR_PATTERNS = [
      /page not found/i,
      /404 not found/i,
      /error 404/i,
      /content not available/i,
      /access denied/i,
      /login required/i,
      /sign in to/i,
      /this page does not exist/i,
      /the page you requested was not found/i,
      /we couldn't find that page/i
    ];

    if (ERROR_PATTERNS.some(pattern => pattern.test(contentLower))) {
      issues.push({
        level: 'error',
        code: 'error_page',
        message: 'Detected error page patterns'
      });
    }

    // Stub detection
    const STUB_PATTERNS = [
      /this article is a stub/i,
      /this section needs expansion/i,
      /help improve this article/i,
      /placeholder page/i,
      /to be written/i,
      /coming soon/i,
      /under construction/i
    ];

    if (STUB_PATTERNS.some(pattern => pattern.test(contentLower))) {
      issues.push({
        level: 'warn',
        code: 'stub_content',
        message: 'Detected stub/placeholder content'
      });
    }

    // Link density
    const linkCount = (content.match(/\[/g) || []).length; // approximate markdown links? Actually we should count <a> but content is plain text now
    // Better: compute from original element before conversion
    // For now, skip link density (needs original element)

    // Determine overall quality
    let quality = 'high';
    if (issues.some(i => i.level === 'error')) {
      quality = 'low';
    } else if (issues.some(i => i.level === 'warn')) {
      quality = 'medium';
    }

    return {
      quality,
      issues
    };
  }
}

module.exports = ContentExtractor;
