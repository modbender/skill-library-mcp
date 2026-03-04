/**
 * Layer 1: Task Detector — Semantic boundary detection via heuristic rules.
 *
 * P0: Rule-based detection (no LLM calls).
 * TODO [P2]: Upgrade to lightweight LLM (Flash-class) for semantic detection.
 */

const START_PATTERNS = [
  // English
  /\b(create|fix|build|analyze|find|set\s*up|write|deploy|install|configure|search|check|monitor|scan|generate|make|send|update|delete|remove|add|move|copy|run|execute|schedule|help\s+me)\b/i,
  // Chinese
  /(帮我|请|能不能|可以|麻烦|搞一个|弄一个|做一个|写一个|创建|修复|查找|分析|设置|配置|搜索|检查|生成|发送|更新|删除|添加)/,
]

const COMPLETE_PATTERNS = [
  /\b(done|completed|finished|saved|sent|delivered|created|deployed|installed|configured|updated)\b/i,
  /(完成|搞定|已发送|已保存|已创建|已部署|已配置|好了|弄好了|做完了|搞好了)/,
]

const FAILED_PATTERNS = [
  /\b(error|failed|failure|crash|broken|bug|cannot|couldn'?t|won'?t|unable)\b/i,
  /(报错|错误|失败|不对|重来|出错|崩了|挂了|不行|有问题)/,
]

export class TaskDetector {
  /**
   * Detect task event from a message.
   * @param {string} message - The user or agent message text.
   * @param {object} sessionContext - Context about the current session.
   * @param {number} [sessionContext.toolsCalled=0]
   * @param {number} [sessionContext.subAgents=0]
   * @param {number} [sessionContext.crossSessionCount=0]
   * @param {number} [sessionContext.externalApiCalls=0]
   * @param {boolean} [sessionContext.cronTriggered=false]
   * @param {number} [sessionContext.userTurns=0]
   * @returns {Promise<{event: string, task_id: string|null, confidence: number, intent_summary: string}>}
   */
  async detect(message, sessionContext = {}) {
    const msg = (message || '').trim()
    if (!msg) {
      return { event: 'TASK_PROGRESS', task_id: null, confidence: 0.1, intent_summary: '' }
    }

    // Check failed first (highest priority signal)
    if (FAILED_PATTERNS.some(p => p.test(msg))) {
      return {
        event: 'TASK_FAILED',
        task_id: null,
        confidence: 0.7,
        intent_summary: '',
      }
    }

    // Check completion
    if (COMPLETE_PATTERNS.some(p => p.test(msg))) {
      return {
        event: 'TASK_COMPLETE',
        task_id: null,
        confidence: 0.7,
        intent_summary: '',
      }
    }

    // Check start
    if (START_PATTERNS.some(p => p.test(msg))) {
      return {
        event: 'TASK_START',
        task_id: null,
        confidence: 0.6,
        intent_summary: '',
      }
    }

    return { event: 'TASK_PROGRESS', task_id: null, confidence: 0.3, intent_summary: '' }
  }

  /**
   * Compute complexity score per PRD §7 formula.
   * @param {object} ctx
   * @returns {{ score: number, level: string }}
   */
  computeComplexity(ctx = {}) {
    const {
      toolsCalled = 0,
      subAgents = 0,
      crossSessionCount = 0,
      externalApiCalls = 0,
      cronTriggered = false,
      userTurns = 0,
    } = ctx

    const score = Math.min(
      100,
      toolsCalled * 5 +
        subAgents * 15 +
        crossSessionCount * 10 +
        externalApiCalls * 3 +
        (cronTriggered ? 20 : 0) +
        userTurns * 2
    )

    let level = 'L1'
    if (score > 60) level = 'L4'
    else if (score > 30) level = 'L3'
    else if (score > 10) level = 'L2'

    return { score, level }
  }
}
