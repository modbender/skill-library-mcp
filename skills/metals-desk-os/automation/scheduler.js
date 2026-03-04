// ============================================================================
// SCHEDULER — Cron-Based Task Scheduling
// ============================================================================
// Handles daily resets, report generation, and periodic tasks.
// ============================================================================

const cron = require('node-cron');
const bus = require('./event-bus');
const { EVENTS } = bus;

class Scheduler {
  constructor(config = {}) {
    this.config = config;
    this.jobs = [];
    this.running = false;
  }

  start() {
    this.running = true;

    // --- Daily Reset at 00:00 UTC (Sunday-Friday) ---
    this._addJob('0 0 * * 0-5', 'daily-reset', () => {
      bus.publish(EVENTS.ALERT_SYSTEM, { type: 'scheduler', message: 'Daily reset triggered' });
      bus.publish('scheduler.daily.reset', { timestamp: new Date().toISOString() });
    });

    // --- Pre-London Prep at 06:30 UTC ---
    this._addJob('30 6 * * 1-5', 'pre-london', () => {
      bus.publish(EVENTS.ALERT_SYSTEM, { type: 'scheduler', message: 'Pre-London session prep' });
      bus.publish('scheduler.pre.london', { timestamp: new Date().toISOString() });
    });

    // --- Pre-NY Prep at 11:30 UTC ---
    this._addJob('30 11 * * 1-5', 'pre-ny', () => {
      bus.publish(EVENTS.ALERT_SYSTEM, { type: 'scheduler', message: 'Pre-NY session prep' });
      bus.publish('scheduler.pre.ny', { timestamp: new Date().toISOString() });
    });

    // --- EOD Performance Report at 21:00 UTC ---
    this._addJob('0 21 * * 1-5', 'eod-report', () => {
      bus.publish(EVENTS.PERFORMANCE_REPORT, { type: 'eod', timestamp: new Date().toISOString() });
    });

    // --- Weekly Report Sunday 22:00 UTC ---
    this._addJob('0 22 * * 0', 'weekly-report', () => {
      bus.publish(EVENTS.PERFORMANCE_REPORT, { type: 'weekly', timestamp: new Date().toISOString() });
    });

    // --- Heartbeat every 60 seconds ---
    this._addJob('* * * * *', 'heartbeat', () => {
      bus.publish(EVENTS.SYSTEM_HEARTBEAT, {
        timestamp: new Date().toISOString(),
        mode: bus.getMode(),
        uptime: process.uptime()
      });
    });

    // --- Macro check every 15 minutes ---
    this._addJob('*/15 * * * *', 'macro-check', () => {
      bus.publish('scheduler.macro.check', { timestamp: new Date().toISOString() });
    });

    console.log('[SCHEDULER] Started with', this.jobs.length, 'jobs');
  }

  stop() {
    this.running = false;
    this.jobs.forEach(j => j.task.stop());
    this.jobs = [];
    console.log('[SCHEDULER] Stopped');
  }

  _addJob(cronExpr, name, handler) {
    const task = cron.schedule(cronExpr, handler, { timezone: 'UTC' });
    this.jobs.push({ name, cronExpr, task });
  }

  getJobs() {
    return this.jobs.map(j => ({ name: j.name, cron: j.cronExpr }));
  }
}

module.exports = Scheduler;
