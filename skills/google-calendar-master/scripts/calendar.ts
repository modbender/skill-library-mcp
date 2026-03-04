/**
 * Google Calendar API v3 operations
 *
 * Usage:
 *   bun run calendar.ts list [--calendar ID] [--from DATE] [--to DATE] [--max N]
 *   bun run calendar.ts get <eventId> [--calendar ID]
 *   bun run calendar.ts create --summary "..." [--start "..."] [--end "..."] [--description "..."] [--location "..."] [--calendar ID] [--all-day]
 *   bun run calendar.ts quick "Meeting with Bob tomorrow 3pm" [--calendar ID]
 *   bun run calendar.ts update <eventId> [--summary "..."] [--start "..."] [--end "..."] [--description "..."] [--location "..."] [--attendees "a@b.com,c@d.com"] [--add-attendees "e@f.com"] [--remove-attendees "a@b.com"] [--calendar ID] [--no-notify]
 *   bun run calendar.ts delete <eventId> [--calendar ID]
 *   bun run calendar.ts calendars
 *   bun run calendar.ts freebusy --from DATE --to DATE [--calendars id1,id2]
 */

import * as fs from 'node:fs';
import * as path from 'node:path';
import { getAccessToken } from './auth';

// ─── Config ──────────────────────────────────────────────────────────────────

const BASE_URL = 'https://www.googleapis.com/calendar/v3';
const DEFAULT_CALENDAR = 'primary';
const DEFAULT_ACCOUNT = 'default';

const TOKENS_DIR = path.join(
	process.env.HOME ?? '~',
	'.config',
	'google-calendar-skill',
	'tokens',
);

function getAccountList(): string[] {
	if (!fs.existsSync(TOKENS_DIR)) return [];
	return fs
		.readdirSync(TOKENS_DIR)
		.filter((f) => f.endsWith('.json'))
		.map((f) => f.replace(/\.json$/, ''));
}

// ─── API helper ──────────────────────────────────────────────────────────────

async function api(
	path: string,
	options: {
		method?: string;
		params?: Record<string, string>;
		body?: unknown;
		account?: string;
	} = {},
): Promise<unknown> {
	const token = await getAccessToken(options.account ?? DEFAULT_ACCOUNT);
	const url = new URL(`${BASE_URL}${path}`);
	if (options.params) {
		for (const [k, v] of Object.entries(options.params)) {
			if (v !== undefined && v !== '') url.searchParams.set(k, v);
		}
	}

	const res = await fetch(url.toString(), {
		method: options.method ?? 'GET',
		headers: {
			Authorization: `Bearer ${token}`,
			'Content-Type': 'application/json',
		},
		body: options.body ? JSON.stringify(options.body) : undefined,
	});

	if (res.status === 204) return {};

	const data = await res.json();
	if (!res.ok) {
		throw new Error(
			`API error ${res.status}: ${JSON.stringify(data.error ?? data)}`,
		);
	}
	return data;
}

// ─── Arg parsing helper ─────────────────────────────────────────────────────

function getFlag(args: string[], flag: string): string | undefined {
	const idx = args.indexOf(flag);
	if (idx === -1 || idx + 1 >= args.length) return undefined;
	return args[idx + 1];
}

function hasFlag(args: string[], flag: string): boolean {
	return args.includes(flag);
}

function getCalendar(args: string[]): string {
	return getFlag(args, '--calendar') ?? DEFAULT_CALENDAR;
}

function getAccount(args: string[]): string {
	return getFlag(args, '--account') ?? DEFAULT_ACCOUNT;
}

// ─── Date helpers ────────────────────────────────────────────────────────────

function toRFC3339(input: string): string {
	const d = new Date(input);
	if (isNaN(d.getTime())) {
		throw new Error(`Invalid date: "${input}"`);
	}
	return d.toISOString();
}

function formatEvent(ev: Record<string, unknown>): string {
	const start = ev.start as Record<string, string> | undefined;
	const end = ev.end as Record<string, string> | undefined;
	const startStr = start?.dateTime ?? start?.date ?? '?';
	const endStr = end?.dateTime ?? end?.date ?? '?';
	const summary = (ev.summary as string) ?? '(no title)';
	const location = ev.location ? `  📍 ${ev.location}` : '';
	const desc = ev.description
		? `  📝 ${(ev.description as string).slice(0, 120)}`
		: '';
	const id = ev.id as string;

	return `• ${startStr} → ${endStr}\n  ${summary}${location}${desc}\n  ID: ${id}`;
}

