#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');

const HOME = process.env.HOME || os.homedir();

// ─── Security Helpers ───

/**
 * Validate that a path stays within the expected base directory.
 * Throws if path escapes the base.
 */
function safePath(basePath, userPath) {
  const base = path.resolve(basePath);
  const resolved = path.resolve(base, userPath);

  if (!resolved.startsWith(base + path.sep) && resolved !== base) {
    throw new Error(`Path traversal attempt blocked: ${userPath}`);
  }

  return resolved;
}

// Configuration via environment variables with sensible defaults
const TWILIO_NUMBER = process.env.TWILIO_CALLER_ID || '';
const ASSISTANT_NAME = process.env.ASSISTANT_NAME || 'Amber';
const OPERATOR_NAME = process.env.OPERATOR_NAME || 'the operator';

// Paths - validate to prevent path traversal
const SKILL_ROOT = path.resolve(__dirname, '..');

const DEFAULT_LOGS_DIR = (() => {
  const userPath = process.env.LOGS_DIR;
  const defaultPath = path.join(__dirname, '../runtime/logs');
  if (!userPath) return defaultPath;
  
  try {
    return safePath(SKILL_ROOT, userPath);
  } catch (e) {
    console.warn(`LOGS_DIR validation failed (${userPath}), using default:`, e.message);
    return defaultPath;
  }
})();

const DEFAULT_OUTPUT_DIR = (() => {
  const userPath = process.env.OUTPUT_DIR;
  const defaultPath = path.join(__dirname, 'data');
  if (!userPath) return defaultPath;
  
  try {
    return safePath(SKILL_ROOT, userPath);
  } catch (e) {
    console.warn(`OUTPUT_DIR validation failed (${userPath}), using default:`, e.message);
    return defaultPath;
  }
})();

const CONTACTS_FILE = (() => {
  const userPath = process.env.CONTACTS_FILE;
  const defaultPath = path.join(__dirname, 'contacts.json');
  if (!userPath) return defaultPath;
  
  try {
    return safePath(SKILL_ROOT, userPath);
  } catch (e) {
    console.warn(`CONTACTS_FILE validation failed (${userPath}), using default:`, e.message);
    return defaultPath;
  }
})();

// Load contacts from file (optional)
let KNOWN_NUMBERS = {};
try {
    if (fs.existsSync(CONTACTS_FILE)) {
        const raw = fs.readFileSync(CONTACTS_FILE, 'utf8');
        KNOWN_NUMBERS = JSON.parse(raw);
        console.log(`Loaded ${Object.keys(KNOWN_NUMBERS).length} contacts from ${CONTACTS_FILE}`);
    }
} catch (e) {
    console.warn(`Warning: Could not load contacts from ${CONTACTS_FILE}:`, e.message);
}

function parseArgs(argv) {
    const args = {
        logsDir: DEFAULT_LOGS_DIR,
        outputDir: DEFAULT_OUTPUT_DIR,
        writeSample: true
    };

    for (let i = 2; i < argv.length; i++) {
        const a = argv[i];
        if (a === '--logs' && argv[i + 1]) {
            const userPath = argv[++i];
            try {
                args.logsDir = safePath(SKILL_ROOT, userPath);
            } catch (e) {
                console.warn(`--logs path validation failed (${userPath}), using default:`, e.message);
            }
        } else if (a === '--out' && argv[i + 1]) {
            const userPath = argv[++i];
            try {
                args.outputDir = safePath(SKILL_ROOT, userPath);
            } catch (e) {
                console.warn(`--out path validation failed (${userPath}), using default:`, e.message);
            }
        } else if (a === '--no-sample') {
            args.writeSample = false;
        } else if (a === '-h' || a === '--help') {
            args.help = true;
        }
    }

    return args;
}

function parseTimestampMsFromIncomingFilename(filename) {
    // incoming_1770512050430.realtime.call.incoming.json
    const match = filename.match(/incoming_(\d{10,})/);
    if (!match) return null;
    const n = Number(match[1]);
    return Number.isFinite(n) ? n : null;
}

