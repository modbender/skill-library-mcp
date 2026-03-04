import { setTimeout as delay } from 'node:timers/promises';
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, isAbsolute, join, normalize, relative } from 'node:path';
import { getConfig, getToolAuth } from '../config.js';
import { safeFetch } from '../lib/safe-fetch.js';
import { ToolSpecSchema, type ToolSpec } from '../types.js';

export type ToolContext = {
  runId: string;
  tokenOwner: string;
  signal?: AbortSignal;
  maxArtifactBytes?: number;
  getArtifactsBytes?: () => number;
  tryReserveArtifactsBytes?: (delta: number) => boolean;
  rollbackArtifactsBytes?: (delta: number) => void;
};
export type ToolCallResult = { ok: boolean; output: unknown; tokens_used: number };
export type ToolHandler = (input: any, ctx: ToolContext) => Promise<ToolCallResult>;

type ToolRegisterErrorCode = 'TOOL_NOT_ALLOWED' | 'TOOL_SPEC_INVALID';

export class ToolRegisterError extends Error {
  readonly retryable = false;
  readonly at = 'tools/register';

  constructor(readonly code: ToolRegisterErrorCode, message: string) {
    super(message);
  }
}

const allowedCharRegex = /^[0-9\s+\-*/().]+$/;

const tokenize = (expr: string): string[] => expr.match(/\d+(?:\.\d+)?|[()+\-*/]/g) ?? [];

const evaluateArithmetic = (expression: string): number => {
  const tokens = tokenize(expression);
  if (tokens.length === 0) throw new Error('empty expression');
  const output: string[] = [];
  const ops: string[] = [];
  const prec: Record<string, number> = { '+': 1, '-': 1, '*': 2, '/': 2 };

  for (const tk of tokens) {
    if (/^\d/.test(tk)) {
      output.push(tk);
      continue;
    }
    if (tk in prec) {
      while (ops.length && ops[ops.length - 1] in prec && prec[ops[ops.length - 1]] >= prec[tk]) {
        output.push(ops.pop() as string);
      }
      ops.push(tk);
      continue;
    }
    if (tk === '(') {
      ops.push(tk);
      continue;
    }
    if (tk === ')') {
      while (ops.length && ops[ops.length - 1] !== '(') {
        output.push(ops.pop() as string);
      }
      if (ops.pop() !== '(') throw new Error('mismatched parentheses');
    }
  }

  while (ops.length) {
    const op = ops.pop() as string;
    if (op === '(' || op === ')') throw new Error('mismatched parentheses');
    output.push(op);
  }

  const stack: number[] = [];
  for (const tk of output) {
    if (/^\d/.test(tk)) {
      stack.push(Number(tk));
      continue;
    }
    const b = stack.pop();
    const a = stack.pop();
    if (a === undefined || b === undefined) throw new Error('bad expression');
    if (tk === '+') stack.push(a + b);
    if (tk === '-') stack.push(a - b);
    if (tk === '*') stack.push(a * b);
    if (tk === '/') stack.push(a / b);
  }

  if (stack.length !== 1 || Number.isNaN(stack[0])) throw new Error('invalid result');
  return stack[0];
};

const isPathAllowed = (rawPath: string, baseDir: string): { ok: true; relativePath: string; fullPath: string } | { ok: false } => {
  if (!rawPath || isAbsolute(rawPath) || rawPath.includes('..') || rawPath.includes('\\')) {
    return { ok: false };
  }

  const normalized = normalize(rawPath).replace(/^\/+/, '');
  if (!normalized || normalized === '.' || normalized.startsWith('..') || normalized.includes('\\')) {
    return { ok: false };
  }

  const fullPath = join(baseDir, normalized);
  const rel = relative(baseDir, fullPath);
  if (rel.startsWith('..') || isAbsolute(rel)) {
    return { ok: false };
  }

  return { ok: true, relativePath: normalized, fullPath };
};

export class ToolRegistry {
  private readonly tools = new Map<string, ToolSpec>();
  private readonly handlers = new Map<string, ToolHandler>();
  private version = 1;

  constructor() {
    this.registerBuiltins();
  }

  getVersion(): number {
    return this.version;
  }

