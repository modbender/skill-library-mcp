const { exec } = require('child_process');
const os = require('os');

const platform = os.platform();

// ── Required Environment Variables ──────────────────────────────────
// OPENCLAW_BIN  → Absolute path to the openclaw binary (e.g. /usr/bin/openclaw, C:\Program Files\OpenClaw\openclaw.exe)
// OPENCLAW_TZ   → User's IANA timezone (e.g. America/Mexico_City, Europe/Madrid, Asia/Tokyo)

const OPENCLAW_BIN = process.env.OPENCLAW_BIN;
const OPENCLAW_TZ = process.env.OPENCLAW_TZ;

function checkEnv() {
    const missing = [];
    if (!OPENCLAW_BIN) missing.push('OPENCLAW_BIN');
    if (!OPENCLAW_TZ) missing.push('OPENCLAW_TZ');
    if (missing.length) {
        console.error(`❌ Missing required environment variable(s): ${missing.join(', ')}`);
        console.error(`   Set them in your .env or shell profile.`);
        console.error(`   Example:`);
        console.error(`     OPENCLAW_BIN=/usr/bin/openclaw`);
        console.error(`     OPENCLAW_TZ=America/Mexico_City`);
        process.exit(1);
    }
}

function execute(command) {
    return new Promise((resolve) => {
        exec(command, (error, stdout, stderr) => {
            resolve({ error, stdout: stdout.trim(), stderr: stderr.trim() });
        });
    });
}

// ── Time Parsing ────────────────────────────────────────────────────

// Parse "YYYY-MM-DD HH:mm" into components
function parseTimeArg(timeArg) {
    const m = timeArg.match(/^(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})$/);
    if (!m) return null;
    return { year: +m[1], month: +m[2], day: +m[3], hour: +m[4], minute: +m[5] };
}

// Convert a datetime in the user's timezone to a Date object (UTC internally)
// This is the key function: it interprets "2026-02-27 15:00" as 15:00 in OPENCLAW_TZ
function userTimeToDate(parsed, tz) {
    // Build an ISO-ish string and use the timezone to get the correct UTC instant
    const isoStr = `${parsed.year}-${String(parsed.month).padStart(2, '0')}-${String(parsed.day).padStart(2, '0')}T${String(parsed.hour).padStart(2, '0')}:${String(parsed.minute).padStart(2, '0')}:00`;

    // Create a formatter that outputs numeric parts in the target timezone
    const fmt = new Intl.DateTimeFormat('en-US', {
        timeZone: tz,
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        hour12: false
    });

    // Binary-search the correct UTC timestamp:
    // We know the target datetime and timezone, we need the UTC epoch.
    // Start with a rough guess, then adjust.
    let guess = new Date(isoStr + 'Z'); // naive UTC guess
    const parts = () => {
        const p = {};
        for (const { type, value } of fmt.formatToParts(guess)) {
            p[type] = +value;
        }
        return p;
    };

    // Adjust in two passes for DST edge cases
    for (let i = 0; i < 2; i++) {
        const p = parts();
        const diffMs =
            ((parsed.year - p.year) * 365.25 * 24 * 3600 * 1000) || // rough year (unused for small diffs)
            0;
        const localGuess = new Date(p.year, p.month - 1, p.day, p.hour, p.minute, p.second);
        const target = new Date(parsed.year, parsed.month - 1, parsed.day, parsed.hour, parsed.minute, 0);
        const offsetMs = target.getTime() - localGuess.getTime();
        guess = new Date(guess.getTime() + offsetMs);
    }

    return guess;
}

// Convert a Date object to "HH:mm" and "MM/DD/YYYY" in the server's local timezone
function dateToServerLocal(date) {
    const h = String(date.getHours()).padStart(2, '0');
    const m = String(date.getMinutes()).padStart(2, '0');
    const mo = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    const y = date.getFullYear();
    return { time: `${h}:${m}`, date: `${mo}/${d}/${y}` };
}

// ── Schedule ────────────────────────────────────────────────────────

