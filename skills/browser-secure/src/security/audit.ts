import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { getAuditLogPath, expandPath, loadConfig } from '../config/loader.js';

export interface AuditAction {
  action: string;
  timestamp: string;
  details?: Record<string, unknown>;
  screenshot?: string;
  userApproved?: boolean;
  approvalToken?: string;
}

export interface AuditSession {
  event: 'BROWSER_SECURE_SESSION';
  timestamp: string;
  sessionId: string;
  site?: string;
  vaultTokenHash?: string;
  actions: AuditAction[];
  session: {
    duration: number;
    autoClosed: boolean;
    cleanupSuccess: boolean;
  };
  chainHash: string;
}

let currentSession: AuditSession | null = null;
let previousHash = '';

export function startAuditSession(site?: string): string {
  const sessionId = `bs-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

  currentSession = {
    event: 'BROWSER_SECURE_SESSION',
    timestamp: new Date().toISOString(),
    sessionId,
    site,
    actions: [],
    session: {
      duration: 0,
      autoClosed: false,
      cleanupSuccess: false
    },
    chainHash: ''
  };

  previousHash = '';
  return sessionId;
}

export function logAction(
  action: string,
  details?: Record<string, unknown>,
  options?: {
    screenshot?: string;
    userApproved?: boolean;
    approvalToken?: string;
  }
): void {
  if (!currentSession) {
    throw new Error('No active audit session');
  }

  const actionEntry: AuditAction = {
    action,
    timestamp: new Date().toISOString(),
    details,
    ...options
  };

  currentSession.actions.push(actionEntry);
}

export function finalizeAuditSession(duration: number, cleanupSuccess: boolean): void {
  if (!currentSession) return;

  currentSession.session.duration = duration;
  currentSession.session.autoClosed = true;
  currentSession.session.cleanupSuccess = cleanupSuccess;

  // Compute chain hash for tamper evidence
  const data = JSON.stringify(currentSession.actions);
  const actionHash = crypto.createHash('sha256').update(data).digest('hex');
  const chainData = {
    previousHash: previousHash || 'genesis',
    sessionId: currentSession.sessionId,
    timestamp: currentSession.timestamp,
    actionHash
  };
  currentSession.chainHash = crypto.createHash('sha256')
    .update(JSON.stringify(chainData))
    .digest('hex');

  // Write to audit log
  writeAuditLog(currentSession);

  // Send to webhook if configured
  sendAuditWebhook(currentSession);

  currentSession = null;
}

function writeAuditLog(session: AuditSession): void {
  const logPath = getAuditLogPath();
  const logDir = path.dirname(logPath);

  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }

  const line = JSON.stringify(session) + '\n';
  fs.appendFileSync(logPath, line, 'utf-8');
}

async function sendAuditWebhook(session: AuditSession): Promise<void> {
  const config = loadConfig();
  const auditConfig = config.security.audit;

  // Check if webhook is enabled
  if (auditConfig.mode === 'file') {
    return;
  }

  const webhookUrl = auditConfig.webhook?.url;
  if (!webhookUrl) {
    return;
  }

  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(auditConfig.webhook?.headers || {})
    };

    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(session)
    });

    if (!response.ok) {
      console.error(`Audit webhook failed: ${response.status} ${response.statusText}`);
    }
  } catch (e) {
    // Log but don't fail - audit to file already succeeded
    console.error(`Audit webhook error: ${e}`);
  }
}

export function readAuditLog(sessionId?: string): AuditSession[] {
  const logPath = getAuditLogPath();

  if (!fs.existsSync(logPath)) {
    return [];
  }

  const content = fs.readFileSync(logPath, 'utf-8');
  const lines = content.trim().split('\n').filter(Boolean);
  const sessions = lines.map(line => JSON.parse(line));

  if (sessionId) {
    return sessions.filter((s: AuditSession) => s.sessionId === sessionId);
  }

  return sessions;
}

export function getCurrentSessionId(): string | null {
  return currentSession?.sessionId || null;
}

export function rotateAuditLog(retentionDays: number): void {
  const logPath = getAuditLogPath();

  if (!fs.existsSync(logPath)) return;

  const cutoff = Date.now() - (retentionDays * 24 * 60 * 60 * 1000);
  const content = fs.readFileSync(logPath, 'utf-8');
  const lines = content.trim().split('\n').filter(Boolean);

  const recent = lines.filter(line => {
    try {
      const session = JSON.parse(line);
      const timestamp = new Date(session.timestamp).getTime();
      return timestamp > cutoff;
    } catch {
      return false;
    }
  });

  fs.writeFileSync(logPath, recent.join('\n') + '\n', 'utf-8');
}
