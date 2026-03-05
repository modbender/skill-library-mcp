/**
 * Session Archiver - Archive Sessions Before Deletion
 *
 * Archives sessions to compressed storage before pruning
 * Maintains archive index and handles restoration
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { exec } = require('child_process');
const { promisify } = require('util');
const SecurityUtils = require('../utils/security');

const execAsync = promisify(exec);

class SessionArchiver {
  constructor(config = {}) {
    this.config = {
      archivePath: config.archivePath || path.join(os.homedir(), '.openclaw', 'archives'),
      retentionDays: config.retentionDays || 30,
      compression: config.compression !== false,
      backupToGithub: config.backupToGithub || false,
      ...config
    };

    this.indexPath = path.join(this.config.archivePath, 'index.json');
    this._ensureArchiveDir();
  }

  /**
   * Ensure archive directory exists
   * @private
   */
  _ensureArchiveDir() {
    if (!fs.existsSync(this.config.archivePath)) {
      fs.mkdirSync(this.config.archivePath, { recursive: true });
    }
  }

  /**
   * Archive sessions before deletion
   * @param {Array} sessions - Sessions to archive
   * @param {string} reason - Reason for archiving
   * @returns {Promise<Object>} Archive result
   */
  async archiveSessions(sessions, reason = 'manual') {
    if (sessions.length === 0) {
      return {
        archived: 0,
        archivePath: null,
        message: 'No sessions to archive'
      };
    }

    const timestamp = this._getTimestamp();
    const archiveName = `sessions-${timestamp}.tar.gz`;
    const archivePath = path.join(this.config.archivePath, archiveName);

    // Create temporary directory for sessions to archive
    const tempDir = path.join(this.config.archivePath, `temp-${timestamp}`);
    fs.mkdirSync(tempDir, { recursive: true });

    try {
      // Copy sessions to temp directory
      for (const session of sessions) {
        const fileName = path.basename(session.path);
        const destPath = path.join(tempDir, fileName);

        await fs.promises.copyFile(session.path, destPath);
      }

      // Create compressed archive
      if (this.config.compression) {
        await this._createTarGz(tempDir, archivePath);
      } else {
        await this._createDirectory(tempDir, archivePath);
      }

      // Update index
      await this._updateIndex({
        archiveName,
        timestamp: new Date().toISOString(),
        sessionCount: sessions.length,
        reason,
        sessions: sessions.map(s => ({
          id: s.sessionId,
          tokens: s.tokenCount,
          messages: s.messageCount
        }))
      });

      // Cleanup temp directory
      await this._rmDir(tempDir);

      return {
        archived: sessions.length,
        archivePath,
        archiveName,
        message: `Archived ${sessions.length} sessions to ${archiveName}`
      };
    } catch (error) {
      // Cleanup on error
      if (fs.existsSync(tempDir)) {
        await this._rmDir(tempDir);
      }
      throw new Error(`Archive failed: ${error.message}`);
    }
  }

  /**
   * Create tar.gz archive
   * @private
   */
  async _createTarGz(sourceDir, targetPath) {
    const sourceName = path.basename(sourceDir);
    const parentDir = path.dirname(sourceDir);

    // Security validation
    SecurityUtils.validatePath(sourceDir, this.config.archivePath);
    SecurityUtils.validatePath(targetPath, this.config.archivePath);

    // Ensure paths don't contain command injection
    if (sourceName.includes("'") || sourceName.includes('"') || sourceName.includes('`')) {
      throw new Error('Invalid characters in source directory name');
    }

    try {
      await execAsync(
        `cd "${parentDir}" && tar -czf "${targetPath}" "${sourceName}"`,
        SecurityUtils.getSafeExecOptions(60000) // 60 second timeout
      );
    } catch (error) {
      SecurityUtils.logSecurityEvent('archive_create_failed', error.message, { sourceDir, targetPath });
      throw new Error(`Compression failed: ${error.message}`);
    }
  }

  /**
   * Create uncompressed directory archive
   * @private
   */
  async _createDirectory(sourceDir, targetPath) {
    const archiveDir = targetPath.replace('.tar.gz', '');
    await fs.promises.mkdir(archiveDir, { recursive: true });

    const files = await fs.promises.readdir(sourceDir);
    for (const file of files) {
      await fs.promises.copyFile(
        path.join(sourceDir, file),
        path.join(archiveDir, file)
      );
    }
  }

  /**
   * Restore archived sessions
   * @param {string} archiveName - Name of archive to restore
   * @param {string} targetPath - Path to restore to
   * @returns {Promise<Object>} Restore result
   */
  async restore(archiveName, targetPath = null) {
    const archivePath = path.join(this.config.archivePath, archiveName);

    if (!fs.existsSync(archivePath)) {
      throw new Error(`Archive not found: ${archiveName}`);
    }

    const restorePath = targetPath || path.join(os.homedir(), '.openclaw', 'agents', 'main', 'sessions');
    const tempExtractDir = path.join(this.config.archivePath, `restore-${Date.now()}`);

    try {
      // Extract archive
      if (archiveName.endsWith('.tar.gz')) {
        await this._extractTarGz(archivePath, tempExtractDir);

        // Find the extracted directory
        const extracted = await fs.promises.readdir(tempExtractDir);
        const sessionDir = path.join(tempExtractDir, extracted[0]);

        // Copy sessions back
        const sessions = await fs.promises.readdir(sessionDir);
        let restoredCount = 0;

        for (const session of sessions) {
          const sourcePath = path.join(sessionDir, session);
          const destPath = path.join(restorePath, session);

          // Don't overwrite existing sessions
          if (!fs.existsSync(destPath)) {
            await fs.promises.copyFile(sourcePath, destPath);
            restoredCount++;
          }
        }

        // Cleanup temp directory
        await this._rmDir(tempExtractDir);

        return {
          restored: restoredCount,
          skipped: sessions.length - restoredCount,
          message: `Restored ${restoredCount} sessions from ${archiveName}`
        };
      } else {
        // Uncompressed directory archive
        const sessions = await fs.promises.readdir(archivePath);
        let restoredCount = 0;

        for (const session of sessions) {
          const sourcePath = path.join(archivePath, session);
          const destPath = path.join(restorePath, session);

          if (!fs.existsSync(destPath)) {
            await fs.promises.copyFile(sourcePath, destPath);
            restoredCount++;
          }
        }

        return {
          restored: restoredCount,
          skipped: sessions.length - restoredCount,
          message: `Restored ${restoredCount} sessions from ${archiveName}`
        };
      }
    } catch (error) {
      if (fs.existsSync(tempExtractDir)) {
        await this._rmDir(tempExtractDir);
      }
      throw new Error(`Restore failed: ${error.message}`);
    }
  }

  /**
   * Extract tar.gz archive
   * @private
   */
  async _extractTarGz(archivePath, targetDir) {
    // Security validation
    SecurityUtils.validatePath(archivePath, this.config.archivePath);
    SecurityUtils.validatePath(targetDir, this.config.archivePath);

    await fs.promises.mkdir(targetDir, { recursive: true });

    try {
      await execAsync(
        `tar -xzf "${archivePath}" -C "${targetDir}"`,
        SecurityUtils.getSafeExecOptions(60000) // 60 second timeout
      );
    } catch (error) {
      SecurityUtils.logSecurityEvent('archive_extract_failed', error.message, { archivePath, targetDir });
      throw new Error(`Extraction failed: ${error.message}`);
    }
  }

  /**
   * List all archives
   * @returns {Promise<Array>} List of archives
   */
  async listArchives() {
    const index = await this._loadIndex();
    return index.archives.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  }

  /**
   * Get archive details
   * @param {string} archiveName - Name of archive
   * @returns {Promise<Object>} Archive details
   */
  async getArchiveDetails(archiveName) {
    const index = await this._loadIndex();
    return index.archives.find(a => a.archiveName === archiveName);
  }

  /**
   * Delete old archives based on retention policy
   * @returns {Promise<Object>} Cleanup result
   */
  async cleanupOldArchives() {
    const index = await this._loadIndex();
    const maxAgeMs = this.config.retentionDays * 24 * 60 * 60 * 1000;
    const now = Date.now();

    const toDelete = [];

    for (const archive of index.archives) {
      const age = now - new Date(archive.timestamp).getTime();

      if (age > maxAgeMs) {
        toDelete.push(archive);
      }
    }

    let deletedCount = 0;
    for (const archive of toDelete) {
      try {
        const archivePath = path.join(this.config.archivePath, archive.archiveName);
        if (fs.existsSync(archivePath)) {
          if (archive.archiveName.endsWith('.tar.gz')) {
            await fs.promises.unlink(archivePath);
          } else {
            await this._rmDir(archivePath);
          }
          deletedCount++;
        }

        // Remove from index
        index.archives = index.archives.filter(a => a.archiveName !== archive.archiveName);
      } catch (error) {
        console.error(`Failed to delete archive ${archive.archiveName}:`, error.message);
      }
    }

    // Save updated index
    await this._saveIndex(index);

    return {
      deleted: deletedCount,
      message: `Deleted ${deletedCount} old archives (>${this.config.retentionDays} days)`
    };
  }

  /**
   * Update archive index
   * @private
   */
  async _updateIndex(archiveInfo) {
    const index = await this._loadIndex();
    index.archives.push(archiveInfo);
    await this._saveIndex(index);
  }

  /**
   * Load archive index
   * @private
   */
  async _loadIndex() {
    if (!fs.existsSync(this.indexPath)) {
      return { archives: [] };
    }

    try {
      const content = await fs.promises.readFile(this.indexPath, 'utf-8');
      return JSON.parse(content);
    } catch (error) {
      return { archives: [] };
    }
  }

  /**
   * Save archive index
   * @private
   */
  async _saveIndex(index) {
    await fs.promises.writeFile(
      this.indexPath,
      JSON.stringify(index, null, 2),
      'utf-8'
    );
  }

  /**
   * Get timestamp for archive naming
   * @private
   */
  _getTimestamp() {
    const now = new Date();
    return now.toISOString().split('T')[0]; // YYYY-MM-DD
  }

  /**
   * Remove directory recursively
   * @private
   */
  async _rmDir(dirPath) {
    if (!fs.existsSync(dirPath)) return;

    const files = await fs.promises.readdir(dirPath);

    for (const file of files) {
      const filePath = path.join(dirPath, file);
      const stat = await fs.promises.stat(filePath);

      if (stat.isDirectory()) {
        await this._rmDir(filePath);
      } else {
        await fs.promises.unlink(filePath);
      }
    }

    await fs.promises.rmdir(dirPath);
  }

  /**
   * Get archive statistics
   */
  async getStats() {
    const index = await this._loadIndex();
    let totalSize = 0;

    for (const archive of index.archives) {
      const archivePath = path.join(this.config.archivePath, archive.archiveName);
      if (fs.existsSync(archivePath)) {
        const stats = await fs.promises.stat(archivePath);
        totalSize += stats.size;
      }
    }

    return {
      totalArchives: index.archives.length,
      totalSessions: index.archives.reduce((sum, a) => sum + a.sessionCount, 0),
      totalSize: this._formatBytes(totalSize),
      oldestArchive: index.archives.length > 0
        ? index.archives.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))[0].timestamp
        : null,
      newestArchive: index.archives.length > 0
        ? index.archives.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))[0].timestamp
        : null
    };
  }

  /**
   * Format bytes to human-readable
   * @private
   */
  _formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }
}

module.exports = SessionArchiver;
