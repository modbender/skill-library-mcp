import { execFile } from 'child_process';
import { format, toZonedTime } from 'date-fns-tz';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

const TIMEZONE = process.env.CEREBRO_TIMEZONE || process.env.TZ || 'America/Chicago';

// Calendars are provided via env to avoid embedding personal calendar IDs in the repo.
// - CEREBRO_CALENDAR_IDS: comma-separated list (recommended)
// - CEREBRO_CALENDAR_NAMES: optional comma-separated list matching ids
// Fallback: primary only.
const CALENDAR_IDS = (process.env.CEREBRO_CALENDAR_IDS || 'primary')
  .split(',')
  .map((s) => s.trim())
  .filter(Boolean);

const CALENDAR_NAMES = (process.env.CEREBRO_CALENDAR_NAMES || '')
  .split(',')
  .map((s) => s.trim());

const CALENDARS = CALENDAR_IDS.map((id, i) => ({
  id,
  name: CALENDAR_NAMES[i] || (id === 'primary' ? 'Primary' : `Calendar ${i + 1}`),
}));

interface CalendarEvent {
    summary: string;
    start: { dateTime?: string; date?: string; timeZone?: string };
    end: { dateTime?: string; date?: string; timeZone?: string };
}

interface NormalizedEvent {
    summary: string;
    start: Date;
    end: Date;
    isAllDay: boolean;
    source: string;
}

function isSafeCalendarId(input: string): boolean {
    // Allow common Google calendar id formats: primary, email-like, uuid-like, group calendar ids.
    return /^[A-Za-z0-9@._-]+$/.test(input);
}

function isSafeAccount(input: string): boolean {
    // Conservative account format validation.
    return /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(input);
}

async function fetchEvents(calendarId: string, from: string, to: string): Promise<CalendarEvent[]> {
    try {
        const account = process.env.GOG_ACCOUNT || process.env.CEREBRO_GOG_ACCOUNT;
        if (!account) {
            throw new Error('Missing env var GOG_ACCOUNT (or CEREBRO_GOG_ACCOUNT) for gog calendar access');
        }
        if (!isSafeAccount(account)) {
            throw new Error('Invalid GOG account format');
        }
        if (!isSafeCalendarId(calendarId)) {
            throw new Error('Invalid calendar id format');
        }

        const { stdout } = await execFileAsync(
            'gog',
            ['calendar', 'events', calendarId, '--from', from, '--to', to, '--json'],
            {
                env: {
                    ...process.env,
                    GOG_ACCOUNT: account,
                },
                timeout: 30_000,
                maxBuffer: 2 * 1024 * 1024,
            }
        );

        const data = JSON.parse(stdout);
        return data.events || [];
    } catch (e) {
        console.error(`Failed to fetch calendar ${calendarId}:`, e);
        return [];
    }
}

async function main() {
    // Default to today + tomorrow
    const now = new Date();
    const from = new Date(now);
    from.setHours(0, 0, 0, 0);
    const to = new Date(now);
    to.setDate(to.getDate() + 2); // 48h window
    to.setHours(23, 59, 59, 999);

    const fromStr = from.toISOString();
    const toStr = to.toISOString();

    // Always refresh from source on each run (deterministic pull)

    const allEvents: NormalizedEvent[] = [];

    for (const cal of CALENDARS) {
        const events = await fetchEvents(cal.id, fromStr, toStr);
        for (const e of events) {
            if (e.start.dateTime) {
                // Time-based event
                const dStart = new Date(e.start.dateTime);
                const dEnd = new Date(e.end.dateTime || e.start.dateTime);
                
                allEvents.push({
                    summary: e.summary,
                    start: dStart,
                    end: dEnd,
                    isAllDay: false,
                    source: cal.name
                });
            } else if (e.start.date) {
                // All-day event
                const dStart = new Date(e.start.date);
                const dEnd = new Date(e.end.date || e.start.date);
                allEvents.push({
                    summary: e.summary,
                    start: dStart,
                    end: dEnd,
                    isAllDay: true,
                    source: cal.name
                });
            }
        }
    }

    // Sort chronologically
    allEvents.sort((a, b) => a.start.getTime() - b.start.getTime());

    // Format output
    console.log(`# Schedule (${format(toZonedTime(now, TIMEZONE), 'yyyy-MM-dd', { timeZone: TIMEZONE })})`);
    
    let currentDay = '';
    
    for (const e of allEvents) {
        const zonedStart = toZonedTime(e.start, TIMEZONE);
        const zonedEnd = toZonedTime(e.end, TIMEZONE);
        
        const dayStr = format(zonedStart, 'EEEE, MMMM d', { timeZone: TIMEZONE });
        
        if (dayStr !== currentDay) {
            console.log(`\n## ${dayStr}`);
            currentDay = dayStr;
        }

        if (e.isAllDay) {
            console.log(`- [All Day] ${e.summary}`);
        } else {
            const timeStr = `${format(zonedStart, 'h:mm a', { timeZone: TIMEZONE })} - ${format(zonedEnd, 'h:mm a', { timeZone: TIMEZONE })}`;
            console.log(`- **${timeStr}**: ${e.summary}`);
        }
    }
}

main().catch(console.error);
