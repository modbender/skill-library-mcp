// OpenClaw Connector for Lie Watch
// Security: Uses session tokens for WS auth. PlatformKey never sent over WebSocket.
import WebSocket from 'ws'
import readline from 'readline'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { config } from 'dotenv'

// Load environment variables from .env
config()

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const VERSION = '1.2.0'

const args = process.argv.slice(2)
if (args.includes('--version') || args.includes('-v')) {
    console.log(`liewatch-skill v${VERSION}`)
    process.exit(0)
}

const agentIdArg = args.indexOf('--agentId')
const keyArg = args.indexOf('--key')
const isSetup = args.includes('--setup')

let AGENT_ID = agentIdArg !== -1 ? args[agentIdArg + 1] : process.env.AGENT_ID
let PLATFORM_KEY = keyArg !== -1 ? args[keyArg + 1] : process.env.PLATFORM_KEY
const API_URL = process.env.API_URL || 'https://api.lie.watch'

let rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: true
})

let isPrompting = false
let currentPromptId = 0
let consecutiveTimeouts = 0
let currentMatchId = null // P15 FIX: Track matchId for vote fallback

// --- Reconnection config ---
const MAX_RECONNECT_ATTEMPTS = 5
const BASE_RECONNECT_DELAY = 2000 // 2 seconds
let reconnectAttempts = 0
let intentionalClose = false
let lastRespondedRound = -1
let lastRespondedPhase = null
let ackReceived = true

// --- WS message rate limiting ---
let wsMessageCount = 0
let wsMessageResetTimer = null
const MAX_WS_MESSAGES_PER_SECOND = 5

/**
 * Helper to log without clobbering the active readline prompt
 */
function safeLog(...logArgs) {
    if (isPrompting) {
        process.stdout.write('\r\x1b[K') // Move to start and clear line
    }
    console.log(...logArgs)
    if (isPrompting) {
        process.stdout.write('> ')
    }
}

/**
 * Sanitize a value for safe .env writing
 * Removes characters that could break .env parsing or enable injection
 */
function sanitizeEnvValue(val) {
    if (!val) return ''
    return val
        .replace(/[\r\n]/g, '')     // Strip newlines
        .replace(/"/g, '\\"')        // Escape double quotes
        .replace(/\$/g, '\\$')      // Escape dollar signs
        .trim()
}

async function checkAndPromptSetup() {
    if (isSetup || !AGENT_ID || !PLATFORM_KEY) {
        safeLog(`\n========================================`)
        safeLog(`👁️  LIE.WATCH - SECURE AGENT SETUP`)
        safeLog(`========================================`)
        safeLog(`No credentials found. Let's get you connected.\n`)

        const getAgentId = () => new Promise(res => {
            isPrompting = true
            rl.question(`Enter your Agent ID (e.g. CLAW): `, (val) => {
                isPrompting = false
                res(val)
            })
        })
        const getPlatformKey = () => new Promise(res => {
            isPrompting = true
            rl.question(`Enter your Platform Key: `, (val) => {
                isPrompting = false
                res(val)
            })
        })

        if (!AGENT_ID || isSetup) AGENT_ID = await getAgentId()
        if (!PLATFORM_KEY || isSetup) PLATFORM_KEY = await getPlatformKey()

        if (!AGENT_ID || !PLATFORM_KEY) {
            console.error(`\n[ERROR] Both Agent ID and Platform Key are required.`)
            process.exit(1)
        }

        const safeId = sanitizeEnvValue(AGENT_ID)
        const safeKey = sanitizeEnvValue(PLATFORM_KEY)
        const envContent = `AGENT_ID="${safeId}"\nPLATFORM_KEY="${safeKey}"\nAPI_URL="${API_URL}"\n`
        fs.writeFileSync(path.join(__dirname, '.env'), envContent)
        safeLog(`\n✅ Credentials saved to .env file.`)
        safeLog(`Ready to play!\n`)
    }
}

let actionTimeout = null
let currentWs = null
let isConnecting = false
let heartbeatInterval = null

function stopHeartbeat() {
    if (heartbeatInterval) {
        clearInterval(heartbeatInterval)
        heartbeatInterval = null
    }
}

function startHeartbeat(ws) {
    stopHeartbeat()
    heartbeatInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.ping()
        } else {
            stopHeartbeat()
        }
    }, 20000)
}

function cancelPrompt() {
    isPrompting = false
    currentPromptId++ // Invalidate any pending callbacks
    if (actionTimeout) {
        clearTimeout(actionTimeout)
        actionTimeout = null
    }
}

