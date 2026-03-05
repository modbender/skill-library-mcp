/**
 * Type definitions for Muninn MCP Server
 */

export interface ProjectManager {
    getCurrentProject(): string | null;
    searchContext(query: string, limit?: number): Promise<string>;
    addMemory(title: string, content: string, category?: string): Promise<string>;
    initProject(projectPath: string): Promise<string>;
    indexProject(projectPath: string): Promise<string>;
    setActiveProject(projectPath: string): Promise<void>;
    isInitialized(projectPath: string): Promise<boolean>;
    autoDetectProject(): Promise<string | null>;
}

export interface MuninnConfig {
    version: string;
    projectName: string;
    createdAt: string;
    autoIndex: boolean;
    watchDebounceMs: number;
}
