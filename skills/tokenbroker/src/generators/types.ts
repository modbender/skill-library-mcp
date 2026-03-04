/**
 * Shared types for the TokenBroker generators
 */

/**
 * Repository analysis data - input for all generators
 */
export interface RepoAnalysis {
    /** Repository owner/username */
    owner: string;
    /** Repository name */
    repoName: string;
    /** Repository description */
    description: string;
    /** Primary programming language */
    language: string;
    /** Number of stars */
    stars: number;
    /** Number of forks */
    forks: number;
    /** Number of open issues */
    openIssues: number;
    /** License type */
    license: string | null;
    /** Repository creation date */
    createdAt: string;
    /** Last updated date */
    updatedAt: string;
    /** Readme content */
    readme: string;
    /** List of main features/capabilities */
    features: string[];
    /** Technology stack detected */
    techStack: string[];
    /** Contributor count */
    contributors: number;
    /** Recent commit activity (last 30 days) */
    recentCommits: number;
    /** Whether the project appears active */
    isActive: boolean;
}
