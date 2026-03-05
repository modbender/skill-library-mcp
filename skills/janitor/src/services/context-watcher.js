/**
 * Context Watcher - Background Monitoring Service
 *
 * Continuously monitors OpenClaw's context usage and triggers
 * automatic cleanup when thresholds are exceeded
 */

class ContextWatcher {
  constructor(monitor, pruner, archiver, emergency, config = {}) {
    this.monitor = monitor;
    this.pruner = pruner;
    this.archiver = archiver;
    this.emergency = emergency;

    this.config = {
      enabled: config.enabled !== false,
      intervalMinutes: config.intervalMinutes || 5,
      alertThreshold: config.alertThreshold || 80,
      emergencyThreshold: config.emergencyThreshold || 95,
      autoCleanup: config.autoCleanup !== false,
      ...config
    };

    this.isRunning = false;
    this.intervalId = null;
    this.checkCount = 0;
    this.cleanupCount = 0;
    this.lastCheck = null;
    this.lastCleanup = null;
  }

  /**
   * Start the background monitoring service
   */
  start() {
    if (this.isRunning) {
      console.log('Context watcher is already running');
      return;
    }

    if (!this.config.enabled) {
      console.log('Context watcher is disabled in config');
      return;
    }

    console.log(`🔍 Starting context watcher (checking every ${this.config.intervalMinutes} minutes)...`);

    this.isRunning = true;

    // Run initial check
    this._performCheck();

    // Schedule periodic checks
    const intervalMs = this.config.intervalMinutes * 60 * 1000;
    this.intervalId = setInterval(() => {
      this._performCheck();
    }, intervalMs);

    console.log('✅ Context watcher started');
  }

  /**
   * Stop the background monitoring service
   */
  stop() {
    if (!this.isRunning) {
      console.log('Context watcher is not running');
      return;
    }

    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }

