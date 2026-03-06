/**
 * SearchFilter - Filter search commands (grep, ripgrep, ack)
 */

const BaseFilter = require('./BaseFilter');

class SearchFilter extends BaseFilter {
  async apply(output, context = {}) {
    // Check if filtering is safe
    if (!this.canFilter(output)) {
      return output;
    }

    // Remove ANSI codes
    output = this.removeAnsiCodes(output);

    // Detect command type
    const command = context.command || '';
    if (command.includes('grep') || command.includes('rg') || command.includes('ack')) {
      return this.filterGrep(output);
    } else {
      return this.filterGeneric(output);
    }
  }

  /**
   * Filter grep/ripgrep output
   */
  filterGrep(output) {
    const lines = output.split('\n').filter(l => l.trim());

    if (lines.length === 0) return 'No matches found';

    // Count matches by file
    const matchesByFile = {};
    let totalMatches = 0;
    let totalLines = 0;

    for (const line of lines) {
      // Skip non-match lines (binary file, permission denied, etc.)
      if (line.includes('Binary file') ||
          line.includes('Permission denied') ||
          line.includes('Is a directory')) {
        continue;
      }

      // Parse grep output format: filename:lineNumber:content
      const parts = line.split(':');

      if (parts.length >= 3) {
        const filename = parts[0];
        const lineNumber = parts[1];
        const content = parts.slice(2).join(':');

        if (!matchesByFile[filename]) {
          matchesByFile[filename] = {
            count: 0,
            lines: []
          };
        }

        matchesByFile[filename].count++;
        matchesByFile[filename].lines.push({
          number: lineNumber,
          content: content.trim()
        });

        totalMatches++;
        totalLines++;
      } else if (parts.length === 2) {
        // Alternative format: filename:content (no line number)
        const filename = parts[0];
        const content = parts[1];

        if (!matchesByFile[filename]) {
          matchesByFile[filename] = {
            count: 0,
            lines: []
          };
        }

        matchesByFile[filename].count++;
        matchesByFile[filename].lines.push({
          number: '?',
          content: content.trim()
        });

        totalMatches++;
        totalLines++;
      }
    }

    // Build summary
    const fileCount = Object.keys(matchesByFile).length;
    const result = [];

    if (fileCount === 0) {
      return 'No matches found';
    }

    result.push(`🔍 Found ${totalMatches} matches in ${fileCount} file(s)`);

    // Show matches by file
    const sortedFiles = Object.entries(matchesByFile)
      .sort((a, b) => b[1].count - a[1].count);

    sortedFiles.forEach(([filename, data], index) => {
      if (index >= 20) return; // Limit to 20 files

      result.push('');
      result.push(`📄 ${filename} (${data.count} match${data.count !== 1 ? 'es' : ''})`);

      // Show first few matches per file
      data.lines.slice(0, 3).forEach(line => {
        const preview = line.content.substring(0, 80);
        result.push(`  ${line.number}: ${preview}${line.content.length > 80 ? '...' : ''}`);
      });

      if (data.lines.length > 3) {
        result.push(`  ... and ${data.lines.length - 3} more matches`);
      }
    });

    if (sortedFiles.length > 20) {
      result.push('');
      result.push(`... and ${sortedFiles.length - 20} more files`);
    }

    return result.join('\n');
  }

  /**
   * Generic search filter
   */
  filterGeneric(output) {
    const lines = output.split('\n').filter(l => l.trim());

    if (lines.length === 0) return 'No matches found';

    if (lines.length <= 20) {
      return output;
    }

    return [
      `🔍 Found ${lines.length} results`,
      ``,
      ...lines.slice(0, 10),
      ``,
      `[... ${lines.length - 15} lines hidden ...]`,
      ``,
      ...lines.slice(-5)
    ].join('\n');
  }
}

module.exports = SearchFilter;
