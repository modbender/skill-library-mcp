#!/usr/bin/env node

const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const os = require("os");
const https = require("https");

// State file location (current working directory)
const STATE_DIR = path.join(process.cwd(), ".hackmd");
const STATE_FILE = path.join(STATE_DIR, "tracked-notes.json");

// API config
const API_BASE = process.env.HMD_API_ENDPOINT_URL || "https://api.hackmd.io/v1";
const API_TOKEN = process.env.HMD_API_ACCESS_TOKEN;

// Ensure state directory exists
function ensureStateDir() {
    if (!fs.existsSync(STATE_DIR)) {
        fs.mkdirSync(STATE_DIR, { recursive: true });
    }
}

// Load state from file
function loadState() {
    ensureStateDir();
    if (!fs.existsSync(STATE_FILE)) {
        return { notes: {} };
    }
    try {
        return JSON.parse(fs.readFileSync(STATE_FILE, "utf8"));
    } catch (e) {
        console.error("Warning: Could not parse state file, starting fresh");
        return { notes: {} };
    }
}

// Save state to file
function saveState(state) {
    ensureStateDir();
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

// Make API request
function apiRequest(endpoint) {
    return new Promise((resolve, reject) => {
        if (!API_TOKEN) {
            reject(new Error("HMD_API_ACCESS_TOKEN not set"));
            return;
        }

        // Ensure endpoint starts with /
        const fullPath = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
        const baseUrl = API_BASE.endsWith("/v1") ? API_BASE : `${API_BASE}/v1`;
        const url = new URL(baseUrl);

        const options = {
            hostname: url.hostname,
            port: 443,
            path: `/v1${fullPath}`,
            method: "GET",
            headers: {
                Authorization: `Bearer ${API_TOKEN}`,
                "Content-Type": "application/json",
            },
        };

        const req = https.request(options, (res) => {
            let data = "";
            res.on("data", (chunk) => (data += chunk));
            res.on("end", () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    try {
                        resolve(JSON.parse(data));
                    } catch (e) {
                        resolve(data);
                    }
                } else {
                    reject(new Error(`API error ${res.statusCode}: ${data}`));
                }
            });
        });

        req.on("error", reject);
        req.end();
    });
}

// Get note metadata via API (includes lastChangedAt)
async function getNoteMetadata(noteId) {
    try {
        return await apiRequest(`/notes/${noteId}`);
    } catch (e) {
        return null;
    }
}

// Get note content (content is included in metadata)
async function getNoteContent(noteId) {
    const note = await getNoteMetadata(noteId);
    return note ? note.content : null;
}

// Command: add <noteId>
async function cmdAdd(noteId) {
    if (!noteId) {
        console.error("Usage: hackmd-track add <noteId>");
        process.exit(1);
    }

    const meta = await getNoteMetadata(noteId);
    if (!meta) {
        console.error(`Error: Could not fetch note ${noteId}`);
        process.exit(1);
    }

    const state = loadState();
    state.notes[noteId] = {
        lastChangedAt: meta.lastChangedAt,
        lastCheckedAt: Date.now(),
        title: meta.title || "Untitled",
    };
    saveState(state);

    console.log(`Tracking: ${meta.title || noteId}`);
    console.log(
        `  lastChangedAt: ${new Date(meta.lastChangedAt).toISOString()}`,
    );
}

// Command: remove <noteId>
function cmdRemove(noteId) {
    if (!noteId) {
        console.error("Usage: hackmd-track remove <noteId>");
        process.exit(1);
    }

    const state = loadState();
    if (!state.notes[noteId]) {
        console.error(`Note ${noteId} is not being tracked`);
        process.exit(1);
    }

    const title = state.notes[noteId].title;
    delete state.notes[noteId];
    saveState(state);

    console.log(`Stopped tracking: ${title || noteId}`);
}

// Command: list
function cmdList() {
    const state = loadState();
    const noteIds = Object.keys(state.notes);

    if (noteIds.length === 0) {
        console.log("No notes being tracked");
        return;
    }

    console.log("Tracked notes:\n");
    for (const noteId of noteIds) {
        const note = state.notes[noteId];
        console.log(`  ${noteId}`);
        console.log(`    Title: ${note.title}`);
        console.log(
            `    Last changed: ${new Date(note.lastChangedAt).toISOString()}`,
        );
        console.log(
            `    Last checked: ${new Date(note.lastCheckedAt).toISOString()}`,
        );
        console.log("");
    }
}

// Command: reset <noteId>
function cmdReset(noteId) {
    if (!noteId) {
        console.error("Usage: hackmd-track reset <noteId>");
        process.exit(1);
    }

    const state = loadState();
    if (!state.notes[noteId]) {
        console.error(`Note ${noteId} is not being tracked`);
        process.exit(1);
    }

    state.notes[noteId].lastChangedAt = 0;
    state.notes[noteId].lastCheckedAt = Date.now();
    saveState(state);

    console.log(`Reset tracking for: ${state.notes[noteId].title || noteId}`);
}

