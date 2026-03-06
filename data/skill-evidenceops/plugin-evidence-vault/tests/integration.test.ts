import { jest } from '@jest/globals';
import * as path from 'path';
import * as fs from 'fs/promises';
import * as os from 'os';
import { EvidenceVaultPlugin } from '../src/tools/index';

describe('EvidenceVaultPlugin Integration', () => {
  let plugin: EvidenceVaultPlugin;
  let tempDir: string;
  
  beforeAll(async () => {
    tempDir = path.join(os.tmpdir(), `evidence-integration-${Date.now()}`);
    await fs.mkdir(tempDir, { recursive: true });
    
    plugin = new EvidenceVaultPlugin({
      config: {
        driver: 'filesystem',
        basePath: tempDir,
        maxFileSizeBytes: 10485760,
        allowedMimeTypes: ['image/jpeg', 'image/png', 'application/pdf', 'text/plain'],
        defaultRetentionDays: 365,
        enforceLegalHold: false,
        auditLogPath: path.join(tempDir, 'audit'),
        redactPatterns: [],
      },
    });
    
    await plugin.initialize();
  });
  
  afterAll(async () => {
    await plugin.shutdown();
    await fs.rm(tempDir, { recursive: true, force: true });
  });
  
  describe('Full Workflow', () => {
    const caseId = 'case-integration-001';
    let evidenceId: string;
    let originalSha256: string;
    
    it('should create case automatically on first ingest', async () => {
      const testFile = path.join(tempDir, 'workflow-test.txt');
      await fs.writeFile(testFile, 'Integration test content');
      
      const result = await plugin.ingest({
        filePath: testFile,
        filename: 'workflow-test.txt',
        caseId,
        channel: 'test-channel',
        sender: 'test-sender',
        messageId: 'msg-001',
        retentionDays: 365,
        metadata: {
          custom: 'metadata',
        },
      });
      
      expect(result.success).toBe(true);
      expect(result.evidenceId).toMatch(/^ev-/);
      
      evidenceId = result.evidenceId;
      originalSha256 = result.sha256;
    });
    
    it('should retrieve manifest with ingested item', async () => {
      const result = await plugin.manifest({ caseId });
      
      expect(result.success).toBe(true);
      expect(result.manifest?.caseId).toBe(caseId);
      expect(result.manifest?.items.length).toBe(1);
      expect(result.manifest?.items[0].evidenceId).toBe(evidenceId);
    });
    
    it('should verify evidence integrity', async () => {
      const result = await plugin.verify({ evidenceId, caseId });
      
      expect(result.success).toBe(true);
      expect(result.verified).toBe(true);
      expect(result.details.hashMatch).toBe(true);
      expect(result.details.originalIntact).toBe(true);
    });
    
    it('should have chain of custody entries', async () => {
      const result = await plugin.manifest({ caseId });
      
      expect(result.manifest?.chainOfCustody.length).toBeGreaterThan(0);
      
      const createEntry = result.manifest?.chainOfCustody.find(
        e => e.event === 'case_created'
      );
      expect(createEntry).toBeDefined();
      
      const ingestEntry = result.manifest?.chainOfCustody.find(
        e => e.event === 'evidence_ingested'
      );
      expect(ingestEntry).toBeDefined();
      expect(ingestEntry?.evidenceId).toBe(evidenceId);
    });
    
    it('should export case as zip', async () => {
      const result = await plugin.export({ caseId, format: 'zip' });
      
      expect(result.success).toBe(true);
      expect(result.exportPath).toMatch(/\.zip$/);
      expect(result.itemCount).toBe(1);
      expect(result.sha256).toMatch(/^[a-f0-9]{64}$/);
      
      const stats = await fs.stat(result.exportPath);
      expect(stats.size).toBeGreaterThan(0);
    });
    
    it('should have audit log entries', async () => {
      const result = await plugin.accessLog({ caseId, limit: 10 });
      
      expect(result.success).toBe(true);
      expect(result.count).toBeGreaterThan(0);
      
      const ingestEvent = result.events.find(
        e => e.eventType === 'evidence_ingested'
      );
      expect(ingestEvent).toBeDefined();
    });
    
    it('should have correct hash chain', async () => {
      const result = await plugin.manifest({ caseId });
      const chain = result.manifest?.chainOfCustody ?? [];
      
      for (let i = 1; i < chain.length; i++) {
        expect(chain[i].previousHash).toBe(chain[i - 1].currentHash);
      }
    });
  });
  
  describe('Channel Security', () => {
    it('should block denied channels', async () => {
      const blockedPlugin = new EvidenceVaultPlugin({
        config: {
          driver: 'filesystem',
          basePath: path.join(tempDir, 'blocked'),
          maxFileSizeBytes: 10485760,
          allowedMimeTypes: ['text/plain'],
          defaultRetentionDays: 365,
          enforceLegalHold: false,
          auditLogPath: path.join(tempDir, 'blocked-audit'),
          redactPatterns: [],
        },
        channelDenylist: ['blocked-channel'],
      });
      
      await blockedPlugin.initialize();
      
      const testFile = path.join(tempDir, 'blocked-test.txt');
      await fs.writeFile(testFile, 'test');
      
      const result = await blockedPlugin.ingest({
        filePath: testFile,
        filename: 'test.txt',
        caseId: 'case-blocked-001',
        channel: 'blocked-channel',
        sender: 'test',
      });
      
      expect(result.success).toBe(false);
      expect(result.error?.code).toBe('E_CHANNEL_BLOCKED');
      
      await blockedPlugin.shutdown();
    });
    
    it('should enforce allowlist', async () => {
      const allowlistPlugin = new EvidenceVaultPlugin({
        config: {
          driver: 'filesystem',
          basePath: path.join(tempDir, 'allowlist'),
          maxFileSizeBytes: 10485760,
          allowedMimeTypes: ['text/plain'],
          defaultRetentionDays: 365,
          enforceLegalHold: false,
          auditLogPath: path.join(tempDir, 'allowlist-audit'),
          redactPatterns: [],
        },
        channelAllowlist: ['allowed-channel'],
      });
      
      await allowlistPlugin.initialize();
      
      const testFile = path.join(tempDir, 'allowlist-test.txt');
      await fs.writeFile(testFile, 'test');
      
      const blockedResult = await allowlistPlugin.ingest({
        filePath: testFile,
        filename: 'test.txt',
        caseId: 'case-allowlist-001',
        channel: 'not-allowed',
        sender: 'test',
      });
      
      expect(blockedResult.success).toBe(false);
      
      const allowedResult = await allowlistPlugin.ingest({
        filePath: testFile,
        filename: 'test.txt',
        caseId: 'case-allowlist-002',
        channel: 'allowed-channel',
        sender: 'test',
      });
      
      expect(allowedResult.success).toBe(true);
      
      await allowlistPlugin.shutdown();
    });
  });
  
  describe('Manifest Determinism', () => {
    it('should produce consistent hashes for same content', async () => {
      const testFile = path.join(tempDir, 'determinism-test.txt');
      const content = 'Same content every time';
      await fs.writeFile(testFile, content);
      
      const plugin1 = new EvidenceVaultPlugin({
        config: {
          driver: 'filesystem',
          basePath: path.join(tempDir, 'det1'),
          maxFileSizeBytes: 10485760,
          allowedMimeTypes: ['text/plain'],
          defaultRetentionDays: 365,
          enforceLegalHold: false,
          auditLogPath: path.join(tempDir, 'det1-audit'),
          redactPatterns: [],
        },
      });
      
      await plugin1.initialize();
      
      const result1 = await plugin1.ingest({
        filePath: testFile,
        filename: 'determinism.txt',
        caseId: 'case-det-001',
        channel: 'test',
        sender: 'test',
      });
      
      await plugin1.shutdown();
      
      const plugin2 = new EvidenceVaultPlugin({
        config: {
          driver: 'filesystem',
          basePath: path.join(tempDir, 'det2'),
          maxFileSizeBytes: 10485760,
          allowedMimeTypes: ['text/plain'],
          defaultRetentionDays: 365,
          enforceLegalHold: false,
          auditLogPath: path.join(tempDir, 'det2-audit'),
          redactPatterns: [],
        },
      });
      
      await plugin2.initialize();
      
      const result2 = await plugin2.ingest({
        filePath: testFile,
        filename: 'determinism.txt',
        caseId: 'case-det-002',
        channel: 'test',
        sender: 'test',
      });
      
      await plugin2.shutdown();
      
      expect(result1.sha256).toBe(result2.sha256);
    });
  });
});
