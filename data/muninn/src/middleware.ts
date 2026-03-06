/**
 * MUNINN MIDDLEWARE - Brain-First Enforcement
 * 
 * This middleware automatically enriches tool calls with Muninn memory context.
 * It implements the "Brain-First" policy by intercepting critical tool calls
 * and injecting relevant project context before execution.
 * 
 * Architecture:
 * - Intercepts all tool calls
 * - For critical tools (filesystem, git, etc.), auto-loads relevant memory
 * - Enriches responses with contextual information
 * - Transparent to the AI - happens automatically
 */

import type { ProjectManager } from './types.js';

// Tools that ALWAYS need context
const CRITICAL_TOOLS = [
    'filesystem_read',
    'filesystem_write',
    'filesystem_write_test',
    'git_diff',
    'git_status',
    'execute_command',
    'replace_file_content',
    'multi_replace_file_content',
    'write_to_file',
    'view_file',
    'view_code_item',
    'edit_file',
    'create_file',
    'delete_file',
    'grep_search',
    'find_by_name'
];

// Tools that might benefit from context
const CONTEXTUAL_TOOLS = [
    'list_dir',
    'run_command'
];

export class MuninnMiddleware {
    constructor(private projectManager: ProjectManager) { }

    /**
     * Intercept a tool call and enrich it with Muninn context
     */
    async interceptToolCall(toolName: string, args: any): Promise<ContextInjection | null> {
        // Skip if no active project
        if (!this.projectManager.getCurrentProject()) {
            return null;
        }

        // Check if this tool needs context
        const needsContext = CRITICAL_TOOLS.includes(toolName) || CONTEXTUAL_TOOLS.includes(toolName);
        if (!needsContext) {
            return null;
        }

        // Infer the query from the tool call
        const query = this.inferQueryFromTool(toolName, args);
        if (!query) {
            return null;
        }

        try {
            // Search Muninn for relevant context
            const memoryContext = await this.projectManager.searchContext(query, 3);

            if (!memoryContext || memoryContext.includes('No matches found')) {
                return null;
            }

            return {
                memoryContext,
                query,
                toolName,
                isCritical: CRITICAL_TOOLS.includes(toolName)
            };
        } catch (err) {
            console.error(`[Middleware] Failed to fetch context for ${toolName}:`, err);
            return null;
        }
    }

    /**
     * Infer a search query from tool arguments
     */
    private inferQueryFromTool(toolName: string, args: any): string | null {
        // File-based tools
        if (args.AbsolutePath || args.TargetFile || args.File) {
            const filePath = args.AbsolutePath || args.TargetFile || args.File;
            const fileName = filePath.split('/').pop();
            return `file: ${fileName}`;
        }

        // Search tools
        if (args.Query) {
            return args.Query;
        }

        // Pattern-based tools
        if (args.Pattern) {
            return args.Pattern;
        }

        // Command execution
        if (args.CommandLine) {
            const command = args.CommandLine.split(' ')[0];
            return `command: ${command}`;
        }

        // Directory operations
        if (args.DirectoryPath) {
            const dirName = args.DirectoryPath.split('/').pop();
            return `directory: ${dirName}`;
        }

        // Generic context query
        return 'relevant context';
    }

    /**
     * Format context for injection into tool response
     */
    formatContextInjection(injection: ContextInjection): string {
        const prefix = injection.isCritical ? '🧠 **CRITICAL CONTEXT**' : '📚 **Relevant Context**';

        return `${prefix} (auto-loaded from Muninn)
Query: "${injection.query}"

${injection.memoryContext}

---
`;
    }

    /**
     * Suggest next tools based on current context
     */
    suggestNextTools(toolName: string, context: string): string[] {
        const suggestions: string[] = [];

        // If we just searched for context, suggest related tools
        if (toolName === 'search_context') {
            if (context.includes('file:') || context.includes('.ts') || context.includes('.js')) {
                suggestions.push('view_file', 'view_code_item');
            }
            if (context.includes('architecture') || context.includes('design')) {
                suggestions.push('list_dir', 'grep_search');
            }
        }

        // If we read a file, suggest checking git status
        if (toolName === 'view_file' || toolName === 'filesystem_read') {
            suggestions.push('git_status', 'grep_search');
        }

        // If we modified code, suggest verification
        if (toolName.includes('write') || toolName.includes('replace')) {
            suggestions.push('run_command', 'view_file');
        }

        return suggestions;
    }
}

export interface ContextInjection {
    memoryContext: string;
    query: string;
    toolName: string;
    isCritical: boolean;
}