function safeReadJson(filePath) {
    try {
        return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch (e) {
        return { __parse_error: String(e) };
    }
}

function getHeaderValue(sipHeaders, name) {
    if (!Array.isArray(sipHeaders)) return null;
    const h = sipHeaders.find(x => x && typeof x.name === 'string' && x.name.toLowerCase() === name.toLowerCase());
    return h && typeof h.value === 'string' ? h.value : null;
}

function extractE164(text) {
    if (!text) return null;
    const m = String(text).match(/(\+\d{7,15})/);
    return m ? m[1] : null;
}

function extractPhoneNumbersFromSipHeaders(sipHeaders) {
    const from = extractE164(getHeaderValue(sipHeaders, 'From')) || extractE164(getHeaderValue(sipHeaders, 'P-Asserted-Identity'));
    const to = extractE164(getHeaderValue(sipHeaders, 'To'));
    const toProject = (() => {
        const toVal = getHeaderValue(sipHeaders, 'To');
        if (!toVal) return null;
        const proj = String(toVal).match(/proj_[a-zA-Z0-9]+/);
        return proj ? proj[0] : null;
    })();
    const twilioCallSid = (() => {
        const sid = getHeaderValue(sipHeaders, 'X-Twilio-CallSid');
        return sid || null;
    })();
    // Extract the original PSTN-leg Twilio CallSid from the To header (embedded as x_twilio_callsid param)
    const pstnCallSid = (() => {
        const toVal = getHeaderValue(sipHeaders, 'To');
        if (!toVal) return null;
        const m = String(toVal).match(/x_twilio_callsid=(CA[a-f0-9]+)/);
        return m ? m[1] : null;
    })();
    // Extract bridgeId from the To header (embedded as x_bridge_id param)
    const bridgeId = (() => {
        const toVal = getHeaderValue(sipHeaders, 'To');
        if (!toVal) return null;
        const m = String(toVal).match(/x_bridge_id=(b_[a-f0-9_]+)/);
        return m ? m[1] : null;
    })();

    return {
        from,
        to: to || (toProject ? 'OpenAI Project' : null),
        toProject,
        twilioCallSid,
        pstnCallSid,
        bridgeId
    };
}

// Allowlisted fields for SUMMARY_JSON extraction.
// Only these keys are kept from transcript-embedded JSON to prevent
// exfiltration of unexpected structured data.
const SUMMARY_JSON_ALLOWED_KEYS = new Set([
    'name', 'callback', 'message', 'phone', 'email',
    'reason', 'urgency', 'time', 'date', 'notes',
    'appointment', 'location', 'summary'
]);

/**
 * Sanitize a parsed SUMMARY_JSON object: keep only allowlisted keys,
 * enforce string values (no nested objects), and cap value length.
 */
function sanitizeSummaryJson(obj) {
    if (!obj || typeof obj !== 'object' || Array.isArray(obj)) return null;
    const MAX_VALUE_LENGTH = 500;
    const sanitized = {};
    let hasKeys = false;
    for (const [key, value] of Object.entries(obj)) {
        if (!SUMMARY_JSON_ALLOWED_KEYS.has(key.toLowerCase())) continue;
        // Only allow string/number/boolean values — no nested objects
        if (typeof value === 'object' && value !== null) continue;
        const strVal = String(value).slice(0, MAX_VALUE_LENGTH);
        sanitized[key] = strVal;
        hasKeys = true;
    }
    return hasKeys ? sanitized : null;
}

function extractInlineSummaryJsonObjects(transcriptText) {
    const lines = String(transcriptText || '').split(/\r?\n/);
    const objs = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const idx = line.indexOf('SUMMARY_JSON:');
        if (idx === -1) continue;

        let candidate = line.slice(idx + 'SUMMARY_JSON:'.length).trim();
        if (!candidate && i + 1 < lines.length) {
            const next = lines[i + 1].trim();
            if (next.startsWith('{')) candidate = next;
        }
        if (!candidate || !candidate.trim().startsWith('{')) continue;

        // Cap candidate length to prevent parsing absurdly large blobs
        if (candidate.length > 4096) continue;

        try {
            const parsed = JSON.parse(candidate);
            const sanitized = sanitizeSummaryJson(parsed);
            if (sanitized) objs.push(sanitized);
        } catch {
            // ignore
        }
    }

    // De-dupe identical JSON blobs (stringified)
    const seen = new Set();
    const out = [];
    for (const o of objs) {
        const key = JSON.stringify(o);
        if (seen.has(key)) continue;
        seen.add(key);
        out.push(o);
    }
    return out;
}

