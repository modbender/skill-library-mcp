import * as fs from 'fs';
import * as path from 'path';

export class BrainStorage {
    private basePath: string;
    private reportsPath: string;
    private brainId: string;

    constructor(brainId: string) {
        this.brainId = brainId;
        this.basePath = path.join(process.cwd(), 'data', brainId);
        this.reportsPath = path.join(this.basePath, 'reports');
        if (!fs.existsSync(this.basePath)) {
            fs.mkdirSync(this.basePath, { recursive: true });
        }
        if (!fs.existsSync(this.reportsPath)) {
            fs.mkdirSync(this.reportsPath, { recursive: true });
        }
    }

    public async appendLog(content: string): Promise<void> {
        const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
        const logFile = path.join(this.basePath, `${date}.md`);
        const timestamp = new Date().toLocaleTimeString();
        const entry = `\n[${timestamp}] ${content}`;
        
        await fs.promises.appendFile(logFile, entry);
    }

    public async readTodayLog(): Promise<string> {
        const date = new Date().toISOString().split('T')[0];
        const logFile = path.join(this.basePath, `${date}.md`);
        
        try {
            return await fs.promises.readFile(logFile, 'utf-8');
        } catch (e) {
            return '';
        }
    }
    
    public async updateContext(content: string): Promise<void> {
        const contextFile = path.join(this.basePath, 'CONTEXT.md');
        await fs.promises.writeFile(contextFile, content);
    }

    public async getContext(): Promise<string> {
         const contextFile = path.join(this.basePath, 'CONTEXT.md');
         try {
             return await fs.promises.readFile(contextFile, 'utf-8');
         } catch (e) {
             return 'No context defined.';
         }
    }

    public async writeReport(kind: 'morning' | 'night', content: string, date?: string): Promise<void> {
        const reportDate = date || new Date().toISOString().split('T')[0];
        const reportFile = path.join(this.reportsPath, `${reportDate}-${kind}.md`);
        const timestamp = new Date().toLocaleTimeString();
        const entry = `\n\n---\n[${timestamp}] ${kind.toUpperCase()} RUN\n\n${content}\n`;
        try {
            await fs.promises.access(reportFile, fs.constants.F_OK);
            await fs.promises.appendFile(reportFile, entry);
        } catch (e) {
            await fs.promises.writeFile(reportFile, `# ${reportDate} ${kind.toUpperCase()} REPORTS\n${entry.trimStart()}`);
        }
    }

    public async readReport(kind: 'morning' | 'night', date?: string): Promise<string> {
        const reportDate = date || new Date().toISOString().split('T')[0];
        const reportFile = path.join(this.reportsPath, `${reportDate}-${kind}.md`);
        try {
            return await fs.promises.readFile(reportFile, 'utf-8');
        } catch (e) {
            return '';
        }
    }

    public async readReportsForDate(date?: string): Promise<{ kind: 'morning' | 'night'; content: string }[]> {
        const reportDate = date || new Date().toISOString().split('T')[0];
        const reports: { kind: 'morning' | 'night'; content: string }[] = [];
        for (const kind of ['morning', 'night'] as const) {
            const content = await this.readReport(kind, reportDate);
            if (content && content.trim().length > 0) {
                reports.push({ kind, content });
            }
        }
        return reports;
    }
}
