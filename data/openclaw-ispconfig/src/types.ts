export interface ISPConfigPluginConfig {
  apiUrl: string;
  username: string;
  password: string;
  serverId?: number;
  defaultServerIp?: string;
  readOnly?: boolean;
  allowedOperations?: string[];
  verifySsl?: boolean;
  timeoutMs?: number;
}

export interface ISPConfigApiEnvelope<T> {
  code?: string;
  message?: string;
  response?: T;
}

export type ISPListResponse<T> = T[];

export interface Client {
  client_id: number;
  company_name?: string;
  contact_name?: string;
  email?: string;
  username?: string;
  parent_client_id?: number;
  web_quota?: number;
  traffic_quota?: number;
  [key: string]: unknown;
}

export interface Site {
  domain_id: number;
  domain: string;
  system_user?: string;
  type?: string;
  active?: string;
  php?: string;
  ssl?: string;
  ssl_letsencrypt?: string;
  ip_address?: string;
  server_id?: number;
  client_id?: number;
  [key: string]: unknown;
}

export interface DnsZone {
  id: number;
  origin?: string;
  server_id?: number;
  client_id?: number;
  active?: string;
  [key: string]: unknown;
}

export interface DnsRecord {
  id?: number;
  zone?: number;
  name?: string;
  type?: string;
  data?: string;
  aux?: number;
  ttl?: number;
  active?: string;
  [key: string]: unknown;
}

export interface MailDomain {
  domain_id: number;
  domain: string;
  server_id?: number;
  active?: string;
  [key: string]: unknown;
}

export interface MailUser {
  mailuser_id: number;
  login?: string;
  email?: string;
  name?: string;
  uid?: number;
  gid?: number;
  mailbox?: string;
  [key: string]: unknown;
}

export interface MailAlias {
  mailalias_id: number;
  source?: string;
  destination?: string;
  [key: string]: unknown;
}

export interface Database {
  database_id: number;
  database_name?: string;
  database_user_id?: number;
  active?: string;
  [key: string]: unknown;
}

export interface DatabaseUser {
  database_user_id: number;
  database_user?: string;
  [key: string]: unknown;
}

export interface ShellUser {
  shell_user_id: number;
  username?: string;
  dir?: string;
  [key: string]: unknown;
}

export interface FtpUser {
  ftp_user_id: number;
  username?: string;
  dir?: string;
  [key: string]: unknown;
}

export interface CronJob {
  cron_id: number;
  command?: string;
  active?: string;
  [key: string]: unknown;
}

export interface ServerInfo {
  server_id: number;
  server_name?: string;
  ip_address?: string;
  [key: string]: unknown;
}

export type JsonMap = Record<string, unknown>;

export interface ToolContext {
  config: ISPConfigPluginConfig;
}

export interface ToolDefinition {
  name: string;
  description: string;
  run: (params: JsonMap, context: ToolContext) => Promise<unknown>;
}
