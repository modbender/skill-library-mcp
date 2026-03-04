/**
 * GitFilter - Filter git command output
 */

const BaseFilter = require('./BaseFilter');

class GitFilter extends BaseFilter {
  async apply(output, context = {}) {
    // Check if filtering is safe
    if (!this.canFilter(output)) {
      return output;
    }

    // Remove ANSI codes
    output = this.removeAnsiCodes(output);

    // Redact secrets (in case of git config, etc.)
    output = this.redactSecrets(output);

    // Route to specific git subcommand handler
    const command = context.command || '';
    if (command.includes('git status')) {
      return this.filterStatus(output);
    } else if (command.includes('git log')) {
      return this.filterLog(output);
    } else if (command.includes('git diff')) {
      return this.filterDiff(output);
    } else if (command.includes('git branch')) {
      return this.filterBranch(output);
    } else if (command.includes('git show')) {
      return this.filterShow(output);
    } else if (command.includes('git config')) {
      return this.filterConfig(output);
    } else {
      // Generic git filter
      return this.filterGeneric(output);
    }
  }

  /**
   * Filter git status output
   */
  filterStatus(output) {
    const lines = output.split('\n').filter(l => l.trim());
    const result = [];

    // Extract branch
    const branchLine = lines.find(l => l.includes('On branch'));
    const branch = branchLine?.match(/On branch\s+(.+)/)?.[1] || 'unknown';
    result.push(`📍 ${branch}`);

    // Check for ahead/behind status
    const statusLine = lines.find(l => l.includes('Your branch is'));
    if (statusLine) {
      if (statusLine.includes('ahead')) {
        // Format: "ahead of 'origin/main' by 3 commits"
        const ahead = statusLine.match(/by\s+(\d+)\s+commit/)?.[1] || statusLine.match(/ahead.*?(\d+)/)?.[1];
        if (ahead) result.push(`↑ Ahead ${ahead} commit${ahead === '1' ? '' : 's'}`);
      }
      if (statusLine.includes('behind')) {
        const behind = statusLine.match(/by\s+(\d+)\s+commit/)?.[1] || statusLine.match(/behind.*?(\d+)/)?.[1];
        if (behind) result.push(`↓ Behind ${behind} commit${behind === '1' ? '' : 's'}`);
      }
      if (!statusLine.includes('ahead') && !statusLine.includes('behind')) {
        result.push('✓ Up to date');
      }
    }

    // Count changes
    let modified = 0;
    let deleted = 0;
    let added = 0;
    let untracked = 0;

    for (const line of lines) {
      if (line.includes('modified:')) modified++;
      if (line.includes('deleted:')) deleted++;
      if (line.includes('new file:')) added++;
      if (line.trim().startsWith('??')) untracked++;
    }

    if (modified > 0) result.push(`✏️  Modified: ${modified}`);
    if (added > 0) result.push(`➕ Added: ${added}`);
    if (deleted > 0) result.push(`🗑️  Deleted: ${deleted}`);
    if (untracked > 0) result.push(`❓ Untracked: ${untracked}`);

    // If no changes
    if (modified === 0 && added === 0 && deleted === 0 && untracked === 0) {
      result.push('✓ Working tree clean');
    }

    return result.join('\n');
  }

  /**
   * Filter git log output
   */
  filterLog(output) {
    const lines = output.split('\n');

    if (lines.length === 0) return '';

    // Try to parse standard git log format
    const commits = [];
    let currentCommit = null;

    for (const line of lines) {
      // Commit hash line
      const commitMatch = line.match(/^commit\s+([a-f0-9]+)/);
      if (commitMatch) {
        if (currentCommit && currentCommit.hash) commits.push(currentCommit);
        currentCommit = { hash: commitMatch[1], message: '', author: '', date: '' };
        continue;
      }

      if (!currentCommit) continue;

      // Author line
      const authorMatch = line.match(/^Author:\s+(.+)/);
      if (authorMatch) {
        currentCommit.author = authorMatch[1].split('<')[0].trim();
        continue;
      }

      // Date line
      const dateMatch = line.match(/^Date:\s+(.+)/);
      if (dateMatch) {
        currentCommit.date = dateMatch[1].trim();
        continue;
      }

      // Commit message (indented lines after Date:)
      if ((line.startsWith('    ') || line.startsWith('\t')) && line.trim()) {
        currentCommit.message += line.trim() + ' ';
      }
    }

    // Add last commit
    if (currentCommit && currentCommit.hash) commits.push(currentCommit);

    if (commits.length === 0) {
      // Fallback: show truncated output
      const truncated = lines.slice(0, 10).join('\n');
      return lines.length > 10 ? `${truncated}\n[... ${lines.length - 10} more lines ...]` : output;
    }

    // Format compactly
    const result = commits.map((commit, index) => {
      const shortHash = commit.hash.substring(0, 7);
      const shortMessage = (commit.message || 'no message').trim().substring(0, 50);
      const shortAuthor = commit.author.split(' ')[0] || 'unknown';
      const prefix = index === 0 ? '📍' : '•';
      return `${prefix} ${shortHash} ${shortMessage} (${shortAuthor})`;
    });

    return result.join('\n');
  }

