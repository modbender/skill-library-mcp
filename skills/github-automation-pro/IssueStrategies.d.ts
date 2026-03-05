/**
 * Issue Automation Strategy
 * 使用 Strategy Pattern 實作 Issue 相關操作
 */
import { ExecutionStrategy, ExecutionContext, StrategyResult, ValidationResult } from '../types';
export declare class IssueCreateStrategy implements ExecutionStrategy {
    readonly name = "issue.create";
    validate(params: unknown): ValidationResult;
    execute(context: ExecutionContext): Promise<StrategyResult>;
}
export declare class IssueListStrategy implements ExecutionStrategy {
    readonly name = "issue.list";
    validate(params: unknown): ValidationResult;
    execute(context: ExecutionContext): Promise<StrategyResult>;
}
export declare class IssueUpdateStrategy implements ExecutionStrategy {
    readonly name = "issue.update";
    validate(params: unknown): ValidationResult;
    execute(context: ExecutionContext): Promise<StrategyResult>;
}
