// neuroboost-elixir/src/pid.mjs
// Homeostasis Controller — PID Resource Management

export class HomeostasisController {
  constructor(targetBurnRate = 0.02) {
    this.targetBurnRate = targetBurnRate; // $/turn
    this.history = []; // [{timestamp, balance, cost}]
    this.emaFast = 0; // α=0.3
    this.emaSlow = 0; // α=0.1
    this.integral = 0;
    this.prevError = 0;
    // PID gains
    this.Kp = 0.5;
    this.Ki = 0.1;
    this.Kd = 0.3;
  }

  record(balance, cost) {
    this.history.push({ t: Date.now(), balance, cost });
    this.emaFast = 0.3 * cost + 0.7 * this.emaFast;
    this.emaSlow = 0.1 * cost + 0.9 * this.emaSlow;
    // Keep last 1000 entries
    if (this.history.length > 1000) this.history.shift();
  }

  // Predict remaining hours at current burn rate
  predictRunway(turnsPerHour = 60) {
    if (this.emaFast <= 0) return Infinity;
    const balance = this.history.at(-1)?.balance || 0;
    return balance / this.emaFast / turnsPerHour;
  }

  // Trend: accelerating / stable / decelerating
  trend() {
    if (this.emaFast > this.emaSlow * 1.2) return 'accelerating';
    if (this.emaFast < this.emaSlow * 0.8) return 'decelerating';
    return 'stable';
  }

  // PID output: positive = spend more, negative = spend less
  adjustment() {
    const error = this.targetBurnRate - this.emaFast;
    this.integral += error;
    // Anti-windup: clamp integral
    this.integral = Math.max(-1, Math.min(1, this.integral));
    const derivative = error - this.prevError;
    this.prevError = error;
    return this.Kp * error + this.Ki * this.integral + this.Kd * derivative;
  }

  // Recommended operating mode
  mode() {
    const runway = this.predictRunway();
    const t = this.trend();
    if (runway > 72) return { mode: 'normal', emoji: '🟢', action: 'Full speed' };
    if (runway > 24 && t !== 'accelerating') return { mode: 'efficient', emoji: '🟡', action: 'Downgrade non-critical models' };
    if (runway > 24 && t === 'accelerating') return { mode: 'saving', emoji: '🟠', action: 'Downgrade all models + reduce frequency' };
    if (runway > 8) return { mode: 'critical', emoji: '🔴', action: 'Minimum model + high-EV only' };
    return { mode: 'hibernate', emoji: '⚫', action: 'Heartbeat only, wait for top-up' };
  }

  report() {
    const runway = this.predictRunway();
    const m = this.mode();
    return {
      currentBurnRate: '$' + this.emaFast.toFixed(4) + '/turn',
      targetBurnRate: '$' + this.targetBurnRate.toFixed(4) + '/turn',
      trend: this.trend(),
      runwayHours: runway === Infinity ? '∞' : runway.toFixed(1) + 'h',
      mode: `${m.emoji} ${m.mode}`,
      action: m.action,
      pidAdjustment: this.adjustment().toFixed(4),
      dataPoints: this.history.length
    };
  }
}