  /**
   * Filter git diff output
   */
  filterDiff(output) {
    const lines = output.split('\n').filter(l => l.trim());

    if (lines.length === 0) return 'No changes';

    // Count changes
    let additions = 0;
    let deletions = 0;
    let files = 0;

    for (const line of lines) {
      if (line.startsWith('+++')) files++;
      if (line.startsWith('diff')) files++;
      if (line.startsWith('+') && !line.startsWith('+++')) additions++;
      if (line.startsWith('-') && !line.startsWith('---')) deletions++;
    }

    const result = [
      `📊 ${Math.ceil(files / 2)} file(s) changed`,
      `➕ ${additions} insertions`,
      `➖ ${deletions} deletions`
    ];

    // Show first few file names
    const fileNames = lines
      .filter(l => l.startsWith('+++ b/') || l.startsWith('--- a/'))
      .map(l => l.replace(/^[\+\-]{3}\s+[ab]\//, ''))
      .slice(0, 5);

    if (fileNames.length > 0) {
      result.push('');
      result.push('📁 Modified files:');
      fileNames.forEach(name => result.push(`  - ${name}`));
      if (files / 2 > 5) {
        result.push(`  ... and ${Math.ceil(files / 2) - 5} more`);
      }
    }

    return result.join('\n');
  }

  /**
   * Filter git branch output
   */
  filterBranch(output) {
    const lines = output.split('\n').filter(l => l.trim());

    const branches = lines.map(line => {
      const isCurrent = line.startsWith('*');
      const name = line.replace(/^\*\s*/, '').trim();
      return { name, current: isCurrent };
    });

    if (branches.length === 0) return 'No branches';

    const current = branches.find(b => b.current);
    const others = branches.filter(b => !b.current);

    const result = [];

    if (current) {
      result.push(`📍 ${current.name} (current)`);
    }

    if (others.length > 0) {
      result.push(`📋 ${others.length} other branch(es):`);
      others.slice(0, 10).forEach(b => result.push(`  - ${b.name}`));
      if (others.length > 10) {
        result.push(`  ... and ${others.length - 10} more`);
      }
    }

    return result.join('\n');
  }

  /**
   * Filter git show output
   */
  filterShow(output) {
    // For git show, show the first ~20 lines
    const lines = output.split('\n');

    const result = [];
    let inDiff = false;

    for (let i = 0; i < Math.min(lines.length, 30); i++) {
      const line = lines[i];

      // Skip diff headers
      if (line.startsWith('diff') || line.startsWith('index') || line.startsWith('---') || line.startsWith('+++')) {
        inDiff = true;
        continue;
      }

      if (inDiff) {
        // Show limited diff context
        if (line.startsWith('+') || line.startsWith('-')) {
          result.push(line);
        }
      } else {
        result.push(line);
      }
    }

    if (lines.length > 30) {
      result.push('');
      result.push(`[... ${lines.length - 30} more lines ...]`);
    }

    return result.join('\n');
  }

  /**
   * Filter git config output
   */
  filterConfig(output) {
    const lines = output.split('\n').filter(l => l.trim());

    if (lines.length < 10) {
      return output; // Small output, keep as-is
    }

    // Group by section
    const sections = {};
    let currentSection = 'general';

    for (const line of lines) {
      if (line.includes('user.') || line.includes('core.') || line.includes('remote.') || line.includes('branch.')) {
        const [key, value] = line.split('=').map(s => s.trim());
        const section = key.split('.')[0];
        if (!sections[section]) sections[section] = [];
        sections[section].push(`${key}: ${value}`);
      }
    }

    const result = ['⚙️  Git Configuration'];
    for (const [section, items] of Object.entries(sections)) {
      result.push(`\n${section}:`);
      items.slice(0, 5).forEach(item => result.push(`  ${item}`));
      if (items.length > 5) {
        result.push(`  ... and ${items.length - 5} more`);
      }
    }

    return result.join('\n');
  }

  /**
   * Generic git filter for other commands
   */
  filterGeneric(output) {
    const lines = output.split('\n').filter(l => l.trim());

    if (lines.length <= 20) {
      return output; // Small output, keep as-is
    }

    // Show first 10 and last 5 lines
    const result = [
      ...lines.slice(0, 10),
      '',
      `[... ${lines.length - 15} lines hidden ...]`,
      '',
      ...lines.slice(-5)
    ];

    return result.join('\n');
  }
}

module.exports = GitFilter;
