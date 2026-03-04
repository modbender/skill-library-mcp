/**
 * NetworkFilter - Filter network operation commands (curl, wget, httpie)
 */

const BaseFilter = require('./BaseFilter');

class NetworkFilter extends BaseFilter {
  async apply(output, context = {}) {
    // Check if filtering is safe
    if (!this.canFilter(output)) {
      return output;
    }

    // Remove ANSI codes
    output = this.removeAnsiCodes(output);

    // Detect command type
    const command = context.command || '';
    if (command.includes('curl')) {
      return this.filterCurl(output, command);
    } else if (command.includes('wget')) {
      return this.filterWget(output);
    } else if (command.includes('http') || command.includes('https')) {
      return this.filterHttpie(output);
    } else {
      return this.filterGeneric(output);
    }
  }

  /**
   * Filter curl output
   */
  filterCurl(output, command) {
    // Extract URL from command
    const urlMatch = command.match(/https?:\/\/[^\s]+/);
    const url = urlMatch ? urlMatch[0] : 'unknown';

    // Check if output is JSON
    const isJson = this.isJson(output);

    // Check if output is HTML
    const isHtml = this.isHtml(output);

    if (isJson) {
      return this.filterJson(output);
    } else if (isHtml) {
      return this.filterHtml(output);
    } else {
      return this.filterText(output, url);
    }
  }

  /**
   * Filter wget output
   */
  filterWget(output) {
    const lines = output.split('\n');

    let downloaded = false;
    let size = 0;
    let speed = 0;
    let filename = '';

    for (const line of lines) {
      const savedMatch = line.match(/saved\s+\[([^\]]+)\]/);
      if (savedMatch) {
        downloaded = true;
        const sizeStr = savedMatch[1];
        const sizeNum = parseInt(sizeStr);
        if (!isNaN(sizeNum)) size = sizeNum;
      }

      const speedMatch = line.match(/\(([\d.]+\s*[KM]?B\/s)\)/);
      if (speedMatch) speed = speedMatch[1];

      const fileMatch = line.match(/saved\s+to\s+['"](.+)['"]/);
      if (fileMatch) filename = fileMatch[1];
    }

    const result = [];
    result.push(downloaded ? '✅ Download complete' : '⏳ Download in progress');
    result.push(`📁 ${filename || 'unknown'}`);
    if (size > 0) result.push(`📊 Size: ${this.formatBytes(size)}`);
    if (speed) result.push(`⚡ Speed: ${speed}`);

    return result.join('\n');
  }

  /**
   * Filter httpie output
   */
  filterHttpie(output) {
    // HTTPie outputs JSON with headers
    const lines = output.split('\n');

    let status = '';
    let headers = {};
    let bodyStart = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // Status line (HTTP/1.1 200 OK)
      const statusMatch = line.match(/^HTTP\/\d\.\d\s+(\d+)\s+(.+)/);
      if (statusMatch) {
        status = `${statusMatch[1]} ${statusMatch[2]}`;
        continue;
      }

      // Headers (Key: Value)
      const headerMatch = line.match(/^([^:]+):\s*(.+)$/);
      if (headerMatch && bodyStart === 0) {
        headers[headerMatch[1].toLowerCase()] = headerMatch[2];
        continue;
      }

      // Empty line marks start of body
      if (line === '' && bodyStart === 0) {
        bodyStart = i + 1;
        break;
      }
    }

    const result = [];

    // Status
    if (status) {
      const statusCode = parseInt(status.split(' ')[0]);
      if (statusCode >= 200 && statusCode < 300) {
        result.push(`✅ ${status}`);
      } else if (statusCode >= 400 && statusCode < 500) {
        result.push(`❌ ${status}`);
      } else {
        result.push(`⚠️  ${status}`);
      }
    }

    // Key headers
    if (headers['content-type']) {
      result.push(`📄 ${headers['content-type']}`);
    }
    if (headers['content-length']) {
      const size = parseInt(headers['content-length']);
      result.push(`📊 Size: ${this.formatBytes(size)}`);
    }

    // Body
    if (bodyStart > 0) {
      const body = lines.slice(bodyStart).join('\n');

      if (this.isJson(body)) {
        const jsonSummary = this.summarizeJson(body);
        result.push(``);
        result.push(`📦 JSON ${jsonSummary}`);
      } else if (this.isHtml(body)) {
        result.push(``);
        result.push(`🌐 HTML document`);
        const title = this.extractHtmlTitle(body);
        if (title) result.push(`   Title: ${title}`);
      } else {
        const preview = body.substring(0, 200);
        result.push(``);
        result.push(`📝 Body preview:`);
        result.push(`   ${preview}...`);
      }
    }

    return result.join('\n');
  }