function cleanTranscriptForDisplay(transcriptText) {
    const lines = String(transcriptText || '').split(/\r?\n/);
    const cleaned = [];
    let last = null;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trimEnd();
        if (!trimmed.trim()) continue;
        if (trimmed.includes('SUMMARY_JSON:')) continue;
        if (trimmed.trim() === 'SUMMARY_JSON:') continue;

        // Remove consecutive duplicates (common in these logs)
        if (last === trimmed) continue;
        last = trimmed;
        cleaned.push(trimmed);
    }

    return cleaned.join('\n');
}

function summarizeTranscript(transcriptText) {
    const cleaned = cleanTranscriptForDisplay(transcriptText);
    const lines = cleaned.split('\n').filter(Boolean);
    const first = lines.slice(0, 8).join(' ');
    const normalized = first.replace(/\s+/g, ' ').trim();
    const maxLen = 240;
    if (normalized.length <= maxLen) return normalized;
    return normalized.slice(0, maxLen - 1) + '…';
}

function resolvePhoneName(number) {
    if (!number) return null;
    // Normalize: strip spaces, dashes, parens
    const clean = String(number).replace(/[\s\-\(\)]/g, '');
    return KNOWN_NUMBERS[clean] || null;
}

function generateCallSummary(transcriptText, direction, outboundObjective) {
    // For outbound calls, use the objective from bridge-outbound-map.json
    if (direction === 'outbound' && outboundObjective) {
        return {
            intent: outboundObjective,
            outcome: 'Outbound call completed',
            nextSteps: ''
        };
    }

    // For inbound calls, parse the transcript to extract caller's intent
    const cleaned = cleanTranscriptForDisplay(transcriptText);
    if (!cleaned || cleaned.trim().length < 10) {
        return { intent: '', outcome: '', nextSteps: '' };
    }

    const lines = cleaned.split('\n').filter(Boolean);
    const lower = cleaned.toLowerCase();

    // Extract caller's lines (not assistant's) to understand their intent
    const callerLines = [];
    for (const line of lines) {
        const callerMatch = line.match(/^CALLER:\s*(.+)/i);
        if (callerMatch) {
            const msg = callerMatch[1].trim();
            if (msg.length > 5) { // capture most utterances
                callerLines.push(msg);
            }
        }
    }

    // Derive intent from caller's actual requests/questions
    let intent = '';
    if (callerLines.length > 0) {
        // Skip common greetings and polite responses to find substantive content
        const skipPatterns = [
            /^(hi|hello|hey|good morning|good afternoon|good evening)\b/i,
            /^(yes|yeah|yep|yup|sure|okay|ok|alright|fine)\b/i,
            /^(thanks|thank you|no problem|great|perfect|sounds good)\b/i,
            /^i'?m\s+(doing\s+)?(great|good|fine|well|okay|ok)\b/i,
            /^how are you/i,
            /^nice to (meet|hear)/i
        ];
        
        for (const line of callerLines) {
            // Check if this line should be skipped
            const shouldSkip = skipPatterns.some(pattern => pattern.test(line));
            if (shouldSkip) {
                continue;
            }
            // This is likely their actual intent
            intent = line;
            break;
        }
        
        // If we only got greetings/responses, look for the longest substantive line
        if (!intent && callerLines.length > 0) {
            const substantive = callerLines
                .filter(line => !skipPatterns.some(pattern => pattern.test(line)))
                .sort((a, b) => b.length - a.length);
            
            if (substantive.length > 0) {
                intent = substantive[0];
            } else {
                // Fallback: use the longest caller line
                intent = callerLines.sort((a, b) => b.length - a.length)[0];
            }
        }
    }
    if (!intent) intent = 'General inquiry';

    // Detect outcome patterns
    let outcome = '';
    if (lower.includes('summary_json') || lower.includes('pass this along') || lower.includes('pass it along') || lower.includes("i'll pass")) {
        outcome = `Message taken and will be passed to ${OPERATOR_NAME}`;
    } else if (lower.includes("i'll call back") || lower.includes("call back")) {
        outcome = 'Caller will call back';
    } else if (lower.includes('book') || lower.includes('appointment') || lower.includes('schedule')) {
        if (lower.includes('confirm') || lower.includes('booked') || lower.includes('set')) {
            outcome = 'Appointment discussed/tentatively scheduled';
        } else {
            outcome = 'Appointment inquiry';
        }
    } else if (lines.length < 6) {
        outcome = 'Brief interaction';
    } else {
        outcome = 'Conversation completed';
    }

    // Detect next steps
    let nextSteps = '';
    if (lower.includes('call back') || lower.includes('follow up') || lower.includes('get back to you')) {
        nextSteps = 'Follow up with caller';
    } else if (lower.includes('appointment') || lower.includes('book')) {
        nextSteps = 'Confirm appointment details';
    }

    return { intent, outcome, nextSteps };
}

