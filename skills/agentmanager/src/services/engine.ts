import AjvModule from 'ajv';
import pino from 'pino';
import type { Plan, Run, RunError, TaskSpec } from '../types.js';
import { RunSchema } from '../types.js';
import { digestOf, nowMs, sleep, stableStringify } from '../lib/utils.js';
import { summarize } from '../lib/summarize.js';
import { appendRunEvent } from '../lib/events.js';
import { getConfig } from '../config.js';
import { type ModelTier, downgradeTier, estimateCost, inferTokens, modelName, upgradeTier } from './model-tier.js';
import type { PricingPolicy } from './pricing-registry.js';
import { ToolRegistry } from './tools.js';
import type { LLMMessage, LLMProvider, LLMRoundResult } from '../providers/llm-provider.js';
import { createProviderRegistry } from '../providers/index.js';
import { ProviderRegistry } from '../providers/provider-registry.js';

export type RunOptions = { maxConcurrency?: number; tokenOwner: string; pricing: PricingPolicy; signal?: AbortSignal; providerId?: string };

const Ajv = (AjvModule as unknown as { new (opts: { strict: boolean }): any });
const ajv = new Ajv({ strict: false });
const MAX_ARTIFACT_BYTES_PER_RUN = getConfig().MAX_ARTIFACT_BYTES_PER_RUN;
const MAX_DEP_PAYLOAD_BYTES = getConfig().MAX_DEP_PAYLOAD_BYTES;

const tierFromModel = (model: string): ModelTier => {
  if (model.includes('premium')) return 'premium';
  if (model.includes('standard')) return 'standard';
  return 'cheap';
};

export class ExecutionEngine {
  private readonly logger = pino({ name: 'execution-engine' });

  constructor(
    private readonly tools: ToolRegistry,
    providerSource: ProviderRegistry | LLMProvider = createProviderRegistry()
  ) {
    if (providerSource instanceof ProviderRegistry) {
      this.providerRegistry = providerSource;
      return;
    }
    const registry = new ProviderRegistry();
    registry.register(providerSource);
    this.providerRegistry = registry;
  }

  private readonly providerRegistry: ProviderRegistry;

  async executeRun(run: Run, opts: RunOptions): Promise<Run> {
    const start = nowMs();
    run.status = 'running';
    run.progress = this.progress(run, new Set());

    try {
      await this.executeWithController(run, opts);
      run.status = 'succeeded';
    } catch (err) {
      const typed = this.toRunError(err);
      if (typed.code === 'RUN_CANCELLED') {
        run.status = 'failed';
        run.error = typed;
      } else if (run.plan.mode === 'multi') {
        run.metrics.fallback = true;
        this.pushEvent(run, 'fallback_start', { reason: typed.code });
        const fallbackTask = run.plan.tasks.find((t) => t.agent === 'executor') ?? run.plan.tasks[0];
        run.plan = {
          ...run.plan,
          mode: 'single',
          tasks: [{ ...fallbackTask, name: 'single_executor', depends_on: [], parallel_group: null }],
          rationale: `${run.plan.rationale} Fallback to single executor.`
        };
        run.results_by_task = {};
        run.progress = { total_tasks: 1, completed_tasks: 0, running_tasks: 0, queued_tasks: 1 };
        run.error = undefined;
        try {
          await this.executeWithController(run, opts);
          run.status = 'succeeded';
          this.pushEvent(run, 'fallback_end', { status: 'succeeded' });
        } catch (fallbackErr) {
          run.status = 'failed';
          run.error = this.toRunError(fallbackErr);
          this.pushEvent(run, 'fallback_end', { status: 'failed', code: run.error.code });
        }
      } else {
        run.status = 'failed';
        run.error = typed;
      }
    }

    if (run.status === 'succeeded') {
      try {
        const finalOutput = this.buildFinalOutput(run);
        this.validateFinalOutput(run.plan, finalOutput);
        run.final_output = finalOutput;
        run.output_digest = digestOf(finalOutput);
      } catch (err) {
        run.status = 'failed';
        run.error = this.toRunError(err, 'final_output');
      }
    }

    run.metrics.cost_estimate = run.metrics.cost_estimate_committed;
    run.metrics.total_ms = nowMs() - start;
    run.metrics.cost_breakdown = Object.fromEntries(
      Object.entries(run.results_by_task).map(([name, result]) => [
        name,
        {
          cost_est: result.meta?.cost_est ?? 0,
          tier: result.meta?.tier ?? 'unknown',
          tool_calls: result.meta?.tool_calls ?? 0
        }
      ])
    );
    run.progress = this.progress(run, new Set());
    this.pushEvent(run, 'run_complete', { status: run.status, cost_estimate: run.metrics.cost_estimate });
    return RunSchema.parse(run);
  }

