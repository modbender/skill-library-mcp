const Lark = require('@larksuiteoapi/node-sdk');
require('dotenv').config({ path: require('path').resolve(__dirname, '../../../.env') });

class CalendarManager {
    constructor() {
        this.client = new Lark.Client({
            appId: process.env.FEISHU_APP_ID,
            appSecret: process.env.FEISHU_APP_SECRET
        });
    }

    async getCalendar(searchKeyword = 'Master') {
        try {
            const listRes = await this.client.calendar.calendar.list();
            if (listRes.code !== 0) throw new Error(`List calendars failed: ${listRes.msg}`);
            
            const calendars = listRes.data.calendar_list || [];
            let target = calendars.find(c => c.summary.includes(searchKeyword) || c.summary.includes("OpenClaw"));
            if (!target && calendars.length > 0) target = calendars[0]; // Fallback

            return target;
        } catch (e) {
            console.error(`[CalendarManager] Error getting calendar: ${e.message}`);
            return null;
        }
    }

    async listEvents(calendarId, startTime = Date.now(), endTime = Date.now() + 86400 * 3000, pageSize = 50) {
        try {
            const params = {
                start_time: String(Math.floor(startTime / 1000)),
                end_time: String(Math.floor(endTime / 1000)),
                page_size: pageSize
            };

            let res = await this.client.calendar.calendarEvent.list({
                path: { calendar_id: calendarId },
                params: params
            });

            if (res.code !== 0) {
                if (calendarId !== 'primary') {
                    console.log(`[CalendarManager] Access failed for ID ${calendarId}, falling back to 'primary'...`);
                    res = await this.client.calendar.calendarEvent.list({
                        path: { calendar_id: 'primary' },
                        params: params
                    });
                }
            }

            if (res.code !== 0) throw new Error(`Fetch events failed: ${res.msg}`);
            return res.data.items || [];
        } catch (e) {
            console.error(`[CalendarManager] Error listing events: ${e.message}`);
            return [];
        }
    }

    async addEvent(calendarId, eventData) {
        try {
            // eventData structure: { summary, description, start_time, end_time, recurrence, ... }
            // Ensure timestamps are strings
            if (typeof eventData.start_time.timestamp === 'number') eventData.start_time.timestamp = String(eventData.start_time.timestamp);
            if (typeof eventData.end_time.timestamp === 'number') eventData.end_time.timestamp = String(eventData.end_time.timestamp);

            const res = await this.client.calendar.calendarEvent.create({
                path: { calendar_id: calendarId },
                data: eventData
            });

            if (res.code !== 0) {
                 if (calendarId !== 'primary') {
                    console.log(`[CalendarManager] Create failed for ID ${calendarId}, falling back to 'primary'...`);
                    return await this.client.calendar.calendarEvent.create({
                        path: { calendar_id: 'primary' },
                        data: eventData
                    });
                }
                throw new Error(`Create event failed: ${res.msg}`);
            }
            return res.data;
        } catch (e) {
            console.error(`[CalendarManager] Error adding event: ${e.message}`);
            return null;
        }
    }
}

module.exports = CalendarManager;