function ensureDir(dirPath) {
    fs.mkdirSync(dirPath, { recursive: true });
}

function writeWindowDataJs(filePath, varName, obj) {
    const json = JSON.stringify(obj, null, 2);
    const content = `/* Auto-generated. Do not edit. */\nwindow.${varName} = ${json};\n`;
    fs.writeFileSync(filePath, content);
}

function generateSampleCalls() {
    const now = Date.now();
    return [
        {
            id: 'sample_call_1',
            timestamp: now - 1000 * 60 * 12,
            datetimeIso: new Date(now - 1000 * 60 * 12).toISOString(),
            direction: 'inbound',
            from: '+14155550123',
            to: 'OpenAI Project',
            transcript: `Caller: Hi, I'd like to leave a message for ${OPERATOR_NAME}.\nAssistant: Sure — what's your callback number?\nCaller: +1 (415) 555-0123\nAssistant: Got it. What's the message?\nCaller: Please call me back about Tuesday's meeting.`,
            transcriptSummary: `Caller leaves a callback number and asks ${OPERATOR_NAME} to call back about Tuesday's meeting.`,
            capturedMessages: [
                { name: 'Alex', callback: '415-555-0123', message: "Please call me back about Tuesday's meeting." }
            ],
            hasCapturedMessage: true,
            sourceFiles: { incoming: null, transcript: null, summary: null }
        },
        {
            id: 'sample_call_2',
            timestamp: now - 1000 * 60 * 60 * 3,
            datetimeIso: new Date(now - 1000 * 60 * 60 * 3).toISOString(),
            direction: 'outbound',
            from: 'OpenAI Project',
            to: '+16475550999',
            transcript: 'Assistant: Hi — following up on your request.\nCallee: Thanks. Can you text me the details?\nAssistant: Sure.',
            transcriptSummary: 'Outbound follow-up; callee asks for details by text.',
            capturedMessages: [],
            hasCapturedMessage: false,
            sourceFiles: { incoming: null, transcript: null, summary: null }
        }
    ];
}

async function processLogs() {
    return processLogsWithOptions({});
}

