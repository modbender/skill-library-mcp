const { Client } = require('@larksuiteoapi/node-sdk');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });

const APP_ID = process.env.FEISHU_APP_ID;
const APP_SECRET = process.env.FEISHU_APP_SECRET;

if (!APP_ID || !APP_SECRET) {
    console.error('Error: FEISHU_APP_ID or FEISHU_APP_SECRET not found in .env');
    process.exit(1);
}

const client = new Client({ appId: APP_ID, appSecret: APP_SECRET });

async function checkCalendar(hours = 24) {
    console.log(`Checking primary calendar for events in next ${hours} hours...`);
    
    try {
        // 1. List calendars to find primary
        const listRes = await client.calendar.calendar.list();
        if (listRes.code !== 0) {
            throw new Error(`Failed to list calendars: ${listRes.msg}`);
        }
        
        const calendars = listRes.data.calendar_list;
        if (!calendars || calendars.length === 0) {
            console.log('No calendars found.');
            return;
        }

        // Assume first calendar is primary or look for "primary" flag
        let primaryCal = calendars[0];
        let calendarId = primaryCal.calendar_id;
        
        const calendarArgIndex = process.argv.indexOf('--calendar');
        if (calendarArgIndex !== -1 && calendarArgIndex + 1 < process.argv.length) {
            const requestedId = process.argv[calendarArgIndex + 1];
            const found = calendars.find(c => c.calendar_id === requestedId);
            if (found) {
                primaryCal = found;
                calendarId = requestedId;
            } else {
                console.warn(`Calendar ID ${requestedId} not found in list. Using default: ${primaryCal.summary}`);
            }
        }

        console.log(`Using Calendar: ${primaryCal.summary} (ID: ${calendarId})`);

        // 2. List events
        const now = Math.floor(Date.now() / 1000);
        const endTime = now + (hours * 3600);
        
        let eventRes = await client.calendar.calendarEvent.list({
            path: { calendar_id: calendarId },
            params: {
                start_time: String(now),
                end_time: String(endTime),
                page_size: 50
            }
        });

        // Fallback for permission errors on specific IDs
        if (eventRes.code !== 0 && calendarId !== 'primary') {
             console.log(`Failed to access calendar ${calendarId} (${eventRes.code}: ${eventRes.msg}). Falling back to 'primary'...`);
             eventRes = await client.calendar.calendarEvent.list({
                path: { calendar_id: 'primary' },
                params: {
                    start_time: String(now),
                    end_time: String(endTime),
                    page_size: 50
                }
            });
            if (eventRes.code === 0) {
                console.log(`Using 'primary' calendar instead.`);
            }
        }

        if (eventRes.code !== 0) {
            throw new Error(`Failed to list events: ${eventRes.msg}`);
        }

        const events = eventRes.data.items || [];
        if (events.length === 0) {
            console.log(`No events found in the next ${hours} hours.`);
        } else {
            console.log(`Found ${events.length} upcoming events:`);
            events.forEach(e => {
                const start = new Date(parseInt(e.start_time.timestamp) * 1000).toLocaleString();
                console.log(`- [${start}] ${e.summary || '(No Title)'}`);
            });
        }

    } catch (error) {
        console.error('Error checking calendar:', error.message);
        process.exit(1);
    }
}

// Parse args
const args = process.argv.slice(2);
let hours = 24;
if (args.includes('--next')) {
    const idx = args.indexOf('--next');
    if (idx + 1 < args.length) {
        hours = parseInt(args[idx + 1], 10) || 24;
    }
}

checkCalendar(hours);
