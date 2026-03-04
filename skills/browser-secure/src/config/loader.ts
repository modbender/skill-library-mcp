import yaml from 'yaml';
import fs from 'fs';
import path from 'path';
import os from 'os';

export interface SitePolicy {
  approvalTier: 'none' | 'prompt' | 'always' | '2fa';
  sessionTtlMinutes?: number;
  require2fa: boolean;
}

export interface SiteConfig {
  vault: string;
  item: string;
  usernameField?: string;
  passwordField?: string;
  tokenField?: string;
  policy?: SitePolicy;
}

export interface SessionConfig {
  ttlMinutes: number;
  warningAtMinutes: number;
  credentialCacheMinutes: number;
}

export interface AuditConfig {
  enabled: boolean;
  logPath: string;
  retentionDays: number;
  mode: 'file' | 'webhook' | 'both';
  webhook?: {
    url: string;
    headers?: Record<string, string>;
  };
}

export interface SecurityConfig {
  defaultTtl: number;
  requireApprovalForLogin: boolean;
  screenshotEveryAction: boolean;
  network: {
    blockLocalhost: boolean;
    blockPrivateIps: boolean;
    allowedHosts: string[];
  };
  audit: AuditConfig;
  session: SessionConfig;
}

export interface IsolationConfig {
  incognitoMode: boolean;
  secureWorkdir: boolean;
  autoCleanup: boolean;
}

export interface BrowserSecureConfig {
  vault: {
    provider: '1password' | 'bitwarden' | 'hashicorp' | 'keychain' | 'env';
    sites: Record<string, SiteConfig>;
  };
  security: SecurityConfig;
  isolation: IsolationConfig;
}

const DEFAULT_CONFIG: BrowserSecureConfig = {
  vault: {
    provider: 'bitwarden',
    sites: {}
  },
  security: {
    defaultTtl: 1800,  // 30 minutes (updated from 300/5 minutes)
    requireApprovalForLogin: true,
    screenshotEveryAction: true,
    network: {
      blockLocalhost: true,
      blockPrivateIps: true,
      allowedHosts: []
    },
    audit: {
      enabled: true,
      logPath: '~/.browser-secure/audit.log',
      retentionDays: 30,
      mode: 'file'
    },
    session: {
      ttlMinutes: 30,
      warningAtMinutes: 25,
      credentialCacheMinutes: 10
    }
  },
  isolation: {
    incognitoMode: true,
    secureWorkdir: true,
    autoCleanup: true
  }
};

export function getConfigPath(): string {
  const envPath = process.env.BROWSER_SECURE_CONFIG;
  if (envPath) return envPath;
  return path.join(os.homedir(), '.browser-secure', 'config.yaml');
}

export function expandPath(p: string): string {
  if (p.startsWith('~/')) {
    return path.join(os.homedir(), p.slice(2));
  }
  return p;
}

export function loadConfig(): BrowserSecureConfig {
  const configPath = getConfigPath();

  if (!fs.existsSync(configPath)) {
    // Create default config
    const configDir = path.dirname(configPath);
    if (!fs.existsSync(configDir)) {
      fs.mkdirSync(configDir, { recursive: true });
    }
    saveConfig(DEFAULT_CONFIG);
    return DEFAULT_CONFIG;
  }

  const content = fs.readFileSync(configPath, 'utf-8');
  const parsed = yaml.parse(content);

  // Deep merge with defaults
  return {
    vault: { ...DEFAULT_CONFIG.vault, ...parsed.vault },
    security: {
      ...DEFAULT_CONFIG.security,
      ...parsed.security,
      network: { ...DEFAULT_CONFIG.security.network, ...parsed.security?.network },
      audit: { ...DEFAULT_CONFIG.security.audit, ...parsed.security?.audit },
      session: { ...DEFAULT_CONFIG.security.session, ...parsed.security?.session }
    },
    isolation: { ...DEFAULT_CONFIG.isolation, ...parsed.isolation }
  };
}

export function getSitePolicy(site: string): SitePolicy | undefined {
  const config = loadConfig();
  return config.vault.sites[site]?.policy;
}

export function getSessionConfig(): SessionConfig {
  const config = loadConfig();
  return config.security.session;
}

export function saveConfig(config: BrowserSecureConfig): void {
  const configPath = getConfigPath();
  const configDir = path.dirname(configPath);

  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }

  fs.writeFileSync(configPath, yaml.stringify(config), 'utf-8');
}

export function getAuditLogPath(): string {
  const config = loadConfig();
  return expandPath(config.security.audit.logPath);
}

export function getAuditWebhookUrl(): string | undefined {
  const config = loadConfig();
  return config.security.audit.webhook?.url;
}

export function checkCredentialSource(source: string): { valid: boolean; error?: string } {
  if (source === 'env') {
    // Check that at least some credentials are available via environment
    const hasEnvCreds = Object.keys(process.env).some(k =>
      k.startsWith('BROWSER_SECURE_') && (k.endsWith('_USERNAME') || k.endsWith('_PASSWORD') || k.endsWith('_TOKEN'))
    );
    if (!hasEnvCreds) {
      return { valid: false, error: 'No environment credentials found. Set BROWSER_SECURE_<SITE>_USERNAME/PASSWORD/TOKEN.' };
    }
    return { valid: true };
  }

  if (source === 'vault') {
    // Vault will be checked at runtime
    return { valid: true };
  }

  if (source === 'cache') {
    return { valid: true };
  }

  return { valid: false, error: `Unknown credential source: ${source}` };
}
