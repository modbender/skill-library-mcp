import { Client, GatewayIntentBits, Message } from 'discord.js';
import * as dotenv from 'dotenv';
import { Brain } from './Brain';
import { ExecutionGraph } from './ExecutionGraph';
import * as path from 'path';

dotenv.config();

export class CerebroRuntime {
    private client: Client;
    private brains: Map<string, Brain> = new Map();
    private heartbeatInterval: NodeJS.Timeout | null = null;
    private channelMap: Map<string, string> = new Map(); // ChannelID -> BrainID
    private lastReportSyncAt: number = 0;
    public graph: ExecutionGraph;

    public getBrains(): Brain[] {
        return Array.from(this.brains.values());
    }

    constructor() {
        this.client = new Client({
            intents: [
                GatewayIntentBits.Guilds,
                GatewayIntentBits.GuildMessages,
                GatewayIntentBits.MessageContent
            ]
        });

        // Initialize Graph (DB)
        const dbPath = path.join(process.cwd(), 'cerebro.db');
        this.graph = new ExecutionGraph(dbPath);

        this.client.on('ready', () => {
            console.log(`Cerebro Online. Logged in as ${this.client.user?.tag}`);
            this.startHeartbeat();
        });

        this.client.on('messageCreate', this.handleMessage.bind(this));
    }

    public registerBrain(brain: Brain) {
        this.brains.set(brain.id, brain);
        // @ts-ignore - Accessing protected property for setup
        this.channelMap.set(brain.discordChannelId, brain.id);
        console.log(`Registered brain: ${brain.name} -> ${brain.id}`);
    }

    public async start(token: string) {
        await this.client.login(token);
    }

    private startHeartbeat() {
        if (this.heartbeatInterval) clearInterval(this.heartbeatInterval);
        
        console.log('Starting heartbeat loop (30s)...');
        this.heartbeatInterval = setInterval(async () => {
            
            // 1. Sync report schedules (config-driven)
            await this.syncReportSchedules();

            // 2. Evaluate Graph (Promote Waiting -> Ready)
            await this.graph.evaluateGraph();

            // 3. Spawn due recurring tasks
            await this.evaluateRecurringTasks();

            // 4. Tick Brains
            this.brains.forEach(async (brain) => {
                try {
                    await brain.onHeartbeat();
                } catch (e) {
                    console.error(`Error in heartbeat for ${brain.name}:`, e);
                }
            });
        }, 30000); // 30s heartbeat
    }

    private async evaluateRecurringTasks(): Promise<void> {
        const now = Date.now();
        const due = await this.graph.getDueRecurringTasks(now);

        for (const recurring of due) {
            const taskId = now.toString() + '-' + Math.floor(Math.random() * 1000).toString();
            await this.graph.createTask({
                id: taskId,
                brainId: recurring.brainId,
                brainName: recurring.brainName,
                status: 'READY' as any,
                title: recurring.title,
                description: recurring.description,
                payload: { recurringTaskId: recurring.id },
                modelOverride: recurring.modelOverride,
                dependencies: [],
                executeAt: now,
                createdAt: now,
                updatedAt: now,
                attempts: 0
            });

            const nextRunAt = this.computeNextRunAt(recurring, now);
            await this.graph.updateRecurringTaskNextRun(recurring.id, nextRunAt, now);
        }
    }

