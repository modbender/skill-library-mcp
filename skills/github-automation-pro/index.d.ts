/**
 * GitHub Automation Skill for OpenClaw
 *
 * @example
 * ```typescript
 * import { createGitHubSkill, SkillConfigBuilder } from '@skillforge/github-automation';
 *
 * // 使用 Builder 建立配置
 * const config = new SkillConfigBuilder()
 *   .setGitHubToken('ghp_xxxx')
 *   .setDefaultOwner('myorg')
 *   .setDefaultRepo('myrepo')
 *   .enableAllFeatures()
 *   .build();
 *
 * // 建立並初始化 Skill
 * const skill = createGitHubSkill();
 * await skill.initialize(config);
 *
 * // 執行操作
 * const result = await skill.execute({
 *   action: 'issue.create',
 *   params: {
 *     title: 'Bug Report',
 *     body: 'Something is broken...',
 *     labels: ['bug'],
 *   },
 * });
 * ```
 */
export { GitHubAutomationSkill, SkillConfigBuilder, createGitHubSkill } from './GitHubSkill';
export type { SkillPlugin, SkillConfig, SkillInput, SkillResult, SkillSchema, ExecutionStrategy, ExecutionContext, StrategyResult, ValidationResult, GitHubIssue, GitHubPullRequest, GitHubRelease, RepoStats, } from './types';
export { StrategyRegistry } from './strategies';
export { IssueCreateStrategy, IssueListStrategy, IssueUpdateStrategy, } from './strategies/IssueStrategies';
export { PRAnalyzeStrategy, PRReviewStrategy, } from './strategies/PRStrategies';
export { ReleaseCreateStrategy, RepoStatsStrategy, RepoHealthStrategy, } from './strategies/ReleaseStrategies';
export { GitHubClient } from './api/GitHubClient';