async function schedule(timeArg, task, userId, channel, timezone) {
    if (!userId || !channel) {
        console.error("❌ Error: Missing required arguments: userId, channel");
        return;
    }

    const tz = timezone || OPENCLAW_TZ;
    const now = new Date().toLocaleString('en-US', { timeZone: tz });

    // Inject system metadata into the payload
    const instruction = `[System: Scheduled Task Executed] 
- Created at: ${now}
- Scheduled for: ${timeArg}
- Original instruction: ${task}`;

    if (platform === 'win32') {
        const parsed = parseTimeArg(timeArg);
        if (!parsed) {
            console.error("❌ Error: On Windows, time must be strictly in YYYY-MM-DD HH:mm format.");
            return;
        }

        // Convert user's timezone → server local time for schtasks
        const targetDate = userTimeToDate(parsed, tz);
        const serverLocal = dateToServerLocal(targetDate);

        const taskId = `OpenClaw_Task_${Date.now()}`;
        const flatInstruction = instruction.replace(/\n/g, ' - ');

        // Quote the binary path in case it contains spaces
        const winCmd = `schtasks /create /tn "${taskId}" /tr "\\"${OPENCLAW_BIN}\\" agent --message \\\\"${flatInstruction}\\\\" --to \\\\"${userId}\\\\" --channel \\\\"${channel}\\\\" --deliver" /sc ONCE /st ${serverLocal.time} /sd ${serverLocal.date} /f`;

        const res = await execute(winCmd);
        if (res.error) {
            console.error(`❌ Error scheduling task on Windows:`, res.stderr || res.stdout);
        } else {
            console.log(`✅ Task successfully scheduled for: ${timeArg} ${tz} (Task ID: ${taskId})`);
        }
    } else {
        // Linux / macOS — 'at' respects the TZ env var natively
        const parsed = parseTimeArg(timeArg);
        let formattedTime;
        if (parsed) {
            formattedTime = `${String(parsed.hour).padStart(2, '0')}:${String(parsed.minute).padStart(2, '0')} ${String(parsed.month).padStart(2, '0')}/${String(parsed.day).padStart(2, '0')}/${parsed.year}`;
        } else {
            formattedTime = timeArg; // let 'at' try parsing relative times
        }

        const safeInstruction = instruction.replace(/'/g, "'\\''");
        const agentCommand = `${OPENCLAW_BIN} agent --message '${safeInstruction}' --to '${userId}' --channel '${channel}' --deliver`;
        const atCmd = `echo "${agentCommand} >> /tmp/to-do.log 2>&1" | TZ="${tz}" at "${formattedTime}"`;

        const res = await execute(atCmd);
        const output = res.stderr || res.stdout;

        console.log(output);
        if (output.includes('job')) {
            console.log(`✅ Task successfully scheduled for: ${timeArg} (${tz})`);
        } else {
            console.error("❌ Failed to schedule via 'at':", output);
        }
    }
}

// ── List ────────────────────────────────────────────────────────────

async function list() {
    if (platform === 'win32') {
        const res = await execute('schtasks /query /fo LIST /tn "OpenClaw_Task_*"');
        if (res.error || res.stdout.includes('ERROR:')) {
            console.log("No pending tasks.");
            return;
        }
        console.log(res.stdout);
    } else {
        const res = await execute('atq | sort -k 6,6 -k 3,3 -k 4,4 -k 5,5');
        if (!res.stdout) {
            console.log("No pending tasks.");
            return;
        }

        console.log("ID\tExecution Time\t\t\tTask Description");
        console.log("--\t--------------\t\t\t----------------");

        const lines = res.stdout.split('\n');
        for (const line of lines) {
            const parts = line.split(/\s+/);
            if (parts.length < 2) continue;

            const id = parts[0];
            const dateStr = parts.slice(1, 6).join(' ');

            const detailRes = await execute(`at -c ${id}`);
            const match = detailRes.stdout.match(/--message '\\[System: Scheduled Task Executed\\] \\\\n- Created at: .*? \\\\n- Scheduled for: .*? \\\\n- Original instruction: (.*?)'/);
            const matchFallback = detailRes.stdout.match(/Original instruction: (.*?)'/);

            let desc = match ? match[1] : (matchFallback ? matchFallback[1] : "(Unknown task)");
            console.log(`${id}\t${dateStr}\t${desc}`);
        }
    }
}

// ── Remove ──────────────────────────────────────────────────────────

async function remove(id) {
    if (!id) {
        console.log("Usage: node skills/to-do/to-do.js delete <id>");
        return;
    }

    if (platform === 'win32') {
        const res = await execute(`schtasks /delete /tn "${id}" /f`);
        if (res.error) console.error("Error:", res.stderr);
        else console.log(`🗑️ Task ${id} deleted.`);
    } else {
        const res = await execute(`atrm ${id}`);
        if (res.error) console.error("Error:", res.stderr);
        else console.log(`🗑️ Task #${id} deleted.`);
    }
}

// ── CLI Routing ─────────────────────────────────────────────────────

const args = process.argv.slice(2);
const action = args[0];

(async () => {
    try {
        // Validate env vars before any action
        checkEnv();

        if (action === 'schedule') {
            const timeArg = args[1];
            const task = args[2];
            const userId = args[3];
            const channel = args[4];
            const timezone = args[5]; // optional override, defaults to OPENCLAW_TZ

            if (!timeArg || !task || !userId || !channel) {
                console.log('Usage: node skills/to-do/to-do.js schedule "YYYY-MM-DD HH:mm" "Instruction" "USER_ID" "CHANNEL" ["TIMEZONE"]');
            } else {
                await schedule(timeArg, task, userId, channel, timezone);
            }
        } else if (action === 'list') {
            await list();
        } else if (action === 'now') {
            const tz = args[1] || OPENCLAW_TZ;
            const now = new Date().toLocaleString('en-US', { timeZone: tz });
            console.log(`🕒 Current Time (${tz}): ${now}`);
        } else if (action === 'delete' || action === 'remove') {
            await remove(args[1]);
        } else {
            console.log(`
To-Do Skill (Cross-Platform)
--------------------------------------------------
Requires env vars: OPENCLAW_BIN, OPENCLAW_TZ

Commands:
  schedule "<time>" "<task>" "<userId>" "<channel>" ["<tz>"]  - Schedule a new task
  list                                                        - List pending tasks
  now  ["<tz>"]                                               - Show current time
  delete <id>                                                 - Remove a task
`);
        }
    } catch (err) {
        console.error("Fatal Error:", err);
    }
})();