  /**
   * Filter JSON output
   */
  filterJson(output) {
    try {
      const json = JSON.parse(output);
      const summary = this.summarizeJson(json);

      const result = [`📦 JSON ${summary}`];

      // Pretty print if small enough
      if (output.length < 2000) {
        result.push(``);
        result.push('```json');
        result.push(JSON.stringify(json, null, 2));
        result.push('```');
      }

      return result.join('\n');
    } catch (error) {
      // Not valid JSON, fall back to text filter
      return this.filterText(output);
    }
  }

  /**
   * Filter HTML output
   */
  filterHtml(output) {
    const title = this.extractHtmlTitle(output);

    const result = [
      '🌐 HTML document',
      `📄 ${this.formatBytes(output.length)}`
    ];

    if (title) {
      result.push(`📝 Title: ${title}`);
    }

    // Extract links count
    const linkMatches = output.match(/<a\s+href/gi);
    if (linkMatches) {
      result.push(`🔗 Links: ${linkMatches.length}`);
    }

    return result.join('\n');
  }

  /**
   * Filter generic text output
   */
  filterText(output, url = 'unknown') {
    const lines = output.split('\n').filter(l => l.trim());

    const result = [
      `📄 Response from ${url}`,
      `📊 ${this.formatBytes(output.length)}`
    ];

    if (lines.length > 0) {
      result.push(`📝 ${lines.length} lines`);
    }

    // Show first few lines
    if (lines.length > 0) {
      result.push(``);
      result.push(`Preview:`);
      lines.slice(0, 5).forEach(l => {
        result.push(`  ${l.substring(0, 80)}`);
      });
      if (lines.length > 5) {
        result.push(`  ... and ${lines.length - 5} more lines`);
      }
    }

    return result.join('\n');
  }

  /**
   * Generic filter
   */
  filterGeneric(output) {
    const lines = output.split('\n').filter(l => l.trim());

    if (lines.length <= 20) {
      return output;
    }

    return [
      ...lines.slice(0, 10),
      ``,
      `[... ${lines.length - 15} lines hidden ...]`,
      ``,
      ...lines.slice(-5)
    ].join('\n');
  }

  /**
   * Check if output is JSON
   */
  isJson(output) {
    try {
      JSON.parse(output.trim());
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Check if output is HTML
   */
  isHtml(output) {
    return /<html|<body|<head|<div/i.test(output);
  }

  /**
   * Extract HTML title
   */
  extractHtmlTitle(html) {
    const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i);
    return titleMatch ? titleMatch[1].trim() : null;
  }

  /**
   * Summarize JSON structure
   */
  summarizeJson(json) {
    if (typeof json !== 'object') {
      return `(${typeof json})`;
    }

    if (Array.isArray(json)) {
      return `array[${json.length}]`;
    }

    const keys = Object.keys(json);
    return `object{${keys.length} keys}`;
  }

  /**
   * Summarize JSON from string
   */
  summarizeJson(jsonStr) {
    try {
      return this.summarizeJson(JSON.parse(jsonStr));
    } catch {
      return '(parse error)';
    }
  }
}

module.exports = NetworkFilter;
