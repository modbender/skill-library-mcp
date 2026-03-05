import type { Policy } from "./types.js";
export interface ToolBaseline {
    avgCallsPerWindow: number;
    toolsSeen: string[];
    totalCalls: number;
    windowSeconds: number;
}
export interface Anomaly {
    type: "new-tool" | "frequency-spike" | "unusual-pattern";
    severity: "low" | "medium" | "high";
    detail: string;
}
export declare function buildBaseline(auditLogPath: string, windowSeconds: number): ToolBaseline;
export declare function detectAnomalies(toolName: string, currentWindowCalls: number, agentId: string, policy: Policy): Anomaly[];
export declare function countCurrentWindowCalls(auditLogPath: string, windowSeconds: number): number;
export declare function isLimitablAvailable(): boolean;
export declare function clearBaselineCache(): void;
