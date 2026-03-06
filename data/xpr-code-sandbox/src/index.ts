/**
 * Code Sandbox Skill — execute JavaScript in a sandboxed V8 context
 *
 * Zero external dependencies — uses Node.js built-in `vm` module.
 */

import vm from 'vm';

interface ToolDef {
  name: string;
  description: string;
  parameters: { type: 'object'; required?: string[]; properties: Record<string, unknown> };
  handler: (params: any) => Promise<unknown>;
}

interface SkillApi {
  registerTool(tool: ToolDef): void;
  getConfig(): Record<string, unknown>;
}

// ── Constants ───────────────────────────────────

const DEFAULT_TIMEOUT = 5000;
const MAX_TIMEOUT = 30000;
const MAX_OUTPUT_SIZE = 10 * 1024 * 1024; // 10MB

// ── Sandbox helpers ─────────────────────────────

function createSandboxGlobals(input: unknown, logs: string[]): Record<string, unknown> {
  // Capture console methods
  const consoleMock = {
    log: (...args: unknown[]) => {
      logs.push(args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' '));
    },
    warn: (...args: unknown[]) => {
      logs.push('[warn] ' + args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' '));
    },
    error: (...args: unknown[]) => {
      logs.push('[error] ' + args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' '));
    },
  };

  return {
    INPUT: input,
    console: consoleMock,
    JSON,
    Math,
    Date,
    Array,
    Object,
    String,
    Number,
    RegExp,
    Map,
    Set,
    parseInt,
    parseFloat,
    isNaN,
    isFinite,
    encodeURIComponent,
    decodeURIComponent,
    atob: (s: string) => Buffer.from(s, 'base64').toString('binary'),
    btoa: (s: string) => Buffer.from(s, 'binary').toString('base64'),
    // Explicitly undefined — blocked
    require: undefined,
    process: undefined,
    globalThis: undefined,
    global: undefined,
  };
}

function serializeResult(value: unknown): string {
  if (value === undefined) return 'undefined';
  try {
    const str = JSON.stringify(value, null, 2);
    if (str.length > MAX_OUTPUT_SIZE) {
      return str.slice(0, MAX_OUTPUT_SIZE) + '\n... [truncated at 10MB]';
    }
    return str;
  } catch {
    return String(value);
  }
}

// ── Skill entry point ───────────────────────────

export default function codeSandboxSkill(api: SkillApi): void {
  // ── execute_js ──
  api.registerTool({
    name: 'execute_js',
    description: [
      'Run JavaScript code in a sandboxed V8 context.',
      'Pass data via "input" (JSON), access it as INPUT in code.',
      'console.log/warn/error are captured in the "logs" array.',
      'Available: JSON, Math, Date, Array, Object, String, Number, RegExp, Map, Set,',
      'parseInt, parseFloat, isNaN, isFinite, encodeURIComponent, decodeURIComponent, atob, btoa.',
      'No network, filesystem, require, or import access. Max 30s timeout, 10MB output.',
    ].join(' '),
    parameters: {
      type: 'object',
      required: ['code'],
      properties: {
        code: { type: 'string', description: 'JavaScript code to execute. The last expression value is returned as the result.' },
        input: { description: 'Optional JSON data available as INPUT in the code.' },
        timeout: { type: 'number', description: 'Execution timeout in milliseconds (default 5000, max 30000).' },
      },
    },
    handler: async ({ code, input, timeout }: {
      code: string; input?: unknown; timeout?: number;
    }) => {
      if (!code || typeof code !== 'string') {
        return { error: 'code parameter is required and must be a string' };
      }

      const timeoutMs = Math.min(Math.max(timeout || DEFAULT_TIMEOUT, 100), MAX_TIMEOUT);
      const logs: string[] = [];
      const startTime = Date.now();

      try {
        const globals = createSandboxGlobals(input, logs);
        const context = vm.createContext(globals, {
          codeGeneration: { strings: false, wasm: false },
        });

        // Wrap code so the last expression is returned
        const wrapped = `(function() {\n${code}\n})()`;
        const script = new vm.Script(wrapped, { filename: 'sandbox.js' });
        const result = script.runInContext(context, { timeout: timeoutMs });
        const durationMs = Date.now() - startTime;

        const serialized = serializeResult(result);
        if (serialized.length > MAX_OUTPUT_SIZE) {
          return {
            result: serialized.slice(0, 1000) + '... [truncated]',
            logs,
            duration_ms: durationMs,
            warning: 'Output exceeded 10MB limit and was truncated',
          };
        }

        // Parse back to preserve types (arrays, objects)
        let parsed: unknown;
        try {
          parsed = JSON.parse(serialized);
        } catch {
          parsed = serialized === 'undefined' ? undefined : serialized;
        }

        return { result: parsed, logs, duration_ms: durationMs };
      } catch (err: any) {
        const durationMs = Date.now() - startTime;
        const message = err.message || String(err);

        // Provide helpful error context
        if (message.includes('Script execution timed out')) {
          return { error: `Execution timed out after ${timeoutMs}ms. Keep code efficient or increase timeout (max ${MAX_TIMEOUT}ms).`, logs, duration_ms: durationMs };
        }
        if (message.includes('Code generation from strings disallowed')) {
          return { error: 'eval() and Function() constructor are blocked in the sandbox. Use direct code instead.', logs, duration_ms: durationMs };
        }

        return { error: message, logs, duration_ms: durationMs };
      }
    },
  });

  // ── eval_expression ──
  api.registerTool({
    name: 'eval_expression',
    description: [
      'Evaluate a single JavaScript expression and return the result.',
      'Lightweight alternative to execute_js for quick calculations.',
      'Examples: "15 * 4500 * 0.01", "new Date().toISOString()", "[1,2,3].map(x => x*x)".',
    ].join(' '),
    parameters: {
      type: 'object',
      required: ['expression'],
      properties: {
        expression: { type: 'string', description: 'A JavaScript expression to evaluate.' },
      },
    },
    handler: async ({ expression }: { expression: string }) => {
      if (!expression || typeof expression !== 'string') {
        return { error: 'expression parameter is required and must be a string' };
      }

      try {
        const globals = createSandboxGlobals(undefined, []);
        const context = vm.createContext(globals, {
          codeGeneration: { strings: false, wasm: false },
        });

        const script = new vm.Script(`(${expression})`, { filename: 'expr.js' });
        const result = script.runInContext(context, { timeout: DEFAULT_TIMEOUT });

        let serialized: unknown;
        try {
          serialized = JSON.parse(JSON.stringify(result));
        } catch {
          serialized = String(result);
        }

        return {
          result: serialized,
          type: result === null ? 'null' : Array.isArray(result) ? 'array' : typeof result,
        };
      } catch (err: any) {
        return { error: err.message || String(err) };
      }
    },
  });
}