// ─── Commands ────────────────────────────────────────────────────────────────

async function listEvents(args: string[]) {
	const calendarId = getCalendar(args);
	const from = getFlag(args, '--from');
	const to = getFlag(args, '--to');
	const max = getFlag(args, '--max') ?? '25';

	const params: Record<string, string> = {
		maxResults: max,
		singleEvents: 'true',
		orderBy: 'startTime',
	};
	if (from) params.timeMin = toRFC3339(from);
	else params.timeMin = new Date().toISOString();
	if (to) params.timeMax = toRFC3339(to);

	const accounts = getAccountList();
	if (accounts.length === 0) {
		console.log('No authenticated accounts. Run: bun run auth.ts login');
		return;
	}

	let total = 0;
	for (const account of accounts) {
		const data = (await api(
			`/calendars/${encodeURIComponent(calendarId)}/events`,
			{ params: { ...params }, account },
		)) as Record<string, unknown>;
		const items = (data.items as Record<string, unknown>[]) ?? [];
		total += items.length;
		if (items.length === 0) continue;
		console.log(`\n── ${account} (${items.length}) ──\n`);
		for (const ev of items) {
			console.log(formatEvent(ev));
			console.log();
		}
	}
	if (total === 0) console.log('No upcoming events found.');
}

async function getEvent(args: string[]) {
	const eventId = args[1];
	if (!eventId) {
		console.error('Usage: bun run calendar.ts get <eventId>');
		process.exit(1);
	}
	const calendarId = getCalendar(args);
	const accounts = getAccountList();
	if (accounts.length === 0) {
		console.error('No authenticated accounts. Run: bun run auth.ts login');
		process.exit(1);
	}

	for (const account of accounts) {
		try {
			const data = await api(
				`/calendars/${encodeURIComponent(calendarId)}/events/${encodeURIComponent(eventId)}`,
				{ account },
			);
			console.log(`── ${account} ──`);
			console.log(JSON.stringify(data, null, 2));
			return;
		} catch {
			// 404 or other: try next account
		}
	}
	console.error(`Event not found: ${eventId}`);
	process.exit(1);
}

async function createEvent(args: string[]) {
	const calendarId = getCalendar(args);
	const account = getAccount(args);
	const summary = getFlag(args, '--summary');
	if (!summary) {
		console.error('--summary is required');
		process.exit(1);
	}

	const allDay = hasFlag(args, '--all-day');
	const startInput = getFlag(args, '--start');
	const endInput = getFlag(args, '--end');
	const description = getFlag(args, '--description');
	const location = getFlag(args, '--location');
	const attendees = getFlag(args, '--attendees');

	const event: Record<string, unknown> = { summary };
	if (description) event.description = description;
	if (location) event.location = location;

	if (allDay) {
		// All-day events use 'date' (YYYY-MM-DD) instead of 'dateTime'
		const startDate = startInput ?? new Date().toISOString().slice(0, 10);
		const endDate =
			endInput ??
			new Date(new Date(startDate).getTime() + 86400000)
				.toISOString()
				.slice(0, 10);
		event.start = { date: startDate };
		event.end = { date: endDate };
	} else {
		const startDt = startInput
			? toRFC3339(startInput)
			: new Date(Date.now() + 3600000).toISOString(); // default: 1h from now
		const endDt = endInput
			? toRFC3339(endInput)
			: new Date(new Date(startDt).getTime() + 3600000).toISOString(); // default: 1h duration
		event.start = { dateTime: startDt };
		event.end = { dateTime: endDt };
	}

	if (attendees) {
		event.attendees = attendees
			.split(',')
			.map((email) => ({ email: email.trim() }));
	}

	// Send invitations when attendees are present
	const sendUpdates = attendees ? 'all' : 'none';

	const data = await api(
		`/calendars/${encodeURIComponent(calendarId)}/events`,
		{ method: 'POST', body: event, account, params: { sendUpdates } },
	);
	const created = data as Record<string, unknown>;
	console.log(`✓ Event created`);
	console.log(`  ID: ${created.id}`);
	console.log(`  Link: ${created.htmlLink}`);
}

