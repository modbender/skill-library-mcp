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

program
    .requiredOption('--summary <text>', 'Event title')
    .requiredOption('--start <time>', 'Start time (YYYY-MM-DD HH:mm)')
    .requiredOption('--end <time>', 'End time (YYYY-MM-DD HH:mm)')
    .option('--desc <text>', 'Description')
    .option('--calendar <id>', 'Target Calendar ID')
    .option('--attendees <ids>', 'Comma-separated user OpenIDs to invite')
    .parse(process.argv);

const options = program.opts();

async function createEvent() {
    try {
        const startTs = Math.floor(new Date(options.start).getTime() / 1000);
        const endTs = Math.floor(new Date(options.end).getTime() / 1000);

        if (isNaN(startTs) || isNaN(endTs)) {
            console.error('Invalid date format.');
            process.exit(1);
        }

        // Auto-discover calendar if not provided
        let targetCalendarId = options.calendar;
        if (!targetCalendarId) {
             try {
                 const calList = await client.calendar.calendar.list();
                 if (calList.code === 0 && calList.data.calendar_list && calList.data.calendar_list.length > 0) {
                     // Prefer 'OpenClaw Assistant', then 'primary', then first in list
                     const botCal = calList.data.calendar_list.find(c => c.summary === 'OpenClaw Assistant') || calList.data.calendar_list[0];
                     targetCalendarId = botCal.calendar_id;
                     console.log(`Auto-selected calendar: ${botCal.summary} (${targetCalendarId})`);
                 }
             } catch (e) {
                 console.warn("Failed to auto-discover calendar:", e.message);
             }
        }

        if (!targetCalendarId) {
            console.error("No calendar found. Please create one first.");
            process.exit(1);
        }

        const attendees = [];
        if (options.attendees) {
            options.attendees.split(',').forEach(id => {
                attendees.push({
                    type: 'user',
                    user_id: id.trim()
                });
            });
        }

        console.log(`Creating event on calendar: ${targetCalendarId}`);

        // Direct Request with Fallback
        
        async function tryCreate(calId) {
            return await client.request({
                method: 'POST',
                url: `/open-apis/calendar/v4/calendars/${encodeURIComponent(calId)}/events?user_id_type=open_id`,
                data: {
                    summary: options.summary,
                    description: options.desc || '',
                    need_notification: true, // Explicitly request notification
                    start_time: { timestamp: String(startTs), timezone: 'Asia/Shanghai' },
                    end_time: { timestamp: String(endTs), timezone: 'Asia/Shanghai' },
                    attendees: attendees.length > 0 ? attendees : undefined,
                    vchat: { vc_type: 'no_meeting' }
                }
            });
        }

        let response = await tryCreate(targetCalendarId);

        // Fallback to primary if specific ID fails (permission issue)
        if (response.code !== 0 && targetCalendarId !== 'primary') {
             console.log(`Creation failed on ${targetCalendarId} (${response.code}). Retrying on 'primary'...`);
             response = await tryCreate('primary');
        }

        if (response.code !== 0) {
            console.error(`Feishu API Error: ${response.msg} (Code: ${response.code})`);
            process.exit(1);
        }

        const evt = response.data.event;
        console.log(`✅ Event Created: ${evt.summary}`);
        console.log(`   Time: ${new Date(parseInt(evt.start_time.timestamp)*1000).toLocaleString()}`);
        console.log(`   Link: ${evt.app_link}`);

    } catch (e) {
        console.error('Error:', e.message);
        if (e.response) console.error('Data:', JSON.stringify(e.response.data));
    }
}

createEvent();