  private async executeWithController(run: Run, opts: RunOptions): Promise<void> {
    const runningTasks = new Set<string>();
    const internalController = new AbortController();
    const signal = opts.signal ? AbortSignal.any([opts.signal, internalController.signal]) : internalController.signal;

    try {
      if (signal.aborted) throw this.cancelError();
      await this.executePlan(run, opts, signal, runningTasks, internalController);
    } catch (error) {
      internalController.abort();
      throw error;
    }
  }

  private async executePlan(
    run: Run,
    opts: RunOptions,
    signal: AbortSignal,
    runningTasks: Set<string>,
    internalController: AbortController
  ): Promise<void> {
    const tasks = run.plan.tasks;
    const completed = new Set<string>();
    const inFlight = new Map<string, Promise<void>>();
    const maxConcurrency = opts.maxConcurrency ?? 8;

    try {
      while (completed.size < tasks.length) {
        if (signal.aborted) throw this.cancelError();
        if (nowMs() - run.created_at > run.plan.budget.max_latency_ms) {
          this.pushEvent(run, 'budget_violation', { code: 'BUDGET_LATENCY' });
          throw this.err('BUDGET_LATENCY', 'Exceeded max latency budget', false, 'replan', 'budget');
        }

        const ready = tasks.filter((t) => !completed.has(t.name) && !runningTasks.has(t.name) && t.depends_on.every((d) => completed.has(d)));

        if (ready.length === 0 && inFlight.size === 0) {
          throw this.err('DAG_DEADLOCK', 'No ready tasks and no running tasks', false, undefined, 'engine');
        }

        while (ready.length > 0 && inFlight.size < maxConcurrency) {
          const task = ready.shift();
          if (!task) break;
          runningTasks.add(task.name);
          run.progress = this.progress(run, runningTasks);
          const job = this.executeTask(task, run, opts, signal)
            .then(() => {
              completed.add(task.name);
            })
            .finally(() => {
              runningTasks.delete(task.name);
              inFlight.delete(task.name);
              run.progress = this.progress(run, runningTasks);
            });
          inFlight.set(task.name, job);
        }

        if (inFlight.size > 0) {
          await Promise.race(inFlight.values());
        }

        this.checkBudget(run, 'budget');
      }
    } catch (error) {
      internalController.abort();
      await Promise.allSettled([...inFlight.values()]);
      throw error;
    } finally {
      await Promise.allSettled([...inFlight.values()]);
    }
  }

