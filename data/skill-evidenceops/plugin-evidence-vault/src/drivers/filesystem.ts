import * as fs from 'fs/promises';
import * as path from 'path';
import * as crypto from 'crypto';
import { Readable } from 'stream';
import { pipeline } from 'stream/promises';
import { createWriteStream, createReadStream, existsSync } from 'fs';
import archiver from 'archiver';
import {
  CaseManifest,
  VaultConfig,
  IngestResult,
  VerifyResult,
  ExportResult,
  AccessLogResult,
  AuditEvent,
  SensitivityTag,
  SCHEMA_VERSION,
  createVaultError,
  VAULT_ERRORS,
  DEFAULT_CONFIG,
} from '../types';
import { BaseDriver, IngestInput } from './interface';
import { sanitizeFilename, sanitizeCaseId, ensureDirectory, sanitizePath } from '../utils/path';
import { hashFile, hashString, generateChainHash, generateId } from '../utils/crypto';
import { redactString, redactObject } from '../utils/redaction';

export class FilesystemDriver extends BaseDriver {
  readonly name = 'filesystem';
  
  private basePath!: string;
  private auditPath!: string;
  private appendOnly: boolean = true;
  
  async initialize(config: VaultConfig): Promise<void> {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.basePath = path.resolve(config.basePath);
    this.auditPath = path.resolve(config.auditLogPath);
    this.appendOnly = true;
    
    await ensureDirectory(this.basePath);
    await ensureDirectory(path.join(this.basePath, 'cases'));
    await ensureDirectory(path.join(this.basePath, 'index'));
    await ensureDirectory(this.auditPath);
    
    await this.ensureCaseIndex();
    
    this.initialized = true;
  }
  
  async healthCheck(): Promise<{ healthy: boolean; details: Record<string, unknown> }> {
    try {
      const testPath = path.join(this.basePath, '.healthcheck');
      await fs.writeFile(testPath, Date.now().toString());
      await fs.unlink(testPath);
      
      return {
        healthy: true,
        details: {
          basePath: this.basePath,
          driver: this.name,
          timestamp: new Date().toISOString(),
        },
      };
    } catch (error) {
      return {
        healthy: false,
        details: {
          error: error instanceof Error ? error.message : 'Unknown error',
        },
      };
    }
  }
  
  async createCase(
    caseId: string,
    sensitivityTag: SensitivityTag = 'confidential'
  ): Promise<{ success: boolean; caseId: string; error?: { code: string; message: string } }> {
    this.ensureInitialized();
    
    const sanitizedCaseId = sanitizeCaseId(caseId);
    if (!sanitizedCaseId) {
      return {
        success: false,
        caseId,
        error: createVaultError(VAULT_ERRORS.INVALID_CASE, 'Invalid case ID format'),
      };
    }
    
    const caseDir = path.join(this.basePath, 'cases', sanitizedCaseId);
    const exists = await this.caseExists(sanitizedCaseId);
    
    if (exists) {
      return {
        success: false,
        caseId: sanitizedCaseId,
        error: createVaultError(VAULT_ERRORS.ALREADY_EXISTS, `Case ${sanitizedCaseId} already exists`),
      };
    }
    
    try {
      await ensureDirectory(caseDir);
      await ensureDirectory(path.join(caseDir, 'originals'));
      await ensureDirectory(path.join(caseDir, 'derivatives'));
      await ensureDirectory(path.join(caseDir, 'metadata'));
      
      const now = new Date().toISOString();
      const retentionDays = this.config.defaultRetentionDays;
      const deleteAfter = new Date(Date.now() + retentionDays * 24 * 60 * 60 * 1000).toISOString();
      
      const manifest: CaseManifest = {
        schemaVersion: SCHEMA_VERSION,
        caseId: sanitizedCaseId,
        createdAt: now,
        updatedAt: now,
        sensitivityTag,
        retentionPolicy: {
          retentionDays,
          legalHold: false,
          deleteAfter,
        },
        items: [],
        chainOfCustody: [
          {
            event: 'case_created',
            timestamp: now,
            actor: 'system',
            previousHash: null,
            currentHash: generateChainHash(null, 'case_created', now, sanitizedCaseId),
          },
        ],
      };
      
      await this.writeManifest(sanitizedCaseId, manifest);
      await this.updateCaseIndex(sanitizedCaseId, 'created');
      
      await this.writeAudit({
        eventType: 'case_created',
        timestamp: now,
        caseId: sanitizedCaseId,
        actor: 'system',
        details: { sensitivityTag },
      });
      
      return { success: true, caseId: sanitizedCaseId };
    } catch (error) {
      return {
        success: false,
        caseId: sanitizedCaseId,
        error: createVaultError(
          VAULT_ERRORS.VAULT_ERROR,
          `Failed to create case: ${error instanceof Error ? error.message : 'Unknown error'}`
        ),
      };
    }
  }
  
