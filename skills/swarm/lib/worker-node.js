/**
 * Specialized Worker Node
 * Each node type has specific tools and capabilities
 * 
 * Security: All outputs are sanitized and injection attempts are detected
 */

const { GeminiClient } = require('./gemini-client');
const { 
  webSearch, 
  webFetch, 
  createAnalyzeTool, 
  createExtractTool, 
  createSynthesizeTool 
} = require('./tools');
const config = require('../config');
const { detectInjection, sanitizeOutput } = require('./security');
const { promptCache } = require('./cache');
const { routePrompt } = require('./router');

const DEFAULT_TASK_TIMEOUT_MS = 30000;
const DEFAULT_RETRIES = 1;
const RETRY_BACKOFF_MS = 1000;

class WorkerNode {
  constructor(id, nodeType = 'analyze') {
    this.id = id;
    this.nodeType = nodeType;
    this.llm = new GeminiClient();
    this.status = 'idle';
    this.currentTask = null;
    this.completedTasks = 0;
    this.totalDuration = 0;
    this.retriedTasks = 0;
    this.routedToPro = 0;
    
    // Get node configuration
    this.config = config.nodeTypes[nodeType] || config.nodeTypes.analyze;
    
    // Initialize tools based on node type
    this.tools = this.initializeTools();
  }

  initializeTools() {
    const tools = {};
    
    // Add tools based on node type
    switch (this.nodeType) {
      case 'search':
        tools.web_search = webSearch;
        break;
      case 'fetch':
        tools.web_fetch = webFetch;
        break;
      case 'analyze':
        tools.analyze = createAnalyzeTool(this.llm);
        break;
      case 'extract':
        tools.extract = createExtractTool(this.llm);
        break;
      case 'synthesize':
        tools.synthesize = createSynthesizeTool(this.llm);
        break;
    }
    
    return tools;
  }

  async execute(task) {
    const maxRetries = task.retries ?? config.scaling?.retries ?? DEFAULT_RETRIES;
    const timeoutMs = task.timeoutMs ?? config.scaling?.timeoutMs ?? DEFAULT_TASK_TIMEOUT_MS;
    let lastError = null;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      if (attempt > 0) {
        this.retriedTasks++;
        const backoff = RETRY_BACKOFF_MS * attempt;
        await new Promise(r => setTimeout(r, backoff));
      }

      const result = await this._executeOnce(task, timeoutMs);
      
      if (result.success) {
        if (attempt > 0) result.retries = attempt;
        return result;
      }

      lastError = result;
      
      // Don't retry on non-transient errors
      if (result.error && /invalid|malformed|unauthorized|forbidden|not found/i.test(result.error)) {
        return result;
      }
    }