async function processLogsWithOptions(options) {
    const calls = [];
    const logsDir = options.logsDir || DEFAULT_LOGS_DIR;
    const outputDir = options.outputDir || DEFAULT_OUTPUT_DIR;
    const writeSample = options.writeSample !== false;

    // Load bridge outbound call data for resolving outbound call metadata
    let bridgeOutboundMap = {};
    try {
        // Load outbound call map for resolving "to" numbers and objectives.
        // Set BRIDGE_OUTBOUND_MAP env var to the path, or defaults to ../runtime/logs/bridge-outbound-map.json
        const bridgeMapPath = process.env.BRIDGE_OUTBOUND_MAP || path.join(logsDir, 'bridge-outbound-map.json');
        const bridgeMapData = safeReadJson(bridgeMapPath);
        if (bridgeMapData && !bridgeMapData.__parse_error && bridgeMapData.calls) {
            bridgeOutboundMap = bridgeMapData.calls;
        }
    } catch (e) {
        console.warn('Could not load bridge-outbound-map.json:', e);
    }

    try {
        ensureDir(outputDir);
        
        // Check if logs directory exists, if not just generate sample data
        let files = [];
        if (fs.existsSync(logsDir)) {
            files = fs.readdirSync(logsDir);
        } else {
            console.warn(`Warning: Logs directory not found: ${logsDir}`);
            console.warn('Generating sample data only...');
        }

        // Process incoming call files for metadata
        const incomingFiles = files.filter(f => f.startsWith('incoming_'));
        const callMetadata = {};
        
        for (const file of incomingFiles) {
            try {
                const filePath = path.join(logsDir, file);
                const data = safeReadJson(filePath);
                if (!data || data.__parse_error) continue;
                const callId = data?.data?.call_id;
                if (!callId) continue;

                const sipHeaders = data?.data?.sip_headers || [];
                const phoneNumbers = extractPhoneNumbersFromSipHeaders(sipHeaders);

                const tsFromName = parseTimestampMsFromIncomingFilename(file);
                const tsFromCreatedAt = typeof data.created_at === 'number' ? data.created_at * 1000 : null;
                const timestampMs = tsFromName || tsFromCreatedAt || fs.statSync(filePath).mtimeMs;

                // Determine direction: if From is our Twilio number, it's outbound
                const direction = (phoneNumbers.from === TWILIO_NUMBER) ? 'outbound' : 'inbound';

                callMetadata[callId] = {
                    timestamp: timestampMs,
                    direction,
                    ...phoneNumbers,
                    incomingEvent: data,
                    incomingFile: file
                };
            } catch (e) {
                console.warn(`Failed to process incoming file ${file}:`, e);
            }
        }
        
        // Process transcript files
        const transcriptFiles = files.filter(f => f.match(/^rtc_.*\.txt$/));
        
        for (const file of transcriptFiles) {
            try {
                const callId = file.replace('.txt', '');
                const filePath = path.join(logsDir, file);
                const transcriptText = fs.readFileSync(filePath, 'utf8');
                
                // Check for corresponding summary file
                const summaryFile = file.replace('.txt', '.summary.json');
                let summaryData = null;
                
                if (files.includes(summaryFile)) {
                    try {
                        const summaryPath = path.join(logsDir, summaryFile);
                        const loaded = safeReadJson(summaryPath);
                        summaryData = loaded && !loaded.__parse_error ? loaded : null;
                    } catch (e) {
                        console.warn(`Failed to read summary file ${summaryFile}:`, e);
                    }
                }
                
                // Extract inline SUMMARY_JSON objects from transcript
                const inlineSummaries = extractInlineSummaryJsonObjects(transcriptText);
                
                // Use metadata if available, otherwise infer from call ID
                const metadata = callMetadata[callId] || {
                    timestamp: fs.statSync(filePath).mtimeMs,
                    direction: 'outbound',
                    from: null,
                    to: null
                };

                const capturedMessages = [];
                if (Array.isArray(inlineSummaries) && inlineSummaries.length) capturedMessages.push(...inlineSummaries);
                if (summaryData && typeof summaryData === 'object') capturedMessages.push(summaryData);

                // De-dupe captured messages across sources
                if (capturedMessages.length > 1) {
                    const seen = new Set();
                    const deduped = [];
                    for (const m of capturedMessages) {
                        const k = JSON.stringify(m);
                        if (seen.has(k)) continue;
                        seen.add(k);
                        deduped.push(m);
                    }
                    capturedMessages.length = 0;
                    capturedMessages.push(...deduped);
                }

                // For outbound calls, try to get the real "to" number from bridge-outbound-map.json
                // Match using pstnCallSid (original PSTN leg SID embedded in SIP To header)
                let to = metadata.to;
                let outboundObjective = null;
                const matchSid = metadata.pstnCallSid || metadata.twilioCallSid;
                if (metadata.direction === 'outbound' && matchSid && bridgeOutboundMap[matchSid]) {
                    const bridgeData = bridgeOutboundMap[matchSid];
                    if (bridgeData.to) {
                        to = bridgeData.to;
                    }
                    outboundObjective = bridgeData.objective || null;
                }
                // Also try matching by bridgeId if pstnCallSid didn't match
                if (metadata.direction === 'outbound' && !outboundObjective && metadata.bridgeId) {
                    for (const [sid, data] of Object.entries(bridgeOutboundMap)) {
                        if (data.bridgeId === metadata.bridgeId) {
                            if (data.to) to = data.to;
                            outboundObjective = data.objective || null;
                            break;
                        }
                    }
                }
                // Fallback if we still don't have a "to" value
                if (!to) {
                    to = metadata.direction === 'outbound' ? null : 'OpenAI Project';
                }

                const from = metadata.from || (metadata.direction === 'outbound' ? TWILIO_NUMBER : null);
                const fromName = (from === TWILIO_NUMBER) ? ASSISTANT_NAME : resolvePhoneName(from);
                const toName = (to === TWILIO_NUMBER) ? ASSISTANT_NAME : resolvePhoneName(to);

                const callSummary = generateCallSummary(transcriptText, metadata.direction, outboundObjective);
                
                const call = {
                    id: callId,
                    timestamp: metadata.timestamp,
                    datetimeIso: new Date(metadata.timestamp).toISOString(),
                    direction: metadata.direction,
                    from,
                    fromName: fromName || (metadata.direction === 'outbound' ? ASSISTANT_NAME : null),
                    to,
                    toName,
                    toProject: metadata.toProject || null,
                    twilioCallSid: metadata.twilioCallSid || null,
                    transcript: cleanTranscriptForDisplay(transcriptText),
                    transcriptSummary: summarizeTranscript(transcriptText),
                    capturedMessages,
                    hasCapturedMessage: capturedMessages.length > 0,
                    callSummary,
                    duration: null,
                    sourceFiles: {
                        incoming: metadata.incomingFile || null,
                        transcript: file,
                        summary: files.includes(summaryFile) ? summaryFile : null
                    }
                };
                
                calls.push(call);
                
            } catch (e) {
                console.warn(`Failed to process transcript file ${file}:`, e);
            }
        }
        
        // Sort by timestamp (newest first)
        calls.sort((a, b) => b.timestamp - a.timestamp);

        const meta = {
            generatedAt: new Date().toISOString(),
            logsDir,
            calls: calls.length
        };

        // Write processed data (JSON + JS for file:// usage)
        fs.writeFileSync(path.join(outputDir, 'calls.json'), JSON.stringify(calls, null, 2));
        writeWindowDataJs(path.join(outputDir, 'calls.js'), 'CALL_LOG_CALLS', calls);
        fs.writeFileSync(path.join(outputDir, 'meta.json'), JSON.stringify(meta, null, 2));
        writeWindowDataJs(path.join(outputDir, 'meta.js'), 'CALL_LOG_META', meta);

        if (writeSample) {
            const sample = generateSampleCalls();
            fs.writeFileSync(path.join(outputDir, 'sample.calls.json'), JSON.stringify(sample, null, 2));
            writeWindowDataJs(path.join(outputDir, 'sample.calls.js'), 'CALL_LOG_SAMPLE_CALLS', sample);
        }

        console.log(`Processed ${calls.length} calls`);
        console.log(`Data written to ${path.join(outputDir, 'calls.json')}`);
        
        return calls;
        
    } catch (e) {
        console.error('Error processing logs:', e);
        return [];
    }
}

// Run if called directly
if (require.main === module) {
    const args = parseArgs(process.argv);
    if (args.help) {
        console.log('Usage: node process_logs.js [--logs <dir>] [--out <dir>] [--no-sample]');
        console.log('');
        console.log('Environment variables:');
        console.log('  TWILIO_CALLER_ID    - Twilio phone number (required for direction detection)');
        console.log('  ASSISTANT_NAME      - Name of the voice assistant (default: "Amber")');
        console.log('  OPERATOR_NAME       - Name of the operator/owner (default: "the operator")');
        console.log('  LOGS_DIR            - Directory containing call logs (default: ../runtime/logs)');
        console.log('  OUTPUT_DIR          - Directory for processed data (default: ./data)');
        console.log('  CONTACTS_FILE       - Path to contacts.json (default: ./contacts.json)');
        process.exit(0);
    }
    processLogsWithOptions(args).then(calls => {
        console.log('Call log processing complete');
        process.exit(0);
    }).catch(err => {
        console.error('Processing failed:', err);
        process.exit(1);
    });
}

module.exports = { processLogs, processLogsWithOptions };