  private async executeTask(task: TaskSpec, run: Run, opts: RunOptions, signal: AbortSignal): Promise<void> {
    if (run.injected_tasks?.[task.name]) {
      const injected = run.injected_tasks[task.name];
      const digestHash = digestOf(injected.payload);
      run.results_by_task[task.name] = {
        payload: injected.payload,
        digest_text: summarize(injected.payload),
        digest_hash: digestHash,
        digest: digestHash,
        evidence: ['task_injected'],
        meta: { model: 'injected', tier: 'cheap', tokens_est: 0, cost_est: 0, tool_calls: 0 }
      };
      run.metrics.steps_executed_total += 1;
      this.pushEvent(run, 'task_injected', { meta: injected.meta }, task.name);
      return;
    }

    if (run.metrics.steps_executed_total + 1 > run.plan.budget.max_steps) {
      throw this.err('BUDGET_STEPS', 'Exceeded max steps', false, 'replan', task.name);
    }

    let tier = this.capTierByOwner(tierFromModel(task.model), opts.pricing.maxTierCap);
    let attempts = 0;

    while (attempts < 3) {
      if (signal.aborted) throw this.cancelError();
      const started = nowMs();
      attempts += 1;
      this.pushEvent(run, 'task_start', {}, task.name);
      try {
        const attemptResult = await this.taskWithTimeout(task, run, opts, tier, signal, attempts);
        run.metrics.cost_estimate_committed = Number((run.metrics.cost_estimate_committed + attemptResult.attempt_cost).toFixed(6));
        run.metrics.cost_estimate = run.metrics.cost_estimate_committed;

        if (task.agent === 'verifier' && attemptResult.payload?.verified === false) {
          throw this.err('VERIFIER_FAILED', 'Verifier rejected results', true, 'upgrade', task.name);
        }

        if (signal.aborted) throw this.cancelError();

        const digestHash = digestOf(attemptResult.payload);
        run.results_by_task[task.name] = {
          payload: attemptResult.payload,
          digest_text: summarize(attemptResult.payload),
          digest_hash: digestHash,
          digest: digestHash,
          evidence: attemptResult.evidence,
          meta: {
            model: modelName(tier),
            tier,
            tokens_est: attemptResult.tokens_estimate,
            cost_est: attemptResult.attempt_cost,
            tool_calls: attemptResult.tool_calls
          }
        };
        run.metrics.tasks_ms[task.name] = nowMs() - started;
        run.metrics.steps_executed_total += 1;
        this.pushEvent(run, 'task_end', { cost_est: attemptResult.attempt_cost }, task.name);
        return;
      } catch (error) {
        const typed = this.toRunError(error, task.name);
        if (typed.code === 'RUN_CANCELLED') throw typed;
        if (typed.code === 'OUTBOUND_PAYLOAD_REJECTED') {
          this.pushEvent(run, 'outbound_payload_rejected', { code: typed.code, at: task.name }, task.name);
        }

        run.metrics.retries += 1;
        const failedCost = this.extractAttemptCost(error);
        if (failedCost > 0) {
          run.metrics.cost_estimate_failed = Number((run.metrics.cost_estimate_failed + failedCost).toFixed(6));
        }

        this.pushEvent(run, 'task_retry', { reason: typed.code, attempt: attempts, failed_cost: failedCost }, task.name);

        if (this.canUpgrade(typed, run)) {
          const next = upgradeTier(tier, opts.pricing.maxTierCap);
          if (next) {
            tier = next;
            run.metrics.model_upgrades += 1;
            this.checkBudget(run, task.name);
            continue;
          }
        }

        if (typed.suggested_action === 'downgrade') {
          const down = downgradeTier(tier);
          if (down) {
            tier = down;
            this.checkBudget(run, task.name);
            continue;
          }
        }

        if (typed.retryable && attempts < 3) {
          const delayMs = 20 * Math.pow(2, attempts - 1);
          await sleep(delayMs, signal);
          continue;
        }
        throw typed;
      }
    }
  }