    // All retries exhausted
    if (lastError) lastError.retriesExhausted = true;
    return lastError;
  }

  async _executeOnce(task, timeoutMs) {
    this.status = 'busy';
    this.currentTask = task;
    const startTime = Date.now();

    try {
      // Security: Scan input for injection attempts
      const inputText = typeof task.input === 'string' ? task.input : JSON.stringify(task.input || '');
      const injectionCheck = detectInjection(inputText);
      
      if (!injectionCheck.safe) {
        console.warn(`[Security] Potential injection detected in task ${task.id}:`, injectionCheck.threats.map(t => t.type).join(', '));
      }
      
      let result;
      
      // Wrap execution with timeout
      const execPromise = (async () => {
        if (task.tool && this.tools[task.tool]) {
          return await this.executeTool(task.tool, task.input, task.options);
        } else {
          return await this.executeLLM(task);
        }
      })();

      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error(`Task timed out after ${timeoutMs}ms`)), timeoutMs)
      );

      result = await Promise.race([execPromise, timeoutPromise]);
      
      // Security: Sanitize output
      if (result && result.response) {
        result.response = sanitizeOutput(result.response);
      }
      
      // Quality validation — detect garbage/empty/low-quality outputs
      const quality = this.validateOutput(result, task);
      if (!quality.pass) {
        const duration = Date.now() - startTime;
        this.status = 'idle';
        this.currentTask = null;
        return {
          nodeId: this.id,
          nodeType: this.nodeType,
          taskId: task.id,
          success: false,
          error: `Quality check failed: ${quality.reason}`,
          durationMs: duration,
          qualityIssue: true,
        };
      }
      
      const duration = Date.now() - startTime;
      this.completedTasks++;
      this.totalDuration += duration;
      this.status = 'idle';
      this.currentTask = null;

      return {
        nodeId: this.id,
        nodeType: this.nodeType,
        taskId: task.id,
        success: true,
        result,
        durationMs: duration,
        cached: result?.cached || false,
        securityWarnings: injectionCheck.safe ? undefined : injectionCheck.threats.length,
      };
    } catch (error) {
      const duration = Date.now() - startTime;
      this.status = 'idle';
      this.currentTask = null;
      
      return {
        nodeId: this.id,
        nodeType: this.nodeType,
        taskId: task.id,
        success: false,
        error: sanitizeOutput(error.message),
        durationMs: duration,
      };
    }
  }

  async executeTool(toolName, input, options = {}) {
    const tool = this.tools[toolName];
    if (!tool) {
      throw new Error(`Tool '${toolName}' not available on ${this.nodeType} node`);
    }
    return await tool(input, options);
  }

  async executeLLM(task) {
    // Chain stages can override system prompt with a perspective
    const sysPrompt = task._systemPrompt || this.config.systemPrompt;
    
    const prompt = `${sysPrompt}

Task: ${task.instruction}

${task.context ? `Context:\n${task.context}` : ''}
${task.input ? `Input:\n${typeof task.input === 'string' ? task.input : JSON.stringify(task.input, null, 2)}` : ''}

Provide a focused, high-quality response. Be concise — prioritize insight density over length.`;

    // Check cache (skip for web search — results should be fresh)
    const useCache = !task.webSearch && !task.grounding && task.cache !== false;
    if (useCache) {
      const cached = promptCache.get(task.instruction, task.input, sysPrompt);
      if (cached) {
        return { response: cached, cached: true };
      }
    }

    const llmOptions = { ...(task._llmOptions || {}) };
    if (task.maxOutputTokens) llmOptions.maxTokens = task.maxOutputTokens;
    // Enable Google Search grounding for research/analysis tasks
    if (task.webSearch || task.grounding) {
      llmOptions.webSearch = true;
    }
    
    // Smart routing — pick model tier based on complexity
    if (config.routing?.enabled !== false) {
      const route = routePrompt({
        instruction: task.instruction,
        input: task.input,
        perspective: task._perspective || '',
        stageIndex: task._stageIndex,
        isLastStage: task._isLastStage,
      }, { threshold: config.routing?.threshold });
      
      if (route.tier === 'pro') {
        llmOptions.model = route.model;
        task._routed = { tier: route.tier, score: route.score };
      }
    }
    
    const result = await this.llm.complete(prompt, llmOptions);
    
    // Store in cache
    if (useCache && result) {
      promptCache.set(task.instruction, task.input, sysPrompt, result);
    }
    
    // Track routing
    if (task._routed?.tier === 'pro') this.routedToPro++;
    
    return { response: result, routed: task._routed || null };
  }

  /**
   * Validate output quality — catch garbage before it propagates through chains
   */
  validateOutput(result, task) {
    const response = result?.response || '';
    
    // Empty or near-empty response
    if (!response || response.trim().length < 5) {
      return { pass: false, reason: 'empty or near-empty response' };
    }
    
    // Repetition detection — same phrase repeated 5+ times indicates degenerate output
    const lines = response.split('\n').map(l => l.trim()).filter(Boolean);
    if (lines.length >= 5) {
      const freq = {};
      for (const line of lines) {
        const key = line.substring(0, 60);
        freq[key] = (freq[key] || 0) + 1;
      }
      const maxRepeat = Math.max(...Object.values(freq));
      if (maxRepeat >= 5 && maxRepeat / lines.length > 0.5) {
        return { pass: false, reason: `degenerate repetition (${maxRepeat}x repeated line)` };
      }
    }
    
    // Refusal detection — model declined to answer
    const refusalPatterns = /^(I cannot|I'm unable to|I apologize|As an AI|I don't have access)/i;
    if (refusalPatterns.test(response.trim()) && response.length < 200) {
      return { pass: false, reason: 'model refusal detected' };
    }
    
    // Truncation detection — response cuts off mid-sentence (no terminal punctuation)
    const lastChar = response.trim().slice(-1);
    const hasTerminal = /[.!?\n\]\)`"']/.test(lastChar);
    if (!hasTerminal && response.length > 500) {
      // Only flag if it's a long response that got cut off
      return { pass: false, reason: 'response appears truncated' };
    }
    
    return { pass: true };
  }

  getStats() {
    const providerInfo = this.llm.getStats();
    return {
      id: this.id,
      type: this.nodeType,
      status: this.status,
      completedTasks: this.completedTasks,
      retriedTasks: this.retriedTasks,
      avgDurationMs: this.completedTasks > 0 
        ? Math.round(this.totalDuration / this.completedTasks) 
        : 0,
      tokens: providerInfo.tokens,
      cost: providerInfo.cost,
      routedToPro: this.routedToPro,
    };
  }
}

module.exports = { WorkerNode };