async function quickAdd(args: string[]) {
	const text = args[1];
	if (!text) {
		console.error(
			'Usage: bun run calendar.ts quick "Meeting with Bob tomorrow 3pm"',
		);
		process.exit(1);
	}
	const calendarId = getCalendar(args);
	const account = getAccount(args);

	const data = (await api(
		`/calendars/${encodeURIComponent(calendarId)}/events/quickAdd`,
		{ method: 'POST', params: { text }, account },
	)) as Record<string, unknown>;

	console.log(`✓ Event created via Quick Add`);
	console.log(`  Summary: ${data.summary}`);
	console.log(`  ID: ${data.id}`);
	console.log(`  Link: ${data.htmlLink}`);
}

async function updateEvent(args: string[]) {
	const eventId = args[1];
	if (!eventId) {
		console.error(
			'Usage: bun run calendar.ts update <eventId> [--summary ...] ...',
		);
		process.exit(1);
	}
	const calendarId = getCalendar(args);
	const accounts = getAccountList();
	if (accounts.length === 0) {
		console.error('No authenticated accounts. Run: bun run auth.ts login');
		process.exit(1);
	}

	for (const account of accounts) {
		try {
			const existing = (await api(
				`/calendars/${encodeURIComponent(calendarId)}/events/${encodeURIComponent(eventId)}`,
				{ account },
			)) as Record<string, unknown>;

			const summary = getFlag(args, '--summary');
			const startInput = getFlag(args, '--start');
			const endInput = getFlag(args, '--end');
			const description = getFlag(args, '--description');
			const location = getFlag(args, '--location');
			const attendees = getFlag(args, '--attendees');
			const addAttendees = getFlag(args, '--add-attendees');
			const removeAttendees = getFlag(args, '--remove-attendees');
			const noNotify = hasFlag(args, '--no-notify');

			if (summary) existing.summary = summary;
			if (description) existing.description = description;
			if (location) existing.location = location;
			if (startInput) existing.start = { dateTime: toRFC3339(startInput) };
			if (endInput) existing.end = { dateTime: toRFC3339(endInput) };

			// --attendees replaces all attendees
			if (attendees) {
				existing.attendees = attendees
					.split(',')
					.map((email) => ({ email: email.trim() }));
			}

			// --add-attendees merges with existing attendees
			if (addAttendees) {
				const current = (existing.attendees as Array<{ email: string }>) ?? [];
				const currentEmails = new Set(current.map((a) => a.email.toLowerCase()));
				const newAttendees = addAttendees
					.split(',')
					.map((e) => e.trim())
					.filter((e) => !currentEmails.has(e.toLowerCase()));
				existing.attendees = [
					...current,
					...newAttendees.map((email) => ({ email })),
				];
			}

			// --remove-attendees removes specific attendees
			if (removeAttendees) {
				const toRemove = new Set(
					removeAttendees.split(',').map((e) => e.trim().toLowerCase()),
				);
				const current = (existing.attendees as Array<{ email: string }>) ?? [];
				existing.attendees = current.filter(
					(a) => !toRemove.has(a.email.toLowerCase()),
				);
			}

			// Determine whether to send notifications (default: send when attendees change)
			const attendeesChanged = !!(attendees || addAttendees || removeAttendees);
			const sendUpdates = attendeesChanged && !noNotify ? 'all' : 'none';

			const data = (await api(
				`/calendars/${encodeURIComponent(calendarId)}/events/${encodeURIComponent(eventId)}`,
				{
					method: 'PUT',
					body: existing,
					account,
					params: { sendUpdates },
				},
			)) as Record<string, unknown>;

			console.log(`✓ Event updated (${account})`);
			console.log(`  ID: ${data.id}`);
			console.log(`  Link: ${data.htmlLink}`);
			if (attendeesChanged && !noNotify) {
				console.log(`  Invitations sent to attendees`);
			}
			return;
		} catch {
			// not in this account, try next
		}
	}
	console.error(`Event not found: ${eventId}`);
	process.exit(1);
}

