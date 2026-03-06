import type { ProjectManager } from './project_manager.js';

export class SessionContextCache {
    private currentContext: string | null = null;
    private lastUpdate: number = 0;
    private isBrainChecked: boolean = false;
    private readonly TTL = 60000; // 1 minute TTL

    async ensureContext(projectManager: ProjectManager): Promise<string | null> {
        const now = Date.now();

        // Return cached if still valid
        if (this.currentContext && (now - this.lastUpdate) < this.TTL) {
            return this.currentContext;
        }

        // Auto-load fresh context
        try {
            const project = projectManager.getCurrentProject();
            if (!project) return null;

            const overview = await projectManager.searchContext('Project Overview', 3);
            this.currentContext = overview;
            this.lastUpdate = now;
            console.error(`[SessionCache] Auto-loaded context for: ${project}`);
            return overview;
        } catch (err) {
            console.error(`[SessionCache] Failed to load context:`, err);
            return null;
        }
    }

    setBrainChecked(checked: boolean): void {
        this.isBrainChecked = checked;
    }

    hasBeenBrainChecked(): boolean {
        return this.isBrainChecked;
    }

    getContext(): string | null {
        return this.currentContext;
    }

    invalidate(): void {
        this.currentContext = null;
        this.lastUpdate = 0;
        this.isBrainChecked = false;
    }
}