    private async syncReportSchedules(): Promise<void> {
        // IMPORTANT: The frontend/DB is the source of truth for which recurring tasks exist.
        // We do not auto-create or overwrite recurring tasks from backend templates by default.
        // If you want the legacy "system task bootstrap" behavior, set:
        //   CEREBRO_MANAGE_SYSTEM_RECURRING=true
        const manageSystemRecurring = process.env.CEREBRO_MANAGE_SYSTEM_RECURRING === 'true';
        if (!manageSystemRecurring) return;

        const now = Date.now();
        if (now - this.lastReportSyncAt < 5 * 60 * 1000) return; // every 5 minutes
        this.lastReportSyncAt = now;

        const brains = this.getBrains();
        for (const brain of brains) {
            const record = await this.graph.getBrainConfig(brain.id);
            if (!record?.config) continue;

            let cfg: any = {};
            try {
                cfg = JSON.parse(record.config || '{}');
            } catch (e) {
                continue;
            }

            if (!cfg.reportTiming || !cfg.reporting?.enabled) continue;

            const existing = await this.graph.getRecurringTasksByBrain(brain.id);
            const ensureReportTask = async (kind: 'morning' | 'night') => {
                const timing = cfg.reportTiming?.[kind];
                if (!timing || typeof timing !== 'string' || !timing.includes(':')) return;
                const [h, m] = timing.split(':');
                const hour = Number(h);
                const minute = Number(m || 0);
                if (Number.isNaN(hour) || Number.isNaN(minute)) return;

                const scheduleConfig = { hour, minute };
                const marker = `REPORT_KIND:${kind}`;
                const title = `${brain.name} Report (${kind})`;
                const baseDesc = `${marker}
Generate the ${kind} report for ${brain.name}. Write markdown to data/${brain.id}/reports/YYYY-MM-DD-${kind}.md.
Always keep report concise, structured, and ready for Daily Digest.
Location: (use local timezone). Timezone: America/Chicago.`;
                const personalExtras = `\nPersonal Life requirements:
- The merged schedule from \`get-schedule.js\` will be pre-injected into your prompt as Context. Treat it as the single source of truth for the calendar.
- Do NOT run \`node dist/scripts/get-schedule.js\` again unless the Context block is missing.
- List events chronologically with no calendar headings.
- Log events added today.
- Compute latest bedtime = earliest event tomorrow (from the script output) minus 10 hours.
- Update memory file at memory/personal-life.md with current calendar model + preferences.`;
                const description = brain.id === 'personal' ? baseDesc + personalExtras : baseDesc;

                const existingTask = existing.find(t => (t.description || '').includes(marker));
                const nextRunAt = this.computeNextRunAt({ scheduleType: 'DAILY', scheduleConfig: JSON.stringify(scheduleConfig) } as any, now);

                if (!existingTask) {
                    await this.graph.createRecurringTask({
                        id: `${brain.id}-report-${kind}`,
                        brainId: brain.id,
                        brainName: brain.name,
                        title,
                        description,
                        modelOverride: cfg.reporting?.modelOverride,
                        scheduleType: 'DAILY',
                        scheduleConfig: JSON.stringify(scheduleConfig),
                        nextRunAt,
                        lastRunAt: undefined,
                        enabled: true,
                        createdAt: now,
                        updatedAt: now
                    });
                } else {
                    await this.graph.updateRecurringTaskSchedule(existingTask.id, 'DAILY', JSON.stringify(scheduleConfig), undefined, nextRunAt);
                    if (existingTask.title !== title || existingTask.description !== description) {
                        await this.graph.deleteRecurringTask(existingTask.id);
                        await this.graph.createRecurringTask({
                            id: `${brain.id}-report-${kind}`,
                            brainId: brain.id,
                            brainName: brain.name,
                            title,
                            description,
                            modelOverride: cfg.reporting?.modelOverride,
                            scheduleType: 'DAILY',
                            scheduleConfig: JSON.stringify(scheduleConfig),
                            nextRunAt,
                            lastRunAt: existingTask.lastRunAt,
                            enabled: existingTask.enabled,
                            createdAt: existingTask.createdAt,
                            updatedAt: now
                        });
                    }
                }
            };

            await ensureReportTask('morning');
            await ensureReportTask('night');

            // Personal Life proactive planning tasks
            if (brain.id === 'personal') {
                const planningCfg = cfg.personalPlanning || { morning: '09:30', night: '20:30' };
                const ensurePlanningTask = async (kind: 'morning' | 'night') => {
                    const timing = planningCfg?.[kind];
                    if (!timing || typeof timing !== 'string' || !timing.includes(':')) return;
                    const [h, m] = timing.split(':');
                    const hour = Number(h);
                    const minute = Number(m || 0);
                    if (Number.isNaN(hour) || Number.isNaN(minute)) return;

                    const scheduleConfig = { hour, minute };
                    const marker = `PERSONAL_PLANNING_KIND:${kind}`;
                    const title = `Personal Life Planning (${kind})`;
                    const description = `${marker}
Update the personal calendar model and proactively schedule energizing/healthy activities inside free slots.
Location: (use local timezone). Timezone: America/Chicago.

**SCHEDULE CONTEXT (pre-injected)**
The merged schedule from \`get-schedule.js\` will already be included below in a Context block (America/Chicago). Use that output as the single source of truth.
Do **NOT** re-run \`node dist/scripts/get-schedule.js\` unless the Context block is missing.

**STEP 2: PLAN**
Rules:
- Only schedule between 09:00–23:00.
- Prefer lunch around 13:00 but choose best mid-to-late-day slot dynamically.
- Avoid scheduling over lunch.
- DO NOT schedule study sessions or school-related tasks (school brain handles study blocks).
- Use Personal Brain config: prioritize items in \`proactiveActivities\` (hobbies, fun, energizing). If empty, suggest gym, walks, recovery, creative time.
- Respect higher-priority school blocks (from script output).
- Use 12-hour AM/PM time format in any summaries or logs.
- After adding events, send a Discord message confirming what was added.
- Log all added events in data/personal/reports/YYYY-MM-DD-${kind}.md and update memory/personal-life.md.
`;

                    const existingPlanning = existing.find(t => (t.description || '').includes(marker));
                    const nextRunAt = this.computeNextRunAt({ scheduleType: 'DAILY', scheduleConfig: JSON.stringify(scheduleConfig) } as any, now);
                    if (!existingPlanning) {
                        await this.graph.createRecurringTask({
                            id: `personal-planning-${kind}`,
                            brainId: brain.id,
                            brainName: brain.name,
                            title,
                            description,
                            modelOverride: cfg.reporting?.modelOverride,
                            scheduleType: 'DAILY',
                            scheduleConfig: JSON.stringify(scheduleConfig),
                            nextRunAt,
                            lastRunAt: undefined,
                            enabled: true,
                            createdAt: now,
                            updatedAt: now
                        });
                    } else {
                        await this.graph.updateRecurringTaskSchedule(existingPlanning.id, 'DAILY', JSON.stringify(scheduleConfig), undefined, nextRunAt);
                        // Also ensure description updates
                        if (existingPlanning.description !== description) {
                             await this.graph.deleteRecurringTask(existingPlanning.id);
                             await this.graph.createRecurringTask({
                                id: `personal-planning-${kind}`,
                                brainId: brain.id,
                                brainName: brain.name,
                                title,
                                description,
                                modelOverride: cfg.reporting?.modelOverride,
                                scheduleType: 'DAILY',
                                scheduleConfig: JSON.stringify(scheduleConfig),
                                nextRunAt,
                                lastRunAt: existingPlanning.lastRunAt,
                                enabled: existingPlanning.enabled,
                                createdAt: existingPlanning.createdAt,
                                updatedAt: now
                            });
                        }
                    }
                };

                await ensurePlanningTask('morning');
                await ensurePlanningTask('night');
            }

            // Schoolwork planning tasks (config-driven)
            if (brain.id === 'school') {
                const planningCfg = cfg.schoolPlanning || { morning: '09:30', night: '20:30' };
                const ensureSchoolPlanning = async (kind: 'morning' | 'night') => {
                    const timing = planningCfg?.[kind];
                    if (!timing || typeof timing !== 'string' || !timing.includes(':')) return;
                    const [h, m] = timing.split(':');
                    const hour = Number(h);
                    const minute = Number(m || 0);
                    if (Number.isNaN(hour) || Number.isNaN(minute)) return;

                    const scheduleConfig = { hour, minute };
                    const marker = `SCHOOL_PLANNING_KIND:${kind}`;
                    const title = `Schoolwork Planning (${kind})`;
                    const description = `${marker}
1) Scan Todoist Inbox for labels @exam, @quiz, @homework, @research, @personal.
2) **CALENDAR CONTEXT (pre-injected)**: The merged schedule from \`get-schedule.js\` will be included in the prompt Context. Use it to find free slots. Do not query gog manually unless the Context block is missing.
3) Build a next-7-days timeline (today + 7d) grouped by date and label.
4) Auto-schedule study blocks using free slots (09:00–23:00):
   - Default: **1 study block per task** (homework/quiz/other).
   - Exams: **3 study blocks total**, spread across days before the due date.
   - Do not stack multiple blocks for non-exams.
   - NEVER schedule over any existing event from the schedule output.
5) If any task due < 48h is not scheduled, FORCE schedule and notify Discord.
6) Write report to data/school/reports/YYYY-MM-DD-${kind}.md with: timeline, blocks scheduled, escalations.
7) Use gog calendar (personal account) to add events; never delete events.
`;

                    const existingPlanning = existing.find(t => (t.description || '').includes(marker));
                    const nextRunAt = this.computeNextRunAt({ scheduleType: 'DAILY', scheduleConfig: JSON.stringify(scheduleConfig) } as any, now);
                    if (!existingPlanning) {
                        await this.graph.createRecurringTask({
                            id: `school-planning-${kind}`,
                            brainId: brain.id,
                            brainName: brain.name,
                            title,
                            description,
                            modelOverride: cfg.reporting?.modelOverride,
                            scheduleType: 'DAILY',
                            scheduleConfig: JSON.stringify(scheduleConfig),
                            nextRunAt,
                            lastRunAt: undefined,
                            enabled: true,
                            createdAt: now,
                            updatedAt: now
                        });
                    } else {
                        await this.graph.updateRecurringTaskSchedule(existingPlanning.id, 'DAILY', JSON.stringify(scheduleConfig), undefined, nextRunAt);
                        if (existingPlanning.description !== description) {
                             await this.graph.deleteRecurringTask(existingPlanning.id);
                             await this.graph.createRecurringTask({
                                id: `school-planning-${kind}`,
                                brainId: brain.id,
                                brainName: brain.name,
                                title,
                                description,
                                modelOverride: cfg.reporting?.modelOverride,
                                scheduleType: 'DAILY',
                                scheduleConfig: JSON.stringify(scheduleConfig),
                                nextRunAt,
                                lastRunAt: existingPlanning.lastRunAt,
                                enabled: existingPlanning.enabled,
                                createdAt: existingPlanning.createdAt,
                                updatedAt: now
                            });
                        }
                    }
                };

                await ensureSchoolPlanning('morning');
                await ensureSchoolPlanning('night');
            }

            // Money weekly search (config-driven)
            if (brain.id === 'money') {
                const runDay = cfg.scheduling?.weeklyRunDay ?? 1;
                const runTime = cfg.scheduling?.weeklyRunTime || '10:00';
                const [h, m] = String(runTime).split(':');
                const hour = Number(h);
                const minute = Number(m || 0);
                if (!Number.isNaN(hour) && !Number.isNaN(minute)) {
                    const scheduleConfig = { day: Number(runDay), hour, minute };
                    const title = 'Money Weekly Search';
                    const description = `MONEY_SEARCH
Spend ~${cfg.moneySearch?.weeklyHours || 2} hours searching the web for AI money-making opportunities and local small-business leads.
- Focus: forums, communities, local businesses, small business sites.
- Avoid: military/government, large corporations.
- Extract contact info (emails) from business sites when possible.
- Draft outreach emails and append to data/money/outreach-queue.json (do NOT send yet).
- Produce a markdown report in data/money/reports/YYYY-MM-DD-search.md with leads, sources, and draft snippets.
- Use office email only; do NOT use personal email.
`;
                    const existingWeekly = existing.find(t => t.id === 'money-weekly-search');
                    const nextRunAt = this.computeNextRunAt({ scheduleType: 'WEEKLY', scheduleConfig: JSON.stringify(scheduleConfig) } as any, now);
                    if (!existingWeekly) {
                        await this.graph.createRecurringTask({
                            id: 'money-weekly-search',
                            brainId: brain.id,
                            brainName: brain.name,
                            title,
                            description,
                            modelOverride: cfg.reporting?.modelOverride,
                            scheduleType: 'WEEKLY',
                            scheduleConfig: JSON.stringify(scheduleConfig),
                            nextRunAt,
                            lastRunAt: undefined,
                            enabled: true,
                            createdAt: now,
                            updatedAt: now
                        });
                    } else {
                        await this.graph.updateRecurringTaskSchedule(existingWeekly.id, 'WEEKLY', JSON.stringify(scheduleConfig), undefined, nextRunAt);
                    }
                }
            }
        }
    }

