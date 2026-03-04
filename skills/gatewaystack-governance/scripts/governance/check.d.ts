import type { GovernanceCheckResult } from "./types.js";
export declare function checkGovernance(params: {
    toolName: string;
    args: string;
    userId: string;
    session?: string;
    policyPath?: string;
}): Promise<GovernanceCheckResult>;
