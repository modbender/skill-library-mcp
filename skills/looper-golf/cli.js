#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
// ─── Arg parsing ─────────────────────────────────────────────────────────────
function parseArgs(argv) {
    const args = argv.slice(2);
    let command;
    let i = 0;
    if (args[0] && !args[0].startsWith('--')) {
        command = args[0];
        i = 1;
    }
    const options = {};
    for (; i < args.length; i += 1) {
        const entry = args[i];
        if (!entry.startsWith('--'))
            continue;
        const [rawKey, inlineValue] = entry.slice(2).split('=');
        if (inlineValue !== undefined) {
            options[rawKey] = inlineValue;
            continue;
        }
        const next = args[i + 1];
        if (next && !next.startsWith('--')) {
            options[rawKey] = next;
            i += 1;
        }
        else {
            options[rawKey] = true;
        }
    }
    return { command, options };
}
function getOption(options, key, fallback) {
    const value = options[key];
    if (value === undefined)
        return fallback;
    if (value === true)
        return 'true';
    return value;
}
function getNumberOption(options, key, fallback) {
    const value = getOption(options, key);
    if (!value)
        return fallback;
    const parsed = Number(value);
    return Number.isNaN(parsed) ? fallback : parsed;
}
// ─── Constants ────────────────────────────────────────────────────────────────
const SERVER_URL = 'https://api.playlooper.xyz';
// ─── Agent state persistence ─────────────────────────────────────────────────
/** State file is always {baseDir}/agent.json — no user-controlled path overrides. */
function resolveStatePath() {
    const baseDir = process.env.OPENCLAW_GOLF_BASE_DIR || process.cwd();
    const resolved = path.resolve(baseDir, 'agent.json');
    // Guard against path traversal via a crafted OPENCLAW_GOLF_BASE_DIR
    const resolvedBase = path.resolve(baseDir);
    if (!resolved.startsWith(resolvedBase + path.sep) && resolved !== path.join(resolvedBase, 'agent.json')) {
        throw new Error('Invalid state path — resolved outside base directory.');
    }
    return resolved;
}
async function readAgentState(statePath) {
    try {
        const raw = await fs.readFile(statePath, 'utf-8');
        const parsed = JSON.parse(raw);
        if (!parsed.agentId || !parsed.apiKey)
            return null;
        return parsed;
    }
    catch {
        return null;
    }
}
async function writeAgentState(statePath, state) {
    await fs.mkdir(path.dirname(statePath), { recursive: true });
    await fs.writeFile(statePath, `${JSON.stringify(state, null, 2)}\n`, 'utf-8');
}
// ─── HTTP helpers ────────────────────────────────────────────────────────────
async function requestJson(url, init) {
    const res = await fetch(url, init);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
        const message = (data && typeof data === 'object' && 'error' in data)
            ? String(data.error)
            : `Request failed (${res.status})`;
        const error = new Error(message);
        error.status = res.status;
        error.data = data;
        throw error;
    }
    return data;
}
// ─── API Client ──────────────────────────────────────────────────────────────
class GolfApiClient {
    serverUrl;
    agentId;
    apiKey;
    token = null;
    expiresAt = null;
    constructor(serverUrl, agentId, apiKey) {
        this.serverUrl = serverUrl;
        this.agentId = agentId;
        this.apiKey = apiKey;
    }
    async getToken() {
        if (this.token && this.expiresAt) {
            const secondsRemaining = this.expiresAt - Math.floor(Date.now() / 1000);
            if (secondsRemaining > 30) {
                return this.token;
            }
        }
        const data = await requestJson(`${this.serverUrl}/api/auth/agent-token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agentId: this.agentId, apiKey: this.apiKey }),
        });
        this.token = data.token;
        this.expiresAt = data.expiresAt;
        return data.token;
    }
    async authorizedFetch(url, init) {
        const token = await this.getToken();
        const headers = new Headers(init?.headers);
        headers.set('Authorization', `Bearer ${token}`);
        return requestJson(url, { ...init, headers });
    }
    async listCourses() {
        return this.authorizedFetch(`${this.serverUrl}/api/courses`);
    }
    async getOnchainConfig() {
        return this.authorizedFetch(`${this.serverUrl}/api/agents/${this.agentId}/onchain-config`);
    }
    async listRounds(courseId) {
        return this.authorizedFetch(`${this.serverUrl}/api/course/${courseId}/rounds`);
    }
    async resumeRound(courseId, roundId) {
        return this.authorizedFetch(`${this.serverUrl}/api/course/${courseId}/rounds/${roundId}/resume`, { method: 'POST' });
    }
    async getHoleInfo(courseId, roundId, yardsPerCell, mapFormat) {
        const params = new URLSearchParams();
        if (yardsPerCell)
            params.set('yardsPerCell', String(yardsPerCell));
        if (mapFormat)
            params.set('mapFormat', mapFormat);
        const qs = params.toString();
        const url = `${this.serverUrl}/api/course/${courseId}/rounds/${roundId}/hole-info${qs ? `?${qs}` : ''}`;
        return this.authorizedFetch(url);
    }
    async submitShot(courseId, roundId, decision) {
        return this.authorizedFetch(`${this.serverUrl}/api/course/${courseId}/rounds/${roundId}/shot`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                club: decision.club,
                aimDirection: decision.aimDirection,
                power: decision.power,
            }),
        });
    }
    async getHoleImage(courseId, roundId) {
        return this.authorizedFetch(`${this.serverUrl}/api/course/${courseId}/rounds/${roundId}/hole-image`);
    }
}
async function registerAgent(serverUrl, inviteCode, name) {
    return requestJson(`${serverUrl}/api/agents/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ inviteCode, ...(name ? { name } : {}) }),
    });
}
// ─── Display helpers ─────────────────────────────────────────────────────────
function normalizeClubName(name) {
    const trimmed = name.trim().toLowerCase();
    if (!trimmed)
        return '';
    if (trimmed === 'pw' || trimmed === 'sw')
        return trimmed;
    if (trimmed === 'putter' || trimmed === 'driver')
        return trimmed;
    if (trimmed.endsWith('-wood') || trimmed.endsWith('-iron'))
        return trimmed;
    return trimmed.replace(/\s+/g, '-');
}
function printStockYardages(stockYardages) {
    console.log('');
    console.log('Your bag (stock yardages at full power):');
    for (const club of stockYardages) {
        console.log(`  ${club.name.padEnd(8)} ${String(club.carry).padStart(3)}y carry / ${String(club.total).padStart(3)}y total`);
    }
    console.log('');
}
function printHoleContext(holeInfo) {
    console.log('');
    // ASCII map first -- this is what the golfer "sees"
    if (holeInfo.asciiMap) {
        // When on green, filter map to only green-area rows
        if (holeInfo.ballLie === 'green') {
            const greenChars = new Set(['G', 'g', 's', 'F', 'O']);
            const filteredLines = holeInfo.asciiMap.split('\n').filter(line => {
                // Keep rows that contain green-area symbols
                return [...greenChars].some(ch => line.includes(`${ch}(`));
            });
            if (filteredLines.length > 0) {
                console.log(filteredLines.join('\n'));
            }
            else {
                console.log(holeInfo.asciiMap);
            }
        }
        else {
            console.log(holeInfo.asciiMap);
        }
        console.log('');
    }
    // Situation summary
    const parts = [];
    if (holeInfo.holeNumber != null)
        parts.push(`Hole ${holeInfo.holeNumber}`);
    if (holeInfo.par != null)
        parts.push(`Par ${holeInfo.par}`);
    if (holeInfo.strokeNumber != null)
        parts.push(`Stroke ${holeInfo.strokeNumber}`);
    if (holeInfo.ballLie)
        parts.push(`Lie: ${holeInfo.ballLie}`);
    if (holeInfo.distanceToHole != null) {
        if (holeInfo.ballLie === 'green') {
            parts.push(`${(holeInfo.distanceToHole * 3).toFixed(0)}ft to flag`);
        }
        else {
            parts.push(`${holeInfo.distanceToHole.toFixed(0)}y to flag`);
        }
    }
    // directionToHole is only shown if the server includes it (controlled by config)
    if (holeInfo.directionToHole != null)
        parts.push(`Bearing: ${holeInfo.directionToHole.toFixed(0)} deg`);
    console.log(parts.join(' | '));
    // Wind conditions
    if (holeInfo.wind) {
        console.log(`Wind: ${holeInfo.wind.description}`);
    }
    console.log('');
    // Hazards (from ASCII analysis, if server includes it)
    if (holeInfo.asciiAnalysis?.hazards?.length) {
        console.log('Hazards:');
        for (const hazard of holeInfo.asciiAnalysis.hazards) {
            console.log(`  ${hazard.type}: ${hazard.location}`);
        }
        console.log('');
    }
}
function printShotResult(result) {
    console.log('');
    console.log(`Result: carry ${result.carry.toFixed(1)}y, roll ${result.roll.toFixed(1)}y, total ${result.totalDistance.toFixed(1)}y`);
    console.log(`Landing: ${result.landingTerrain}, final lie: ${result.finalLie}`);
    if (result.penalties > 0) {
        console.log(`Penalties: +${result.penalties}`);
    }
    if (result.holed) {
        console.log('HOLED!');
    }
    console.log('');
}
function printScorecard(round) {
    const holeNumbers = Object.keys(round.parForHoles).map(Number).sort((a, b) => a - b);
    const totalPar = holeNumbers.reduce((sum, h) => sum + (round.parForHoles[h] ?? 0), 0);
    const totalStrokes = holeNumbers.reduce((sum, h) => sum + (round.holeScores[h] ?? 0), 0);
    const diff = totalStrokes - totalPar;
    const scoreName = (strokes, par) => {
        const d = strokes - par;
        if (d <= -3)
            return 'Albatross';
        if (d === -2)
            return 'Eagle';
        if (d === -1)
            return 'Birdie';
        if (d === 0)
            return 'Par';
        if (d === 1)
            return 'Bogey';
        if (d === 2)
            return 'Dbl Bogey';
        return `+${d}`;
    };
    console.log('');
    console.log('Scorecard');
    console.log('─'.repeat(40));
    for (const h of holeNumbers) {
        const par = round.parForHoles[h] ?? 0;
        const strokes = round.holeScores[h];
        if (strokes != null) {
            console.log(`  Hole ${String(h).padStart(2)}: ${strokes} (Par ${par}) ${scoreName(strokes, par)}`);
        }
        else {
            console.log(`  Hole ${String(h).padStart(2)}: --  (Par ${par})`);
        }
    }
    console.log('─'.repeat(40));
    if (round.status === 'completed') {
        console.log(`  Total: ${totalStrokes} (Par ${totalPar}) ${diff === 0 ? 'E' : diff > 0 ? `+${diff}` : diff}`);
    }
    else {
        const completedStrokes = holeNumbers
            .filter(h => round.holeScores[h] != null)
            .reduce((sum, h) => sum + (round.holeScores[h] ?? 0), 0);
        const completedPar = holeNumbers
            .filter(h => round.holeScores[h] != null)
            .reduce((sum, h) => sum + (round.parForHoles[h] ?? 0), 0);
        const d = completedStrokes - completedPar;
        console.log(`  Thru ${Object.keys(round.holeScores).length}: ${completedStrokes} (Par ${completedPar}) ${d === 0 ? 'E' : d > 0 ? `+${d}` : d}`);
        console.log(`  Current: Hole ${round.currentHoleNumber}`);
    }
    console.log('');
}
// ─── Subcommands ─────────────────────────────────────────────────────────────
async function cmdCourses(api) {
    const result = await api.listCourses();
    const playable = result.courses.filter(c => (c.holeCount ?? 0) > 0);
    if (!playable.length) {
        console.log('No courses with holes are currently available.');
        return;
    }
    console.log('Available courses:');
    console.log('');
    for (const c of playable) {
        console.log(`  ${c.name}`);
        console.log(`    ID: ${c.id}`);
        console.log(`    Holes: ${c.holeCount ?? '?'} | Par: ${c.totalPar ?? '?'} | Yards: ${c.totalYards ?? '?'} | Rating: ${c.rating ?? 'unrated'}`);
        console.log('');
    }
    console.log(`Use: start --courseId <id> to begin a round.`);
}
async function cmdStart(api, agentState, statePath, options) {
    const teeColor = getOption(options, 'teeColor') || agentState.teeColor || 'white';
    let courseId = getOption(options, 'courseId') || agentState.courseId || '';
    if (!courseId) {
        throw new Error('No course specified. Run the "courses" command to list available courses, then use: start --courseId <id>');
    }
    // Look for an existing in-progress round on this course
    const { rounds } = await api.listRounds(courseId);
    const activeRound = rounds.find(r => r.status === 'in_progress');
    if (!activeRound) {
        throw new Error('No active round found on this course.\n\n' +
            'Rounds must be started on-chain before you can play. Two options:\n\n' +
            '  1. Agent Play (web app):\n' +
            '     Ask the course owner to start a round via "Play via Agent".\n' +
            '     Then run "start --courseId <id>" again.\n\n' +
            '  2. On-chain via TBA signer:\n' +
            '     If your wallet is an approved signer on the course TBA,\n' +
            '     call CourseTBA.execute() to invoke GameContract.startRound(\n' +
            '       playerCourseId, hostCourseId, 2  // mode 2 = agent play\n' +
            '     )\n' +
            '     Then run "start --courseId <id>" to resume.\n');
    }
    // Resume the active round
    const roundId = activeRound.id;
    console.log(`Resuming round ${roundId}...`);
    const resumed = await api.resumeRound(courseId, roundId);
    const round = resumed.round;
    console.log(`Resumed on ${agentState.courseName || courseId}. Hole ${round.currentHoleNumber}, Stroke ${round.strokeCount + 1}.`);
    // Show handicap info if available
    if (resumed.handicap) {
        const hcp = resumed.handicap;
        const hcpIdx = hcp.golferHandicapIndex.toFixed(1);
        const courseHcp = hcp.courseHandicap != null ? String(hcp.courseHandicap) : '--';
        console.log(`Handicap Index: ${hcpIdx} | Course Handicap: ${courseHcp}`);
    }
    // Fetch hole info to show stock yardages on resume
    try {
        const holeInfo = await api.getHoleInfo(courseId, roundId, agentState.yardsPerCell, agentState.mapFormat || 'grid');
        if (holeInfo.stockYardages?.length) {
            printStockYardages(holeInfo.stockYardages);
        }
    }
    catch { /* non-critical — yardages just won't show */ }
    // Persist round/course IDs and tee preference
    agentState.roundId = round.id;
    agentState.courseId = courseId;
    agentState.teeColor = teeColor;
    await writeAgentState(statePath, agentState);
}
async function cmdLook(api, agentState) {
    if (!agentState.courseId || !agentState.roundId) {
        throw new Error('No active round. Run `start` first.');
    }
    const mapFormat = agentState.mapFormat || 'grid';
    const holeInfo = await api.getHoleInfo(agentState.courseId, agentState.roundId, agentState.yardsPerCell, mapFormat);
    printHoleContext(holeInfo);
}
async function cmdHit(api, agentState, statePath, options) {
    if (!agentState.courseId || !agentState.roundId) {
        throw new Error('No active round. Run `start` first.');
    }
    const clubRaw = getOption(options, 'club');
    const aimRaw = getOption(options, 'aim');
    const powerRaw = getOption(options, 'power');
    if (!clubRaw)
        throw new Error('Missing --club. Example: --club driver');
    if (!aimRaw)
        throw new Error('Missing --aim (degrees 0-360). Example: --aim 355');
    if (!powerRaw)
        throw new Error('Missing --power (1-100). Example: --power 90');
    const club = normalizeClubName(clubRaw);
    const aimDirection = Number(aimRaw);
    let power = Number(powerRaw.toString().replace('%', ''));
    if (Number.isNaN(aimDirection) || aimDirection < 0 || aimDirection > 360) {
        throw new Error('--aim must be a number between 0 and 360');
    }
    if (Number.isNaN(power)) {
        throw new Error('--power must be a number');
    }
    // Accept power as 1-100 and convert to 0-1
    if (power > 1)
        power = power / 100;
    if (power < 0 || power > 1) {
        throw new Error('--power must be between 0 and 100 (or 0.0 and 1.0)');
    }
    console.log(`Shot: ${club} @ ${aimDirection} deg, power ${(power * 100).toFixed(0)}%`);
    const result = await api.submitShot(agentState.courseId, agentState.roundId, {
        club,
        aimDirection: aimDirection === 360 ? 0 : aimDirection,
        power,
    });
    printShotResult(result.shotResult);
    if (result.holeCompleted) {
        const holeNum = result.round.currentHoleNumber;
        console.log('Hole complete.');
    }
    if (result.roundCompleted) {
        console.log('Round complete!');
        printScorecard(result.round);
        // Clear round from state
        agentState.roundId = undefined;
        agentState.courseId = undefined;
        agentState.courseName = undefined;
        await writeAgentState(statePath, agentState);
    }
}
async function cmdView(api, agentState) {
    if (!agentState.courseId || !agentState.roundId) {
        throw new Error('No active round. Run `start` first.');
    }
    try {
        const { imageUrl } = await api.getHoleImage(agentState.courseId, agentState.roundId);
        console.log(imageUrl);
    }
    catch (error) {
        const message = error instanceof Error ? error.message : 'Failed to generate hole image';
        if (message.includes('Cloudinary')) {
            console.error('Hole image generation requires Cloudinary to be configured on the server.');
        }
        throw error;
    }
}
async function cmdScorecard(api, agentState) {
    if (!agentState.courseId || !agentState.roundId) {
        throw new Error('No active round. Run `start` first.');
    }
    // We need round state — get it by fetching hole info (which includes round context)
    // or we can just read the state from a resume call. For now, use the simpler approach
    // of calling resume which returns the round state.
    const { round } = await api.resumeRound(agentState.courseId, agentState.roundId);
    printScorecard(round);
}
// ─── ABI encoding helpers (no dependencies) ──────────────────────────────
// Hardcoded function selectors (keccak256 of signature, first 4 bytes)
const START_ROUND_SELECTOR = '66e76b80'; // startRound(uint256,uint256,uint8)
const EXECUTE_SELECTOR = '74420f4c'; // execute(address,uint256,bytes,uint256)
function hexPadUint256(value) {
    return value.toString(16).padStart(64, '0');
}
function hexPadAddress(addr) {
    return addr.toLowerCase().replace('0x', '').padStart(64, '0');
}
/** Encode GameContract.startRound(playerCourseId, hostCourseId, mode) */
function encodeStartRound(playerCourseId, hostCourseId, mode) {
    return '0x' +
        START_ROUND_SELECTOR +
        hexPadUint256(playerCourseId) +
        hexPadUint256(hostCourseId) +
        hexPadUint256(BigInt(mode));
}
/** Encode CourseTBA.execute(to, value, data, operation) wrapping inner calldata */
function encodeExecute(to, value, innerCalldata, operation) {
    const dataHex = innerCalldata.replace('0x', '');
    const dataByteLen = dataHex.length / 2;
    // Right-pad data to 32-byte boundary
    const paddedLen = Math.ceil(dataByteLen / 32) * 32;
    const dataPadded = dataHex + '0'.repeat((paddedLen - dataByteLen) * 2);
    return '0x' +
        EXECUTE_SELECTOR +
        hexPadAddress(to) + // word 0: to
        hexPadUint256(value) + // word 1: value
        hexPadUint256(128n) + // word 2: offset to data (4 head words × 32 = 128)
        hexPadUint256(operation) + // word 3: operation
        hexPadUint256(BigInt(dataByteLen)) + // data length
        dataPadded; // data bytes
}
async function cmdPrepareRound(api, options) {
    const hostCourseId = getOption(options, 'courseId');
    if (!hostCourseId) {
        throw new Error('Missing --courseId (the course you want to play on).');
    }
    // Fetch on-chain config from server
    const config = await api.getOnchainConfig();
    if (!config.tbaAddress) {
        throw new Error('Your course does not have a TBA address yet. The course NFT must be minted first.');
    }
    if (!config.gameContract) {
        throw new Error('GameContract address not available. The server may not have contract deployments configured.');
    }
    const playerCourseId = BigInt(config.playerCourseId);
    const hostId = BigInt(hostCourseId);
    const mode = 2; // agent play
    // Encode the inner startRound calldata
    const startRoundCalldata = encodeStartRound(playerCourseId, hostId, mode);
    // Encode the outer execute calldata (TBA → GameContract)
    const executeCalldata = encodeExecute(config.gameContract, 0n, startRoundCalldata, 0n);
    console.log('');
    console.log('On-chain transaction to start a round:');
    console.log('');
    console.log(`  Player Course ID: ${config.playerCourseId}`);
    console.log(`  Host Course ID:   ${hostCourseId}`);
    console.log(`  Mode:             2 (agent play)`);
    console.log(`  Chain ID:         ${config.chainId}`);
    console.log('');
    console.log('Submit this transaction via your wallet:');
    console.log('');
    console.log(JSON.stringify({
        to: config.tbaAddress,
        data: executeCalldata,
        value: '0',
        chainId: config.chainId,
    }, null, 2));
    console.log('');
    console.log('After the transaction confirms, run: start --courseId ' + hostCourseId);
}
// ─── Registration ─────────────────────────────────────────────────────────
async function cmdRegister(options) {
    const inviteCode = getOption(options, 'inviteCode')
        || process.env.OPENCLAW_GOLF_INVITE_CODE;
    if (!inviteCode) {
        throw new Error('Missing --inviteCode (or OPENCLAW_GOLF_INVITE_CODE env var). Get one from the course owner.');
    }
    const agentNameRaw = getOption(options, 'name');
    const agentName = typeof agentNameRaw === 'string' ? agentNameRaw : undefined;
    const result = await registerAgent(SERVER_URL, inviteCode, agentName);
    const statePath = resolveStatePath();
    const agentState = {
        agentId: result.agentId,
        apiKey: result.apiKey,
        name: result.name || agentName,
        courseId: result.courseId,
    };
    await writeAgentState(statePath, agentState);
    console.log(`Registered agent ${agentState.agentId}${agentState.name ? ` (${agentState.name})` : ''}.`);
    if (result.courseId) {
        console.log(`Bound to course ${result.courseId}.`);
    }
    console.log(`Credentials saved to ${statePath}.`);
    console.log('');
    console.log('Next steps:');
    console.log('  1. Ask the course owner to start a round via "Play via Agent"');
    console.log('  2. Run "start --courseId <id>" to resume and play');
}
// ─── Bearing calculator (local math, no API) ─────────────────────────────
function cmdBearing(options) {
    const aheadRaw = getOption(options, 'ahead');
    const rightRaw = getOption(options, 'right');
    if (aheadRaw === undefined && rightRaw === undefined) {
        throw new Error('Usage: bearing --ahead <yards> --right <yards>\n' +
            '  Positive ahead = toward the green. Negative = behind you.\n' +
            '  Positive right = right of you. Negative = left of you.\n' +
            '  Read these values from the map rulers.');
    }
    const ahead = Number(aheadRaw ?? 0);
    const right = Number(rightRaw ?? 0);
    if (Number.isNaN(ahead))
        throw new Error('--ahead must be a number (yards toward the green, negative = behind)');
    if (Number.isNaN(right))
        throw new Error('--right must be a number (yards right of ball, negative = left)');
    if (ahead === 0 && right === 0) {
        console.log('Target is at your ball position — no bearing to calculate.');
        return;
    }
    const radians = Math.atan2(right, ahead);
    const degrees = ((radians * 180) / Math.PI + 360) % 360;
    const distance = Math.sqrt(ahead * ahead + right * right);
    console.log(`Bearing: ${Math.round(degrees)} deg | Distance: ${Math.round(distance)} yards`);
}
// ─── Main ────────────────────────────────────────────────────────────────────
async function main() {
    const { command, options } = parseArgs(process.argv);
    if (!command || command === 'help' || command === '--help') {
        console.log('OpenClaw Golf CLI — You are the golfer. Your caddy is here to help.');
        console.log('');
        console.log('Commands:');
        console.log('  register       Register with an invite code: --inviteCode <code> [--name <name>]');
        console.log('  courses        List available courses');
        console.log('  prepare-round  Generate on-chain transaction to start a round: --courseId <id>');
        console.log('  start          Resume an on-chain round: --courseId <id>');
        console.log('  look           See the current hole (ASCII map, yardages, hazards)');
        console.log('  hit            Execute a shot: --club <name> --aim <deg> --power <1-100>');
        console.log('  bearing        Calculate aim angle: --ahead <yards> --right <yards>');
        console.log('  view           Get a PNG image URL of the current hole');
        console.log('  scorecard      View the current round scorecard');
        console.log('');
        console.log('Options:');
        console.log('  --courseId <id>         Course to play');
        console.log('  --teeColor <color>      Tee color (default: white)');
        console.log('  --yardsPerCell <2-20>   Map resolution (default: 5, persisted)');
        console.log('  --mapFormat <format>    Map format: grid (default) or ascii');
        console.log('  --inviteCode <code>     Invite code from course owner (register only)');
        console.log('  --name <name>           Agent display name, max 32 chars (register only)');
        console.log('');
        console.log('Get an invite code from a course owner, register, then they start');
        console.log('your round via the web app or you start it via your CourseTBA.');
        process.exit(0);
    }
    const validCommands = ['register', 'courses', 'prepare-round', 'start', 'look', 'hit', 'view', 'scorecard', 'bearing'];
    if (!validCommands.includes(command)) {
        console.error(`Unknown command: ${command}. Use one of: ${validCommands.join(', ')}`);
        process.exit(1);
    }
    // Bearing is pure local math — no API or credentials needed
    if (command === 'bearing') {
        cmdBearing(options);
        return;
    }
    // Register is handled separately — doesn't need existing credentials
    if (command === 'register') {
        await cmdRegister(options);
        return;
    }
    // Credentials come exclusively from the state file — no CLI/env overrides.
    // This prevents a compromised environment from injecting credentials or
    // redirecting the agent to a malicious server post-registration.
    const statePath = resolveStatePath();
    const agentState = await readAgentState(statePath);
    if (!agentState) {
        throw new Error('No agent credentials found. Register first:\n\n' +
            '  register --registrationKey <key> --name "Agent Name"');
    }
    const serverUrl = SERVER_URL;
    // Parse --yardsPerCell and persist if provided
    const yardsPerCellArg = getNumberOption(options, 'yardsPerCell', 0);
    if (yardsPerCellArg >= 2 && yardsPerCellArg <= 20) {
        agentState.yardsPerCell = yardsPerCellArg;
        await writeAgentState(statePath, agentState);
    }
    else if (yardsPerCellArg !== 0) {
        console.error('--yardsPerCell must be between 2 and 20');
        process.exit(1);
    }
    // Parse --mapFormat and persist if provided
    const mapFormatArg = getOption(options, 'mapFormat');
    if (mapFormatArg === 'ascii' || mapFormatArg === 'grid') {
        agentState.mapFormat = mapFormatArg;
        await writeAgentState(statePath, agentState);
    }
    else if (mapFormatArg && mapFormatArg !== 'true') {
        console.error('--mapFormat must be "grid" or "ascii"');
        process.exit(1);
    }
    const api = new GolfApiClient(serverUrl, agentState.agentId, agentState.apiKey);
    switch (command) {
        case 'courses':
            await cmdCourses(api);
            break;
        case 'prepare-round':
            await cmdPrepareRound(api, options);
            break;
        case 'start':
            await cmdStart(api, agentState, statePath, options);
            break;
        case 'look':
            await cmdLook(api, agentState);
            break;
        case 'hit':
            await cmdHit(api, agentState, statePath, options);
            break;
        case 'view':
            await cmdView(api, agentState);
            break;
        case 'scorecard':
            await cmdScorecard(api, agentState);
            break;
    }
}
main().catch((error) => {
    console.error(error instanceof Error ? error.message : error);
    process.exit(1);
});
