import { ContextBrain } from './ContextBrain';
import { TaskStatus } from '../core/Task';

export class JobBrain extends ContextBrain {
    
    public async handleUserMessage(message: string): Promise<void> {
        const parts = message.split(' ');
        const command = parts[0].toLowerCase();

        if (command === '!job') {
            const sub = parts[1]?.toLowerCase();
            
            if (sub === 'add') {
                // Usage: !job add <Company> <Position> <URL>
                const company = parts[2];
                const position = parts[3];
                const url = parts[4] || '';
                
                if (!company || !position) {
                    await this.sendMessage("Usage: `!job add <Company> <Position> [URL]`");
                    return;
                }

                await this.graph.createJob({
                    id: Date.now().toString(),
                    company,
                    position,
                    url,
                    status: 'APPLIED',
                    notes: '',
                    dateApplied: Date.now(),
                    updatedAt: Date.now()
                });
                
                await this.sendMessage(`✅ Tracked application for **${position}** at **${company}**.`);
            } 
            else if (sub === 'list') {
                const jobs = await this.graph.getJobs();
                const list = jobs.slice(0, 10).map(j => 
                    `• \`${j.id}\` **${j.company}** - ${j.position} (${j.status})`
                ).join('\n');
                await this.sendMessage(list.length > 0 ? `**Recent Jobs:**\n${list}` : "No jobs tracked yet.");
            }
            else if (sub === 'remove' || sub === 'delete') {
                const id = parts[2];
                if (!id) {
                    await this.sendMessage("Usage: `!job remove <ID>`");
                    return;
                }
                await this.graph.deleteJob(id);
                await this.sendMessage(`✅ Removed job \`${id}\`.`);
            }
        } else {
            // Delegate non-job commands (!log, !read, !context, !task) to ContextBrain
            await super.handleUserMessage(message);
        }
    }
}
