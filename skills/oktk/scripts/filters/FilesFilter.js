/**
 * FilesFilter - Filter file operation commands (ls, find, tree)
 */

const BaseFilter = require('./BaseFilter');

class FilesFilter extends BaseFilter {
  async apply(output, context = {}) {
    // Check if filtering is safe
    if (!this.canFilter(output)) {
      return output;
    }

    // Remove ANSI codes
    output = this.removeAnsiCodes(output);

    // Detect command type
    const command = context.command || '';
    if (command.includes('ls')) {
      return this.filterLs(output);
    } else if (command.includes('find')) {
      return this.filterFind(output);
    } else if (command.includes('tree')) {
      return this.filterTree(output);
    } else {
      return this.filterGeneric(output);
    }
  }

  /**
   * Filter ls -la output
   */
  filterLs(output) {
    const lines = output.split('\n').filter(l => l.trim());

    if (lines.length === 0) return '';

    // Parse header line (total N)
    const totalMatch = lines[0].match(/total\s+(\d+)/);
    const totalSize = totalMatch ? parseInt(totalMatch[1]) * 512 : 0; // ls shows 512-byte blocks

    const result = [];

    // Directory info
    const currentDir = lines[0].includes('.') ? '.' : 'unknown';
    result.push(`📁 ${currentDir} (${lines.length - 1} items, ${this.formatBytes(totalSize)} total)`);

    // Parse file entries
    const files = [];
    const dirs = [];
    const others = [];

    for (let i = 1; i < lines.length; i++) {
      const line = lines[i];
      const parts = line.split(/\s+/);

      if (parts.length >= 9) {
        const isDir = parts[0].startsWith('d');
        const name = parts.slice(8).join(' ');
        const size = parseInt(parts[4]) || 0;

        const entry = {
          name,
          size,
          type: isDir ? 'dir' : 'file'
        };

        if (isDir) dirs.push(entry);
        else if (name.includes('.') || name.length < 30) files.push(entry);
        else others.push(entry);
      }
    }

    // Show directories
    if (dirs.length > 0) {
      result.push('');
      result.push(`📂 Directories (${dirs.length}):`);
      dirs.slice(0, 15).forEach(d => {
        result.push(`  ${d.name}`);
      });
      if (dirs.length > 15) {
        result.push(`  ... and ${dirs.length - 15} more`);
      }
    }

    // Show files
    if (files.length > 0) {
      result.push('');
      result.push(`📄 Files (${files.length}):`);

      // Show largest files first
      files.sort((a, b) => b.size - a.size);
      files.slice(0, 15).forEach(f => {
        result.push(`  ${f.name} (${this.formatBytes(f.size)})`);
      });
      if (files.length > 15) {
        result.push(`  ... and ${files.length - 15} more`);
      }
    }

    // Show others
    if (others.length > 0) {
      result.push('');
      result.push(`📦 Other (${others.length}):`);
      others.slice(0, 5).forEach(o => {
        result.push(`  ${o.name}`);
      });
      if (others.length > 5) {
        result.push(`  ... and ${others.length - 5} more`);
      }
    }

    return result.join('\n');
  }

  /**
   * Filter find output
   */
  filterFind(output) {
    const lines = output.split('\n').filter(l => l.trim());

    if (lines.length === 0) return 'No files found';

    // Count by extension
    const extensions = {};
    const dirs = [];
    const files = [];

    for (const line of lines) {
      if (line.includes('Permission denied')) continue;

      const isDir = line.endsWith('/');
      if (isDir) {
        dirs.push(line);
      } else {
        const ext = line.split('.').pop();
        const baseExt = ext.length > 5 ? 'unknown' : ext;
        extensions[baseExt] = (extensions[baseExt] || 0) + 1;
        files.push(line);
      }
    }

    const result = [`🔍 Found ${files.length + dirs.length} items`];

    // Show directories
    if (dirs.length > 0) {
      result.push(``);
      result.push(`📂 ${dirs.length} directories`);
      dirs.slice(0, 5).forEach(d => result.push(`  ${d}`));
      if (dirs.length > 5) {
        result.push(`  ... and ${dirs.length - 5} more`);
      }
    }

    // Show files by extension
    if (files.length > 0) {
      result.push(``);
      result.push(`📄 ${files.length} files`);
      result.push(`  By extension:`);

      const sortedExts = Object.entries(extensions)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

      sortedExts.forEach(([ext, count]) => {
        result.push(`    .${ext}: ${count}`);
      });

      if (Object.keys(extensions).length > 10) {
        result.push(`    ... and ${Object.keys(extensions).length - 10} more extensions`);
      }

      // Show sample files
      result.push(``);
      result.push(`  Sample files:`);
      files.slice(0, 10).forEach(f => {
        const name = f.split('/').pop();
        result.push(`    ${name}`);
      });
      if (files.length > 10) {
        result.push(`    ... and ${files.length - 10} more files`);
      }
    }

    return result.join('\n');
  }

  /**
   * Filter tree output
   */
  filterTree(output) {
    const lines = output.split('\n').filter(l => l.trim());

    if (lines.length === 0) return '';

    // Extract tree structure
    const dirs = lines.filter(l => l.includes('├──') || l.includes('└──') || l.includes('│'));
    const files = dirs.filter(l => !l.includes('/'));

    const result = [`🌳 Tree (${lines.length} items)`];

    // Show top-level structure
    const topLevel = lines.filter(l => !l.includes('│') || l.startsWith('├──') || l.startsWith('└──'));

    if (topLevel.length > 0) {
      result.push(``);
      result.push(`📁 Top-level (${topLevel.length} items):`);
      topLevel.slice(0, 20).forEach(l => {
        result.push(`  ${l}`);
      });
      if (topLevel.length > 20) {
        result.push(`  ... and ${topLevel.length - 20} more items`);
      }
    }

    return result.join('\n');
  }

  /**
   * Generic file filter
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
}

module.exports = FilesFilter;
