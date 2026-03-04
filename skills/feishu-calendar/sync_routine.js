const CalendarManager = require('./lib/CalendarManager');
const manager = new CalendarManager();

async function addRoutineEvents() {
    console.log('📅 Syncing Routine Tasks to Calendar (via CalendarManager)...');
    
    // 1. Find Bot Calendar
    const botCal = await manager.getCalendar('OpenClaw Assistant');
    if (!botCal) return console.error("Calendar not found");

    // 2. Define Routine Events
    const routines = [
        {
            summary: '🛡️ System Maintenance (Auto-Restart)',
            description: 'Automated health check and process restart to prevent memory leaks.',
            hour: 4, // 04:00 UTC
            minute: 0,
            duration: 300, // 5 mins
            rrule: 'FREQ=DAILY',
            color: -1
        },
        {
            summary: '🌅 Morning Briefing',
            description: 'Generate and send a morning briefing card (yesterday highlights + today agenda) to Master.',
            hour: 1, // 01:30 UTC = 09:30 CST
            minute: 30, 
            duration: 300, // 5 mins
            rrule: 'FREQ=DAILY',
            color: -1
        },
        {
            summary: '📝 Xiaoxia\'s Diary',
            description: 'Reflect on the day, write diary, and update Feishu Doc.',
            hour: 20, // 20:00 UTC = 04:00 CST (next day) -- wait, 20:00 UTC is late.
            minute: 0,
            duration: 900, // 15 mins
            rrule: 'FREQ=DAILY',
            color: -1 
        },
        {
            summary: '🦐 ClawdChat Check',
            description: 'Check community feed and interact with other agents.',
            hour: 0, 
            minute: 0,
            duration: 300, // 5 mins
            rrule: 'FREQ=DAILY;INTERVAL=1;BYHOUR=0,4,8,12,16,20', // Every 4 hours
            color: -1
        },
        {
            summary: '🔄 Calendar Sync',
            description: 'Check for new tasks and sync heartbeat state.',
            hour: 0,
            minute: 15,
            duration: 60, // 1 min
            rrule: 'FREQ=HOURLY;INTERVAL=1;BYMINUTE=15,45',
            color: -1
        }
    ];

    // 3. Create Events
    const now = new Date();
    
    for (const task of routines) {
        console.log(`Scheduling: ${task.summary}`);
        
        // Calculate next occurrence for start_time
        const start = new Date(now);
        start.setUTCHours(task.hour, task.minute, 0, 0);
        if (start < now) start.setDate(start.getDate() + 1);
        
        const startTs = Math.floor(start.getTime() / 1000);
        const endTs = startTs + task.duration;

        const eventData = {
            summary: task.summary,
            description: task.description,
            start_time: { timestamp: String(startTs), timezone: 'UTC' },
            end_time: { timestamp: String(endTs), timezone: 'UTC' },
            recurrence: task.rrule,
            permissions: 'public'
        };

        const res = await manager.addEvent(botCal.calendar_id, eventData);
        if (res) console.log(`✅ Added: ${task.summary}`);
        else console.error(`❌ Failed ${task.summary}`);
    }
}

addRoutineEvents();
