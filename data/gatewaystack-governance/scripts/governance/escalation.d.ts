export type InjectionSeverity = "HIGH" | "MEDIUM" | "LOW" | "NONE";
export declare function classifyInjectionSeverity(matches: string[]): InjectionSeverity;
export declare function isFirstTimeToolUse(agentId: string, toolName: string): boolean;
export declare function recordToolUse(agentId: string, toolName: string): void;
export declare function hashArgs(args: string): string;
export declare function generateApprovalToken(toolName: string, argsHash: string, ttlSeconds: number): string;
export declare function checkApprovalToken(token: string, toolName: string, argsHash: string): boolean;
/**
 * Check if any approved token exists for this tool + args combination.
 * Used by before_tool_call to allow retries after approval.
 */
export declare function hasApprovedToken(toolName: string, argsHash: string): boolean;
/**
 * Consume the first matching approved token for this tool + args.
 */
export declare function consumeApprovedToken(toolName: string, argsHash: string): boolean;
/**
 * Approve a pending review token (called by CLI `gatewaystack approve <token>`).
 */
export declare function approveToken(token: string): {
    success: boolean;
    detail: string;
};
export declare function formatReviewBlock(reason: string, token: string): string;