    this.isRunning = false;
    console.log('⏹️  Context watcher stopped');
  }

  /**
   * Perform a context usage check
   * @private
   */
  async _performCheck() {
    try {
      this.checkCount++;
      this.lastCheck = new Date();

      const usage = await this.monitor.getContextUsage();

      console.log(`\n[${this.lastCheck.toISOString()}] Context check #${this.checkCount}:`);
      console.log(`  Tokens: ${this.monitor.formatTokens(usage.currentTokens)}/200k (${usage.utilizationPercent.toFixed(1)}%)`);
      console.log(`  Sessions: ${usage.sessions.length}`);
      console.log(`  Status: ${usage.status.emoji} ${usage.status.level}`);

      // Check if cleanup is needed
      if (usage.utilizationPercent >= this.config.emergencyThreshold) {
        console.log(`\n  🚨 CRITICAL: Emergency cleanup required!`);

        if (this.config.autoCleanup) {
          await this._triggerEmergencyCleanup();
        } else {
          console.log(`  ℹ️  Auto-cleanup is disabled. Manual intervention required.`);
        }
      } else if (usage.utilizationPercent >= this.config.alertThreshold) {
        console.log(`\n  ⚠️  WARNING: High usage detected, cleanup recommended`);

        if (this.config.autoCleanup) {
          await this._triggerRoutineCleanup(usage.utilizationPercent);
        } else {
          console.log(`  ℹ️  Auto-cleanup is disabled. Run 'janitor context clean' manually.`);
        }
      } else {
        console.log(`  ✅ Usage is within normal range`);
      }
    } catch (error) {
      console.error(`❌ Context check failed:`, error.message);
    }
  }

  /**
   * Trigger routine cleanup
   * @private
   */
  async _triggerRoutineCleanup(utilizationPercent) {
    try {
      console.log(`\n🧹 Triggering routine cleanup...`);

      const strategy = this.pruner.getRecommendedStrategy(utilizationPercent);

      // Get sessions to prune
      const usage = await this.monitor.getContextUsage();
      const sessionsToPrune = usage.sessions
        .filter(s => !this._isProtected(s))
        .sort((a, b) => a.lastActive - b.lastActive);

      // Determine how many to prune
      let pruneCount;
      if (utilizationPercent > 90) {
        pruneCount = Math.ceil(sessionsToPrune.length * 0.5);
      } else if (utilizationPercent > 85) {
        pruneCount = Math.ceil(sessionsToPrune.length * 0.35);
      } else {
        pruneCount = Math.ceil(sessionsToPrune.length * 0.25);
      }

      const toPrune = sessionsToPrune.slice(0, pruneCount);

      if (toPrune.length === 0) {
        console.log(`  ℹ️  No sessions available to prune (all are protected)`);
        return;
      }

      // Archive before pruning
      console.log(`  📦 Archiving ${toPrune.length} sessions...`);
      const archiveResult = await this.archiver.archiveSessions(toPrune, 'auto-cleanup');

      // Prune sessions
      console.log(`  🗑️  Pruning ${toPrune.length} sessions...`);
      const pruneResult = await this.pruner.prune(strategy);

      // Verify results
      const afterUsage = await this.monitor.getContextUsage();

      console.log(`\n  ✅ Cleanup complete:`);
      console.log(`     - Archived: ${archiveResult.archived} sessions`);
      console.log(`     - Pruned: ${pruneResult.sessionsPruned} sessions`);
      console.log(`     - Freed: ${this.monitor.formatTokens(pruneResult.tokensFreed)} tokens`);
      console.log(`     - New usage: ${afterUsage.utilizationPercent.toFixed(1)}%`);

      this.cleanupCount++;
      this.lastCleanup = new Date();
    } catch (error) {
      console.error(`  ❌ Routine cleanup failed:`, error.message);
    }
  }

  /**
   * Trigger emergency cleanup
   * @private
   */
  async _triggerEmergencyCleanup() {
    try {
      console.log(`\n🚨 Triggering EMERGENCY cleanup...`);

      const result = await this.emergency.execute();

      if (result.success) {
        console.log(`\n  ✅ Emergency cleanup successful!`);
        console.log(`     - Before: ${result.beforeUsage.percent.toFixed(1)}% (${result.beforeUsage.sessions} sessions)`);
        console.log(`     - After: ${result.afterUsage.percent.toFixed(1)}% (${result.afterUsage.sessions} sessions)`);
        console.log(`     - Duration: ${result.duration}ms`);
      } else {
        console.log(`\n  ❌ Emergency cleanup failed!`);
        console.log(`     Error: ${result.error || 'Unknown error'}`);
      }

      this.cleanupCount++;
      this.lastCleanup = new Date();
    } catch (error) {
      console.error(`  ❌ Emergency cleanup failed:`, error.message);
    }
  }

  /**
   * Check if session is protected from pruning
   * @private
   */
  _isProtected(session) {
    const ageHours = (Date.now() - session.lastActive.getTime()) / (1000 * 60 * 60);

    // Always keep recent sessions (24 hours)
    if (ageHours < 24) return true;

    // Keep high-engagement sessions
    if (session.messageCount >= 10) return true;

    // Keep high-priority sessions
    if (session.priority === 'high') return true;

    return false;
  }

  /**
   * Get watcher status
   */
  getStatus() {
    return {
      running: this.isRunning,
      enabled: this.config.enabled,
      intervalMinutes: this.config.intervalMinutes,
      checkCount: this.checkCount,
      cleanupCount: this.cleanupCount,
      lastCheck: this.lastCheck,
      lastCleanup: this.lastCleanup,
      nextCheck: this.isRunning
        ? new Date(Date.now() + this.config.intervalMinutes * 60 * 1000)
        : null,
      autoCleanup: this.config.autoCleanup
    };
  }

  /**
   * Get statistics
   */
  getStats() {
    return {
      totalChecks: this.checkCount,
      totalCleanups: this.cleanupCount,
      lastCheck: this.lastCheck,
      lastCleanup: this.lastCleanup,
      uptime: this.isRunning
        ? Date.now() - (this.lastCheck ? this.lastCheck.getTime() : Date.now())
        : 0
    };
  }

  /**
   * Perform immediate check (manual trigger)
   */
  async checkNow() {
    console.log('🔍 Performing immediate context check...');
    await this._performCheck();
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig) {
    this.config = {
      ...this.config,
      ...newConfig
    };

    console.log('⚙️  Configuration updated');

    // Restart if running to apply new interval
    if (this.isRunning && newConfig.intervalMinutes) {
      this.stop();
      this.start();
    }
  }
}

module.exports = ContextWatcher;
