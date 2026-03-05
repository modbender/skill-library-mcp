/**
 * Layer 3: Analytics Engine — TES computation and aggregation.
 */

const COMPLEXITY_WEIGHTS = { L1: 0.5, L2: 1.0, L3: 2.0, L4: 4.0 }

const DEFAULT_MEDIAN_COST = { L1: 0.005, L2: 0.03, L3: 0.15, L4: 0.80 }

export class AnalyticsEngine {
  /**
   * @param {import('./ledger.js').TaskLedger} ledger
   */
  constructor(ledger) {
    this.ledger = ledger
  }

  /**
   * Compute TES for a single task.
   * TES = quality_score / (normalized_cost × complexity_weight)
   * Where complexity_weight = 1 / (1 + ln(complexity_score + 1))
   * @param {object} task
   * @returns {number}
   */
  computeTES(task) {
    if (!task || task.quality_score === 0) return 0

    const medianCost = DEFAULT_MEDIAN_COST[task.complexity_level] || 0.03
    const normalizedCost = Math.max(0.01, task.total_cost_usd / medianCost)
    const complexityWeight = 1.0 / (1.0 + Math.log(task.complexity_score + 1))

    return task.quality_score / (normalizedCost * complexityWeight)
  }

  /**
   * Get per-model aggregated TES.
   * @param {object} [filters]
   * @returns {object[]}
   */
  getModelStats(filters) {
    const tasks = this.ledger.listTasks({ ...filters, limit: 10000 })
    const modelMap = new Map()

    for (const task of tasks) {
      const models = JSON.parse(task.models_used || '[]')
      const tes = task.tes ?? this.computeTES(task)

      for (const model of models) {
        if (!modelMap.has(model)) {
          modelMap.set(model, { model, tasks: 0, totalTes: 0, totalCost: 0, successes: 0 })
        }
        const m = modelMap.get(model)
        m.tasks++
        m.totalTes += tes
        m.totalCost += task.total_cost_usd
        if (task.quality_score > 0) m.successes++
      }
    }

    return [...modelMap.values()].map(m => ({
      model: m.model,
      tasks: m.tasks,
      avgTes: m.tasks ? m.totalTes / m.tasks : 0,
      totalCost: m.totalCost,
      successRate: m.tasks ? m.successes / m.tasks : 0,
    }))
  }

  /**
   * Get per-session aggregated stats.
   * @param {object} [filters]
   * @returns {object[]}
   */
  getSessionStats(filters) {
    const tasks = this.ledger.listTasks({ ...filters, limit: 10000 })
    const sessionMap = new Map()

    for (const task of tasks) {
      const sessions = JSON.parse(task.sessions || '[]')
      const tes = task.tes ?? this.computeTES(task)

      for (const sess of sessions) {
        if (!sessionMap.has(sess)) {
          sessionMap.set(sess, { session: sess, tasks: 0, totalTes: 0, totalCost: 0 })
        }
        const s = sessionMap.get(sess)
        s.tasks++
        s.totalTes += tes
        s.totalCost += task.total_cost_usd
      }
    }

    return [...sessionMap.values()].map(s => ({
      session: s.session,
      tasks: s.tasks,
      avgTes: s.tasks ? s.totalTes / s.tasks : 0,
      totalCost: s.totalCost,
    }))
  }

  /**
   * Get per-cron aggregated stats.
   * @param {object} [filters]
   * @returns {object[]}
   */
  getCronStats(filters) {
    const tasks = this.ledger.listTasks({ ...filters, limit: 10000 })
      .filter(t => t.cron_id)
    const cronMap = new Map()

    for (const task of tasks) {
      if (!cronMap.has(task.cron_id)) {
        cronMap.set(task.cron_id, { cron_id: task.cron_id, tasks: 0, totalTes: 0, totalCost: 0, successes: 0 })
      }
      const c = cronMap.get(task.cron_id)
      c.tasks++
      c.totalTes += task.tes ?? this.computeTES(task)
      c.totalCost += task.total_cost_usd
      if (task.quality_score > 0) c.successes++
    }

    return [...cronMap.values()].map(c => ({
      cron_id: c.cron_id,
      tasks: c.tasks,
      avgTes: c.tasks ? c.totalTes / c.tasks : 0,
      totalCost: c.totalCost,
      successRate: c.tasks ? c.successes / c.tasks : 0,
    }))
  }

  /**
   * Get weekly summary for current week.
   * @returns {object}
   */
  getWeeklySummary() {
    const now = new Date()
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    const tasks = this.ledger.listTasks({ from: weekAgo.toISOString(), limit: 10000 })

    const completed = tasks.filter(t => t.status === 'completed')
    const failed = tasks.filter(t => t.status === 'failed')
    const totalCost = tasks.reduce((s, t) => s + t.total_cost_usd, 0)
    const avgTes = completed.length
      ? completed.reduce((s, t) => s + (t.tes ?? this.computeTES(t)), 0) / completed.length
      : 0

    return {
      period: `${weekAgo.toISOString().slice(0, 10)} → ${now.toISOString().slice(0, 10)}`,
      totalTasks: tasks.length,
      completed: completed.length,
      failed: failed.length,
      totalCost: Math.round(totalCost * 100) / 100,
      avgTes: Math.round(avgTes * 100) / 100,
    }
  }

  /**
   * Get the most expensive tasks.
   * @param {number} [limit=10]
   * @returns {object[]}
   */
  getTopExpensiveTasks(limit = 10) {
    return this.ledger.db
      .prepare('SELECT * FROM tasks ORDER BY total_cost_usd DESC LIMIT ?')
      .all(limit)
  }
}
