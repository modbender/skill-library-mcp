/**
 * GitHub API Client
 * 封裝 Octokit REST API，提供統一介面
 */
import { GitHubIssue, GitHubPullRequest, GitHubRelease, RepoStats } from '../types';
export declare class GitHubClient {
    private octokit;
    private _token;
    constructor(token: string);
    /**
     * 取得目前使用的 GitHub Token（部分遮蔽）
     */
    getToken(): string;
    listIssues(owner: string, repo: string, options?: {
        state?: 'open' | 'closed' | 'all';
        labels?: string[];
        assignee?: string;
        perPage?: number;
    }): Promise<GitHubIssue[]>;
    createIssue(owner: string, repo: string, title: string, body?: string, options?: {
        labels?: string[];
        assignees?: string[];
    }): Promise<GitHubIssue>;
    updateIssue(owner: string, repo: string, issueNumber: number, updates: {
        title?: string;
        body?: string;
        state?: 'open' | 'closed';
        labels?: string[];
        assignees?: string[];
    }): Promise<GitHubIssue>;
    getPullRequest(owner: string, repo: string, pullNumber: number): Promise<GitHubPullRequest>;
    listPullRequests(owner: string, repo: string, options?: {
        state?: 'open' | 'closed' | 'all';
        perPage?: number;
    }): Promise<GitHubPullRequest[]>;
    getPullRequestFiles(owner: string, repo: string, pullNumber: number): Promise<Array<{
        filename: string;
        status: string;
        changes: number;
    }>>;
    createRelease(owner: string, repo: string, tagName: string, options?: {
        name?: string;
        body?: string;
        draft?: boolean;
        prerelease?: boolean;
        targetCommitish?: string;
    }): Promise<GitHubRelease>;
    generateReleaseNotes(owner: string, repo: string, tagName: string, previousTag?: string): Promise<string>;
    getRepoStats(owner: string, repo: string): Promise<RepoStats>;
    getRateLimit(): Promise<{
        limit: number;
        remaining: number;
        resetAt: Date;
    }>;
    private mapIssue;
    private mapPullRequest;
    private mapRelease;
    private calculateHealthScore;
}
