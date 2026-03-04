import type { Policy } from "./types.js";
export interface DlpMatch {
    type: string;
    value: string;
    start: number;
    end: number;
    confidence: number;
}
export interface DlpScanResult {
    matches: DlpMatch[];
    hasMatches: boolean;
    summary: string;
}
export declare function scanOutput(output: string, policy: Policy): DlpScanResult;
export declare function redactOutput(output: string, policy: Policy): string;
export declare function logDlpScan(scanResult: DlpScanResult, toolName: string, policy: Policy): void;
export declare function isTransformablAvailable(): boolean;
