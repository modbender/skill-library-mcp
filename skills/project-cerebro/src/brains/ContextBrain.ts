import { Brain, BrainConfig } from '../core/Brain';
import { TaskStatus } from '../core/Task';
import { BrainStorage } from '../core/Storage';
import { Client } from 'discord.js';
import { ExecutionGraph } from '../core/ExecutionGraph';

export class ContextBrain extends Brain {
    private storage: BrainStorage;

    constructor(config: BrainConfig, client: Client, graph: ExecutionGraph) {
        super(config, client, graph);
        this.storage = new BrainStorage(this.id);
    }
    
    public async handleUserMessage(message: string): Promise<void> {
        const parts = message.split(' ');
        const command = parts[0].toLowerCase();
        const content = parts.slice(1).join(' ');

        if (command === '!log') {
            if (!content) {
                 await this.sendMessage("Usage: `!log <Entry>`");
                 return;
            }
            await this.storage.appendLog(content);
            await this.sendMessage("✅ Logged.");
        } 
        else if (command === '!read') {
            const logs = await this.storage.readTodayLog();
            if (!logs) {
                await this.sendMessage("📄 **Daily Log:**\n(Empty)");
            } else {
                // Discord limit is 2000 chars, might need truncation in real app
                await this.sendMessage(`📄 **Daily Log:**\n${logs.slice(-1900)}`);
            }
        }
        else if (command === '!context') {
             if (parts[1] === 'set') {
                 const newContext = parts.slice(2).join(' ');
                 await this.storage.updateContext(newContext);
                 await this.sendMessage("✅ Context updated.");
             } else {
                 const ctx = await this.storage.getContext();
                 await this.sendMessage(`🧠 **Current Context:**\n${ctx}`);
             }
        }
        else if (message.startsWith('!task')) {
             const title = message.replace('!task', '').trim() || 'Manual Task';
            await this.graph.createTask({
                id: Date.now().toString(),
                brainId: this.id,
                status: TaskStatus.READY,
                title: title,
                payload: {},
                dependencies: [],
                createdAt: Date.now(),
                updatedAt: Date.now(),
                attempts: 0
            });
            await this.sendMessage(`✅ Task "${title}" created.`);
        }
    }
}