  async caseExists(caseId: string): Promise<boolean> {
    const sanitized = sanitizeCaseId(caseId);
    if (!sanitized) return false;
    
    const manifestPath = path.join(this.basePath, 'cases', sanitized, 'manifest.json');
    return existsSync(manifestPath);
  }
  
  async ingest(input: IngestInput): Promise<IngestResult> {
    this.ensureInitialized();
    
    try {
      this.validateCaseId(input.caseId);
      this.validateMimeType(input.mimeType);
      this.validateFileSize(input.size);
      
      const sanitizedCaseId = sanitizeCaseId(input.caseId);
      if (!sanitizedCaseId) {
        return this.ingestError(input.caseId, VAULT_ERRORS.INVALID_CASE, 'Invalid case ID');
      }
      
      const exists = await this.caseExists(sanitizedCaseId);
      if (!exists) {
        await this.createCase(sanitizedCaseId);
      }
      
      const evidenceId = generateId('ev');
      const sanitizedFilename = sanitizeFilename(input.filename);
      const ext = path.extname(sanitizedFilename);
      const storedFilename = `${evidenceId}${ext}`;
      
      const caseDir = path.join(this.basePath, 'cases', sanitizedCaseId);
      const originalsDir = path.join(caseDir, 'originals');
      const targetPath = path.join(originalsDir, storedFilename);
      
      const validatedPath = sanitizePath(storedFilename, originalsDir);
      if (!validatedPath) {
        return this.ingestError(input.caseId, VAULT_ERRORS.PATH_TRAVERSAL, 'Path traversal detected');
      }
      
      const sha256 = await hashFile(input.filePath);
      
      await fs.copyFile(input.filePath, targetPath);
      
      try {
        await fs.chmod(targetPath, 0o444);
      } catch {
        // Ignore chmod errors on Windows
      }
      
      const manifestResult = await this.getManifest(sanitizedCaseId);
      if (!manifestResult.success || !manifestResult.manifest) {
        return this.ingestError(sanitizedCaseId, VAULT_ERRORS.VAULT_ERROR, 'Failed to read manifest');
      }
      
      const manifest = manifestResult.manifest;
      const now = new Date().toISOString();
      const lastChainEntry = manifest.chainOfCustody[manifest.chainOfCustody.length - 1];
      const newChainHash = generateChainHash(
        lastChainEntry?.currentHash ?? null,
        'evidence_ingested',
        now,
        evidenceId
      );
      
      const newItem = {
        evidenceId,
        original: {
          filename: sanitizedFilename,
          sha256,
          size: input.size,
          mime: input.mimeType,
          receivedAt: now,
          source: input.sourceContext,
        },
        metadata: input.metadata ?? {},
        derivatives: [],
        vault: {
          provider: 'filesystem' as const,
          vaultUrl: `file://${targetPath}`,
          ingestedAt: now,
        },
      };
      
      manifest.items.push(newItem);
      manifest.updatedAt = now;
      manifest.chainOfCustody.push({
        event: 'evidence_ingested',
        timestamp: now,
        actor: input.sourceContext.sessionId ?? 'unknown',
        evidenceId,
        previousHash: lastChainEntry?.currentHash ?? null,
        currentHash: newChainHash,
      });
      
      await this.writeManifest(sanitizedCaseId, manifest);
      
      await this.writeAudit({
        eventType: 'evidence_ingested',
        timestamp: now,
        caseId: sanitizedCaseId,
        evidenceId,
        actor: input.sourceContext.sessionId ?? 'unknown',
        details: redactObject({
          filename: sanitizedFilename,
          sha256,
          size: input.size,
          source: input.sourceContext,
        }),
        hash: newChainHash,
        previousHash: lastChainEntry?.currentHash,
      });
      
      return {
        success: true,
        evidenceId,
        sha256,
        vaultUrl: `file://${targetPath}`,
        timestamp: now,
      };
    } catch (error) {
      return this.ingestError(
        input.caseId,
        VAULT_ERRORS.VAULT_ERROR,
        error instanceof Error ? error.message : 'Unknown error'
      );
    }
  }
  
