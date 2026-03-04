/**
 * Calendar script — read calendar data via Google Calendar API.
 * 
 * Usage:
 *   node calendar.js --account <label> --action <action> [options]
 * 
 * Actions:
 *   list-calendars              List all calendars
 *   events                      List upcoming events
 *   get-event                   Get a specific event
 *   freebusy                    Check free/busy status
 * 
 * Options:
 *   --calendar <id>             Calendar ID (default: "primary")
 *   --days <number>             Number of days to look ahead (default: 7)
 *   --max <number>              Max results (default: 20)
 *   --event-id <id>             Event ID (for get-event)
 *   --query <text>              Search text for events
 */

const { google } = require('googleapis');
const { getAuthClient, parseArgs } = require('./shared');

const args = parseArgs(process.argv);

if (!args.account) {
  console.error('Usage: node calendar.js --account <label> --action <action>');
  process.exit(1);
}

const action = args.action || 'events';
const calendarId = args.calendar || 'primary';
const days = parseInt(args.days || '7', 10);
const maxResults = parseInt(args.max || '20', 10);

async function run() {
  const auth = getAuthClient(args.account);
  const calendar = google.calendar({ version: 'v3', auth });

  switch (action) {
    case 'list-calendars': {
      const res = await calendar.calendarList.list();
      const calendars = res.data.items || [];
      const output = calendars.map(c => ({
        id: c.id,
        summary: c.summary,
        description: c.description || null,
        primary: c.primary || false,
        accessRole: c.accessRole,
        timeZone: c.timeZone,
        backgroundColor: c.backgroundColor,
      }));
      console.log(JSON.stringify(output, null, 2));
      break;
    }

    case 'events': {
      const now = new Date();
      const future = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);
      
      const params = {
        calendarId,
        timeMin: now.toISOString(),
        timeMax: future.toISOString(),
        maxResults,
        singleEvents: true,
        orderBy: 'startTime',
      };
      
      if (args.query) {
        params.q = args.query;
      }

      const res = await calendar.events.list(params);
      const events = (res.data.items || []).map(e => ({
        id: e.id,
        summary: e.summary,
        description: e.description || null,
        location: e.location || null,
        start: e.start.dateTime || e.start.date,
        end: e.end.dateTime || e.end.date,
        allDay: !!e.start.date,
        status: e.status,
        creator: e.creator ? e.creator.email : null,
        organizer: e.organizer ? e.organizer.email : null,
        attendees: (e.attendees || []).map(a => ({
          email: a.email,
          name: a.displayName || null,
          responseStatus: a.responseStatus,
        })),
        htmlLink: e.htmlLink,
        calendarId,
      }));
      
      console.log(JSON.stringify({
        account: args.account,
        calendarId,
        timeRange: { from: now.toISOString(), to: future.toISOString() },
        count: events.length,
        events,
      }, null, 2));
      break;
    }

    case 'get-event': {
      if (!args['event-id']) {
        console.error('--event-id is required for get-event');
        process.exit(1);
      }
      const res = await calendar.events.get({
        calendarId,
        eventId: args['event-id'],
      });
      const e = res.data;
      console.log(JSON.stringify({
        id: e.id,
        summary: e.summary,
        description: e.description || null,
        location: e.location || null,
        start: e.start.dateTime || e.start.date,
        end: e.end.dateTime || e.end.date,
        allDay: !!e.start.date,
        status: e.status,
        creator: e.creator,
        organizer: e.organizer,
        attendees: e.attendees || [],
        recurrence: e.recurrence || null,
        reminders: e.reminders || null,
        htmlLink: e.htmlLink,
      }, null, 2));
      break;
    }

    case 'freebusy': {
      const now = new Date();
      const future = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);
      
      const res = await calendar.freebusy.query({
        requestBody: {
          timeMin: now.toISOString(),
          timeMax: future.toISOString(),
          items: [{ id: calendarId }],
        },
      });

      const busy = res.data.calendars[calendarId]?.busy || [];
      console.log(JSON.stringify({
        account: args.account,
        calendarId,
        timeRange: { from: now.toISOString(), to: future.toISOString() },
        busySlots: busy,
      }, null, 2));
      break;
    }

    default:
      console.error(`Unknown action: ${action}`);
      console.error('Available: list-calendars, events, get-event, freebusy');
      process.exit(1);
  }
}

run().catch((err) => {
  console.error(`Calendar error: ${err.message}`);
  if (err.message.includes('invalid_grant') || err.message.includes('Token has been expired')) {
    console.error(`\nToken may be expired. Re-authorize:\n  node auth.js --account ${args.account}`);
  }
  process.exit(1);
});
