/**
 * GitHub Backup Service
 *
 * Backs up session archives to GitHub repository for safe keeping
 */

const { exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs');
const path = require('path');
const SecurityUtils = require('../utils/security');

const execAsync = promisify(exec);

class GitHubBackup {
  constructor(config = {}) {
    this.config = {
      enabled: config.enabled || false,
      repoUrl: config.repoUrl || process.env.GITHUB_BACKUP_REPO,
      branch: config.branch || 'main',
      localPath: config.localPath || path.join(require('os').homedir(), '.openclaw', 'github-backup'),
      commitMessage: config.commitMessage || 'Backup session archives',
      autoSync: config.autoSync !== false,
      ...config
    };

    // Validate configuration
    if (this.config.enabled && this.config.repoUrl) {
      try {
        SecurityUtils.validateGitRepo(this.config.repoUrl);
      } catch (error) {
        console.warn(`[SECURITY] Invalid GitHub repo URL: ${error.message}`);
        this.config.enabled = false;
      }
    }

    this.initialized = false;
  }

  /**
   * Initialize GitHub backup repository
   * @returns {Promise<boolean>}
   */
  async initialize() {
    if (!this.config.enabled || !this.config.repoUrl) {
      return false;
    }

    try {
      // Check if local path exists
      if (!fs.existsSync(this.config.localPath)) {
        console.log('Cloning GitHub backup repository...');
        await this._cloneRepo();
      } else {
        // Pull latest changes
        console.log('Updating GitHub backup repository...');
        await this._pullRepo();
      }

      this.initialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize GitHub backup:', error.message);
      return false;
    }
  }

  /**
   * Backup archive to GitHub
   * @param {string} archivePath - Path to archive file
   * @param {string} archiveName - Name of archive
   * @returns {Promise<Object>} Backup result
   */
  async backup(archivePath, archiveName) {
    if (!this.config.enabled) {
      return {
        success: false,
        message: 'GitHub backup is disabled'
      };
    }

    if (!this.initialized) {
      await this.initialize();
    }

    if (!this.initialized) {
      return {
        success: false,
        message: 'GitHub backup not initialized'
      };
    }

    try {
      // Copy archive to backup directory
      const backupPath = path.join(this.config.localPath, archiveName);
      await fs.promises.copyFile(archivePath, backupPath);

      // Commit and push
      if (this.config.autoSync) {
        await this._commitAndPush(archiveName);
      }

      return {
        success: true,
        message: `Backed up ${archiveName} to GitHub`,
        path: backupPath
      };
    } catch (error) {
      return {
        success: false,
        message: `Backup failed: ${error.message}`,
        error: error.message
      };
    }
  }

  /**
   * Restore archive from GitHub
   * @param {string} archiveName - Name of archive to restore
   * @param {string} targetPath - Path to restore to
   * @returns {Promise<Object>} Restore result
   */
  async restore(archiveName, targetPath) {
    if (!this.config.enabled || !this.initialized) {
      return {
        success: false,
        message: 'GitHub backup not available'
      };
    }

    try {
      // Pull latest
      await this._pullRepo();

      // Check if archive exists
      const backupPath = path.join(this.config.localPath, archiveName);

      if (!fs.existsSync(backupPath)) {
        return {
          success: false,
          message: `Archive ${archiveName} not found in GitHub backup`
        };
      }

      // Copy to target
      await fs.promises.copyFile(backupPath, targetPath);

      return {
        success: true,
        message: `Restored ${archiveName} from GitHub backup`,
        path: targetPath
      };
    } catch (error) {
      return {
        success: false,
        message: `Restore failed: ${error.message}`,
        error: error.message
      };
    }
  }

  /**
   * List archives in GitHub backup
   * @returns {Promise<Array>} List of archive names
   */
  async list() {
    if (!this.config.enabled || !this.initialized) {
      return [];
    }

    try {
      // Pull latest
      await this._pullRepo();

      // List .tar.gz files
      const files = await fs.promises.readdir(this.config.localPath);

      return files
        .filter(f => f.endsWith('.tar.gz'))
        .map(f => ({
          name: f,
          path: path.join(this.config.localPath, f)
        }));
    } catch (error) {
      console.error('Failed to list GitHub backups:', error.message);
      return [];
    }
  }

  /**
   * Delete old archives from GitHub (retention policy)
   * @param {number} retentionDays - Days to keep archives
   * @returns {Promise<Object>} Cleanup result
   */
  async cleanup(retentionDays = 90) {
    if (!this.config.enabled || !this.initialized) {
      return {
        deleted: 0,
        message: 'GitHub backup not available'
      };
    }

    try {
      const maxAgeMs = retentionDays * 24 * 60 * 60 * 1000;
      const now = Date.now();

      const files = await fs.promises.readdir(this.config.localPath);
      let deleted = 0;

      for (const file of files) {
        if (!file.endsWith('.tar.gz')) continue;

        const filePath = path.join(this.config.localPath, file);
        const stats = await fs.promises.stat(filePath);
        const age = now - stats.mtime.getTime();

        if (age > maxAgeMs) {
          await fs.promises.unlink(filePath);
          deleted++;
        }
      }

      if (deleted > 0 && this.config.autoSync) {
        await this._commitAndPush(`Cleanup: removed ${deleted} old archives`);
      }

      return {
        deleted,
        message: `Deleted ${deleted} old archives from GitHub backup`
      };
    } catch (error) {
      return {
        deleted: 0,
        message: `Cleanup failed: ${error.message}`,
        error: error.message
      };
    }
  }

  /**
   * Sync (commit and push) changes
   * @returns {Promise<boolean>}
   */
  async sync() {
    if (!this.config.enabled || !this.initialized) {
      return false;
    }

    try {
      await this._commitAndPush();
      return true;
    } catch (error) {
      console.error('Sync failed:', error.message);
      return false;
    }
  }

  /**
   * Clone repository
   * @private
   */
  async _cloneRepo() {
    // Security: Validate repo URL
    SecurityUtils.validateGitRepo(this.config.repoUrl);

    const parentDir = path.dirname(this.config.localPath);

    if (!fs.existsSync(parentDir)) {
      await fs.promises.mkdir(parentDir, { recursive: true });
    }

    try {
      await execAsync(
        `git clone "${this.config.repoUrl}" "${this.config.localPath}"`,
        SecurityUtils.getSafeExecOptions(120000) // 2 minutes for clone
      );
    } catch (error) {
      SecurityUtils.logSecurityEvent('git_clone_failed', error.message, { repoUrl: '***redacted***' });
      throw error;
    }
  }

  /**
   * Pull latest changes
   * @private
   */
  async _pullRepo() {
    try {
      await execAsync(
        `cd "${this.config.localPath}" && git pull origin "${this.config.branch}"`,
        SecurityUtils.getSafeExecOptions(60000) // 1 minute for pull
      );
    } catch (error) {
      SecurityUtils.logSecurityEvent('git_pull_failed', error.message, {});
      throw error;
    }
  }

  /**
   * Commit and push changes
   * @private
   */
  async _commitAndPush(message = null) {
    const commitMsg = message || this.config.commitMessage;

    // Security: Sanitize commit message
    const safeCommitMsg = SecurityUtils.sanitizeShellArg(commitMsg);

    try {
      // Add all changes
      await execAsync(
        `cd "${this.config.localPath}" && git add .`,
        SecurityUtils.getSafeExecOptions(30000)
      );

      // Check if there are changes to commit
      const { stdout } = await execAsync(
        `cd "${this.config.localPath}" && git status --porcelain`,
        SecurityUtils.getSafeExecOptions(10000)
      );

      if (stdout.trim().length === 0) {
        // No changes to commit
        return;
      }

      // Commit (using heredoc for safety)
      await execAsync(
        `cd "${this.config.localPath}" && git commit -m "$(cat <<'EOF'\n${safeCommitMsg}\nEOF\n)"`,
        SecurityUtils.getSafeExecOptions(30000)
      );

      // Push
      await execAsync(
        `cd "${this.config.localPath}" && git push origin "${this.config.branch}"`,
        SecurityUtils.getSafeExecOptions(60000)
      );
    } catch (error) {
      SecurityUtils.logSecurityEvent('git_commit_push_failed', error.message, {});
      throw error;
    }
  }

  /**
   * Get backup status
   */
  getStatus() {
    return {
      enabled: this.config.enabled,
      initialized: this.initialized,
      repoUrl: this.config.repoUrl ? '***configured***' : null,
      localPath: this.config.localPath,
      autoSync: this.config.autoSync
    };
  }

  /**
   * Test GitHub connection
   */
  async test() {
    if (!this.config.enabled || !this.config.repoUrl) {
      return {
        success: false,
        message: 'GitHub backup not configured'
      };
    }

    try {
      await this.initialize();

      return {
        success: true,
        message: 'GitHub backup connection successful',
        repoUrl: this.config.repoUrl
      };
    } catch (error) {
      return {
        success: false,
        message: `Connection failed: ${error.message}`,
        error: error.message
      };
    }
  }
}

module.exports = GitHubBackup;
