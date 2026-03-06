export interface ArticlePayload {
  title: string;
  summary?: string;
  content: string;
}

export interface MetricItem {
  label: string;
  value: number;
  unit?: string;
}

export interface MetricPayload {
  title: string;
  summary?: string;
  metrics: MetricItem[];
  scripts?: unknown[];
  logs?: string[];
}

export interface AuditFinding {
  severity: string;
  message: string;
}

export interface AuditPayload {
  title: string;
  summary?: string;
  findings: AuditFinding[];
}

export interface Channel {
  name: string;
  icon: string;
}

export interface HashBoxRequest {
  type: "article" | "metric" | "audit";
  channel: Channel;
  payload: ArticlePayload | MetricPayload | AuditPayload;
}

export interface PluginTool {
  name: string;
  description: string;
  execute: (...args: unknown[]) => Promise<unknown>;
}

export interface PluginAction {
  name: string;
  description: string;
  execute: (...args: unknown[]) => Promise<unknown>;
}

/** Agent command from Firestore queue */
export interface AgentCommand {
  id: string;
  userId: string;
  commandType: "add_feed" | "ping_metrics";
  payload: {
    topic?: string;
    raw_instruction: string;
  };
  status: "pending" | "processing" | "completed" | "error";
}

/** Callback for processing incoming commands */
export type CommandHandler = (command: AgentCommand) => Promise<void>;

/** OpenClaw plugin context — provided by framework at init */
export interface PluginContext {
  injectMessage: (message: string) => Promise<void>;
}

/** Extended plugin interface with lifecycle hooks */
export interface HashBoxPlugin {
  name: string;
  description: string;
  tools: PluginTool[];
  actions: PluginAction[];
  initialize?: (context: PluginContext) => Promise<void>;
  destroy?: () => Promise<void>;
}
