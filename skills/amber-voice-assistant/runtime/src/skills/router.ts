/**
 * Amber Skills — Router
 * 
 * Routes function calls from OpenAI Realtime to the appropriate skill handler.
 * Enforces timeouts, sanitizes inputs, builds constrained API context.
 */

import { LoadedSkill, SkillResult } from './types.js';
import { buildSkillContext, ApiDependencies } from './api.js';
import OpenAI from 'openai';

/** In-memory registry of loaded skills, keyed by function name */
const skillRegistry = new Map<string, LoadedSkill>();

/**
 * Initialize the router with loaded skills.
 */
export function registerSkills(skills: LoadedSkill[]): void {
  skillRegistry.clear();
  for (const skill of skills) {
    const fnName = skill.manifest.amber.function_schema.name;
    if (skillRegistry.has(fnName)) {
      console.warn(`[skills/router] Duplicate function name "${fnName}" — skipping ${skill.manifest.name}`);
      continue;
    }
    skillRegistry.set(fnName, skill);
  }
  console.log(`[skills/router] ${skillRegistry.size} skill function(s) registered`);
}

/**
 * Check if a function name belongs to a registered skill.
 */
export function isSkillFunction(fnName: string): boolean {
  return skillRegistry.has(fnName);
}

/**
 * Call a skill handler directly by function name, bypassing the Realtime API.
 * Used for automatic runtime-managed calls (CRM lookup at call start, log at call end).
 * Does NOT enforce confirmation_required — these are internal, not caller-triggered.
 */
export async function callSkillDirectly(
  fnName: string,
  params: Record<string, any>,
  apiDeps: ApiDependencies
): Promise<SkillResult> {
  const skill = skillRegistry.get(fnName);
  if (!skill) {
    return { success: false, message: `Skill not found: ${fnName}` };
  }
  const context = buildSkillContext(skill.manifest.amber.permissions, apiDeps);
  return executeWithTimeout(skill.handler, params, context, skill.manifest.amber.timeout_ms);
}

/**
 * Get OpenAI-compatible tool definitions for all registered skills.
 * These get merged with OPENCLAW_TOOLS and sent to the Realtime API.
 */
export function getSkillTools(): Array<{ type: 'function'; name: string; description: string; parameters: Record<string, any> }> {
  const tools: Array<{ type: 'function'; name: string; description: string; parameters: Record<string, any> }> = [];

  for (const skill of skillRegistry.values()) {
    const schema = skill.manifest.amber.function_schema;
    tools.push({
      type: 'function' as const,
      name: schema.name,
      description: schema.description,
      parameters: schema.parameters,
    });
  }

  return tools;
}

/**
 * Sanitize a string input — strip control characters, enforce max length.
 */
function sanitizeInput(value: any, maxLength: number = 1000): string {
  if (typeof value !== 'string') return String(value ?? '').slice(0, maxLength);
  return value.replace(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g, '').slice(0, maxLength);
}

/**
 * Sanitize all string values in a params object.
 */
function sanitizeParams(params: Record<string, any>): Record<string, any> {
  const sanitized: Record<string, any> = {};
  for (const [key, value] of Object.entries(params)) {
    if (typeof value === 'string') {
      sanitized[key] = sanitizeInput(value);
    } else if (typeof value === 'number' || typeof value === 'boolean') {
      sanitized[key] = value;
    } else if (value === null || value === undefined) {
      sanitized[key] = value;
    } else {
      // Nested objects — sanitize recursively
      sanitized[key] = sanitizeParams(value);
    }
  }
  return sanitized;
}

/**
 * Execute a skill handler with timeout enforcement.
 */
async function executeWithTimeout(
  handler: LoadedSkill['handler'],
  params: any,
  context: ReturnType<typeof buildSkillContext>,
  timeoutMs: number
): Promise<SkillResult> {
  return Promise.race([
    handler(params, context),
    new Promise<SkillResult>((_, reject) =>
      setTimeout(() => reject(new Error(`Skill timed out after ${timeoutMs}ms`)), timeoutMs)
    ),
  ]);
}

