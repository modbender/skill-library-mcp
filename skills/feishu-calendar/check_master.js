const CalendarManager = require('./lib/CalendarManager');
const { getTimestampCST } = require('../common/time-helper.js');
const manager = new CalendarManager();

(async () => {
    try {
        const calendar = await manager.getCalendar('Master');
        if (!calendar) {
            console.log("No accessible calendars found.");
            return;
        }

        console.log(`Using Calendar: ${calendar.summary} (ID: ${calendar.calendar_id})`);
        
        // List events for next 3 days
        const events = await manager.listEvents(calendar.calendar_id, Date.now(), Date.now() + 86400 * 3000, 50);

        if (events && events.length > 0) {
            console.log(`Found ${events.length} events.`);
            events.forEach(e => console.log(`- [${getTimestampCST(e.start_time.timestamp * 1000)}] ${e.summary}`));
        } else {
            console.log("No events found.");
        }
    } catch (e) {
        console.error("Error in check_master:", e.message);
    }
})();
