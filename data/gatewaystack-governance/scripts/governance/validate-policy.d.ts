export interface PolicyValidationResult {
    valid: boolean;
    errors: string[];
    warnings: string[];
}
export declare function validatePolicy(policy: unknown): PolicyValidationResult;