  async verify(evidenceId: string, caseId?: string): Promise<VerifyResult> {
    this.ensureInitialized();
    
    try {
      let targetCaseId = caseId;
      
      if (!targetCaseId) {
        const indexData = await this.readCaseIndex();
        for (const [cid, caseInfo] of Object.entries(indexData)) {
          const manifestResult = await this.getManifest(cid);
          if (manifestResult.success && manifestResult.manifest) {
            const item = manifestResult.manifest.items.find(i => i.evidenceId === evidenceId);
            if (item) {
              targetCaseId = cid;
              break;
            }
          }
        }
      }
      
      if (!targetCaseId) {
        return {
          success: false,
          evidenceId,
          caseId: caseId ?? '',
          verified: false,
          details: {
            originalIntact: false,
            hashMatch: false,
            lastVerifiedAt: new Date().toISOString(),
          },
          error: createVaultError(VAULT_ERRORS.NOT_FOUND, 'Evidence not found'),
        };
      }
      
      const manifestResult = await this.getManifest(targetCaseId);
      if (!manifestResult.success || !manifestResult.manifest) {
        return {
          success: false,
          evidenceId,
          caseId: targetCaseId,
          verified: false,
          details: {
            originalIntact: false,
            hashMatch: false,
            lastVerifiedAt: new Date().toISOString(),
          },
          error: createVaultError(VAULT_ERRORS.NOT_FOUND, 'Case manifest not found'),
        };
      }
      
      const item = manifestResult.manifest.items.find(i => i.evidenceId === evidenceId);
      if (!item) {
        return {
          success: false,
          evidenceId,
          caseId: targetCaseId,
          verified: false,
          details: {
            originalIntact: false,
            hashMatch: false,
            lastVerifiedAt: new Date().toISOString(),
          },
          error: createVaultError(VAULT_ERRORS.NOT_FOUND, 'Evidence item not found in case'),
        };
      }
      
      const filePath = item.vault.vaultUrl.replace('file://', '');
      let originalIntact = false;
      let hashMatch = false;
      
      try {
        const currentHash = await hashFile(filePath);
        hashMatch = currentHash === item.original.sha256;
        originalIntact = hashMatch;
      } catch {
        originalIntact = false;
        hashMatch = false;
      }
      
      const now = new Date().toISOString();
      await this.writeAudit({
        eventType: 'evidence_verified',
        timestamp: now,
        caseId: targetCaseId,
        evidenceId,
        actor: 'system',
        details: { originalIntact, hashMatch },
      });
      
      return {
        success: true,
        evidenceId,
        caseId: targetCaseId,
        verified: hashMatch && originalIntact,
        details: {
          originalIntact,
          hashMatch,
          lastVerifiedAt: now,
        },
      };
    } catch (error) {
      return {
        success: false,
        evidenceId,
        caseId: caseId ?? '',
        verified: false,
        details: {
          originalIntact: false,
          hashMatch: false,
          lastVerifiedAt: new Date().toISOString(),
        },
        error: createVaultError(
          VAULT_ERRORS.VAULT_ERROR,
          error instanceof Error ? error.message : 'Unknown error'
        ),
      };
    }
  }
  
