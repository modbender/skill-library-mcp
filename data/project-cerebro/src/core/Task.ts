export enum TaskStatus {
    PENDING = 'PENDING',
    WAITING = 'WAITING', // Waiting on time or dependency
    READY = 'READY',     // Eligible for execution
    EXECUTING = 'EXECUTING',
    PAUSED = 'PAUSED',
    BLOCKED = 'BLOCKED',
    NEEDS_REVIEW = 'NEEDS_REVIEW',
    COMPLETED = 'COMPLETED',
    FAILED = 'FAILED'
}

export interface TaskDependency {
    taskId: string;
    type: 'HARD' | 'SOFT'; // HARD = must complete, SOFT = optional/informational
}

export interface TaskRetryPolicy {
    maxAttempts: number;
    backoffType: 'FIXED' | 'EXPONENTIAL';
    backoffMs: number;
}

export interface Task {
    id: string;
    brainId: string;
    status: TaskStatus;
    title: string;
    description?: string;
    payload: any; // Flexible payload for different task types
    modelOverride?: string; // Model alias or ID
    brainName?: string; // Cache for UI
    
    // Dependencies & Scheduling
    dependencies: TaskDependency[];
    executeAt?: number; // Unix timestamp for scheduled execution
    createdAt: number;
    updatedAt: number;
    
    // Execution History
    attempts: number;
    retryPolicy?: TaskRetryPolicy;
    error?: string;
    output?: string; // Path to artifact or summary
}
