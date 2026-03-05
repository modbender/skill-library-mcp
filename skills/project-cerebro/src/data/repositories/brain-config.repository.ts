/**
 * Brain configuration repository
 */

import { DatabaseConnection } from '../database';
import { logger } from '../../lib/logger';
import { DatabaseError } from '../../lib/errors';

export interface BrainConfigRecord {
  brainId: string;
  config: Record<string, any>;
  updatedAt: number;
}

export class BrainConfigRepository {
  constructor(private db: DatabaseConnection) {}

  /**
   * Get config for a brain
   */
  get(brainId: string): Record<string, any> | null {
    try {
      const stmt = this.db.getDb().prepare('SELECT config FROM brain_configs WHERE brainId = ?');
      const row = stmt.get(brainId) as any;
      return row ? JSON.parse(row.config) : null;
    } catch (error) {
      logger.error('Failed to get brain config', error as Error, { brainId });
      throw new DatabaseError('Failed to get brain config');
    }
  }

  /**
   * Set config for a brain
   */
  set(brainId: string, config: Record<string, any>): void {
    try {
      const now = Date.now();
      const stmt = this.db.getDb().prepare(`
        INSERT OR REPLACE INTO brain_configs (brainId, config, updatedAt)
        VALUES (?, ?, ?)
      `);
      stmt.run(brainId, JSON.stringify(config), now);
      logger.info('Brain config updated', { brainId });
    } catch (error) {
      logger.error('Failed to set brain config', error as Error, { brainId });
      throw new DatabaseError('Failed to set brain config');
    }
  }

  /**
   * Delete config for a brain
   */
  delete(brainId: string): void {
    try {
      const stmt = this.db.getDb().prepare('DELETE FROM brain_configs WHERE brainId = ?');
      stmt.run(brainId);
      logger.info('Brain config deleted', { brainId });
    } catch (error) {
      logger.error('Failed to delete brain config', error as Error, { brainId });
      throw new DatabaseError('Failed to delete brain config');
    }
  }

  /**
   * Get all brain configs
   */
  getAll(): BrainConfigRecord[] {
    try {
      const stmt = this.db.getDb().prepare('SELECT * FROM brain_configs');
      const rows = stmt.all() as any[];
      return rows.map((row) => ({
        brainId: row.brainId,
        config: JSON.parse(row.config),
        updatedAt: row.updatedAt,
      }));
    } catch (error) {
      logger.error('Failed to get all brain configs', error as Error);
      throw new DatabaseError('Failed to get all brain configs');
    }
  }
}
