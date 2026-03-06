export type DockerOperation =
  | "ps"
  | "logs"
  | "inspect"
  | "start"
  | "stop"
  | "restart"
  | "compose_up"
  | "compose_down"
  | "compose_ps";

export interface DockerTlsConfig {
  caPath?: string;
  certPath?: string;
  keyPath?: string;
  rejectUnauthorized?: boolean;
}

export interface ComposeProjectConfig {
  name: string;
  path: string;
}

export interface PluginConfig {
  socketPath: string;
  host?: string;
  port?: number;
  tls?: DockerTlsConfig;
  readOnly: boolean;
  allowedOperations?: DockerOperation[];
  composeProjects: ComposeProjectConfig[];
  timeoutMs: number;
}

export interface DockerContainerInfo {
  id: string;
  name: string;
  image: string;
  state: string;
  status: string;
}

export interface ToolContext {
  signal?: AbortSignal;
}
