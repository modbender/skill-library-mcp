/**
 * GitHub Automation Skill - 主類別
 *
 * 使用設計模式：
 * - Builder Pattern: 複雜設定物件的建構
 * - Strategy Pattern: 不同操作使用不同策略
 * - Factory Pattern: Skill 實例建立
 */
import { SkillPlugin, SkillConfig, SkillInput, SkillResult, SkillSchema } from './types';
export declare class SkillConfigBuilder {
    private config;
    setGitHubToken(token: string): this;
    setDefaultOwner(owner: string): this;
    setDefaultRepo(repo: string): this;
    enableFeature(feature: keyof NonNullable<SkillConfig['features']>): this;
    enableAllFeatures(): this;
    build(): SkillConfig;
}
export declare class GitHubAutomationSkill implements SkillPlugin {
    readonly name = "github-automation";
    readonly version = "1.0.0";
    private config?;
    private strategies;
    private client?;
    constructor();
    initialize(config: SkillConfig): Promise<void>;
    execute(input: SkillInput): Promise<SkillResult>;
    getSchema(): SkillSchema;
    dispose(): Promise<void>;
    private isFeatureEnabled;
}
export declare function createGitHubSkill(): GitHubAutomationSkill;
