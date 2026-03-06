/**
 * Janitor - Lightweight AI Agent Cleanup Skill for ClawHub.ai
 *
 * Minimal version with core cleanup features.
 * For advanced features, see: https://github.com/openclaw/janitor
 *
 * v1.1.0 - Added Session Management Features
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Session Management Components
const SessionMonitor = require('./src/session-management/monitor');
const SessionPruner = require('./src/session-management/pruner');
const SessionArchiver = require('./src/session-management/archiver');
const SessionAnalyzer = require('./src/session-management/analyzer');
const EmergencyCleanup = require('./src/session-management/emergency');
const ContextWatcher = require('./src/services/context-watcher');
const Dashboard = require('./src/utils/dashboard');
const Notifier = require('./src/services/notifier');
const GitHubBackup = require('./src/services/github-backup');

class Janitor {
  constructor(config = {}) {
    this.config = {
      enabled: true,
      unusedFileAgeDays: 7,
      // Session Management Configuration
      sessionManagement: {
        enabled: config.sessionManagement?.enabled !== false,
        monitoring: {
          intervalMinutes: config.sessionManagement?.monitoring?.intervalMinutes || 5,
          alertThreshold: config.sessionManagement?.monitoring?.alertThreshold || 80,
          emergencyThreshold: config.sessionManagement?.monitoring?.emergencyThreshold || 95
        },
        pruning: {
          maxSessionAge: config.sessionManagement?.pruning?.maxSessionAge || 7,
          maxContextTokens: config.sessionManagement?.pruning?.maxContextTokens || 160000,
          keepRecentHours: config.sessionManagement?.pruning?.keepRecentHours || 24,
          keepMinimumSessions: config.sessionManagement?.pruning?.keepMinimumSessions || 5
        },
        archiving: {
          enabled: config.sessionManagement?.archiving?.enabled !== false,
          retentionDays: config.sessionManagement?.archiving?.retentionDays || 30,
          compression: config.sessionManagement?.archiving?.compression !== false
        },
        preservation: {
          pinned: config.sessionManagement?.preservation?.pinned !== false,
          highEngagement: config.sessionManagement?.preservation?.highEngagement !== false,
          minMessagesForImportant: config.sessionManagement?.preservation?.minMessagesForImportant || 10
        },
        notifications: {
          enabled: config.sessionManagement?.notifications?.enabled || false,
          channels: config.sessionManagement?.notifications?.channels || ['log'],
          onCleanup: config.sessionManagement?.notifications?.onCleanup !== false,
          onEmergency: config.sessionManagement?.notifications?.onEmergency !== false,
          telegram: config.sessionManagement?.notifications?.telegram || {},
          discord: config.sessionManagement?.notifications?.discord || {}
        }
      },
      ...config
    };

    this.stats = {
      totalCleanups: 0,
      totalFilesDeleted: 0,
      totalSpaceSaved: 0
    };

    // Initialize session management components
    this._initSessionManagement();
  }

  /**
   * Initialize session management components
   * @private
   */
  _initSessionManagement() {
    if (!this.config.sessionManagement.enabled) {
      return;
    }

    // Initialize components
    this.sessionMonitor = new SessionMonitor({
      maxTokens: 200000,
      alertThreshold: this.config.sessionManagement.monitoring.alertThreshold,
      emergencyThreshold: this.config.sessionManagement.monitoring.emergencyThreshold
    });

    this.sessionArchiver = new SessionArchiver({
      retentionDays: this.config.sessionManagement.archiving.retentionDays,
      compression: this.config.sessionManagement.archiving.compression
    });

    this.sessionPruner = new SessionPruner(this.sessionMonitor, {
      maxSessionAge: this.config.sessionManagement.pruning.maxSessionAge,
      maxContextTokens: this.config.sessionManagement.pruning.maxContextTokens,
      keepRecentHours: this.config.sessionManagement.pruning.keepRecentHours,
      keepMinimumSessions: this.config.sessionManagement.pruning.keepMinimumSessions,
      minMessagesForImportant: this.config.sessionManagement.preservation.minMessagesForImportant,
      preservePinned: this.config.sessionManagement.preservation.pinned,
      preserveHighEngagement: this.config.sessionManagement.preservation.highEngagement
    });

    this.emergencyCleanup = new EmergencyCleanup(
      this.sessionMonitor,
      this.sessionPruner,
      this.sessionArchiver,
      {
        keepRecentHours: this.config.sessionManagement.pruning.keepRecentHours,
        emergencyThreshold: this.config.sessionManagement.monitoring.emergencyThreshold
      }
    );

    this.contextWatcher = new ContextWatcher(
      this.sessionMonitor,
      this.sessionPruner,
      this.sessionArchiver,
      this.emergencyCleanup,
      {
        enabled: this.config.sessionManagement.enabled,
        intervalMinutes: this.config.sessionManagement.monitoring.intervalMinutes,
        alertThreshold: this.config.sessionManagement.monitoring.alertThreshold,
        emergencyThreshold: this.config.sessionManagement.monitoring.emergencyThreshold,
        autoCleanup: true
      }
    );

    this.dashboard = new Dashboard(this.sessionMonitor);

    this.sessionAnalyzer = new SessionAnalyzer({
      minMessagesForImportant: this.config.sessionManagement.preservation.minMessagesForImportant,
      toolUsageWeight: 0.3,
      conversationDepthWeight: 0.25,
      recencyWeight: 0.25,
      engagementWeight: 0.2
    });

    this.notifier = new Notifier({
      enabled: this.config.sessionManagement.notifications?.enabled || false,
      channels: this.config.sessionManagement.notifications?.channels || ['log'],
      telegram: this.config.sessionManagement.notifications?.telegram,
      discord: this.config.sessionManagement.notifications?.discord
    });

    this.githubBackup = new GitHubBackup({
      enabled: this.config.sessionManagement.archiving?.backupToGithub || false,
      repoUrl: process.env.GITHUB_BACKUP_REPO,
      autoSync: true
    });

    // Initialize GitHub backup if enabled
    if (this.githubBackup.config.enabled) {
      this.githubBackup.initialize().catch(err => {
        console.warn('GitHub backup initialization failed:', err.message);
      });
    }
  }

  /**
   * Main cleanup method - removes cache, logs, and temp files
   */
  async cleanup(workingDir = process.cwd()) {
    console.log('🧹 Janitor: Starting cleanup...');
    const startTime = Date.now();

    let filesDeleted = 0;
    let spaceSaved = 0;

    // Clean cache directories
    const cacheTargets = [
      path.join(workingDir, 'node_modules', '.cache'),
      path.join(workingDir, '.cache'),
      path.join(workingDir, 'dist'),
      path.join(workingDir, 'coverage'),
      path.join(workingDir, 'tmp')
    ];

    for (const target of cacheTargets) {
      if (fs.existsSync(target)) {
        const result = this._cleanDir(target, 2);
        filesDeleted += result.files;
        spaceSaved += result.bytes;
      }
    }

    // Clean .DS_Store files (macOS)
    const dsResult = this._cleanDSStore(workingDir);
    filesDeleted += dsResult.files;

    // Clean old logs
    const logResult = this._cleanOldLogs(workingDir);
    filesDeleted += logResult.files;
    spaceSaved += logResult.bytes;

    // Free memory
    this._freeMemory();

    // Update stats
    this.stats.totalCleanups++;
    this.stats.totalFilesDeleted += filesDeleted;
    this.stats.totalSpaceSaved += spaceSaved;

    const duration = Date.now() - startTime;
    const result = {
      filesDeleted,
      spaceSaved: this._formatBytes(spaceSaved),
      duration: `${duration}ms`,
      memoryFreed: true
    };

    console.log(`✅ Cleanup complete: ${filesDeleted} files, ${result.spaceSaved} saved`);
    return result;
  }

  /**
   * Clean directory recursively (limited depth for safety)
   */
  _cleanDir(dirPath, maxDepth = 2, currentDepth = 0) {
    let filesDeleted = 0;
    let bytesFreed = 0;

    if (currentDepth >= maxDepth || !fs.existsSync(dirPath)) {
      return { files: 0, bytes: 0 };
    }

    try {
      const files = fs.readdirSync(dirPath);

      for (const file of files) {
        const filePath = path.join(dirPath, file);

        try {
          const stats = fs.statSync(filePath);

          if (stats.isFile()) {
            bytesFreed += stats.size;
            fs.unlinkSync(filePath);
            filesDeleted++;
          } else if (stats.isDirectory()) {
            const result = this._cleanDir(filePath, maxDepth, currentDepth + 1);
            filesDeleted += result.files;
            bytesFreed += result.bytes;

            try {
              fs.rmdirSync(filePath);
            } catch (e) {
              // Directory not empty, skip
            }
          }
        } catch (e) {
          continue;
        }
      }
    } catch (e) {
      // Directory access error, skip
    }

    return { files: filesDeleted, bytes: bytesFreed };
  }

  /**
   * Clean .DS_Store files (macOS metadata)
   */
  _cleanDSStore(baseDir) {
    let filesDeleted = 0;

    const findAndDelete = (dir, depth = 0) => {
      if (depth > 3) return;

      try {
        const files = fs.readdirSync(dir);

        for (const file of files) {
          const filePath = path.join(dir, file);

          if (file === '.DS_Store') {
            try {
              fs.unlinkSync(filePath);
              filesDeleted++;
            } catch (e) {}
          } else {
            try {
              const stats = fs.statSync(filePath);
              if (stats.isDirectory() && !this._isProtected(filePath)) {
                findAndDelete(filePath, depth + 1);
              }
            } catch (e) {}
          }
        }
      } catch (e) {}
    };

    findAndDelete(baseDir);
    return { files: filesDeleted };
  }

  /**
   * Clean old log files (>7 days)
   */
  _cleanOldLogs(baseDir) {
    let filesDeleted = 0;
    let bytesFreed = 0;
    const maxAgeDays = 7;

    const searchLogs = (dir, depth = 0) => {
      if (depth > 2) return;

      try {
        const files = fs.readdirSync(dir);

        for (const file of files) {
          const filePath = path.join(dir, file);

          if (file.endsWith('.log')) {
            try {
              const stats = fs.statSync(filePath);
              const ageMs = Date.now() - stats.mtime.getTime();
              const ageDays = ageMs / (1000 * 60 * 60 * 24);

              if (ageDays > maxAgeDays) {
                bytesFreed += stats.size;
                fs.unlinkSync(filePath);
                filesDeleted++;
              }
            } catch (e) {}
          } else {
            try {
              const stats = fs.statSync(filePath);
              if (stats.isDirectory() && !this._isProtected(filePath)) {
                searchLogs(filePath, depth + 1);
              }
            } catch (e) {}
          }
        }
      } catch (e) {}
    };

    searchLogs(baseDir);
    return { files: filesDeleted, bytes: bytesFreed };
  }

  /**
   * Check if path is protected (should not delete)
   */
  _isProtected(filePath) {
    const protectedPaths = [
      'node_modules',
      '.git',
      'src',
      'package.json',
      'README.md',
      '.env'
    ];

    return protectedPaths.some(name => filePath.includes(name));
  }

  /**
   * Free up memory
   */
  _freeMemory() {
    if (global.gc) {
      global.gc();
      console.log('   🗑️  Memory freed');
    }
  }

  /**
   * Format bytes to human-readable
   */
  _formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Get current stats
   */
  getStats() {
    const memUsed = process.memoryUsage();
    return {
      totalCleanups: this.stats.totalCleanups,
      totalFilesDeleted: this.stats.totalFilesDeleted,
      totalSpaceSaved: this._formatBytes(this.stats.totalSpaceSaved),
      memoryUsage: {
        heapUsed: this._formatBytes(memUsed.heapUsed),
        heapTotal: this._formatBytes(memUsed.heapTotal)
      }
    };
  }

  /**
   * Generate report
   */
  async report() {
    const stats = this.getStats();

    console.log('\n📊 Janitor Report:');
    console.log(`   Total Cleanups: ${stats.totalCleanups}`);
    console.log(`   Files Deleted: ${stats.totalFilesDeleted}`);
    console.log(`   Space Saved: ${stats.totalSpaceSaved}`);
    console.log(`   Memory (Heap): ${stats.memoryUsage.heapUsed}`);
    console.log('\n   💡 For advanced features (backup, scheduling, etc.):');
    console.log('      https://github.com/openclaw/janitor\n');

    return {
      timestamp: new Date().toISOString(),
      status: 'healthy',
      stats
    };
  }

  // ========================================
  // Session Management Methods
  // ========================================

  /**
   * Get current context usage
   */
  async getContextUsage() {
    if (!this.config.sessionManagement.enabled) {
      throw new Error('Session management is disabled');
    }

    return await this.sessionMonitor.getContextUsage();
  }

  /**
   * Show context dashboard
   */
  async showDashboard() {
    if (!this.config.sessionManagement.enabled) {
      throw new Error('Session management is disabled');
    }

    return await this.dashboard.generate();
  }

  /**
   * Show compact context status
   */
  async showContextStatus() {
    if (!this.config.sessionManagement.enabled) {
      throw new Error('Session management is disabled');
    }

    return await this.dashboard.compactReport();
  }

  /**
   * Clean context (prune old sessions)
   */
  async cleanContext(strategy = 'moderate') {
    if (!this.config.sessionManagement.enabled) {
      throw new Error('Session management is disabled');
    }

    console.log(`🧹 Starting context cleanup (${strategy} strategy)...\n`);

    // Get current usage
    const beforeUsage = await this.sessionMonitor.getContextUsage();
    console.log(`Before: ${this.sessionMonitor.formatTokens(beforeUsage.currentTokens)}/200k (${beforeUsage.utilizationPercent.toFixed(1)}%)`);

    // Preview what will be pruned
    const preview = await this.sessionPruner.dryRun(strategy);
    console.log(`\nWill prune ${preview.wouldPrune} sessions (${this.sessionMonitor.formatTokens(preview.wouldFreeTokens)} tokens)`);

    // Get sessions to prune
    const sessionsToPrune = preview.sessions.map(s => {
      const session = beforeUsage.sessions.find(sess => sess.sessionId === s.id);
      return session;
    }).filter(s => s);

    // Archive sessions first
    if (sessionsToPrune.length > 0) {
      console.log(`\n📦 Archiving ${sessionsToPrune.length} sessions...`);
      const archiveResult = await this.sessionArchiver.archiveSessions(sessionsToPrune, 'manual-cleanup');
      console.log(`   ✅ ${archiveResult.message}`);
    }

    // Prune sessions
    console.log(`\n🗑️  Pruning sessions...`);
    const pruneResult = await this.sessionPruner.prune(strategy);

    // Get new usage
    const afterUsage = await this.sessionMonitor.getContextUsage();

    console.log(`\n✅ Cleanup complete:`);
    console.log(`   Sessions pruned: ${pruneResult.sessionsPruned}`);
    console.log(`   Tokens freed: ${this.sessionMonitor.formatTokens(pruneResult.tokensFreed)}`);
    console.log(`   After: ${this.sessionMonitor.formatTokens(afterUsage.currentTokens)}/200k (${afterUsage.utilizationPercent.toFixed(1)}%)`);

    return {
      before: beforeUsage,
      after: afterUsage,
      pruned: pruneResult.sessionsPruned,
      tokensFreed: pruneResult.tokensFreed
    };
  }

  /**
   * Emergency cleanup
   */
  async emergencyClean() {
    if (!this.config.sessionManagement.enabled) {
      throw new Error('Session management is disabled');
    }

    const result = await this.emergencyCleanup.execute();
    console.log(this.emergencyCleanup.generateReport(result));

    return result;
  }

  /**
   * Start background context monitoring
   */
  startMonitoring() {
    if (!this.config.sessionManagement.enabled) {
      throw new Error('Session management is disabled');
    }

    this.contextWatcher.start();
  }

  /**
   * Stop background context monitoring
   */
  stopMonitoring() {
    if (!this.config.sessionManagement.enabled) {
      throw new Error('Session management is disabled');
    }

    this.contextWatcher.stop();
  }

  /**
   * Get monitoring status
   */
  getMonitoringStatus() {
    if (!this.config.sessionManagement.enabled) {
      return { enabled: false };
    }

    return this.contextWatcher.getStatus();
  }

  /**
   * List archives
   */
  async listArchives() {
    if (!this.config.sessionManagement.enabled) {
      throw new Error('Session management is disabled');
    }

    const archives = await this.sessionArchiver.listArchives();

    console.log('\n📦 Session Archives:\n');

    if (archives.length === 0) {
      console.log('  No archives found\n');
      return archives;
    }

    for (const archive of archives) {
      const date = new Date(archive.timestamp).toLocaleDateString();
      console.log(`  ${archive.archiveName}`);
      console.log(`    Date: ${date}`);
      console.log(`    Sessions: ${archive.sessionCount}`);
      console.log(`    Reason: ${archive.reason}`);
      console.log('');
    }

    return archives;
  }

  /**
   * Restore archive
   */
  async restoreArchive(archiveName) {
    if (!this.config.sessionManagement.enabled) {
      throw new Error('Session management is disabled');
    }

    console.log(`📦 Restoring archive: ${archiveName}...`);

    const result = await this.sessionArchiver.restore(archiveName);

    console.log(`✅ ${result.message}`);
    if (result.skipped > 0) {
      console.log(`   (Skipped ${result.skipped} sessions that already exist)`);
    }

    return result;
  }

  /**
   * List sessions
   */
  async listSessions(sortBy = 'size') {
    if (!this.config.sessionManagement.enabled) {
      throw new Error('Session management is disabled');
    }

    return await this.dashboard.listSessions(sortBy);
  }

  /**
   * Cleanup old archives
   */
  async cleanupArchives() {
    if (!this.config.sessionManagement.enabled) {
      throw new Error('Session management is disabled');
    }

    console.log('🗑️  Cleaning up old archives...');

    const result = await this.sessionArchiver.cleanupOldArchives();

    console.log(`✅ ${result.message}`);

    return result;
  }

  /**
   * Get archive statistics
   */
  async getArchiveStats() {
    if (!this.config.sessionManagement.enabled) {
      throw new Error('Session management is disabled');
    }

    return await this.sessionArchiver.getStats();
  }
}

module.exports = Janitor;
