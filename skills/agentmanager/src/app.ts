import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import express from 'express';
import pinoHttpModule from 'pino-http';
import pino from 'pino';
import { z } from 'zod';
import { PlanRequestSchema, PlanSchema, RunRequestSchema, ToolSpecSchema, type RunError } from './types.js';
import { EnqueuePlanInvalidError, OrchestratorService, StrategyNotFoundError } from './services/orchestrator.js';
import { PlanValidationError, validatePlan } from './services/plan-validator.js';
import { ToolRegisterError } from './services/tools.js';
import { ERROR_CATALOG } from './errors/catalog.js';
import { digestOf } from './lib/utils.js';
import { getConfig } from './config.js';
import { redactEventForOutput, redactTelemetryValue } from './security/redaction.js';
import { GATEWAY_STEP_PATH, PROVIDER_ADAPTER_REQUEST_EXAMPLE, PROVIDER_ADAPTER_REQUEST_SCHEMA, PROVIDER_ADAPTER_RESPONSE_EXAMPLE, PROVIDER_ADAPTER_RESPONSE_SCHEMA } from './providers/adapter-contract.js';

const sendError = (res: express.Response, status: number, error: RunError): express.Response => res.status(status).json(error);

type ParsedRunRequest = {
  body: z.infer<typeof RunRequestSchema>;
  tokenOwner: string;
  syncTimeoutMs: number;
};

const resolveOpenApiPath = (): string => {
  const base = dirname(fileURLToPath(import.meta.url));
  const candidates = [join(base, '../openapi/openapi.json'), join(base, '../../openapi/openapi.json')];
  const found = candidates.find((p) => existsSync(p));
  if (!found) throw new Error('openapi.json not found');
  return found;
};

const tokenRequired = (): boolean => getConfig().REQUIRE_RUN_TOKEN;
const allowedTokens = (): Set<string> => new Set(getConfig().RUN_TOKENS.split(',').map((v) => v.trim()).filter(Boolean));

const parseTokenOwner = (req: express.Request): { ok: true; tokenOwner: string } | { ok: false } => {
  const token = req.header('X-Run-Token')?.trim();
  if (!tokenRequired()) return { ok: true, tokenOwner: token || 'anonymous' };
  if (!token) return { ok: false };
  const allowed = allowedTokens();
  if (!allowed.has(token)) return { ok: false };
  return { ok: true, tokenOwner: token };
};

const requireReadToken = (req: express.Request): { ok: true } | { ok: false } => {
  const token = req.header('X-Run-Token')?.trim();
  if (tokenRequired()) return token ? { ok: true } : { ok: false };
  if (getConfig().ALLOW_ANONYMOUS_READ || getConfig().NODE_ENV === 'test') return { ok: true };
  return token ? { ok: true } : { ok: false };
};

const parseRunRequest = (req: express.Request): ParsedRunRequest | { error: RunError } => {
  const parse = RunRequestSchema.safeParse(req.body);
  if (!parse.success) {
    return { error: { code: 'VALIDATION_ERROR', message: parse.error.message, retryable: false, at: 'run' } };
  }

  const token = parseTokenOwner(req);
  if (!token.ok) {
    return { error: { code: 'AUTH_INVALID_TOKEN', message: 'Missing or invalid X-Run-Token', retryable: false, at: 'auth' } };
  }

  const syncTimeoutMs = Number(req.query.timeout_ms ?? getConfig().RUN_SYNC_TIMEOUT_MS);
  return {
    body: parse.data,
    tokenOwner: token.tokenOwner,
    syncTimeoutMs
  };
};