  register(specs: ToolSpec[]): { tools_version: number; tools: ToolSpec[] } {
    specs.forEach((spec) => {
      const validated = ToolSpecSchema.parse(spec);
      this.validateSpecSize(validated);
      if (!this.isExternalToolAllowed(validated.name)) {
        throw new ToolRegisterError('TOOL_NOT_ALLOWED', `Tool ${validated.name} is not allowed by server policy`);
      }
      if (validated.callback_url && !this.isCallbackUrlAllowed(validated.callback_url)) {
        throw new ToolRegisterError('TOOL_NOT_ALLOWED', 'Tool callback_url is not allowed by server policy');
      }

      this.tools.set(validated.name, validated);
      if (validated.callback_url) {
        const url = validated.callback_url;
        this.handlers.set(validated.name, async (input, ctx) => {
          const env = getConfig();
          const toolTimeout = AbortSignal.timeout(validated.timeout_ms ?? 10_000);
          const signal = ctx.signal ? AbortSignal.any([ctx.signal, toolTimeout]) : toolTimeout;

          try {
                        const authHeader = validated.auth_ref ? getToolAuth(validated.auth_ref) : undefined;
            const body = JSON.stringify({ input, run_id: ctx.runId, token_owner: ctx.tokenOwner });
            if (Buffer.byteLength(body, 'utf8') > env.MAX_TOOL_CALLBACK_REQUEST_BYTES) {
              return { ok: false, output: { error: 'OUTBOUND_PAYLOAD_REJECTED', retryable: false }, tokens_used: 1 };
            }
            const res = getConfig().TOOL_CALLBACK_ALLOW_LOCAL_TEST
              ? await (async () => {
                  const native = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', ...(authHeader ? { Authorization: `Bearer ${authHeader}` } : {}) },
                    body,
                    redirect: 'error',
                    signal
                  });
                  return { status: native.status, headers: native.headers, bodyText: await native.text() };
                })()
              : await safeFetch(url, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json', ...(authHeader ? { Authorization: `Bearer ${authHeader}` } : {}) },
                  body,
                  timeoutMs: validated.timeout_ms,
                  maxBytes: env.TOOL_CALLBACK_MAX_BYTES,
                  signal
                });
            if (res.status < 200 || res.status >= 300) return { ok: false, output: { error: `HTTP_${res.status}`, retryable: res.status >= 500 || res.status === 429 }, tokens_used: 0 };
            const contentType = res.headers.get('content-type') ?? '';
            if (!contentType.toLowerCase().includes('application/json')) {
              return { ok: false, output: { error: 'TOOL_HTTP_BAD_CONTENT_TYPE' }, tokens_used: 0 };
            }
            const output = JSON.parse(res.bodyText) as { tokens_used?: number };
            return { ok: true, output, tokens_used: output.tokens_used ?? 30 };
          } catch (error) {
            if (error instanceof Error && (error.name === 'AbortError' || error.name === 'TimeoutError')) {
              return { ok: false, output: { error: 'TOOL_TIMEOUT', retryable: true }, tokens_used: 1 };
            }
            return { ok: false, output: { error: error instanceof Error ? error.message : 'TOOL_HTTP_FAILED' }, tokens_used: 1 };
          }
        });
      } else if (!this.handlers.has(validated.name)) {
        this.handlers.set(validated.name, async (input) => ({ ok: true, output: input, tokens_used: 30 }));
      }
    });
    this.version += 1;
    return { tools_version: this.version, tools: this.list() };
  }

  list(): ToolSpec[] {
    return [...this.tools.values()];
  }

  has(name: string): boolean {
    return this.tools.has(name);
  }

  getSpec(name: string): ToolSpec | undefined {
    return this.tools.get(name);
  }

  isToolAllowed(name: string): boolean {
    return this.tools.has(name);
  }

  setHandler(name: string, handler: ToolHandler): void {
    this.handlers.set(name, handler);
  }

  async call(name: string, input: any, ctx: ToolContext): Promise<ToolCallResult> {
    const handler = this.handlers.get(name);
    const spec = this.tools.get(name);
    if (!handler || !spec) {
      throw new Error(`unknown tool: ${name}`);
    }

    const timeoutController = new AbortController();
    const compositeSignal = ctx.signal ? AbortSignal.any([ctx.signal, timeoutController.signal]) : timeoutController.signal;

    try {
      const timeout = (async () => {
        await delay(spec.timeout_ms, undefined, { signal: timeoutController.signal });
        return { ok: false, output: { error: 'TOOL_TIMEOUT' }, tokens_used: 1 } as ToolCallResult;
      })();

      const call = handler(input, { ...ctx, signal: compositeSignal });
      return await Promise.race([call, timeout]);
    } finally {
      timeoutController.abort();
    }
  }

  private validateSpecSize(spec: ToolSpec): void {
    if (spec.name.length > 64) {
      throw new ToolRegisterError('TOOL_SPEC_INVALID', `Tool name too long: ${spec.name.length} > 64`);
    }
    if (spec.description.length > 512) {
      throw new ToolRegisterError('TOOL_SPEC_INVALID', `Tool description too long: ${spec.description.length} > 512`);
    }
    const schemaLength = JSON.stringify(spec.input_schema).length;
    if (schemaLength > 20_000) {
      throw new ToolRegisterError('TOOL_SPEC_INVALID', `Tool input_schema too large: ${schemaLength} > 20000`);
    }
    if (spec.timeout_ms < 1 || spec.timeout_ms > 120_000) {
      throw new ToolRegisterError('TOOL_SPEC_INVALID', 'Tool timeout_ms out of allowed range');
    }
  }

  private isExternalToolAllowed(name: string): boolean {
    const allowlist = getConfig().TOOL_ALLOWLIST
      .split(',')
      .map((v) => v.trim())
      .filter(Boolean);
    return allowlist.includes(name);
  }

  private isCallbackUrlAllowed(raw: string): boolean {
    try {
      const env = getConfig();
      const url = new URL(raw);
      if (url.username || url.password) return false;
      if (url.protocol !== 'https:' && !(env.ALLOW_INSECURE_HTTP_TOOLS && url.protocol === 'http:')) return false;
      if (getConfig().TOOL_CALLBACK_ALLOW_LOCAL_TEST) return true;
      return env.TOOL_CALLBACK_ALLOWLIST.trim().length > 0;
    } catch {
      return false;
    }
  }

  private registerBuiltins(): void {
    this.tools.set('file_store', {
      name: 'file_store',
      description: 'Store content under ./runs/artifacts for a run id',
      input_schema: { type: 'object', properties: { path: { type: 'string' }, content: { type: 'string' } }, required: ['path', 'content'] },
      timeout_ms: 1000,
      tags: ['builtin', 'io', 'safe']
    });

    this.tools.set('js_eval', {
      name: 'js_eval',
      description: 'Evaluate arithmetic-only expression and return numeric result',
      input_schema: { type: 'object', properties: { expression: { type: 'string' } }, required: ['expression'] },
      timeout_ms: 500,
      tags: ['builtin', 'compute', 'safe']
    });

    this.handlers.set('file_store', async (input, ctx) => {
      const rawPath = String(input.path || 'out.txt');
      const content = String(input.content || '');
      const bytes = Buffer.byteLength(content);
      const baseDir = join(process.cwd(), 'runs', 'artifacts', ctx.runId);
      mkdirSync(baseDir, { recursive: true });

      const allowed = isPathAllowed(rawPath, baseDir);
      if (!allowed.ok) {
        return { ok: false, output: { error: 'PATH_NOT_ALLOWED', attempted_bytes: 0 }, tokens_used: 20 };
      }

      const reserved = ctx.tryReserveArtifactsBytes ? ctx.tryReserveArtifactsBytes(bytes) : true;
      if (!reserved) {
        return { ok: false, output: { error: 'ARTIFACT_LIMIT', attempted_bytes: 0 }, tokens_used: 20 };
      }

      try {
        mkdirSync(dirname(allowed.fullPath), { recursive: true });
        writeFileSync(allowed.fullPath, content, 'utf8');
      } catch (error) {
        ctx.rollbackArtifactsBytes?.(bytes);
        throw error;
      }

      return { ok: true, output: { path: allowed.relativePath, bytes }, tokens_used: 80 };
    });

    this.handlers.set('js_eval', async (input) => {
      const expression = String(input.expression || '0').trim();
      if (expression.length > 200 || !allowedCharRegex.test(expression)) {
        return { ok: false, output: { error: 'EXPRESSION_NOT_ALLOWED' }, tokens_used: 20 };
      }

      try {
        const result = evaluateArithmetic(expression);
        return { ok: true, output: result, tokens_used: 40 };
      } catch {
        return { ok: false, output: { error: 'EXPRESSION_NOT_ALLOWED' }, tokens_used: 20 };
      }
    });
  }
}
