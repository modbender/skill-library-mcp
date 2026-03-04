/**
 * Brain service - manages brain registry and lifecycle
 */

import { logger } from '../lib/logger';
import { BrainNotFoundError } from '../lib/errors';
import { IBrain, BrainState } from '../domain/types/brain';
import { eventBus, EventType } from '../domain/events';

export class BrainService {
  private brains: Map<string, IBrain> = new Map();

  /**
   * Register a brain
   */
  register(brain: IBrain): void {
    if (this.brains.has(brain.id)) {
      logger.warn('Brain already registered, replacing', { brainId: brain.id });
    }

    this.brains.set(brain.id, brain);
    logger.info('Brain registered', {
      brainId: brain.id,
      name: brain.name,
    });
  }

  /**
   * Unregister a brain
   */
  unregister(brainId: string): void {
    if (!this.brains.has(brainId)) {
      throw new BrainNotFoundError(brainId);
    }

    this.brains.delete(brainId);
    logger.info('Brain unregistered', { brainId });
  }

  /**
   * Get a brain by ID
   */
  get(brainId: string): IBrain {
    const brain = this.brains.get(brainId);
    if (!brain) {
      throw new BrainNotFoundError(brainId);
    }
    return brain;
  }

  /**
   * Check if a brain exists
   */
  has(brainId: string): boolean {
    return this.brains.has(brainId);
  }

  /**
   * Get all brains
   */
  getAll(): IBrain[] {
    return Array.from(this.brains.values());
  }

  /**
   * Get all brain states
   */
  getAllStates(): BrainState[] {
    return this.getAll().map((brain) => brain.getState());
  }

  /**
   * Initialize all brains
   */
  async initAll(): Promise<void> {
    logger.info('Initializing all brains', { count: this.brains.size });

    for (const brain of this.brains.values()) {
      try {
        await brain.init();
      } catch (error) {
        logger.error('Failed to initialize brain', error as Error, {
          brainId: brain.id,
        });
      }
    }

    logger.info('All brains initialized');
  }

  /**
   * Toggle auto mode for a brain
   */
  async toggleAutoMode(brainId: string, enabled: boolean): Promise<void> {
    const brain = this.get(brainId);
    brain.toggleAutoMode(enabled);

    await eventBus.emit({
      type: EventType.BRAIN_AUTO_MODE_CHANGED,
      timestamp: Date.now(),
      payload: { brainId, autoMode: enabled },
    });

    logger.info('Brain auto mode toggled', { brainId, enabled });
  }

  /**
   * Force run a brain
   */
  async forceRun(brainId: string): Promise<void> {
    const brain = this.get(brainId);
    await brain.forceRun();
    logger.info('Brain force run triggered', { brainId });
  }

  /**
   * Run heartbeat for all brains
   */
  async heartbeatAll(): Promise<void> {
    logger.debug('Running heartbeat for all brains');

    for (const brain of this.brains.values()) {
      try {
        await brain.onHeartbeat();
      } catch (error) {
        logger.error('Heartbeat failed for brain', error as Error, {
          brainId: brain.id,
        });
      }
    }
  }

  /**
   * Handle user message for a specific brain
   */
  async handleUserMessage(brainId: string, message: string): Promise<void> {
    const brain = this.get(brainId);
    await brain.handleUserMessage(message);
    logger.info('User message handled', { brainId, messageLength: message.length });
  }
}
