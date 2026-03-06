/**
 * Pull Request Assistant Strategy
 * PR 審查輔助功能
 */
import { ExecutionStrategy, ExecutionContext, StrategyResult, ValidationResult } from '../types';
export declare class PRAnalyzeStrategy implements ExecutionStrategy {
    readonly name = "pr.analyze";
    validate(params: unknown): ValidationResult;
    execute(context: ExecutionContext): Promise<StrategyResult>;
    private analyzePR;
}
export declare class PRReviewStrategy implements ExecutionStrategy {
    readonly name = "pr.review";
    validate(params: unknown): ValidationResult;
    execute(context: ExecutionContext): Promise<StrategyResult>;
}
