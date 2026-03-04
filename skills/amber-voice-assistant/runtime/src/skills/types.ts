/**
 * Amber Skills — Type definitions
 */

export interface AmberSkillPermissions {
  local_binaries?: string[];
  telegram?: boolean;
  openclaw_action?: boolean;
  network?: boolean;
}

export interface AmberSkillFunctionSchema {
  name: string;
  description: string;
  parameters: Record<string, any>;  // JSON Schema
}

export interface AmberSkillConfig {
  capabilities: ('read' | 'act')[];
  confirmation_required: boolean;
  confirmation_prompt?: string;
  timeout_ms: number;
  permissions: AmberSkillPermissions;
  function_schema: AmberSkillFunctionSchema;
}

export interface AmberSkillManifest {
  name: string;
  version: string;
  description: string;
  amber: AmberSkillConfig;
}

export interface SkillCallContext {
  /** Must be string[] — uses execFileSync (no shell spawned, no injection risk). */
  exec: (cmd: string[]) => Promise<string>;
  callLog: {
    write: (entry: Record<string, any>) => void;
  };
  gateway: {
    post: (payload: Record<string, any>) => Promise<any>;
    sendMessage: (message: string) => Promise<any>;
  };
  call: {
    id: string;
    callerId: string;
    transcript: string;
  };
  operator: {
    name: string;
    telegramId?: string;
  };
}

export interface SkillResult {
  success: boolean;
  skipped?: boolean;
  result?: any;
  message?: string;
  error?: string;
}

export type SkillHandler = (params: any, context: SkillCallContext) => Promise<SkillResult>;

export interface LoadedSkill {
  manifest: AmberSkillManifest;
  handler: SkillHandler;
  path: string;
}