  async export(caseId: string, format: 'zip' | 'tar' = 'zip'): Promise<ExportResult> {
    this.ensureInitialized();
    
    const sanitizedCaseId = sanitizeCaseId(caseId);
    if (!sanitizedCaseId) {
      return {
        success: false,
        caseId,
        exportPath: '',
        sha256: '',
        size: 0,
        itemCount: 0,
        timestamp: new Date().toISOString(),
        error: createVaultError(VAULT_ERRORS.INVALID_CASE, 'Invalid case ID'),
      };
    }
    
    const manifestResult = await this.getManifest(sanitizedCaseId);
    if (!manifestResult.success || !manifestResult.manifest) {
      return {
        success: false,
        caseId: sanitizedCaseId,
        exportPath: '',
        sha256: '',
        size: 0,
        itemCount: 0,
        timestamp: new Date().toISOString(),
        error: createVaultError(VAULT_ERRORS.NOT_FOUND, 'Case not found'),
      };
    }
    
    const manifest = manifestResult.manifest;
    const caseDir = path.join(this.basePath, 'cases', sanitizedCaseId);
    const exportDir = path.join(this.basePath, 'exports');
    await ensureDirectory(exportDir);
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const exportFilename = `${sanitizedCaseId}-export-${timestamp}.zip`;
    const exportPath = path.join(exportDir, exportFilename);
    
    try {
      await new Promise<void>((resolve, reject) => {
        const output = createWriteStream(exportPath);
        const archive = archiver('zip', { zlib: { level: 9 } });
        
        output.on('close', () => resolve());
        archive.on('error', (err) => reject(err));
        
        archive.pipe(output);
        
        archive.directory(path.join(caseDir, 'originals'), 'originals');
        archive.directory(path.join(caseDir, 'derivatives'), 'derivatives');
        archive.file(path.join(caseDir, 'manifest.json'), { name: 'manifest.json' });
        
        archive.finalize();
      });
      
      const stats = await fs.stat(exportPath);
      const sha256 = await hashFile(exportPath);
      const now = new Date().toISOString();
      
      await this.writeAudit({
        eventType: 'evidence_exported',
        timestamp: now,
        caseId: sanitizedCaseId,
        actor: 'system',
        details: {
          exportPath,
          sha256,
          size: stats.size,
          itemCount: manifest.items.length,
        },
      });
      
      return {
        success: true,
        caseId: sanitizedCaseId,
        exportPath,
        sha256,
        size: stats.size,
        itemCount: manifest.items.length,
        timestamp: now,
      };
    } catch (error) {
      return {
        success: false,
        caseId: sanitizedCaseId,
        exportPath: '',
        sha256: '',
        size: 0,
        itemCount: 0,
        timestamp: new Date().toISOString(),
        error: createVaultError(
          VAULT_ERRORS.VAULT_ERROR,
          `Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`
        ),
      };
    }
  }
  
