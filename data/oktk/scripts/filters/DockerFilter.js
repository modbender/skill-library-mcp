/**
 * DockerFilter - Filter docker command output
 */

const BaseFilter = require('./BaseFilter');

class DockerFilter extends BaseFilter {
  async apply(output, context = {}) {
    if (!this.canFilter(output)) {
      return output;
    }

    output = this.removeAnsiCodes(output);
    const command = context.command || '';

    if (command.includes('docker ps')) {
      return this.filterPs(output);
    } else if (command.includes('docker images')) {
      return this.filterImages(output);
    } else if (command.includes('docker logs')) {
      return this.filterLogs(output);
    } else if (command.includes('docker build')) {
      return this.filterBuild(output);
    } else if (command.includes('docker compose') || command.includes('docker-compose')) {
      return this.filterCompose(output);
    }

    return this.filterGeneric(output);
  }

  /**
   * Filter docker ps output
   */
  filterPs(output) {
    const lines = output.split('\n').filter(l => l.trim());
    if (lines.length <= 1) return '🐳 No containers running';

    const containers = lines.slice(1).map(line => {
      const parts = line.split(/\s{2,}/);
      const id = parts[0]?.substring(0, 12) || '?';
      const image = parts[1]?.split(':')[0] || '?';
      const status = parts[4]?.includes('Up') ? '✅' : '❌';
      const name = parts[parts.length - 1] || '?';
      return `${status} ${name} (${image})`;
    });

    return `🐳 ${containers.length} container(s):\n${containers.join('\n')}`;
  }

  /**
   * Filter docker images output
   */
  filterImages(output) {
    const lines = output.split('\n').filter(l => l.trim());
    if (lines.length <= 1) return '📦 No images';

    const images = lines.slice(1).map(line => {
      const parts = line.split(/\s{2,}/);
      const repo = parts[0] || '?';
      const tag = parts[1] || 'latest';
      const size = parts[parts.length - 1] || '?';
      return `  ${repo}:${tag} (${size})`;
    });

    return `📦 ${images.length} image(s):\n${images.slice(0, 10).join('\n')}${images.length > 10 ? `\n  ... +${images.length - 10} more` : ''}`;
  }

  /**
   * Filter docker logs output
   */
  filterLogs(output) {
    const lines = output.split('\n').filter(l => l.trim());
    if (lines.length === 0) return '📜 No logs';

    // Show last 10 lines
    const lastLines = lines.slice(-10);
    const errors = lines.filter(l => /error|exception|fail/i.test(l)).length;
    const warnings = lines.filter(l => /warn/i.test(l)).length;

    const result = [`📜 ${lines.length} log lines`];
    if (errors > 0) result.push(`❌ ${errors} errors`);
    if (warnings > 0) result.push(`⚠️  ${warnings} warnings`);
    result.push('');
    result.push('Last 10 lines:');
    result.push(...lastLines.map(l => l.substring(0, 100)));

    return result.join('\n');
  }

  /**
   * Filter docker build output
   */
  filterBuild(output) {
    const lines = output.split('\n').filter(l => l.trim());
    
    // Extract key info
    const steps = lines.filter(l => /^Step \d+/i.test(l) || /^\[.*\]/.test(l));
    const success = output.includes('Successfully built') || output.includes('Successfully tagged');
    const imageId = output.match(/Successfully built ([a-f0-9]+)/)?.[1];
    const tag = output.match(/Successfully tagged (.+)/)?.[1];

    const result = [];
    if (success) {
      result.push('✅ Build successful');
      if (tag) result.push(`🏷️  ${tag}`);
      if (imageId) result.push(`🆔 ${imageId.substring(0, 12)}`);
    } else {
      result.push('❌ Build failed');
      // Show last few lines for error context
      result.push(...lines.slice(-5));
    }
    result.push(`📊 ${steps.length} steps`);

    return result.join('\n');
  }

  /**
   * Filter docker compose output
   */
  filterCompose(output) {
    const lines = output.split('\n').filter(l => l.trim());
    
    const created = lines.filter(l => /created/i.test(l)).length;
    const started = lines.filter(l => /started|running/i.test(l)).length;
    const stopped = lines.filter(l => /stopped|exited/i.test(l)).length;

    const result = ['🐳 Docker Compose'];
    if (created > 0) result.push(`  ➕ Created: ${created}`);
    if (started > 0) result.push(`  ✅ Running: ${started}`);
    if (stopped > 0) result.push(`  ⏹️  Stopped: ${stopped}`);

    return result.join('\n');
  }

  /**
   * Generic docker filter
   */
  filterGeneric(output) {
    const lines = output.split('\n').filter(l => l.trim());
    if (lines.length <= 10) return output;

    return [
      ...lines.slice(0, 5),
      `[... ${lines.length - 10} lines hidden ...]`,
      ...lines.slice(-5)
    ].join('\n');
  }
}

module.exports = DockerFilter;