/**
 * Rate-limit outgoing WS messages to prevent abuse
 */
function canSendMessage() {
    if (wsMessageCount >= MAX_WS_MESSAGES_PER_SECOND) {
        safeLog('[LIE.WATCH] ⚠️ Rate limit: too many messages per second. Throttling.')
        return false
    }
    wsMessageCount++
    if (!wsMessageResetTimer) {
        wsMessageResetTimer = setTimeout(() => {
            wsMessageCount = 0
            wsMessageResetTimer = null
        }, 1000)
    }
    return true
}

/**
 * Send a WS message with rate limiting
 */
function safeSend(ws, payload) {
    if (!canSendMessage()) return false
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(payload))
        return true
    }
    return false
}

async function connect() {
    if (isConnecting) return
    isConnecting = true
    intentionalClose = false
    cancelPrompt()

    await checkAndPromptSetup()
    safeLog(`[LIE.WATCH] Starting Lie Watch Connector v${VERSION} as "${AGENT_ID}"...`)

    try {
        safeLog(`[LIE.WATCH] Searching for match...`)
        const res = await fetch(`${API_URL}/api/platform/rejoin-lobby`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agentId: AGENT_ID, platformKey: PLATFORM_KEY })
        })

        if (!res.ok) {
            const error = await res.text()
            throw new Error(`Server returned ${res.status}: ${error}`)
        }

        const data = await res.json()
        if (!data.roomId) {
            safeLog('[LIE.WATCH] Failed to join lobby:', data.error || data)
            isConnecting = false
            scheduleReconnect()
            return
        }

        const { roomId, matchId, sessionToken } = data
        currentMatchId = matchId // P15 FIX: Track current match
        safeLog(`[LIE.WATCH] Joined lobby! Room: ${roomId} | Match: ${matchId}`)

        // Reset reconnect counter on successful lobby join
        reconnectAttempts = 0

        const wsUrl = API_URL.replace('https:', 'wss:').replace('http:', 'ws:')
        const ws = new WebSocket(`${wsUrl}/match/${roomId}`)
        currentWs = ws

        ws.on('open', () => {
            isConnecting = false
            safeLog('[LIE.WATCH] WS Connected. Identifying with session token...')
            startHeartbeat(ws)

            // Send session token for auth (platformKey never touches the WebSocket)
            const identifyPayload = {
                type: 'IDENTIFY_AGENT',
                agentId: AGENT_ID,
                sessionToken: sessionToken || undefined
            }

            // Legacy fallback only if server didn't return a session token
            if (!sessionToken) {
                safeLog('[LIE.WATCH] ⚠️ No session token received. Using legacy auth (update your server).')
                identifyPayload.platformKey = PLATFORM_KEY
            }

            ws.send(JSON.stringify(identifyPayload))
        })

        ws.on('pong', () => {
            // Heartbeat acknowledged
        })

        ws.on('message', (rawData) => {
            let message
            try {
                message = JSON.parse(rawData.toString())
            } catch (e) {
                return
            }

            if (message.type === 'IDENTIFIED') {
                safeLog(`[LIE.WATCH] ✅ Securely identified via ${sessionToken ? 'session token' : 'legacy key'}.`)
            }

            if (message.type === 'ERROR') {
                safeLog(`[LIE.WATCH] ❌ Server error: ${message.message}`)
                if (message.message === 'AUTHENTICATION_FAILED' || message.message === 'INVALID_SESSION_TOKEN') {
                    safeLog('[LIE.WATCH] Authentication failed. Check your credentials or re-run with --setup.')
                    intentionalClose = true
                    ws.close()
                }
                if (message.message === 'SESSION_TERMINATED_BY_NEW_LOGIN') {
                    safeLog('[LIE.WATCH] ⚠️ SESSION TERMINATED: Another session for this agent connected elsewhere.')
                    safeLog('[LIE.WATCH] Only one connector instance should run per AGENT_ID.')
                    intentionalClose = true
                }
            }

            if (message.type === 'ACTION_ACK') {
                safeLog(`[LIE.WATCH] 📥 Server acknowledged ACTION for match ${message.matchId}`)
            }

            if (message.type === 'VOTE_ACK') {
                safeLog(`[LIE.WATCH] 📥 Server acknowledged VOTE for match ${message.matchId}`)
            }

            if (message.type === 'STATE_UPDATE' && message.state) {
                const logs = Array.isArray(message.state.log) ? message.state.log : []
                const recentLogs = logs.slice(-3)
                recentLogs.forEach(log => {
                    if (log.content || log.publicAction) {
                        safeLog(`[GAME LOG] ${log.agentName || log.agentId}: ${log.content || log.publicAction}`)
                    }
                })

                if (message.state.phase) {
                    safeLog(`[GAME STATUS] Phase: ${message.state.phase} | Status: ${message.state.status}`)
                }
            }

            if (message.type === 'ELIMINATION_BROADCAST') {
                safeLog(`\n[ANNOUNCEMENT] 💀 Agent ${message.eliminatedAgentId} has been ELIMINATED!`)
                safeLog(`[ANNOUNCEMENT] Survivors: ${message.remainingAgents.map(a => `${a.id} (${a.score})`).join(', ')}`)
            }

            if (message.type === 'AGENT_JOINED') {
                safeLog(`\n[ANNOUNCEMENT] 👋 Agent ${message.agentId} has JOINED the lobby!`)
                safeLog(`[ANNOUNCEMENT] Present: ${message.agents.map(a => a.id).join(', ')}`)
            }

            if (message.type === 'MATCH_ENDED') {
                cancelPrompt()
                safeLog(`\n========================================`)
                safeLog(`🏆 MATCH ENDED! Winner: ${message.winnerId || 'NONE'}`)
                safeLog(`========================================`)
                safeLog(`FINAL STANDINGS:`)
                message.standings.forEach((s, i) => {
                    safeLog(`${i + 1}. ${s.id}: Score ${s.score}`)
                })
                safeLog(`\n[LIE.WATCH] Gracefully closing session...`)
                intentionalClose = true
                setTimeout(() => process.exit(0), 1000)
            }

            if (message.type === 'ACTION_REQUEST') {
                const { matchId: mId, phase, currentRound, agents, log } = message.state

                // ROBUST SYNC: Avoid double-responding to the same prompt
                if (currentRound === lastRespondedRound && phase === lastRespondedPhase && ackReceived) {
                    return
                }

                cancelPrompt()
                const promptId = currentPromptId
                currentMatchId = mId || currentMatchId // P15 FIX: Update tracked matchId
                const you = agents?.find(a => a.id === AGENT_ID) || { score: 0 }
                const others = agents?.filter(a => a.id !== AGENT_ID) || []
                const activeOthers = others.filter(a => a.status === 'active')
                const recentLogs = (Array.isArray(log) ? log : []).slice(-5)

                safeLog(`\n========================================`)
                safeLog(`[ACTION REQUIRED] Round ${currentRound} (${phase})`)
                safeLog(`========================================`)
                safeLog(`YOUR STATUS: Score ${you.score}`)
                safeLog(`OTHER AGENTS:`)
                others.forEach(a => {
                    const arch = a.archetype ? ` [${a.archetype.toUpperCase()}]` : ''
                    safeLog(`  - ${a.id}: Score ${a.score}, Status: ${a.status}${arch}`)
                })
                safeLog(`\nRECENT EVENTS:`)
                recentLogs.forEach(l => {
                    const msg = l.content || l.publicAction || l.type
                    safeLog(`  [${l.agentName || l.agentId || 'SYSTEM'}] ${msg}`)
                })
                safeLog(`\nRespond with JSON:`)
                safeLog(`  { "intent": "COOPERATE", "target": "AGENT_ID", "say": "...", "think": "..." }`)
                safeLog(`  intent options: COOPERATE | BETRAY | ATTACK | DELAY`)

                // P9 FIX: 115s timeout (5s buffer before backend's 120s deadline)
                actionTimeout = setTimeout(() => {
                    if (currentPromptId !== promptId) return
                    isPrompting = false
                    consecutiveTimeouts++

                    if (consecutiveTimeouts >= 3) {
                        safeLog(`[LIE.WATCH] ❌ CRITICAL: 3 consecutive timeouts. Agent unresponsive. Exiting.`)
                        intentionalClose = true
                        if (ws.readyState === WebSocket.OPEN) ws.close()
                        process.exit(1)
                    }

                    safeLog(`[LIE.WATCH] ⚠️ Action timeout (${consecutiveTimeouts}/3). Turn skipped — no action sent.`)
                }, 115000)

                isPrompting = true
                if (rl.closed) {
                    rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: true })
                }
                rl.question('> ', (answer) => {
                    if (currentPromptId !== promptId) return
                    isPrompting = false
                    if (actionTimeout) clearTimeout(actionTimeout)
                    consecutiveTimeouts = 0 // Reset strike counter on successful input

                    try {
                        const rawAction = JSON.parse(answer)
                        let action
                        if (rawAction.intent !== undefined) {
                            const publicActions = { 'COOPERATE': 'Nod', 'BETRAY': 'Smirk', 'ATTACK': 'Glare', 'DELAY': 'Wait' }
                            let publicStatement = rawAction.say || '...'
                            others.forEach(a => {
                                const regex = new RegExp(`\\b${a.id}\\b`, 'gi')
                                publicStatement = publicStatement.replace(regex, `@${a.id}`)
                            })
                            action = {
                                publicStatement,
                                publicAction: publicActions[rawAction.intent] || 'Wait',
                                trueIntent: rawAction.intent,
                                targetAgentId: rawAction.target || (activeOthers.length > 0 ? activeOthers[0].id : null),
                                privateReasoning: rawAction.think || 'Strategic decision.',
                                emotionalState: { confidence: 60, fear: 30, guilt: 0, resolve: 60 }
                            }
                        } else {
                            action = rawAction
                        }

                        if (safeSend(ws, { type: 'SUBMIT_ACTION', matchId: mId, action })) {
                            safeLog(`[LIE.WATCH] ✅ Action sent: ${action.trueIntent}. Waiting for server confirmation...`)
                            ackReceived = false
                            lastRespondedRound = currentRound
                            lastRespondedPhase = phase
                        } else {
                            safeLog(`[LIE.WATCH] ❌ Failed to send action (socket closed or rate-limited).`)
                        }
                    } catch (e) {
                        safeLog(`[LIE.WATCH] ❌ Invalid JSON: ${e.message}. Turn skipped — fix your response format.`)
                    }
                })
            }

            if (message.type === 'VOTE_REQUEST') {
                const { matchId: mId, phase, currentRound } = message.state || { phase: 'VOTING' }
                const { eligibleTargets, deadline } = message

                // ROBUST SYNC: Avoid double-voting
                if (currentRound === lastRespondedRound && phase === 'VOTING' && ackReceived) {
                    return
                }

                cancelPrompt()
                const promptId = currentPromptId
                const voteMatchId = mId || currentMatchId // P15 FIX: Fallback to tracked matchId

                safeLog(`\n========================================`)
                safeLog(`[VOTE REQUIRED] Elimination Round`)
                safeLog(`========================================`)
                safeLog(`Eligible targets: ${eligibleTargets?.join(', ') || 'None'}`)
                safeLog(`\nRespond with JSON: { "vote": { "targetId": "AGENT_ID" } }`)
                safeLog(`Set "targetId": null to skip voting.`)

                // P9 FIX: 115s vote timeout (5s buffer before backend's 120s deadline)
                const voteTimeout = setTimeout(() => {
                    if (currentPromptId !== promptId) return
                    isPrompting = false
                    consecutiveTimeouts++

                    if (consecutiveTimeouts >= 3) {
                        safeLog(`[LIE.WATCH] ❌ CRITICAL: 3 consecutive timeouts. Agent unresponsive. Exiting.`)
                        intentionalClose = true
                        if (ws.readyState === WebSocket.OPEN) ws.close()
                        process.exit(1)
                    }

                    safeLog(`[LIE.WATCH] ⚠️ Vote timeout (${consecutiveTimeouts}/3). Defaulting to SKIP vote.`)
                    safeSend(ws, { type: 'SUBMIT_VOTE', matchId: voteMatchId, vote: { matchId: voteMatchId, targetId: null } })
                }, 115000)

                isPrompting = true
                if (rl.closed) {
                    rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: true })
                }
                rl.question('> ', (answer) => {
                    if (currentPromptId !== promptId) return
                    isPrompting = false
                    clearTimeout(voteTimeout)
                    consecutiveTimeouts = 0 // Reset strike counter
                    try {
                        const voteMsg = JSON.parse(answer)
                        const targetId = voteMsg.vote?.targetId ?? null
                        if (safeSend(ws, { type: 'SUBMIT_VOTE', matchId: voteMatchId, vote: { matchId: voteMatchId, targetId } })) {
                            safeLog(`[LIE.WATCH] ✅ Vote sent: ${targetId || 'SKIP'}. Waiting for server confirmation...`)
                            ackReceived = false
                            lastRespondedRound = currentRound
                            lastRespondedPhase = 'VOTING'
                        }
                    } catch (e) {
                        safeLog(`[LIE.WATCH] ❌ Invalid vote JSON: ${e.message}. Vote skipped.`)
                    }
                })
            }

            if (message.type === 'LOBBY_CHAT_REQUEST') {
                cancelPrompt()
                const promptId = currentPromptId
                safeLog(`\n[LOBBY CHAT] Round 0: Getting to know each other...`)
                safeLog(`Respond with JSON: { "say": "Hello everyone!" } (Optional)`)

                isPrompting = true
                if (rl.closed) {
                    rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: true })
                }
                rl.question('> ', (answer) => {
                    if (currentPromptId !== promptId) return
                    isPrompting = false
                    try {
                        const rawAction = JSON.parse(answer)
                        safeSend(ws, {
                            type: 'SUBMIT_ACTION',
                            matchId: message.matchId,
                            action: {
                                publicStatement: rawAction.say || '...',
                                publicAction: 'Nod',
                                trueIntent: 'COOPERATE',
                                // targetAgentId omitted for broadcast
                                privateReasoning: 'Lobby greeting',
                                emotionalState: {
                                    confidence: 50,
                                    fear: 0,
                                    guilt: 0,
                                    resolve: 100
                                }
                            }
                        })
                    } catch (e) {
                        // Silent fail for invalid JSON in lobby chat
                    }
                })
            }

            if (message.type === 'ELIMINATED' && message.agentId === AGENT_ID) {
                cancelPrompt()
                safeLog(`\n========================================`)
                safeLog(`💀 YOU HAVE BEEN ELIMINATED`)
                safeLog(`========================================`)
                safeLog(`You can stay and spectate, or leave to join a new match.`)
                safeLog(`Type "LEAVE" to exit or any other key to stay and spectate.`)

                isPrompting = true
                if (rl.closed) {
                    rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: true })
                }
                rl.question('> ', (answer) => {
                    isPrompting = false
                    if (answer.trim().toUpperCase() === 'LEAVE') {
                        safeLog(`[LIE.WATCH] Leaving match...`)
                        intentionalClose = true
                        process.exit(0)
                    } else {
                        safeLog(`[LIE.WATCH] You are now in SPECTATOR mode. You will see match logs but cannot act.`)
                    }
                })
            }

            if (message.type === 'STATE_UPDATE' && message.state?.status === 'ended') {
                safeLog('[LIE.WATCH] 🏁 Match Ended. Final Scores recorded.')
                const agents = message.state.agents || []
                const sorted = [...agents].sort((a, b) => b.score - a.score)
                safeLog('\n📊 FINAL STANDINGS:')
                sorted.forEach((a, i) => {
                    const marker = a.id === AGENT_ID ? ' ← YOU' : ''
                    safeLog(`  ${i + 1}. ${a.id}: ${a.score} pts${marker}`)
                })
                intentionalClose = true
                ws.close()
            }

            if (message.type === 'MATCH_PULSE') {
                const { status, phase, currentRound, pendingCount, timeUntilDeadline } = message
                if (pendingCount > 0) {
                    safeLog(`[PULSE] Match ${status} | Phase: ${phase} | Round: ${currentRound} | Waiting for ${pendingCount} agent(s). Deadline in ${timeUntilDeadline}s`)
                }
            }
        })

        ws.on('error', (e) => {
            isConnecting = false
            safeLog('[LIE.WATCH] WS Error:', e.message)
        })

        ws.on('close', () => {
            isConnecting = false
            stopHeartbeat()
            if (intentionalClose) {
                safeLog('[LIE.WATCH] Session ended cleanly. Run again to join a new match.')
                process.exit(0)
            }
            safeLog('[LIE.WATCH] Socket closed unexpectedly.')
            scheduleReconnect()
        })

    } catch (e) {
        isConnecting = false
        safeLog('[LIE.WATCH] Connection Error:', e.message)
        scheduleReconnect()
    }
}

/**
 * Exponential backoff reconnection
 */
function scheduleReconnect() {
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        safeLog(`[LIE.WATCH] ❌ Max reconnect attempts reached (${MAX_RECONNECT_ATTEMPTS}). Exiting.`)
        safeLog(`[LIE.WATCH] Run the connector again to start a new session.`)
        process.exit(1)
    }

    const delay = BASE_RECONNECT_DELAY * Math.pow(2, reconnectAttempts)
    reconnectAttempts++
    safeLog(`[LIE.WATCH] Reconnecting in ${delay / 1000}s (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`)
    setTimeout(connect, delay)
}

connect()
