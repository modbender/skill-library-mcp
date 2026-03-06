/**
 * Node Scaling for Clawdbot
 * Main entry point
 */

const { Dispatcher } = require('./dispatcher');
const { WorkerNode } = require('./worker-node');
const { createProvider, loadProviderFromConfig, PROVIDERS, COST_RANKING } = require('./providers');
const { webSearch, webFetch, createAnalyzeTool, createExtractTool, createSynthesizeTool } = require('./tools');
const { SwarmMetrics, metrics } = require('./metrics');
const { swarmEvents, EVENTS } = require('./events');
const { SwarmDisplay, initDisplay, getDisplay } = require('./display');
const { runDiagnostics, getMachineProfile, printReport } = require('./diagnostics');
const { SwarmDaemon } = require('./daemon');
const { SwarmClient, isDaemonRunning, parallel: parallelClient, research: researchClient } = require('./client');
const { SECURITY_POLICY, securePrompt, detectInjection, sanitizeOutput } = require('./security');
const { buildChainPhases, validateChain, PERSPECTIVES, TRANSFORMS } = require('./chain');
const { buildAutoChain, previewChain, DEPTH_PRESETS, TASK_PATTERNS } = require('./chain-builder');
const { runBenchmark, SCORING_DIMENSIONS, formatComparisonTable } = require('./benchmark');
const { PromptCache, promptCache } = require('./cache');
const { TEMPLATES, getTemplate, listTemplates } = require('./templates');
const { routePrompt, routeBatch, TIERS } = require('./router');
const { diagnoseError, formatErrorEvent, formatErrorCLI } = require('./errors');
const { reflect, criticize, SCORE_DIMENSIONS } = require('./reflect');
const { SCHEMAS, listSchemas, getSchema, validateAgainstSchema } = require('./structured');
const { vote, pickLongest, pickBySimilarity } = require('./voting');

/**
 * Create a configured dispatcher ready for use
 */
function createDispatcher(config = {}) {
  return new Dispatcher(config);
}

/**
 * Quick parallel execution helper
 * @param {string[]} prompts - Array of prompts to execute
 * @param {object} options - Configuration options
 */
async function parallel(prompts, options = {}) {
  const dispatcher = new Dispatcher();
  
  const tasks = prompts.map(prompt => ({
    nodeType: 'analyze',
    instruction: prompt,
  }));
  
  const results = await dispatcher.executeParallel(tasks);
  dispatcher.shutdown();
  
  return {
    results: results.results.map(r => r.success ? r.result?.response : null),
    stats: {
      totalDuration: results.totalDurationMs,
      successful: results.results.filter(r => r.success).length,
      failed: results.results.filter(r => !r.success).length,
    },
  };
}

/**
 * Research helper - searches, fetches, and analyzes multiple subjects
 * @param {string[]} subjects - Subjects to research
 * @param {string} topic - Research topic/angle
 */
async function research(subjects, topic, options = {}) {
  const dispatcher = new Dispatcher();
  
  const phases = [
    {
      name: 'Search',
      tasks: subjects.map(subject => ({
        nodeType: 'search',
        tool: 'web_search',
        input: `${subject} ${topic}`,
        options: { count: 3 },
        metadata: { subject },
      })),
    },
    {
      name: 'Fetch',
      tasks: (prev) => {
        return prev[0].results
          .filter(r => r.success && r.result?.results?.[0])
          .map((r, i) => ({
            nodeType: 'fetch',
            tool: 'web_fetch',
            input: r.result.results[0].url,
            options: { maxChars: 8000 },
            metadata: { subject: subjects[i] },
          }));
      },
    },
    {
      name: 'Analyze',
      tasks: (prev) => {
        const fetches = prev[1].results.filter(r => r.success);
        return subjects.map((subject, i) => ({
          nodeType: 'analyze',
          instruction: `Analyze and summarize information about ${subject} regarding ${topic}. Be thorough but concise.`,
          input: fetches[i]?.result?.content?.substring(0, 5000) || '',
          metadata: { subject },
        }));
      },
    },
  ];
  
  const result = await dispatcher.orchestrate(phases);
  const stats = dispatcher.getNodeStats();
  dispatcher.shutdown();
  
  return {
    subjects,
    topic,
    analyses: result.phases[2]?.results
      .filter(r => r.success)
      .map((r, i) => ({
        subject: subjects[i],
        analysis: r.result?.response || r.result,
      })) || [],
    stats: {
      totalDuration: result.totalDurationMs,
      phases: result.phases.map(p => ({
        name: p.phase,
        duration: p.totalDurationMs,
      })),
      nodeStats: stats,
    },
  };
}

module.exports = {
  // Core
  Dispatcher,
  WorkerNode,
  createDispatcher,
  
  // Providers
  createProvider,
  loadProviderFromConfig,
  PROVIDERS,
  COST_RANKING,
  
  // Tools
  webSearch,
  webFetch,
  createAnalyzeTool,
  createExtractTool,
  createSynthesizeTool,
  
  // Helpers
  parallel,
  research,
  
  // Metrics
  SwarmMetrics,
  metrics,
  
  // Events & Display
  swarmEvents,
  EVENTS,
  SwarmDisplay,
  initDisplay,
  getDisplay,
  
  // Diagnostics
  runDiagnostics,
  getMachineProfile,
  printReport,
  
  // Daemon & Client
  SwarmDaemon,
  SwarmClient,
  isDaemonRunning,
  parallelClient,
  researchClient,
  
  // Security
  SECURITY_POLICY,
  securePrompt,
  detectInjection,
  sanitizeOutput,
  
  // Chain
  buildChainPhases,
  validateChain,
  PERSPECTIVES,
  TRANSFORMS,
  
  // Chain Builder (dynamic)
  buildAutoChain,
  previewChain,
  DEPTH_PRESETS,
  TASK_PATTERNS,
  
  // Benchmark
  runBenchmark,
  SCORING_DIMENSIONS,
  formatComparisonTable,
  
  // Cache
  PromptCache,
  promptCache,
  
  // Templates
  TEMPLATES,
  getTemplate,
  listTemplates,
  
  // Router
  routePrompt,
  routeBatch,
  TIERS,
  
  // Errors
  diagnoseError,
  formatErrorEvent,
  formatErrorCLI,
  
  // Reflection
  reflect,
  criticize,
  SCORE_DIMENSIONS,
  
  // Structured Output
  SCHEMAS,
  listSchemas,
  getSchema,
  validateAgainstSchema,
  
  // Voting
  vote,
  pickLongest,
  pickBySimilarity,
};
