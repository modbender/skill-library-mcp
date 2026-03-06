const { program } = require('commander');
const Lark = require('@larksuiteoapi/node-sdk');
require('dotenv').config({ path: require('path').resolve(__dirname, '../../.env') });

const APP_ID = process.env.FEISHU_APP_ID;
const APP_SECRET = process.env.FEISHU_APP_SECRET;

if (!APP_ID || !APP_SECRET) {
    console.error('Error: FEISHU_APP_ID or FEISHU_APP_SECRET not set.');
    process.exit(1);
}

const client = new Lark.Client({
    appId: APP_ID,
    appSecret: APP_SECRET,
});

async function clearTestEvents() {
    try {
        console.log('🧹 Cleaning up test events...');
        
        // 1. Find Bot Calendar
        let botCalendarId;
        const calList = await client.calendar.calendar.list();
        if (calList.code === 0 && calList.data.calendar_list) {
            const botCal = calList.data.calendar_list.find(c => c.summary === 'OpenClaw Assistant');
            if (botCal) botCalendarId = botCal.calendar_id;
        }

        if (!botCalendarId) {
            // Try fallback
            try {
                const primary = await client.calendar.calendar.get({ calendar_id: 'primary' });
                if (primary.code === 0) botCalendarId = 'primary';
            } catch(e) {}
        }

        if (!botCalendarId) {
            console.error('❌ Bot calendar not found.');
            return;
        }

        // 2. List Events
        let res = await client.request({
            method: 'GET',
            url: `/open-apis/calendar/v4/calendars/${encodeURIComponent(botCalendarId)}/events`,
            params: { page_size: 50 }
        });
        
        // Fallback for list
        if (res.code !== 0 && botCalendarId !== 'primary') {
             console.log(`Access failed for ${botCalendarId}. Retrying primary...`);
             botCalendarId = 'primary';
             res = await client.request({
                method: 'GET',
                url: `/open-apis/calendar/v4/calendars/primary/events`,
                params: { page_size: 50 }
            });
        }

        if (res.code === 0 && res.data.items) {
            for (const evt of res.data.items) {
                if (evt.summary.includes('Test') || evt.summary.includes('Invite')) {
                    console.log(`🗑️ Deleting: ${evt.summary} (${evt.event_id})`);
                    await client.request({
                        method: 'DELETE',
                        url: `/open-apis/calendar/v4/calendars/${encodeURIComponent(botCalendarId)}/events/${evt.event_id}`
                    });
                }
            }
        }
    } catch (e) {
        console.error('Cleanup Error:', e.message);
    }
}

async function addMaintenanceSchedule() {
    try {
        console.log('📅 Adding Daily Maintenance Schedule...');
        
        // 1. Get calendar list to find appropriate target
        let botCalendarId;
        const calList = await client.calendar.calendar.list();
        if (calList.code === 0 && calList.data.calendar_list) {
            const botCal = calList.data.calendar_list.find(c => c.summary === 'OpenClaw Assistant');
            if (botCal) botCalendarId = botCal.calendar_id;
        }
        
        // If not found, default to primary immediately to avoid unnecessary checks
        if (!botCalendarId) botCalendarId = 'primary';

        // Recurrence Rule: Daily at 04:00 AM
        // RRULE:FREQ=DAILY;BYHOUR=4;BYMINUTE=0;BYSECOND=0
        
        // Create Recurring Event
        // Note: For recurring, start_time is the first instance
        const now = new Date();
        const tomorrow4am = new Date(now);
        tomorrow4am.setDate(now.getDate() + 1);
        tomorrow4am.setHours(4, 0, 0, 0);
        
        const startTs = Math.floor(tomorrow4am.getTime() / 1000);
        const endTs = startTs + 300; // 5 minutes duration
        
        // Helper to attempt creation
        async function create(calId) {
            return await client.request({
                method: 'POST',
                url: `/open-apis/calendar/v4/calendars/${encodeURIComponent(calId)}/events`,
                data: {
                    summary: '🛡️ System Maintenance (Auto-Restart)',
                    description: 'Routine system health check and gateway restart if idle.',
                    start_time: { timestamp: String(startTs), timezone: 'Asia/Shanghai' },
                    end_time: { timestamp: String(endTs), timezone: 'Asia/Shanghai' },
                    recurrence: 'FREQ=DAILY;INTERVAL=1', // Daily
                    color: -1, 
                    permissions: 'public'
                }
            });
        }

        let res = await create(botCalendarId);
        
        // Fallback retry if specific ID failed (e.g. permission error) and it wasn't already primary
        if (res.code !== 0 && botCalendarId !== 'primary') {
             console.log(`Creation failed on ${botCalendarId} (${res.code}). Retrying on 'primary'...`);
             res = await create('primary');
        }

        if (res.code === 0) {
            console.log(`✅ Maintenance Schedule Added: ${res.data.event.app_link}`);
        } else {
            console.error(`❌ Failed to add schedule: ${res.msg}`);
        }

    } catch (e) {
        console.error('Schedule Error:', e.message);
    }
}

(async () => {
    await clearTestEvents();
    await addMaintenanceSchedule();
})();