  async getManifest(caseId: string): Promise<{ success: boolean; manifest?: CaseManifest; error?: { code: string; message: string } }> {
    this.ensureInitialized();
    
    const sanitizedCaseId = sanitizeCaseId(caseId);
    if (!sanitizedCaseId) {
      return {
        success: false,
        error: createVaultError(VAULT_ERRORS.INVALID_CASE, 'Invalid case ID'),
      };
    }
    
    const manifestPath = path.join(this.basePath, 'cases', sanitizedCaseId, 'manifest.json');
    
    try {
      const content = await fs.readFile(manifestPath, 'utf-8');
      const manifest = JSON.parse(content) as CaseManifest;
      return { success: true, manifest };
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        return {
          success: false,
          error: createVaultError(VAULT_ERRORS.NOT_FOUND, `Case ${sanitizedCaseId} not found`),
        };
      }
      return {
        success: false,
        error: createVaultError(
          VAULT_ERRORS.VAULT_ERROR,
          `Failed to read manifest: ${error instanceof Error ? error.message : 'Unknown error'}`
        ),
      };
    }
  }
  
  async updateManifest(caseId: string, manifest: CaseManifest): Promise<{ success: boolean; error?: { code: string; message: string } }> {
    this.ensureInitialized();
    
    const sanitizedCaseId = sanitizeCaseId(caseId);
    if (!sanitizedCaseId) {
      return {
        success: false,
        error: createVaultError(VAULT_ERRORS.INVALID_CASE, 'Invalid case ID'),
      };
    }
    
    try {
      manifest.updatedAt = new Date().toISOString();
      await this.writeManifest(sanitizedCaseId, manifest);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: createVaultError(
          VAULT_ERRORS.VAULT_ERROR,
          `Failed to update manifest: ${error instanceof Error ? error.message : 'Unknown error'}`
        ),
      };
    }
  }
  
  async writeAudit(event: AuditEvent): Promise<{ success: boolean; error?: { code: string; message: string } }> {
    this.ensureInitialized();
    
    const sanitizedCaseId = sanitizeCaseId(event.caseId);
    if (!sanitizedCaseId) {
      return {
        success: false,
        error: createVaultError(VAULT_ERRORS.INVALID_CASE, 'Invalid case ID for audit'),
      };
    }
    
    const auditPath = path.join(this.basePath, 'cases', sanitizedCaseId, 'audit.jsonl');
    const redactedEvent = redactObject(event as unknown as Record<string, unknown>) as unknown as AuditEvent;
    const line = JSON.stringify(redactedEvent) + '\n';
    
    try {
      await fs.appendFile(auditPath, line, 'utf-8');
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: createVaultError(
          VAULT_ERRORS.VAULT_ERROR,
          `Failed to write audit: ${error instanceof Error ? error.message : 'Unknown error'}`
        ),
      };
    }
  }
  
  async getAccessLog(caseId: string, limit: number = 100): Promise<AccessLogResult> {
    this.ensureInitialized();
    
    const sanitizedCaseId = sanitizeCaseId(caseId);
    if (!sanitizedCaseId) {
      return {
        success: false,
        caseId,
        events: [],
        count: 0,
        error: createVaultError(VAULT_ERRORS.INVALID_CASE, 'Invalid case ID'),
      };
    }
    
    const auditPath = path.join(this.basePath, 'cases', sanitizedCaseId, 'audit.jsonl');
    
    try {
      const content = await fs.readFile(auditPath, 'utf-8');
      const lines = content.trim().split('\n').filter(Boolean);
      const events = lines
        .slice(-limit)
        .map(line => JSON.parse(line) as AuditEvent);
      
      return {
        success: true,
        caseId: sanitizedCaseId,
        events,
        count: events.length,
      };
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        return {
          success: true,
          caseId: sanitizedCaseId,
          events: [],
          count: 0,
        };
      }
      return {
        success: false,
        caseId: sanitizedCaseId,
        events: [],
        count: 0,
        error: createVaultError(
          VAULT_ERRORS.VAULT_ERROR,
          `Failed to read audit log: ${error instanceof Error ? error.message : 'Unknown error'}`
        ),
      };
    }
  }
  
  private async writeManifest(caseId: string, manifest: CaseManifest): Promise<void> {
    const manifestPath = path.join(this.basePath, 'cases', caseId, 'manifest.json');
    const content = JSON.stringify(manifest, null, 2);
    await fs.writeFile(manifestPath, content, 'utf-8');
  }
  
  private async ensureCaseIndex(): Promise<void> {
    const indexPath = path.join(this.basePath, 'index', 'cases-index.json');
    if (!existsSync(indexPath)) {
      await fs.writeFile(indexPath, JSON.stringify({}, null, 2), 'utf-8');
    }
  }
  
  private async readCaseIndex(): Promise<Record<string, unknown>> {
    const indexPath = path.join(this.basePath, 'index', 'cases-index.json');
    try {
      const content = await fs.readFile(indexPath, 'utf-8');
      return JSON.parse(content);
    } catch {
      return {};
    }
  }
  
  private async updateCaseIndex(caseId: string, action: string): Promise<void> {
    const index = await this.readCaseIndex();
    index[caseId] = {
      action,
      timestamp: new Date().toISOString(),
    };
    const indexPath = path.join(this.basePath, 'index', 'cases-index.json');
    await fs.writeFile(indexPath, JSON.stringify(index, null, 2), 'utf-8');
  }
  
  private ingestError(caseId: string, code: string, message: string): IngestResult {
    return {
      success: false,
      evidenceId: '',
      sha256: '',
      vaultUrl: '',
      timestamp: new Date().toISOString(),
      error: createVaultError(code, message),
    };
  }
}