  private async taskWithTimeout(
    task: TaskSpec,
    run: Run,
    opts: RunOptions,
    tier: ModelTier,
    signal: AbortSignal,
    attempt: number
  ): Promise<{ payload: Record<string, unknown>; evidence?: string[]; tokens_estimate: number; attempt_cost: number; tool_calls: number }> {
    const timeoutMs = task.timeout_ms ?? 30_000;
    const renderedInput = this.renderTaskInput(task.input);
    const depContexts = task.depends_on
      .map((n) => {
        const r = run.results_by_task[n];
        if (!r) return null;
        const serialized = stableStringify(r.payload);
        const bytes = Buffer.byteLength(serialized, 'utf8');
        if (bytes > MAX_DEP_PAYLOAD_BYTES) {
          const clipped = serialized.slice(0, MAX_DEP_PAYLOAD_BYTES);
          this.pushEvent(run, 'dependency_truncated', { task: n, original_bytes: bytes, truncated_bytes: MAX_DEP_PAYLOAD_BYTES }, task.name);
          return { task: n, digest: r.digest_text, payload: clipped, truncated: true };
        }
        return { task: n, digest: r.digest_text, payload: r.payload, truncated: false };
      })
      .filter((v): v is NonNullable<typeof v> => Boolean(v));
    const deps = depContexts.map((ctx) => ctx.digest);
    const tokens = inferTokens(renderedInput, task.max_output_tokens);
    const baseAttemptCost = estimateCost(tokens, tier, opts.pricing.tierPricePerToken);

    const action = async () => {
      if (signal.aborted) throw this.cancelError();
      let toolCalls = 0;
      let toolCost = 0;
      let latestTokens = tokens;
      let attemptCost = baseAttemptCost;

      try {
      const messages: LLMMessage[] = [
        { role: 'system', content: task.system_prompt ?? `You are ${task.agent} using ${modelName(tier)}.` },
        { role: 'user', content: renderedInput }
      ];
      if (depContexts.length > 0) {
        messages.push({
          role: 'assistant',
          content: `Dependency results: ${JSON.stringify(depContexts)}`
        });
      }

      const loopLimit = Math.max(1, Math.min(8, run.plan.budget.max_tool_calls + 2));
      for (let step = 1; step <= loopLimit; step += 1) {
        const requestId = `${run.id}:${task.name}:a${attempt}:s${step}`;
        if (signal.aborted) throw this.cancelError();
        if (nowMs() - run.created_at > run.plan.budget.max_latency_ms) {
          this.pushEvent(run, 'budget_violation', { code: 'BUDGET_LATENCY' }, task.name);
          throw this.err('BUDGET_LATENCY', 'Exceeded max latency budget', false, 'replan', task.name);
        }

        const provider = this.providerRegistry.resolve({ taskProviderId: task.provider_id, runProviderId: opts.providerId });
        const supportedTools = task.tools_allowed
          .map((name) => this.tools.getSpec(name))
          .filter((spec): spec is NonNullable<typeof spec> => Boolean(spec));

        this.pushEvent(run, 'llm_step_start', { step, provider: provider.id, request_id: requestId }, task.name);
        this.pushEvent(run, 'llm_round_start', { step, provider: provider.id }, task.name);
        const providerResult: LLMRoundResult = provider.executeRound
          ? await provider.executeRound({
              run_id: run.id,
              runId: run.id,
              task,
              taskName: task.name,
              step,
              attempt,
              requestId,
              tier,
              signal,
              tokenOwner: opts.tokenOwner,
              dependencyDigests: deps,
              messages,
              tools: supportedTools
            })
          : await (async () => {
              if (!provider.step) throw this.err('PROVIDER_NOT_IMPLEMENTED', `Provider ${provider.id} does not support executeRound`, false, undefined, task.name);
              const legacy = await provider.step(task, { run_id: run.id, runId: run.id, task, taskName: task.name, step, attempt, requestId, tier, signal, tokenOwner: opts.tokenOwner, dependencyDigests: deps, messages, tools: supportedTools });
              if (legacy.type === 'final') {
                return {
                  output_json: legacy.payload,
                  usage: {
                    output_tokens: legacy.tokens_actual ?? legacy.tokens_est
                  },
                  model: task.model
                };
              }
              return {
                tool_calls: legacy.tool_calls.map((call) => ({ call_id: call.id, name: call.name, arguments: call.args })),
                usage: {
                  output_tokens: legacy.tokens_actual ?? legacy.tokens_est
                },
                model: task.model
              };
            })();
        if (signal.aborted) throw this.cancelError();

        const usedTokens = (providerResult.usage?.input_tokens ?? 0) + (providerResult.usage?.output_tokens ?? 0);
        if (usedTokens > 0) {
          latestTokens = usedTokens;
        }

        if (!providerResult.tool_calls || providerResult.tool_calls.length === 0) {
          this.pushEvent(run, 'llm_step_final', { step }, task.name);
          this.pushEvent(run, 'llm_round_final', { step }, task.name);
          const payload = providerResult.output_json
            ?? (providerResult.output_text ? { output_text: providerResult.output_text } : { task: task.name, provider: provider.id, model: providerResult.model ?? modelName(tier) });
          return {
            payload: { ...payload, model: providerResult.model ?? modelName(tier) },
            evidence: deps,
            tokens_estimate: latestTokens,
            attempt_cost: Number((baseAttemptCost + toolCost).toFixed(6)),
            tool_calls: toolCalls
          };
        }

        this.pushEvent(run, 'llm_step_tool_calls', { step, count: providerResult.tool_calls.length }, task.name);
        this.pushEvent(run, 'llm_round_tool_calls', { step, count: providerResult.tool_calls.length }, task.name);
        for (const call of providerResult.tool_calls) {
          if (signal.aborted) throw this.cancelError();
          if (!task.tools_allowed.includes(call.name)) {
            throw this.err('TOOL_NOT_ALLOWED', `Tool ${call.name} is not allowed for task`, false, undefined, task.name);
          }
          if (!this.tools.isToolAllowed(call.name)) {
            throw this.err('TOOL_NOT_ALLOWED', `Tool ${call.name} is disallowed by registry policy`, false, undefined, task.name);
          }
          const toolSpec = this.tools.getSpec(call.name);
          if (!toolSpec) {
            throw this.err('TOOL_NOT_ALLOWED', `Tool ${call.name} is not registered`, false, undefined, task.name);
          }
          const validateArgs = ajv.compile(toolSpec.input_schema);
          const args = call.arguments ?? {};
          if (!validateArgs(args)) {
            throw this.err('TOOL_ARGS_INVALID', ajv.errorsText(validateArgs.errors), false, undefined, task.name);
          }

          const bytesLock = {
            tryReserve: (delta: number): boolean => {
              if (run.metrics.artifacts_bytes + delta > MAX_ARTIFACT_BYTES_PER_RUN) return false;
              run.metrics.artifacts_bytes += delta;
              return true;
            },
            rollback: (delta: number): void => {
              run.metrics.artifacts_bytes = Math.max(0, run.metrics.artifacts_bytes - delta);
            }
          };

          this.pushEvent(run, 'tool_call_requested', { step, tool_name: call.name, tool_call_id: call.call_id }, task.name);
          this.pushEvent(run, 'tool_call_start', { step, tool_name: call.name, tool_call_id: call.call_id }, task.name);
          this.pushEvent(run, 'tool_call_started', { step, tool_name: call.name, tool_call_id: call.call_id }, task.name);
          const startedTool = nowMs();
          const toolRes = await this.tools.call(call.name, args, {
            runId: run.id,
            tokenOwner: opts.tokenOwner,
            signal,
            maxArtifactBytes: MAX_ARTIFACT_BYTES_PER_RUN,
            getArtifactsBytes: () => run.metrics.artifacts_bytes,
            tryReserveArtifactsBytes: bytesLock.tryReserve,
            rollbackArtifactsBytes: bytesLock.rollback
          });

          toolCalls += 1;
          run.metrics.tool_calls += 1;
          const inc = estimateCost(toolRes.tokens_used, tier, opts.pricing.tierPricePerToken);
          toolCost = Number((toolCost + inc).toFixed(6));
          const outputError = (toolRes.output as { error?: string } | undefined)?.error;
          if (outputError === 'ARTIFACT_LIMIT') {
            this.pushEvent(run, 'artifact_limit', { tool_name: call.name }, task.name);
          }
          if (!toolRes.ok) {
            this.pushEvent(run, 'tool_call_failed', {
              step,
              tool_name: call.name,
              tool_call_id: call.call_id,
              latency_ms: nowMs() - startedTool,
              error_code: outputError ?? 'TOOL_FAILED',
              retryable: outputError === 'TOOL_TIMEOUT'
            }, task.name);
          }
          this.pushEvent(run, 'tool_call_end', { step, tool_name: call.name, tool_call_id: call.call_id, ok: toolRes.ok }, task.name);
          this.pushEvent(run, 'tool_call_finished', {
            step,
            tool_name: call.name,
            tool_call_id: call.call_id,
            ok: toolRes.ok,
            latency_ms: nowMs() - startedTool,
            retryable: outputError === 'TOOL_TIMEOUT'
          }, task.name);
          messages.push({ role: 'tool', name: call.name, tool_call_id: call.call_id, content: stableStringify(toolRes.output) });
          this.checkBudget(run, task.name);
        }
      }

      throw this.err('LLM_LOOP_LIMIT', 'Exceeded LLM tool-calling loop limit', false, 'replan', task.name);
      } catch (error) {
        const typed = (typeof error === 'object' && error && 'code' in error)
          ? error as RunError & { attempt_cost?: number }
          : this.err('INTERNAL', error instanceof Error ? error.message : 'unknown', false, undefined, task.name) as RunError & { attempt_cost?: number };
        typed.attempt_cost = Number((baseAttemptCost + toolCost).toFixed(6));
        throw typed;
      }
    };

    const timeoutPromise = (async () => {
      await sleep(timeoutMs, signal);
      const err = this.err('TASK_TIMEOUT', `Task timeout > ${timeoutMs}ms`, true, 'retry', task.name) as RunError & { attempt_cost?: number };
      err.attempt_cost = baseAttemptCost;
      throw err;
    })();

    return Promise.race([action(), timeoutPromise]);
  }

