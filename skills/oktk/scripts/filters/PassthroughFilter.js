/**
 * PassthroughFilter - Minimal safe filtering (always succeeds)
 * Used as fallback when specialized filters fail
 */

const BaseFilter = require('./BaseFilter');

class PassthroughFilter extends BaseFilter {
  async apply(output, context = {}) {
    try {
      // This filter MUST always succeed
      // Only do safe, minimal transformations

      // 1. Remove ANSI color codes (safe operation)
      let clean = output.replace(/\x1b\[[0-9;]*m/g, '');

      // 2. Remove carriage returns (safe operation)
      clean = clean.replace(/\r/g, '');

      // 3. Trim excessive whitespace (safe operation)
      // Replace 3+ consecutive newlines with 2 newlines
      clean = clean.replace(/\n{3,}/g, '\n\n');

      // 4. Trim trailing whitespace (safe operation)
      clean = clean.trim();

      // 5. Safety check: truncate if HUGE (prevents memory issues)
      const MAX_SIZE = 1000000; // 1MB
      if (clean.length > MAX_SIZE) {
        const keepStart = Math.floor(MAX_SIZE / 2);
        const keepEnd = Math.floor(MAX_SIZE / 2);

        clean = [
          clean.substring(0, keepStart),
          `\n\n[... ${clean.length - MAX_SIZE} characters truncated ...]\n\n`,
          clean.substring(clean.length - keepEnd)
        ].join('');
      }

      // 6. Return as-is if all else fails
      return clean;

    } catch (error) {
      // If even this fails, return original output
      // This should NEVER happen, but we're paranoid
      return output;
    }
  }
}

module.exports = PassthroughFilter;
