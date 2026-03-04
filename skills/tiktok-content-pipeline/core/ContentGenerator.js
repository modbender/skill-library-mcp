/**
 * Content Generator Base Class
 * 
 * Abstract interface for all content generators.
 * Each niche extends this with domain-specific logic (e.g. gaming, property, collectibles).
 */

class ContentGenerator {
  constructor(config) {
    this.config = config;
    this.assetsDir = config.assetsDir;
    this.dataDir = config.dataDir;
  }

  /**
   * Generate content based on type and options
   * 
   * @param {string} contentType - Type of content to generate
   * @param {Object} options - Content-specific options
   * @param {string} outputDir - Where to save generated content
   * @returns {Promise<Object>} Generated content metadata
   */
  async generate(contentType, options = {}, outputDir) {
    if (!this.getSupportedTypes().includes(contentType)) {
      throw new Error(`Content type '${contentType}' not supported by ${this.constructor.name}`);
    }

    const startTime = Date.now();
    const result = await this._generateContent(contentType, options, outputDir);
    const duration = Date.now() - startTime;

    return {
      ...result,
      contentType,
      duration,
      timestamp: new Date().toISOString(),
      generator: this.constructor.name
    };
  }

  /**
   * Get supported content types for this generator
   * @returns {Array<string>} Supported content types
   */
  getSupportedTypes() {
    throw new Error('getSupportedTypes must be implemented by subclass');
  }

  /**
   * Get content type configuration
   * @param {string} contentType 
   * @returns {Object} Content type config
   */
  getContentConfig(contentType) {
    return this.config.content.types[contentType] || {};
  }

  /**
   * Generate hook/caption for content type
   * @param {string} contentType 
   * @param {Object} context - Content context (player, property, etc.)
   * @returns {string} Generated hook
   */
  generateHook(contentType, context = {}) {
    const hooks = this.config.hooks[contentType] || [];
    if (hooks.length === 0) return '';

    // Simple random selection - could be made smarter with performance data
    const hook = hooks[Math.floor(Math.random() * hooks.length)];
    
    // Replace placeholders
    return this._replacePlaceholders(hook, context);
  }

  /**
   * Generate a question hook for driving comment engagement.
   * Returns null if no question hooks are configured for this content type.
   */
  generateQuestionHook(contentType, context = {}) {
    const questionHooks = (this.config.questionHooks || {})[contentType] || [];
    if (questionHooks.length === 0) return null;

    const hook = questionHooks[Math.floor(Math.random() * questionHooks.length)];
    return this._replacePlaceholders(hook, context);
  }

  /**
   * Get the slide 1 hook text — 50/50 chance of using a question hook
   * when one is available, to drive comment engagement.
   * @returns {{ text: string, isQuestion: boolean }}
   */
  getSlide1Hook(contentType, context = {}) {
    const questionHook = this.generateQuestionHook(contentType, context);
    if (questionHook && Math.random() < 0.5) {
      return { text: questionHook, isQuestion: true };
    }
    return { text: this.generateHook(contentType, context), isQuestion: false };
  }

  /**
   * Build a caption, appending the question hook if present.
   */
  buildCaption(hook, slide1Hook) {
    if (slide1Hook.isQuestion) {
      return `${hook}\n\n${slide1Hook.text}`;
    }
    return hook;
  }

  /**
   * Get optimal hashtags for content type
   * @param {string} contentType 
   * @returns {Array<string>} Hashtags
   */
  getHashtags(contentType) {
    const hashtagSets = this.config.content.hashtagSets || {};
    return hashtagSets[contentType] || hashtagSets.default || [];
  }

  /**
   * Abstract method - implement in subclass
   * @private
   */
  async _generateContent(contentType, options, outputDir) {
    throw new Error('_generateContent must be implemented by subclass');
  }

  /**
   * Get SEO keyword overlay text for a given content type and slide number.
   * Returns 1-2 keywords to overlay on the slide, cycling through available keywords.
   * 
   * @param {string} contentType - Content type key
   * @param {number} slideNumber - 1-indexed slide number
   * @returns {string|null} Keyword text to overlay, or null if no keywords configured
   */
  getSearchKeywordOverlay(contentType, slideNumber) {
    const keywords = (this.config.searchKeywords || {})[contentType];
    if (!keywords || keywords.length === 0) return null;

    // Pick 1-2 keywords per slide, cycling through the list
    const idx = (slideNumber - 1) % keywords.length;
    const picked = [keywords[idx]];
    // Add a second keyword on even slides if available
    if (slideNumber % 2 === 0 && keywords.length > 1) {
      const idx2 = (idx + 1) % keywords.length;
      picked.push(keywords[idx2]);
    }
    return picked.join(' · ');
  }

  /**
   * Build an ImageMagick argument fragment that composites a semi-transparent
   * keyword overlay at the bottom of a slide. Append this to an existing
   * `convert` command (before the output path).
   * 
   * @param {string} keywordText - Text to overlay
   * @param {Object} slideSize - { width, height }
   * @returns {string} ImageMagick CLI fragment
   */
  buildKeywordOverlayArgs(keywordText, slideSize) {
    if (!keywordText) return '';
    const { width } = slideSize;
    const escapedText = keywordText.replace(/'/g, "'\\''");
    // Small, semi-transparent white text at the bottom
    return ` \\( -size ${width}x60 xc:none -fill "rgba(255,255,255,0.35)" ` +
           `-font Arial -pointsize 22 -gravity center -annotate +0+0 '${escapedText}' \\) ` +
           `-gravity south -composite`;
  }

  /**
   * Replace placeholders in text with context values
   * @private
   */
  _replacePlaceholders(text, context) {
    return text.replace(/\{(\w+)\}/g, (match, key) => {
      return context[key] || match;
    });
  }

  /**
   * Ensure output directory exists
   * @private
   */
  _ensureOutputDir(outputDir) {
    const fs = require('fs');
    const path = require('path');
    
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    return outputDir;
  }
}

module.exports = ContentGenerator;