export interface HandleSkillCallDeps {
  clawdClient: OpenAI | null;
  operatorName: string;
  operatorTelegramId?: string;
  callId: string;
  callerId: string;
  transcript: string;
  writeJsonl: (entry: Record<string, any>) => void;
  sendFunctionCallOutput: (ws: any, fnCallId: string, output: string) => void;
}

/**
 * Handle a skill function call from the Realtime API.
 * 
 * This is the main entry point called from index.ts when a function call
 * matches a registered skill.
 */
export async function handleSkillCall(
  fnName: string,
  fnArgs: string,
  ws: any,
  fnCallId: string,
  deps: HandleSkillCallDeps
): Promise<void> {
  const skill = skillRegistry.get(fnName);
  if (!skill) {
    deps.sendFunctionCallOutput(ws, fnCallId, JSON.stringify({ error: `Unknown skill function: ${fnName}` }));
    return;
  }

  const manifest = skill.manifest;

  deps.writeJsonl({
    type: 'c2.skill_call',
    call_id: deps.callId,
    received_at: new Date().toISOString(),
    skill_name: manifest.name,
    fn_name: fnName,
    fn_args: fnArgs,
  });

  try {
    // Parse and sanitize arguments
    let params: Record<string, any>;
    try {
      params = JSON.parse(fnArgs);
    } catch {
      params = {};
    }
    params = sanitizeParams(params);

    // Router-level confirmation enforcement for 'act' skills.
    // All 'act' skills require confirmed: true by default.
    // A skill may opt out by explicitly setting confirmation_required: false in its manifest,
    // but this should only be done for non-destructive actions (e.g. read-only lookups declared as 'act').
    // This is a programmatic guarantee enforced at the router level — not left to LLM prompting.
    const isActSkill = manifest.amber.capabilities.includes('act');
    if (isActSkill && manifest.amber.confirmation_required !== false) {
      if (params.confirmed !== true) {
        deps.sendFunctionCallOutput(ws, fnCallId, JSON.stringify({
          response: 'This action requires explicit caller confirmation before it can proceed. Please confirm the details with the caller and call this function again with confirmed: true.',
          success: false,
          requires_confirmation: true,
        }));
        return;
      }
    }

    // Build constrained API context
    const apiDeps: ApiDependencies = {
      clawdClient: deps.clawdClient,
      operatorName: deps.operatorName,
      operatorTelegramId: deps.operatorTelegramId,
      callId: deps.callId,
      callerId: deps.callerId,
      transcript: deps.transcript,
      writeJsonl: deps.writeJsonl,
    };

    const context = buildSkillContext(manifest.amber.permissions, apiDeps);

    // Execute with timeout
    const result = await executeWithTimeout(
      skill.handler,
      params,
      context,
      manifest.amber.timeout_ms
    );

    deps.writeJsonl({
      type: 'c2.skill_result',
      call_id: deps.callId,
      received_at: new Date().toISOString(),
      skill_name: manifest.name,
      fn_name: fnName,
      success: result.success,
      has_message: !!result.message,
    });

    // Send result back to Realtime API
    // The 'message' field is what Amber should speak to the caller
    const output = result.message
      ? JSON.stringify({ response: result.message, success: result.success })
      : JSON.stringify(result);

    deps.sendFunctionCallOutput(ws, fnCallId, output);

  } catch (e: any) {
    const errorMsg = e.message || String(e);
    console.error(`[skills/router] Error in ${manifest.name}:`, errorMsg);

    deps.writeJsonl({
      type: 'c2.skill_error',
      call_id: deps.callId,
      received_at: new Date().toISOString(),
      skill_name: manifest.name,
      fn_name: fnName,
      error: errorMsg,
    });

    // Graceful fallback — never crash
    const operatorRef = deps.operatorName || 'the operator';
    const fallbackMessage = `I wasn't able to complete that — I'll make a note for ${operatorRef} to follow up.`;
    deps.sendFunctionCallOutput(ws, fnCallId, JSON.stringify({ response: fallbackMessage, success: false, error: errorMsg }));
  }
}
