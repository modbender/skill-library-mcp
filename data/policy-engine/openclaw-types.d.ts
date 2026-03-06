/**
 * Ambient type declarations for the OpenClaw plugin API.
 *
 * At runtime, OpenClaw's tsx/jiti loader resolves "openclaw/plugins/types"
 * from the installed OpenClaw package. This file provides type-checking
 * during development without pulling in the entire OpenClaw source tree.
 */

declare module "openclaw/plugin-sdk" {
  export type PluginLogger = {
    debug?: (message: string) => void;
    info: (message: string) => void;
    warn: (message: string) => void;
    error: (message: string) => void;
  };

  export type PluginHookName =
    | "before_agent_start"
    | "agent_end"
    | "before_compaction"
    | "after_compaction"
    | "message_received"
    | "message_sending"
    | "message_sent"
    | "before_tool_call"
    | "after_tool_call"
    | "tool_result_persist"
    | "session_start"
    | "session_end"
    | "gateway_start"
    | "gateway_stop";

  export type PluginHookAgentContext = {
    agentId?: string;
    sessionKey?: string;
    workspaceDir?: string;
    messageProvider?: string;
  };

  export type PluginHookToolContext = {
    agentId?: string;
    sessionKey?: string;
    toolName: string;
  };

  export type PluginHookBeforeToolCallEvent = {
    toolName: string;
    params: Record<string, unknown>;
  };

  export type PluginHookBeforeToolCallResult = {
    params?: Record<string, unknown>;
    block?: boolean;
    blockReason?: string;
  };

  export type PluginHookAfterToolCallEvent = {
    toolName: string;
    params: Record<string, unknown>;
    result?: unknown;
    error?: string;
    durationMs?: number;
  };

  export type PluginHookBeforeAgentStartEvent = {
    prompt: string;
    messages?: unknown[];
  };

  export type PluginHookBeforeAgentStartResult = {
    systemPrompt?: string;
    prependContext?: string;
  };

  export type PluginCommandContext = {
    senderId?: string;
    channel: string;
    isAuthorizedSender: boolean;
    args?: string;
    commandBody: string;
    config: Record<string, unknown>;
  };

  export type PluginCommandResult = {
    text?: string;
    [key: string]: unknown;
  };

  export type PluginCommandHandler = (
    ctx: PluginCommandContext,
  ) => PluginCommandResult | Promise<PluginCommandResult>;

  export type OpenClawPluginCommandDefinition = {
    name: string;
    description: string;
    acceptsArgs?: boolean;
    requireAuth?: boolean;
    handler: PluginCommandHandler;
  };

  export type PluginHookHandlerMap = {
    before_agent_start: (
      event: PluginHookBeforeAgentStartEvent,
      ctx: PluginHookAgentContext,
    ) => Promise<PluginHookBeforeAgentStartResult | void> | PluginHookBeforeAgentStartResult | void;
    agent_end: (event: any, ctx: PluginHookAgentContext) => Promise<void> | void;
    before_compaction: (event: any, ctx: PluginHookAgentContext) => Promise<void> | void;
    after_compaction: (event: any, ctx: PluginHookAgentContext) => Promise<void> | void;
    message_received: (event: any, ctx: any) => Promise<void> | void;
    message_sending: (event: any, ctx: any) => Promise<any> | any;
    message_sent: (event: any, ctx: any) => Promise<void> | void;
    before_tool_call: (
      event: PluginHookBeforeToolCallEvent,
      ctx: PluginHookToolContext,
    ) => Promise<PluginHookBeforeToolCallResult | void> | PluginHookBeforeToolCallResult | void;
    after_tool_call: (
      event: PluginHookAfterToolCallEvent,
      ctx: PluginHookToolContext,
    ) => Promise<void> | void;
    tool_result_persist: (event: any, ctx: any) => any;
    session_start: (event: any, ctx: any) => Promise<void> | void;
    session_end: (event: any, ctx: any) => Promise<void> | void;
    gateway_start: (event: any, ctx: any) => Promise<void> | void;
    gateway_stop: (event: any, ctx: any) => Promise<void> | void;
  };

  export type OpenClawPluginApi = {
    id: string;
    name: string;
    version?: string;
    description?: string;
    source: string;
    config: Record<string, unknown>;
    pluginConfig?: Record<string, unknown>;
    runtime: unknown;
    logger: PluginLogger;
    registerTool: (tool: unknown, opts?: unknown) => void;
    registerHook: (events: string | string[], handler: unknown, opts?: unknown) => void;
    registerHttpHandler: (handler: unknown) => void;
    registerHttpRoute: (params: { path: string; handler: unknown }) => void;
    registerChannel: (registration: unknown) => void;
    registerGatewayMethod: (method: string, handler: unknown) => void;
    registerCli: (registrar: unknown, opts?: unknown) => void;
    registerService: (service: unknown) => void;
    registerProvider: (provider: unknown) => void;
    registerCommand: (command: OpenClawPluginCommandDefinition) => void;
    resolvePath: (input: string) => string;
    on: <K extends PluginHookName>(
      hookName: K,
      handler: PluginHookHandlerMap[K],
      opts?: { priority?: number },
    ) => void;
  };
}
