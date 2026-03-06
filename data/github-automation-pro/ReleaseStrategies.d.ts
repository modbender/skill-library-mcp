/**
 * Release Automation Strategy
 * 自動化發布功能
 */
import { ExecutionStrategy, ExecutionContext, StrategyResult, ValidationResult } from '../types';
export declare class ReleaseCreateStrategy implements ExecutionStrategy {
    readonly name = "release.create";
    validate(params: unknown): ValidationResult;
    execute(context: ExecutionContext): Promise<StrategyResult>;
}
export declare class RepoStatsStrategy implements ExecutionStrategy {
    readonly name = "repo.stats";
    validate(): ValidationResult;
    execute(context: ExecutionContext): Promise<StrategyResult>;
}
export declare class RepoHealthStrategy implements ExecutionStrategy {
    readonly name = "repo.health";
    validate(): ValidationResult;
    execute(context: ExecutionContext): Promise<StrategyResult>;
    private assessHealth;
    private generateRecommendations;
}