  private checkBudget(run: Run, at: string): void {
    if (run.metrics.tool_calls > run.plan.budget.max_tool_calls) {
      this.pushEvent(run, 'budget_violation', { code: 'BUDGET_TOOL_CALLS' }, at);
      throw this.err('BUDGET_TOOL_CALLS', 'Exceeded max tool calls', false, 'downgrade', at);
    }
    const totalSpentCost = Number((run.metrics.cost_estimate_committed + run.metrics.cost_estimate_failed).toFixed(6));
    if (totalSpentCost > run.plan.budget.max_cost_estimate) {
      this.pushEvent(run, 'budget_violation', { code: 'BUDGET_COST' }, at);
      throw this.err('BUDGET_COST', `Exceeded max cost estimate (total_spent=${totalSpentCost})`, false, 'downgrade', at);
    }
  }

  private renderTaskInput(input: TaskSpec['input']): string {
    if (typeof input === 'string') return input;
    const parts = [
      input.text ? `text: ${input.text}` : '',
      input.instructions ? `instructions: ${input.instructions}` : '',
      input.user_request_ref ? `user_request_ref: ${input.user_request_ref}` : '',
      input.refs?.length ? `refs: ${stableStringify(input.refs)}` : '',
      input.payload !== undefined ? `payload: ${stableStringify(input.payload)}` : ''
    ].filter(Boolean);
    return parts.join('\n');
  }