    public computeNextRunAt(recurring: any, fromTime: number): number {
        const cfg = recurring.scheduleConfig ? JSON.parse(recurring.scheduleConfig) : {};
        const base = new Date(fromTime);

        switch (recurring.scheduleType) {
            case 'HOURLY': {
                const minute = typeof cfg.minute === 'number' ? cfg.minute : 0;
                const next = new Date(base);
                next.setSeconds(0, 0);
                next.setMinutes(minute);
                if (next.getTime() <= fromTime) {
                    next.setHours(next.getHours() + 1);
                }
                return next.getTime();
            }
            case 'DAILY': {
                const hour = typeof cfg.hour === 'number' ? cfg.hour : 9;
                const minute = typeof cfg.minute === 'number' ? cfg.minute : 0;
                const next = new Date(base);
                next.setSeconds(0, 0);
                next.setHours(hour, minute, 0, 0);
                if (next.getTime() <= fromTime) {
                    next.setDate(next.getDate() + 1);
                }
                return next.getTime();
            }
            case 'WEEKLY': {
                const day = typeof cfg.day === 'number' ? cfg.day : 1; // 0=Sun
                const hour = typeof cfg.hour === 'number' ? cfg.hour : 9;
                const minute = typeof cfg.minute === 'number' ? cfg.minute : 0;
                const next = new Date(base);
                next.setSeconds(0, 0);
                next.setHours(hour, minute, 0, 0);
                const delta = (day - next.getDay() + 7) % 7;
                next.setDate(next.getDate() + (delta === 0 && next.getTime() <= fromTime ? 7 : delta));
                return next.getTime();
            }
            case 'INTERVAL':
            default: {
                const intervalMs = recurring.intervalMs || 60 * 60 * 1000;
                return fromTime + intervalMs;
            }
        }
    }

    private async handleMessage(message: Message) {
        // Allow bot messages only for task completion signals
        if (message.author.bot) {
            const match = message.content.match(/\u2063\u2063TASK_DONE:(.+?)\u2063/);
            if (match) {
                const taskId = match[1];
                try {
                    await this.graph.updateTaskStatus(taskId, 'COMPLETED' as any);
                    const brainId = this.channelMap.get(message.channelId);
                    const brain = brainId ? this.brains.get(brainId) : null;
                    if (brain) brain.status = 'IDLE';
                } catch (e) {
                    console.error('Failed to mark task complete:', e);
                }
            }
            return;
        }

        const brainId = this.channelMap.get(message.channelId);
        if (brainId) {
            const brain = this.brains.get(brainId);
            console.log(`Routing message from ${message.author.username} to ${brain?.name}`);
            
            // Delegate to the specific brain implementation
            if (brain) {
                await brain.handleUserMessage(message.content);
            }
        }
    }
}