const enqueueOrFail = (
  res: express.Response,
  orchestrator: OrchestratorService,
  parsed: ParsedRunRequest
): { run_id?: string; status?: string; ok?: boolean; dry_run?: boolean; normalized_plan?: unknown; estimated_cost?: number; estimated_latency_ms?: number; task_count?: number } | undefined => {
  try {
    return orchestrator.enqueueRun({
      userRequest: parsed.body.user_request,
      plan: parsed.body.plan,
      idempotencyKey: parsed.body.idempotency_key,
      budgetLevel: parsed.body.options?.budget_level,
      strategyHint: parsed.body.options?.strategy_hint,
      maxConcurrency: parsed.body.options?.max_concurrency,
      dryRun: parsed.body.options?.dry_run,
      planOptions: parsed.body.options,
      providerId: parsed.body.options?.provider_id,
      tokenOwner: parsed.tokenOwner
    });
  } catch (error) {
    if (error instanceof StrategyNotFoundError) {
      sendError(res, 400, { code: 'STRATEGY_NOT_FOUND', message: error.message, retryable: false, at: 'strategy_hint' });
      return undefined;
    }
    if (orchestrator.isRateLimitError(error)) {
      orchestrator.logRateLimited(parsed.tokenOwner, error.message);
      sendError(res, 429, { code: 'RATE_LIMIT', message: error.message, retryable: true, suggested_action: 'retry', at: 'run' });
      return undefined;
    }
    if (error instanceof EnqueuePlanInvalidError) {
      sendError(res, 400, { code: 'PLAN_INVALID', message: error.message, retryable: false, at: 'plan' });
      return undefined;
    }
    sendError(res, 500, { code: 'INTERNAL', message: error instanceof Error ? error.message : 'unknown', retryable: false, at: 'run' });
    return undefined;
  }
};