  private buildFinalOutput(run: Run): unknown {
    if (run.plan.mode === 'single') {
      return run.results_by_task.single_executor?.payload ?? Object.values(run.results_by_task)[0]?.payload ?? { summary: 'no output' };
    }

    const verifier = run.results_by_task.verifier?.payload;
    if ((verifier as { summary?: unknown } | undefined)?.summary) return (verifier as { summary: unknown }).summary;
    if (verifier) return verifier;
    return {
      summary: 'Completed multi-agent run',
      details: Object.fromEntries(Object.entries(run.results_by_task).map(([k, v]) => [k, v.payload]))
    };
  }

  private validateFinalOutput(plan: Plan, finalOutput: unknown): void {
    if (plan.output_contract.type !== 'json') return;
    if (!plan.output_contract.schema) return;
    const validate = ajv.compile(plan.output_contract.schema);
    if (!validate(finalOutput)) {
      throw this.err('OUTPUT_CONTRACT_FAIL', ajv.errorsText(validate.errors), true, 'upgrade', 'final_output');
    }
  }

  private canUpgrade(error: RunError, run: Run): boolean {
    const upgradeCodes = new Set(['MODEL_TOO_WEAK', 'VERIFIER_FAILED', 'OUTPUT_CONTRACT_FAIL', 'JSON_PARSE_FAIL']);
    if (!upgradeCodes.has(error.code) && error.suggested_action !== 'upgrade') return false;
    return run.metrics.model_upgrades < run.plan.budget.max_model_upgrades;
  }

  private capTierByOwner(tier: ModelTier, cap: ModelTier): ModelTier {
    const order: ModelTier[] = ['cheap', 'standard', 'premium'];
    return order.indexOf(tier) <= order.indexOf(cap) ? tier : cap;
  }

  private progress(run: Run, runningTasks: Set<string>): Run['progress'] {
    const total = run.plan.tasks.length;
    const completed = Object.keys(run.results_by_task).length;
    const running = runningTasks.size;
    return {
      total_tasks: total,
      completed_tasks: completed,
      running_tasks: running,
      queued_tasks: Math.max(0, total - completed - running)
    };
  }

  private pushEvent(run: Run, type: string, data?: Record<string, unknown>, taskName?: string): void {
    appendRunEvent(run, type, data, taskName);
  }

  private extractAttemptCost(error: unknown): number {
    if (typeof error === 'object' && error && 'attempt_cost' in error) {
      const val = (error as { attempt_cost?: unknown }).attempt_cost;
      if (typeof val === 'number') return val;
    }
    return 0;
  }

  private toRunError(err: unknown, at?: string): RunError {
    if (typeof err === 'object' && err && 'code' in err && 'message' in err) {
      const runError = err as RunError;
      if (runError.code === 'ABORT_ERR') {
        return { code: 'RUN_CANCELLED', message: 'Run cancelled', retryable: false, at: 'cancel' };
      }
      return { ...runError, at: runError.at ?? at };
    }
    if (err instanceof Error && err.name === 'AbortError') {
      return { code: 'RUN_CANCELLED', message: 'Run cancelled', retryable: false, at: 'cancel' };
    }
    return this.err('INTERNAL', err instanceof Error ? err.message : stableStringify(err), false, undefined, at);
  }

  private err(code: string, message: string, retryable: boolean, suggested_action?: RunError['suggested_action'], at?: string): RunError {
    this.logger.error({ code, message, retryable, suggested_action, at }, 'run error');
    return { code, message, retryable, suggested_action, at };
  }

  private cancelError(): RunError {
    return { code: 'RUN_CANCELLED', message: 'Run cancelled', retryable: false, at: 'cancel' };
  }
}