async function deleteEvent(args: string[]) {
	const eventId = args[1];
	if (!eventId) {
		console.error('Usage: bun run calendar.ts delete <eventId>');
		process.exit(1);
	}
	const calendarId = getCalendar(args);
	const accounts = getAccountList();
	if (accounts.length === 0) {
		console.error('No authenticated accounts. Run: bun run auth.ts login');
		process.exit(1);
	}

	for (const account of accounts) {
		try {
			await api(
				`/calendars/${encodeURIComponent(calendarId)}/events/${encodeURIComponent(eventId)}`,
				{ method: 'DELETE', account },
			);
			console.log(`✓ Event deleted (${account}): ${eventId}`);
			return;
		} catch {
			// not in this account, try next
		}
	}
	console.error(`Event not found: ${eventId}`);
	process.exit(1);
}

async function listCalendars(args: string[]) {
	const accounts = getAccountList();
	if (accounts.length === 0) {
		console.log('No authenticated accounts. Run: bun run auth.ts login');
		return;
	}

	for (const account of accounts) {
		const data = (await api('/users/me/calendarList', { account })) as Record<
			string,
			unknown
		>;
		const items = (data.items as Record<string, unknown>[]) ?? [];
		console.log(`\n── ${account} (${items.length} calendars) ──\n`);
		for (const cal of items) {
			const primary = cal.primary ? ' (primary)' : '';
			const access = cal.accessRole ?? '';
			console.log(
				`• ${cal.summary}${primary}\n  ID: ${cal.id}\n  Access: ${access}\n`,
			);
		}
	}
}

async function freeBusy(args: string[]) {
	const from = getFlag(args, '--from');
	const to = getFlag(args, '--to');
	if (!from || !to) {
		console.error(
			'Usage: bun run calendar.ts freebusy --from DATE --to DATE [--calendars id1,id2]',
		);
		process.exit(1);
	}

	const calendarIds = getFlag(args, '--calendars')?.split(',') ?? ['primary'];
	const accounts = getAccountList();
	if (accounts.length === 0) {
		console.error('No authenticated accounts. Run: bun run auth.ts login');
		process.exit(1);
	}

	for (const account of accounts) {
		const data = (await api('/freeBusy', {
			method: 'POST',
			account,
			body: {
				timeMin: toRFC3339(from),
				timeMax: toRFC3339(to),
				items: calendarIds.map((id) => ({ id: id.trim() })),
			},
		})) as Record<string, unknown>;
		console.log(`── ${account} ──`);
		console.log(JSON.stringify(data, null, 2));
		console.log('');
	}
}

// ─── CLI dispatch ────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const command = args[0];

async function main() {
	switch (command) {
		case 'list':
			await listEvents(args);
			break;
		case 'get':
			await getEvent(args);
			break;
		case 'create':
			await createEvent(args);
			break;
		case 'quick':
			await quickAdd(args);
			break;
		case 'update':
			await updateEvent(args);
			break;
		case 'delete':
			await deleteEvent(args);
			break;
		case 'calendars':
			await listCalendars(args);
			break;
		case 'freebusy':
			await freeBusy(args);
			break;
		default:
			console.log(
				[
					'Usage: bun run calendar.ts <command> [options]',
					'',
					'Commands (list/get/update/delete/calendars/freebusy run for all accounts; output is labeled by account):',
					'  list       List upcoming events',
					'  get        Get event details by ID',
					'  create     Create a new event (requires --account)',
					'  quick      Quick-add event from natural language (requires --account)',
					'  update     Update an existing event',
					'  delete     Delete an event',
					'  calendars  List available calendars',
					'  freebusy   Query free/busy information',
					'',
				'Options:',
				'  --calendar ID              Calendar ID (default: primary)',
				'  --account ALIAS            For create/quick only: which account to use (default: default)',
				'  --attendees "a@b,c@d"      Set attendees (create: adds; update: replaces all)',
				'  --add-attendees "a@b"      Add attendees without removing existing (update only)',
				'  --remove-attendees "a@b"   Remove specific attendees (update only)',
				'  --no-notify                Skip sending email invitations (update only)',
				].join('\n'),
			);
			process.exit(1);
	}
}

main().catch((e) => {
	console.error(`✗ ${e.message}`);
	process.exit(1);
});