export const createApp = (orchestrator: OrchestratorService): express.Express => {
  const app = express();
  app.disable('x-powered-by');
  const logger = pino({ name: 'api' });
  const cachedOpenApi = Object.freeze(JSON.parse(readFileSync(resolveOpenApiPath(), 'utf8')));

  app.use(express.json({ limit: '1mb' }));
  const pinoHttp = pinoHttpModule as unknown as (opts: { logger: pino.Logger }) => express.RequestHandler;
  app.use(pinoHttp({ logger }));

  app.get('/healthz', (_req, res) => res.json({ ok: true }));
  app.get('/openapi.json', (_req, res) => res.json(cachedOpenApi));
  app.get('/v1/capabilities', (req, res) => {
    const includeDisabled = String(req.query.include_disabled ?? '').toLowerCase() === 'true';
    return res.json(orchestrator.getCapabilities(includeDisabled));
  });
  app.get('/v1/errors', (_req, res) => res.json({ errors: ERROR_CATALOG }));

  app.get('/v1/provider-adapter/schema', (_req, res) => res.json({
    schema_version: 'v1',
    request_schema: PROVIDER_ADAPTER_REQUEST_SCHEMA,
    response_schema: PROVIDER_ADAPTER_RESPONSE_SCHEMA,
    endpoints: { gateway_step_path: GATEWAY_STEP_PATH },
    examples: {
      request: PROVIDER_ADAPTER_REQUEST_EXAMPLE,
      response: PROVIDER_ADAPTER_RESPONSE_EXAMPLE
    }
  }));

  app.post('/v1/tools/register', (req, res) => {
    if (((getConfig().ENABLE_TOOL_REGISTER ?? getConfig().ENABLE_TOOL_REGISTRATION) !== '1')) {
      return sendError(res, 403, { code: 'TOOL_REGISTER_DISABLED', message: 'Tool registration is disabled', retryable: false, at: 'tools/register' });
    }

    const parse = z.array(ToolSpecSchema).safeParse(req.body?.tools ?? req.body);
    if (!parse.success) {
      return sendError(res, 400, { code: 'TOOL_SPEC_INVALID', message: parse.error.message, retryable: false, at: 'tools/register' });
    }

    try {
      return res.json(orchestrator.getTools().register(parse.data));
    } catch (error) {
      if (error instanceof ToolRegisterError) {
        const status = error.code === 'TOOL_NOT_ALLOWED' ? 403 : 400;
        return sendError(res, status, { code: error.code, message: error.message, retryable: false, at: 'tools/register' });
      }
      return sendError(res, 500, { code: 'INTERNAL', message: error instanceof Error ? error.message : 'unknown', retryable: false, at: 'tools/register' });
    }
  });

  app.get('/v1/tools', (_req, res) => res.json({ tools_version: orchestrator.getTools().getVersion(), tools: orchestrator.getTools().list() }));

  app.post('/v1/plan', (req, res) => {
    const token = parseTokenOwner(req);
    if (!token.ok) return sendError(res, 401, { code: 'AUTH_INVALID_TOKEN', message: 'Missing or invalid X-Run-Token', retryable: false, at: 'auth' });

    const parse = z.union([
      z.object({ plan: PlanSchema, options: z.record(z.any()).optional() }),
      PlanRequestSchema
    ]).safeParse(req.body);
    if (!parse.success) {
      return sendError(res, 400, { code: 'VALIDATION_ERROR', message: parse.error.message, retryable: false, at: 'plan' });
    }

    try {
      if ('user_request' in parse.data) {
        const generated = orchestrator.createPlan(parse.data.user_request, parse.data.options?.budget_level ?? 'normal', token.tokenOwner, parse.data.options?.strategy_hint, parse.data.options);
        return res.json(generated);
      }

      validatePlan(parse.data.plan, orchestrator.getTools());
      const normalizedPlan = orchestrator.normalizeClientPlan(parse.data.plan, parse.data.options?.budget_level ?? 'normal', token.tokenOwner);
      const costByTask = Object.fromEntries(normalizedPlan.tasks.map((t) => [t.name, 0.001]));
      return res.json({
        ok: true,
        normalized_plan: normalizedPlan,
        diagnostics: { dag_ok: true, schema_errors: [], unknown_tools: [], missing_tasks: [] },
        recommendations: {
          suggested_budget_level: parse.data.options?.budget_level ?? 'normal',
          suggested_max_concurrency: Math.min(8, normalizedPlan.tasks.length),
          latency_estimate_ms: normalizedPlan.tasks.length * 300,
          cost_estimate: { total_est: normalizedPlan.tasks.length * 0.001, by_task: costByTask }
        }
      });
    } catch (error) {
      if (error instanceof StrategyNotFoundError) {
        return sendError(res, 400, { code: 'STRATEGY_NOT_FOUND', message: error.message, retryable: false, at: 'strategy_hint' });
      }
      if (error instanceof PlanValidationError) {
        return sendError(res, 400, { code: 'PLAN_INVALID', message: error.message, retryable: false, at: 'plan' });
      }
      return sendError(res, 500, { code: 'INTERNAL', message: error instanceof Error ? error.message : 'unknown', retryable: false, at: 'plan' });
    }
  });

  app.post('/v1/plan/generate', (req, res) => {
    const token = parseTokenOwner(req);
    if (!token.ok) return sendError(res, 401, { code: 'AUTH_INVALID_TOKEN', message: 'Missing or invalid X-Run-Token', retryable: false, at: 'auth' });
    const parse = PlanRequestSchema.safeParse(req.body);
    if (!parse.success) {
      return sendError(res, 400, { code: 'VALIDATION_ERROR', message: parse.error.message, retryable: false, at: 'plan' });
    }
    try {
      const plan = orchestrator.createPlan(parse.data.user_request, parse.data.options?.budget_level ?? 'normal', token.tokenOwner, parse.data.options?.strategy_hint, parse.data.options);
      return res.json(plan);
    } catch (error) {
      if (error instanceof StrategyNotFoundError) {
        return sendError(res, 400, { code: 'STRATEGY_NOT_FOUND', message: error.message, retryable: false, at: 'strategy_hint' });
      }
      return sendError(res, 400, { code: 'PLAN_INVALID', message: error instanceof Error ? error.message : 'invalid plan', retryable: false, at: 'plan' });
    }
  });

  app.post('/v1/plan/validate', (req, res) => {
    const token = parseTokenOwner(req);
    if (!token.ok) return sendError(res, 401, { code: 'AUTH_INVALID_TOKEN', message: 'Missing or invalid X-Run-Token', retryable: false, at: 'auth' });

    const parse = z.object({ plan: PlanSchema }).safeParse(req.body);
    if (!parse.success) {
      return sendError(res, 400, { code: 'PLAN_INVALID', message: parse.error.message, retryable: false, at: 'plan' });
    }

    try {
      validatePlan(parse.data.plan, orchestrator.getTools());
      return res.json({ ok: true });
    } catch (error) {
      return sendError(res, 400, { code: 'PLAN_INVALID', message: error instanceof Error ? error.message : 'invalid plan', retryable: false, at: 'plan' });
    }
  });

  app.post('/v1/run', (req, res) => {
    const parsed = parseRunRequest(req);
    if ('error' in parsed) return sendError(res, parsed.error.code === 'AUTH_INVALID_TOKEN' ? 401 : 400, parsed.error);
    const response = enqueueOrFail(res, orchestrator, parsed);
    if (!response) return;
    if (response.dry_run) return res.status(200).json(response);
    return res.status(202).json(response);
  });

  app.post('/v1/run/sync', async (req, res) => {
    const parsed = parseRunRequest(req);
    if ('error' in parsed) return sendError(res, parsed.error.code === 'AUTH_INVALID_TOKEN' ? 401 : 400, parsed.error);

    const response = enqueueOrFail(res, orchestrator, parsed);
    if (!response) return;
    if (response.dry_run) return res.status(200).json(response);

    const waitAbort = new AbortController();
    req.on('close', () => waitAbort.abort());

    try {
      const run = await orchestrator.waitForCompletion(response.run_id!, parsed.syncTimeoutMs, waitAbort.signal);
      return res.json(run);
    } catch (error) {
      if (typeof error === 'object' && error && 'code' in error && 'message' in error) {
        const typed = error as RunError;
        const status = typed.code === 'RUN_SYNC_TIMEOUT' ? 408 : 499;
        return sendError(res, status, typed);
      }
      return sendError(res, 500, { code: 'INTERNAL', message: error instanceof Error ? error.message : 'unknown', retryable: false, at: 'run/sync' });
    }
  });

  app.get('/v1/runs', (req, res) => {
    const token = parseTokenOwner(req);
    if (!token.ok) return sendError(res, 401, { code: 'AUTH_INVALID_TOKEN', message: 'Missing or invalid X-Run-Token', retryable: false, at: 'auth' });

    const limitRaw = Number(req.query.limit ?? '50');
    const limit = Math.max(1, Math.min(200, Number.isFinite(limitRaw) ? limitRaw : 50));
    const status = typeof req.query.status === 'string' ? req.query.status as 'queued' | 'running' | 'succeeded' | 'failed' : undefined;
    const owner = tokenRequired() ? token.tokenOwner : (typeof req.query.owner === 'string' ? req.query.owner : token.tokenOwner);
    return res.json(orchestrator.listRuns({ owner, status, limit, cursor: typeof req.query.cursor === 'string' ? req.query.cursor : undefined }));
  });

  app.post('/v1/run/:id/cancel', (req, res) => {
    const token = parseTokenOwner(req);
    if (!token.ok) return sendError(res, 401, { code: 'AUTH_INVALID_TOKEN', message: 'Missing or invalid X-Run-Token', retryable: false, at: 'auth' });

    const run = orchestrator.cancelRun(req.params.id);
    if (!run) return sendError(res, 404, { code: 'RUN_NOT_FOUND', message: 'Run not found', retryable: false, at: req.params.id });
    return res.json(run);
  });

  app.get('/v1/run/:id', (req, res) => {
    const token = requireReadToken(req);
    if (!token.ok) return sendError(res, 401, { code: 'AUTH_INVALID_TOKEN', message: 'Missing or invalid X-Run-Token', retryable: false, at: 'auth' });

    const run = orchestrator.getRun(req.params.id);
    if (!run) return sendError(res, 404, { code: 'RUN_NOT_FOUND', message: 'Run not found', retryable: false, at: req.params.id });
    return res.json(run);
  });

  app.get('/v1/run/:id/stream', (req, res) => {
    const token = requireReadToken(req);
    if (!token.ok) return sendError(res, 401, { code: 'AUTH_INVALID_TOKEN', message: 'Missing or invalid X-Run-Token', retryable: false, at: 'auth' });

    const run = orchestrator.getRun(req.params.id);
    if (!run) return sendError(res, 404, { code: 'RUN_NOT_FOUND', message: 'Run not found', retryable: false, at: req.params.id });

    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.flushHeaders?.();

    const heartbeatMs = getConfig().SSE_HEARTBEAT_MS;
    const afterQuery = Number(req.query.after ?? '0');
    const lastEventHeader = Number(req.header('Last-Event-ID') ?? '0');
    const startAfter = Math.max(0, Number.isFinite(afterQuery) ? afterQuery : 0, Number.isFinite(lastEventHeader) ? lastEventHeader : 0);
    let lastSeq = startAfter;
    let lastActivity = Date.now();
    let timer: NodeJS.Timeout | undefined;

    const sendEvents = (): void => {
      const latest = orchestrator.getRun(req.params.id);
      if (!latest) return;
      const events = latest.logs.filter((e) => e.seq > lastSeq);
      if (events.length > 0) {
        for (const event of events) {
          res.write(`id: ${event.seq}\n`);
          res.write(`data: ${JSON.stringify(redactEventForOutput(event as unknown as Record<string, unknown>))}\n\n`);
        }
        lastSeq = events[events.length - 1].seq;
        lastActivity = Date.now();
      } else if (latest.status !== 'succeeded' && latest.status !== 'failed' && Date.now() - lastActivity >= heartbeatMs) {
        res.write(': ping\n\n');
        lastActivity = Date.now();
      }

      if (latest.status === 'succeeded' || latest.status === 'failed') {
        res.write(`data: ${JSON.stringify({ ts: Date.now(), type: 'stream_complete', run_id: latest.id, data: { status: latest.status } })}\n\n`);
        if (timer) clearInterval(timer);
        res.end();
      }
    };

    sendEvents();
    timer = setInterval(sendEvents, 200);
    req.on('close', () => {
      if (timer) clearInterval(timer);
      res.end();
    });
  });

  app.get('/v1/run/:id/report', (req, res) => {
    const token = requireReadToken(req);
    if (!token.ok) return sendError(res, 401, { code: 'AUTH_INVALID_TOKEN', message: 'Missing or invalid X-Run-Token', retryable: false, at: 'auth' });

    const run = orchestrator.getRun(req.params.id);
    if (!run) return sendError(res, 404, { code: 'RUN_NOT_FOUND', message: 'Run not found', retryable: false, at: req.params.id });

    return res.json({
      run_id: run.id,
      status: run.status,
      created_at: run.created_at,
      plan_summary: {
        mode: run.plan.mode,
        rationale: run.plan.rationale,
        tasks: run.plan.tasks.map((t) => ({ name: t.name, agent: t.agent, depends_on: t.depends_on, tools_allowed: t.tools_allowed }))
      },
      results_by_task: redactTelemetryValue(run.results_by_task),
      events: { base: run.logs_base, count: run.logs.length, items: run.logs.map((e) => redactEventForOutput(e as unknown as Record<string, unknown>)) },
      metrics: run.metrics,
      error: run.error,
      final_output: run.final_output,
      output_digest: run.output_digest
    });
  });

  app.get('/v1/run/:id/replay', (req, res) => {
    const token = requireReadToken(req);
    if (!token.ok) return sendError(res, 401, { code: 'AUTH_INVALID_TOKEN', message: 'Missing or invalid X-Run-Token', retryable: false, at: 'auth' });
    const run = orchestrator.getRun(req.params.id);
    if (!run) return sendError(res, 404, { code: 'RUN_NOT_FOUND', message: 'Run not found', retryable: false, at: req.params.id });
    return res.json({
      run: { id: run.id, created_at: run.created_at, status: run.status, token_owner: run.token_owner },
      plan_digest: digestOf(run.plan),
      events: run.logs.map((e) => redactEventForOutput(e as unknown as Record<string, unknown>)),
      results_index: redactTelemetryValue(Object.fromEntries(Object.entries(run.results_by_task).map(([k, v]) => [k, { digest_hash: v.digest_hash, payload: v.payload }])))
    });
  });

  app.post('/v1/run/:id/task/:name/inject', (req, res) => {
    const token = parseTokenOwner(req);
    if (!token.ok) return sendError(res, 401, { code: 'AUTH_INVALID_TOKEN', message: 'Missing or invalid X-Run-Token', retryable: false, at: 'auth' });
    const payload = req.body?.payload;
    const meta = req.body?.meta;
    const updated = orchestrator.injectTaskResult(req.params.id, req.params.name, payload, meta);
    if (!updated) return sendError(res, 404, { code: 'RUN_NOT_FOUND', message: 'Run not found', retryable: false, at: req.params.id });
    return res.json({ ok: true, run_id: updated.id, task: req.params.name });
  });

  app.get('/v1/run/:id/events', (req, res) => {
    const token = requireReadToken(req);
    if (!token.ok) return sendError(res, 401, { code: 'AUTH_INVALID_TOKEN', message: 'Missing or invalid X-Run-Token', retryable: false, at: 'auth' });

    const after = Number(req.query.after ?? '0');
    const result = orchestrator.getRunEvents(req.params.id, Number.isFinite(after) ? after : 0);
    if (!result) return sendError(res, 404, { code: 'RUN_NOT_FOUND', message: 'Run not found', retryable: false, at: req.params.id });
    return res.json({ ...result, events: result.events.map((e) => redactEventForOutput(e as unknown as Record<string, unknown>)) });
  });

  return app;
};
