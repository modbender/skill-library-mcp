/**
 * Brains repository - DB-backed brain definitions
 */

import { DatabaseConnection } from '../database';
import { logger } from '../../lib/logger';
import { DatabaseError } from '../../lib/errors';

export interface BrainRecord {
  id: string;
  name: string;
  channelKey: string;
  type: 'context' | 'job' | 'nexus';
  description: string;
  openClawAgentId?: string;
  discordChannelId?: string;
  enabled: boolean;
  createdAt: number;
  updatedAt: number;
}

export interface CreateBrainInput {
  id: string;
  name: string;
  channelKey: string;
  type?: 'context' | 'job' | 'nexus';
  description?: string;
  openClawAgentId?: string;
  discordChannelId?: string;
  enabled?: boolean;
}

export class BrainsRepository {
  constructor(private db: DatabaseConnection) {}

  /**
   * Get all brains
   */
  getAll(): BrainRecord[] {
    try {
      const stmt = this.db.getDb().prepare('SELECT * FROM brains ORDER BY name');
      const rows = stmt.all() as any[];
      return rows.map(this.mapRow);
    } catch (error) {
      logger.error('Failed to get all brains', error as Error);
      throw new DatabaseError('Failed to get all brains');
    }
  }

  /**
   * Get brain by ID
   */
  getById(id: string): BrainRecord | null {
    try {
      const stmt = this.db.getDb().prepare('SELECT * FROM brains WHERE id = ?');
      const row = stmt.get(id) as any;
      return row ? this.mapRow(row) : null;
    } catch (error) {
      logger.error('Failed to get brain by ID', error as Error, { id });
      throw new DatabaseError('Failed to get brain by ID');
    }
  }

  /**
   * Create a brain
   */
  create(input: CreateBrainInput): BrainRecord {
    try {
      const now = Date.now();
      const stmt = this.db.getDb().prepare(`
        INSERT INTO brains (id, name, channelKey, type, description, openClawAgentId, discordChannelId, enabled, createdAt, updatedAt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);
      stmt.run(
        input.id,
        input.name,
        input.channelKey,
        input.type || 'context',
        input.description || '',
        input.openClawAgentId || input.id,
        input.discordChannelId || null,
        input.enabled !== false ? 1 : 0,
        now,
        now
      );
      logger.info('Brain created', { id: input.id });
      return this.getById(input.id)!;
    } catch (error) {
      logger.error('Failed to create brain', error as Error, { input });
      throw new DatabaseError('Failed to create brain');
    }
  }

  /**
   * Update a brain
   */
  update(id: string, updates: Partial<CreateBrainInput>): BrainRecord | null {
    try {
      const existing = this.getById(id);
      if (!existing) return null;

      const now = Date.now();
      const stmt = this.db.getDb().prepare(`
        UPDATE brains SET
          name = ?,
          channelKey = ?,
          type = ?,
          description = ?,
          openClawAgentId = ?,
          discordChannelId = ?,
          enabled = ?,
          updatedAt = ?
        WHERE id = ?
      `);
      stmt.run(
        updates.name ?? existing.name,
        updates.channelKey ?? existing.channelKey,
        updates.type ?? existing.type,
        updates.description ?? existing.description,
        updates.openClawAgentId ?? existing.openClawAgentId,
        updates.discordChannelId ?? existing.discordChannelId,
        updates.enabled !== undefined ? (updates.enabled ? 1 : 0) : (existing.enabled ? 1 : 0),
        now,
        id
      );
      logger.info('Brain updated', { id });
      return this.getById(id);
    } catch (error) {
      logger.error('Failed to update brain', error as Error, { id, updates });
      throw new DatabaseError('Failed to update brain');
    }
  }

  /**
   * Delete a brain
   */
  delete(id: string): boolean {
    try {
      const stmt = this.db.getDb().prepare('DELETE FROM brains WHERE id = ?');
      const result = stmt.run(id);
      logger.info('Brain deleted', { id });
      return result.changes > 0;
    } catch (error) {
      logger.error('Failed to delete brain', error as Error, { id });
      throw new DatabaseError('Failed to delete brain');
    }
  }

  /**
   * Seed brains from JSON config (migration helper)
   */
  seedFromJson(brainsJson: any): void {
    try {
      const existing = this.getAll();
      if (existing.length > 0) {
        logger.info('Brains already seeded, skipping', { count: existing.length });
        return;
      }

      // Seed regular brains
      for (const brain of brainsJson.brains || []) {
        this.create({
          id: brain.id,
          name: brain.name,
          channelKey: brain.channelKey,
          type: brain.type || 'context',
          description: brain.description,
          openClawAgentId: brain.openClawAgentId || brain.id,
        });
      }

      // Seed nexus
      if (brainsJson.nexus) {
        this.create({
          id: brainsJson.nexus.id,
          name: brainsJson.nexus.name,
          channelKey: brainsJson.nexus.channelKey,
          type: 'nexus',
          description: brainsJson.nexus.description,
          openClawAgentId: brainsJson.nexus.openClawAgentId || brainsJson.nexus.id,
        });
      }

      // Digest brain removed; use Nexus for digest tasks.

      logger.info('Brains seeded from JSON', { count: this.getAll().length });
    } catch (error) {
      logger.error('Failed to seed brains from JSON', error as Error);
      throw new DatabaseError('Failed to seed brains from JSON');
    }
  }

  private mapRow(row: any): BrainRecord {
    return {
      id: row.id,
      name: row.name,
      channelKey: row.channelKey,
      type: row.type,
      description: row.description,
      openClawAgentId: row.openClawAgentId,
      discordChannelId: row.discordChannelId,
      enabled: !!row.enabled,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
    };
  }
}
