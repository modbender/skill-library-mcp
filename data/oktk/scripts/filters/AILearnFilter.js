/**
 * AILearnFilter - Learn to filter new commands using AI
 * 
 * When an unknown command is encountered and AI learning is enabled,
 * this filter uses a cheap/local LLM to analyze the output and
 * extract the essential information.
 * 
 * The learned patterns are cached for future use.
 */

const BaseFilter = require('./BaseFilter');
const fs = require('fs');
const path = require('path');

class AILearnFilter extends BaseFilter {
  constructor(context = {}) {
    super(context);
    
    // Config
    this.enabled = process.env.OKTK_AI_LEARN === '1' || context.aiLearn === true;
    this.model = process.env.OKTK_AI_MODEL || 'glm-flash'; // Default to cheap model
    this.learnedDir = path.join(process.env.HOME, '.oktk', 'learned');
    
    // Ensure learned dir exists
    if (this.enabled) {
      try {
        fs.mkdirSync(this.learnedDir, { recursive: true });
      } catch (e) {}
    }
  }

  /**
   * Check if we have a learned pattern for this command
   */
  getLearnedPattern(command) {
    const cmdKey = this.getCommandKey(command);
    const patternFile = path.join(this.learnedDir, `${cmdKey}.json`);
    
    try {
      const data = fs.readFileSync(patternFile, 'utf8');
      return JSON.parse(data);
    } catch {
      return null;
    }
  }

  /**
   * Save learned pattern
   */
  saveLearnedPattern(command, pattern) {
    const cmdKey = this.getCommandKey(command);
    const patternFile = path.join(this.learnedDir, `${cmdKey}.json`);
    
    try {
      fs.writeFileSync(patternFile, JSON.stringify(pattern, null, 2));
      return true;
    } catch (e) {
      console.error('Failed to save pattern:', e.message);
      return false;
    }
  }

  /**
   * Get a stable key for the command type
   */
  getCommandKey(command) {
    // Extract the base command (first 1-2 words)
    const parts = command.trim().split(/\s+/);
    const key = parts.slice(0, 2).join('-').toLowerCase()
      .replace(/[^a-z0-9-]/g, '');
    return key || 'unknown';
  }

  /**
   * Apply filter - use learned pattern or learn new one
   */
  async apply(output, context = {}) {
    if (!this.canFilter(output)) {
      return output;
    }

    const command = context.command || '';
    
    // Check for learned pattern first
    const learned = this.getLearnedPattern(command);
    if (learned) {
      return this.applyLearnedPattern(output, learned);
    }

    // If AI learning is not enabled, return truncated output
    if (!this.enabled) {
      return this.truncateOutput(output);
    }

    // Learn new pattern using AI
    try {
      const pattern = await this.learnPattern(command, output);
      if (pattern) {
        this.saveLearnedPattern(command, pattern);
        return this.applyLearnedPattern(output, pattern);
      }
    } catch (e) {
      console.error('AI learning failed:', e.message);
    }

    return this.truncateOutput(output);
  }

  /**
   * Learn a new pattern using heuristics
   * (AI-based learning removed for security - uses smart heuristics instead)
   */
  async learnPattern(command, output) {
    // Use heuristic-based pattern creation (no external calls)
    return this.createSimplePattern(command, output);
  }

  /**
   * Create a simple pattern without AI
   */
  createSimplePattern(command, output) {
    const lines = output.split('\n').filter(l => l.trim());
    
    // Count patterns
    const hasNumbers = lines.some(l => /\d+/.test(l));
    const hasErrors = lines.some(l => /error|fail|exception/i.test(l));
    const hasSuccess = lines.some(l => /success|ok|pass|done/i.test(l));

    return {
      summary_template: `📋 ${lines.length} lines${hasErrors ? '\\n❌ Contains errors' : ''}${hasSuccess ? '\\n✅ Success indicators found' : ''}`,
      extract_rules: [
        { name: 'line_count', pattern: '.*', count: true },
        { name: 'errors', pattern: '(error|fail|exception).*', flags: 'i' },
      ],
      importance: ['errors', 'line_count']
    };
  }

  /**
   * Apply a learned pattern to output
   */
  applyLearnedPattern(output, pattern) {
    const lines = output.split('\n').filter(l => l.trim());
    const extracted = {};

    // Extract values using rules
    for (const rule of (pattern.extract_rules || [])) {
      try {
        if (rule.count) {
          extracted[rule.name] = lines.length;
        } else {
          const regex = new RegExp(rule.pattern, rule.flags || 'i');
          const match = output.match(regex);
          extracted[rule.name] = match ? match[1] || match[0] : rule.default || '';
        }
      } catch (e) {
        extracted[rule.name] = rule.default || '';
      }
    }

    // Apply template
    let result = pattern.summary_template || '📋 {line_count} lines';
    for (const [key, value] of Object.entries(extracted)) {
      result = result.replace(new RegExp(`\\{${key}\\}`, 'g'), value);
    }

    // Always include errors if present
    const errors = lines.filter(l => /error|fail|exception/i.test(l));
    if (errors.length > 0 && !result.includes('error')) {
      result += `\n❌ ${errors.length} error(s):\n${errors.slice(0, 3).join('\n')}`;
    }

    return result;
  }

  /**
   * Simple truncation fallback
   */
  truncateOutput(output) {
    const lines = output.split('\n').filter(l => l.trim());
    
    if (lines.length <= 15) {
      return output;
    }

    // Show first 7 and last 5 lines
    return [
      ...lines.slice(0, 7),
      `\n[... ${lines.length - 12} lines hidden ...]\n`,
      ...lines.slice(-5)
    ].join('\n');
  }

  /**
   * List all learned patterns
   */
  listLearned() {
    try {
      const files = fs.readdirSync(this.learnedDir);
      return files.filter(f => f.endsWith('.json')).map(f => f.replace('.json', ''));
    } catch {
      return [];
    }
  }

  /**
   * Clear learned patterns
   */
  clearLearned() {
    try {
      const files = fs.readdirSync(this.learnedDir);
      for (const file of files) {
        fs.unlinkSync(path.join(this.learnedDir, file));
      }
      return true;
    } catch {
      return false;
    }
  }
}

module.exports = AILearnFilter;