// Command: changes <noteId> | --all
async function cmdChanges(noteId, options = {}) {
    const state = loadState();
    const verbose = options.verbose || false;
    const jsonOutput = options.json || false;

    // Check single note
    if (noteId && noteId !== "--all") {
        const meta = await getNoteMetadata(noteId);
        if (!meta) {
            console.error(`Error: Could not fetch note ${noteId}`);
            process.exit(1);
        }

        const tracked = state.notes[noteId];
        const storedLastChanged = tracked ? tracked.lastChangedAt : 0;

        // Update tracking state
        state.notes[noteId] = {
            lastChangedAt: meta.lastChangedAt,
            lastCheckedAt: Date.now(),
            title: meta.title || "Untitled",
        };
        saveState(state);

        // Check if changed
        if (meta.lastChangedAt > storedLastChanged) {
            if (jsonOutput) {
                console.log(
                    JSON.stringify(
                        {
                            changed: true,
                            noteId,
                            title: meta.title,
                            lastChangedAt: meta.lastChangedAt,
                            lastChangeUser: meta.lastChangeUser,
                            content: meta.content,
                        },
                        null,
                        2,
                    ),
                );
            } else {
                if (verbose) {
                    console.error(`Changed: ${meta.title}`);
                    console.error(
                        `  By: ${meta.lastChangeUser?.name || "Unknown"}`,
                    );
                    console.error(
                        `  At: ${new Date(meta.lastChangedAt).toISOString()}`,
                    );
                    console.error("---");
                }
                console.log(meta.content);
            }
        } else {
            if (jsonOutput) {
                console.log(
                    JSON.stringify(
                        { changed: false, noteId, title: meta.title },
                        null,
                        2,
                    ),
                );
            } else if (verbose) {
                console.error(`No changes: ${meta.title}`);
            }
        }
        return;
    }

    // Check all tracked notes
    if (noteId === "--all") {
        const noteIds = Object.keys(state.notes);
        if (noteIds.length === 0) {
            if (jsonOutput) {
                console.log(JSON.stringify({ changed: [], unchanged: [] }));
            } else {
                console.error("No notes being tracked");
            }
            return;
        }

        const results = { changed: [], unchanged: [] };

        for (const id of noteIds) {
            const meta = await getNoteMetadata(id);
            if (!meta) {
                console.error(`Warning: Could not fetch note ${id}`);
                continue;
            }

            const storedLastChanged = state.notes[id].lastChangedAt;

            // Update tracking state
            state.notes[id] = {
                lastChangedAt: meta.lastChangedAt,
                lastCheckedAt: Date.now(),
                title: meta.title || "Untitled",
            };

            if (meta.lastChangedAt > storedLastChanged) {
                results.changed.push({
                    noteId: id,
                    title: meta.title,
                    lastChangedAt: meta.lastChangedAt,
                    lastChangeUser: meta.lastChangeUser,
                    content: meta.content,
                });
            } else {
                results.unchanged.push({
                    noteId: id,
                    title: meta.title,
                });
            }
        }

        saveState(state);

        if (jsonOutput) {
            console.log(JSON.stringify(results, null, 2));
        } else {
            if (results.changed.length === 0) {
                if (verbose) console.error("No changes detected");
            } else {
                for (const note of results.changed) {
                    console.log(`\n=== ${note.title} (${note.noteId}) ===`);
                    console.log(
                        `Changed by: ${note.lastChangeUser?.name || "Unknown"}`,
                    );
                    console.log(
                        `At: ${new Date(note.lastChangedAt).toISOString()}`,
                    );
                    console.log("---");
                    console.log(note.content);
                }
            }
        }
        return;
    }

    console.error("Usage: hackmd-track changes <noteId> | --all");
    process.exit(1);
}

// Parse command line arguments
function parseArgs(args) {
    const options = { verbose: false, json: false };
    const positional = [];

    for (const arg of args) {
        if (arg === "-v" || arg === "--verbose") {
            options.verbose = true;
        } else if (arg === "--json") {
            options.json = true;
        } else {
            positional.push(arg);
        }
    }

    return { positional, options };
}

// Main
async function main() {
    const args = process.argv.slice(2);

    if (args.length === 0) {
        console.log(`hackmd-track - Change tracking for HackMD notes

Usage:
  hackmd-track add <noteId>        Add note to tracking
  hackmd-track remove <noteId>     Remove note from tracking
  hackmd-track list                List tracked notes
  hackmd-track reset <noteId>      Reset lastChangedAt (next check will show as changed)
  hackmd-track changes <noteId>    Get content if changed since last check
  hackmd-track changes --all       Check all tracked notes for changes

Options:
  -v, --verbose    Show status messages
  --json           Output as JSON

Environment:
  HMD_API_ACCESS_TOKEN    Required. Your HackMD API token.
  HMD_API_ENDPOINT_URL    Optional. API endpoint (default: https://api.hackmd.io/v1)

State file: ./.hackmd/tracked-notes.json (in current directory)
`);
        return;
    }

    if (!API_TOKEN) {
        console.error(
            "Error: HMD_API_ACCESS_TOKEN environment variable not set",
        );
        process.exit(1);
    }

    const { positional, options } = parseArgs(args);
    const command = positional[0];

    switch (command) {
        case "add":
            await cmdAdd(positional[1]);
            break;
        case "remove":
            cmdRemove(positional[1]);
            break;
        case "list":
            cmdList();
            break;
        case "reset":
            cmdReset(positional[1]);
            break;
        case "changes":
            await cmdChanges(positional[1], options);
            break;
        default:
            console.error(`Unknown command: ${command}`);
            process.exit(1);
    }
}

main().catch((e) => {
    console.error(`Error: ${e.message}`);
    process.exit(1);
});
