/**
 * Domain events for decoupling brain execution from integrations
 */

import { Task, TaskStatus } from './types/task';

export enum EventType {
  TASK_CREATED = 'TASK_CREATED',
  TASK_STATUS_CHANGED = 'TASK_STATUS_CHANGED',
  TASK_EXECUTION_STARTED = 'TASK_EXECUTION_STARTED',
  TASK_EXECUTION_COMPLETED = 'TASK_EXECUTION_COMPLETED',
  TASK_EXECUTION_FAILED = 'TASK_EXECUTION_FAILED',
  BRAIN_AUTO_MODE_CHANGED = 'BRAIN_AUTO_MODE_CHANGED',
  RECURRING_TASK_TRIGGERED = 'RECURRING_TASK_TRIGGERED',
}

export interface DomainEvent {
  type: EventType;
  timestamp: number;
  payload: any;
}

export interface TaskCreatedEvent extends DomainEvent {
  type: EventType.TASK_CREATED;
  payload: {
    task: Task;
  };
}

export interface TaskStatusChangedEvent extends DomainEvent {
  type: EventType.TASK_STATUS_CHANGED;
  payload: {
    taskId: string;
    oldStatus: TaskStatus;
    newStatus: TaskStatus;
  };
}

export interface TaskExecutionStartedEvent extends DomainEvent {
  type: EventType.TASK_EXECUTION_STARTED;
  payload: {
    task: Task;
    brainId: string;
  };
}

export interface TaskExecutionCompletedEvent extends DomainEvent {
  type: EventType.TASK_EXECUTION_COMPLETED;
  payload: {
    taskId: string;
    brainId: string;
    output?: string;
  };
}

export interface TaskExecutionFailedEvent extends DomainEvent {
  type: EventType.TASK_EXECUTION_FAILED;
  payload: {
    taskId: string;
    brainId: string;
    error: string;
  };
}

export interface BrainAutoModeChangedEvent extends DomainEvent {
  type: EventType.BRAIN_AUTO_MODE_CHANGED;
  payload: {
    brainId: string;
    autoMode: boolean;
  };
}

export interface RecurringTaskTriggeredEvent extends DomainEvent {
  type: EventType.RECURRING_TASK_TRIGGERED;
  payload: {
    recurringTaskId: string;
    taskId: string;
  };
}

type EventHandler = (event: DomainEvent) => void | Promise<void>;

/**
 * Simple event bus for domain events
 */
export class EventBus {
  private handlers: Map<EventType, EventHandler[]> = new Map();

  /**
   * Subscribe to an event type
   */
  on(eventType: EventType, handler: EventHandler): void {
    const handlers = this.handlers.get(eventType) || [];
    handlers.push(handler);
    this.handlers.set(eventType, handlers);
  }

  /**
   * Unsubscribe from an event type
   */
  off(eventType: EventType, handler: EventHandler): void {
    const handlers = this.handlers.get(eventType) || [];
    const filtered = handlers.filter((h) => h !== handler);
    this.handlers.set(eventType, filtered);
  }

  /**
   * Emit an event
   */
  async emit(event: DomainEvent): Promise<void> {
    const handlers = this.handlers.get(event.type) || [];
    await Promise.all(handlers.map((handler) => handler(event)));
  }
}

// Singleton instance
export const eventBus = new EventBus();
