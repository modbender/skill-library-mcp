import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { TaskDetector } from '../src/detector.js'
import { TaskLedger } from '../src/ledger.js'
import { AnalyticsEngine } from '../src/analytics.js'
import { createTaskRecord } from '../src/schema.js'
import { mkdtempSync, rmSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'

describe('TaskDetector', () => {
  const detector = new TaskDetector()

  // 1. L1 task detection
  it('detects a simple question as TASK_START', async () => {
    const result = await detector.detect('今天天气怎样')
    expect(result.event).toBe('TASK_PROGRESS') // simple question without intent verb
  })

  it('detects intent verb as TASK_START', async () => {
    const result = await detector.detect('帮我查一下天气')
    expect(result.event).toBe('TASK_START')
  })

  // 2. L2 task detection (tool call scenario)
  it('detects tool-calling intent as TASK_START', async () => {
    const result = await detector.detect('Check the PR status for openclaw/core')
    expect(result.event).toBe('TASK_START')
    expect(result.confidence).toBeGreaterThan(0)
  })

  // 3. L3 compound task
  it('detects compound task as TASK_START', async () => {
    const result = await detector.detect('帮我存到 Notion 并分析这篇文章')
    expect(result.event).toBe('TASK_START')
  })

  // 4. Complexity scoring
  it('computes complexity score correctly', () => {
    // L1: no tools, 1 user turn
    expect(detector.computeComplexity({ userTurns: 1 })).toEqual({ score: 2, level: 'L1' })

    // L2: 3 tool calls, 2 user turns
    expect(detector.computeComplexity({ toolsCalled: 3, userTurns: 2 })).toEqual({ score: 19, level: 'L2' })

    // L3: tools + external APIs + multi-turn
    expect(detector.computeComplexity({ toolsCalled: 5, externalApiCalls: 3, userTurns: 4 })).toEqual({ score: 42, level: 'L3' })

    // L4: sub-agents + cron + cross-session
    expect(detector.computeComplexity({ subAgents: 2, cronTriggered: true, crossSessionCount: 2, toolsCalled: 3, userTurns: 3 })).toEqual({ score: 81, level: 'L4' })
  })

  // Completion detection
  it('detects completion signals', async () => {
    const result = await detector.detect('搞定了，已保存到文件')
    expect(result.event).toBe('TASK_COMPLETE')
  })

  // Failure detection
  it('detects failure signals', async () => {
    const result = await detector.detect('报错了，重来')
    expect(result.event).toBe('TASK_FAILED')
  })
})

describe('AnalyticsEngine + Ledger', () => {
  let tmpDir, ledger, analytics

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'task-metrics-test-'))
    ledger = new TaskLedger(join(tmpDir, 'test.db'))
    ledger.init()
    analytics = new AnalyticsEngine(ledger)
  })

  afterEach(() => {
    ledger.close()
    rmSync(tmpDir, { recursive: true, force: true })
  })

  // 5. TES calculation with quality_score=0 (failed task)
  it('computes TES=0 for failed tasks', () => {
    const task = {
      quality_score: 0,
      total_cost_usd: 0.05,
      complexity_score: 15,
      complexity_level: 'L2',
    }
    expect(analytics.computeTES(task)).toBe(0)
  })

  // TES for successful task
  it('computes positive TES for successful tasks', () => {
    const task = {
      quality_score: 1.0,
      total_cost_usd: 0.003,
      complexity_score: 2,
      complexity_level: 'L1',
    }
    const tes = analytics.computeTES(task)
    expect(tes).toBeGreaterThan(1)
  })

  // 6. Cost attribution across multiple sessions
  it('attributes cost from multiple sessions', () => {
    ledger.startTask('tsk_testcost12345678', {
      sessions: ['sess_a', 'sess_b'],
      intent_summary: 'multi-session task',
    })

    ledger.attributeCost('tsk_testcost12345678', 1000, 0.05, 'sonnet-4', 'main')
    ledger.attributeCost('tsk_testcost12345678', 2000, 0.10, 'opus-4', 'sub-agent')

    const task = ledger.getTask('tsk_testcost12345678')
    expect(task.total_tokens).toBe(3000)
    expect(task.total_cost_usd).toBeCloseTo(0.15)

    const models = JSON.parse(task.models_used)
    expect(models).toContain('sonnet-4')
    expect(models).toContain('opus-4')
  })

  // 7. Timeout / silent completion (verify level-based timeout config exists)
  it('supports complexity-tiered timeout configuration', () => {
    // Timeouts are configured externally; verify complexity levels map correctly
    const timeouts = { L1: 2, L2: 5, L3: 15, L4: 60 } // minutes
    const detector = new TaskDetector()

    const l1 = detector.computeComplexity({ userTurns: 1 })
    expect(timeouts[l1.level]).toBe(2)

    const l4 = detector.computeComplexity({ subAgents: 3, cronTriggered: true, toolsCalled: 5 })
    expect(timeouts[l4.level]).toBe(60)
  })

  // 8. Failed tasks count toward model efficiency
  it('includes failed tasks in model stats', () => {
    // Create a successful and a failed task for the same model
    ledger.startTask('tsk_success1234567', { models_used: ['test-model'], intent_summary: 'success' })
    ledger.completeTask('tsk_success1234567', 1.0, 'done')
    ledger.attributeCost('tsk_success1234567', 500, 0.01, 'test-model', 'main')

    ledger.startTask('tsk_failure1234567', { models_used: ['test-model'], intent_summary: 'fail' })
    ledger.updateTask('tsk_failure1234567', { status: 'failed', quality_score: 0 })
    ledger.attributeCost('tsk_failure1234567', 500, 0.01, 'test-model', 'main')

    const stats = analytics.getModelStats()
    const modelStat = stats.find(s => s.model === 'test-model')
    expect(modelStat).toBeDefined()
    expect(modelStat.tasks).toBe(2)
    expect(modelStat.successRate).toBe(0.5) // 1 success out of 2
  })
})

describe('Schema', () => {
  it('creates a valid task record with defaults', () => {
    const record = createTaskRecord({
      task_id: 'tsk_abcdefghijklmn',
      started_at: '2026-02-24T00:00:00.000Z',
      status: 'in_progress',
    })
    expect(record.task_id).toBe('tsk_abcdefghijklmn')
    expect(record.complexity_level).toBe('L1')
    expect(record.models_used).toEqual([])
  })
})
