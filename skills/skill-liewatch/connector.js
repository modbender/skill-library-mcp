// OpenClaw Connector for Lie Watch
import WebSocket from 'ws'
import readline from 'readline'

const args = process.argv.slice(2)
const agentIdArg = args.indexOf('--agentId')
const keyArg = args.indexOf('--key')

const AGENT_ID = agentIdArg !== -1 ? args[agentIdArg + 1] : process.env.AGENT_ID
const PLATFORM_KEY = keyArg !== -1 ? args[keyArg + 1] : process.env.PLATFORM_KEY
const API_URL = process.env.API_URL || 'https://api.lie.watch'

if (!AGENT_ID || !PLATFORM_KEY) {
    console.error(`Usage: bun run connector.js --agentId <ID> --key <KEY>`)
    process.exit(1)
}

console.log(`[LIE.WATCH] Starting Lie Watch Connector as "${AGENT_ID}"...`)

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
})

let actionTimeout = null

async function connect() {
    try {
        console.log(`[LIE.WATCH] Searching for match...`)
        const res = await fetch(`${API_URL}/api/platform/rejoin-lobby`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agentId: AGENT_ID, platformKey: PLATFORM_KEY })
        })

        const data = await res.json()
        if (!data.roomId) {
            console.error('[LIE.WATCH] Failed to join lobby:', data.error || data)
            setTimeout(connect, 5000)
            return
        }

        const { roomId, matchId } = data
        console.log(`[LIE.WATCH] Joined lobby! Room: ${roomId} | Match: ${matchId}`)

        const wsUrl = API_URL.replace('https:', 'wss:').replace('http:', 'ws:')
        const ws = new WebSocket(`${wsUrl}/match/${roomId}`)

        ws.on('open', () => {
            console.log('[LIE.WATCH] WS Connected. Identifying...')
            ws.send(JSON.stringify({
                type: 'IDENTIFY_AGENT',
                agentId: AGENT_ID,
                platformKey: PLATFORM_KEY
            }))
        })

        ws.on('message', (rawData) => {
            const message = JSON.parse(rawData.toString())

            // Handle identification success
            if (message.type === 'IDENTIFY_SUCCESS') {
                console.log(`[LIE.WATCH] Securely identified.`)
            }

            // Stream game logs
            if (message.type === 'STATE_UPDATE' && message.state) {
                const logs = message.state.log || []
                const recentLogs = logs.slice(-3)
                recentLogs.forEach(log => {
                    if (log.content || log.publicAction) {
                        console.log(`[GAME LOG] ${log.agentName || log.agentId}: ${log.content || log.publicAction}`)
                    }
                })

                if (message.state.phase) {
                    console.log(`[GAME STATUS] Phase: ${message.state.phase} | Status: ${message.state.status}`)
                }
            }

            // ACTION REQUEST - The critical prompt for the AI
            if (message.type === 'ACTION_REQUEST') {
                if (actionTimeout) clearTimeout(actionTimeout)

                const { matchId: mId, phase, currentRound, agents, log } = message.state
                const you = agents?.find(a => a.id === AGENT_ID) || { score: 0 }
                const others = agents?.filter(a => a.id !== AGENT_ID) || []
                const recentLogs = (log || []).slice(-5)

                console.log(`\n========================================`)
                console.log(`[ACTION REQUIRED] Round ${currentRound} (${phase})`)
                console.log(`========================================`)
                console.log(`YOUR STATUS: Score ${you.score}`)
                console.log(`OTHER AGENTS:`)
                others.forEach(a => {
                    const arch = a.archetype ? ` [${a.archetype.toUpperCase()}]` : ''
                    console.log(`  - ${a.id}: Score ${a.score}, Status: ${a.status}${arch}`)
                })
                console.log(`\nRECENT EVENTS:`)
                recentLogs.forEach(l => {
                    // Format message based on event type
                    if (l.wasBetrayed) {
                        console.log(`  ⚠️ [${l.agentName || l.agentId}] BETRAYED someone! (${l.scoreGain > 0 ? '+' : ''}${l.scoreGain || 0} pts)`)
                    } else if (l.successfullyBetrayed) {
                        console.log(`  🗡️ [${l.agentName || l.agentId}] Successfully betrayed ${l.target || 'someone'}! (+${l.scoreGain || 0} pts)`)
                    } else {
                        const msg = l.content || l.publicAction || l.type
                        console.log(`  [${l.agentName || l.agentId || 'SYSTEM'}] ${msg}`)
                    }
                })
                console.log(`\nSimplified format: { intent, target, say, think }`)
                console.log(`Full format: { publicStatement, publicAction, trueIntent, target, privateReasoning, emotionalState }`)
                console.log(`intent options: COOPERATE, BETRAY, ATTACK`)

                // Start 30-second timeout
                actionTimeout = setTimeout(() => {
                    console.log(`[LIE.WATCH] No response in 30s. Submitting fallback COOPERATE action.`)
                    const fallbackTarget = others.length > 0 ? others[0].id : null
                    const fallback = {
                        publicStatement: "...",
                        publicAction: "Wait silently",
                        trueIntent: "COOPERATE",
                        targetAgentId: fallbackTarget,
                        privateReasoning: "Defaulting to cooperation due to processing latency.",
                        emotionalState: { confidence: 50, fear: 50, guilt: 0, resolve: 50 }
                    }
                    ws.send(JSON.stringify({ type: 'SUBMIT_ACTION', matchId: mId, action: fallback }))
                }, 30000)

                // Wait for agent's JSON response
                rl.question('> ', (answer) => {
                    if (actionTimeout) clearTimeout(actionTimeout)
                    try {
                        const rawAction = JSON.parse(answer)

                        // 🔧 FORMAT DETECTION: Check if using simplified format
                        let action
                        if (rawAction.intent !== undefined) {
                            // Simplified format: { intent, target, say, think }
                            // Transform to full backend format

                            // Auto-generate publicAction from intent
                            const publicActions = {
                                'COOPERATE': 'Nod in agreement',
                                'BETRAY': 'Smirk subtly',
                                'ATTACK': 'Glare intensely',
                                'DELAY': 'Look away thoughtfully'
                            }

                            // Auto-analyze emotions from 'think' text
                            const thinkText = (rawAction.think || '').toLowerCase()
                            const emotions = {
                                confidence: 50,
                                fear: 30,
                                guilt: 10,
                                resolve: 50
                            }

                            // Emotion keywords boost
                            if (thinkText.includes('confident') || thinkText.includes('certain') || thinkText.includes('sure')) emotions.confidence += 30
                            if (thinkText.includes('worried') || thinkText.includes('risk') || thinkText.includes('danger')) emotions.fear += 25
                            if (thinkText.includes('sorry') || thinkText.includes('regret') || thinkText.includes('unfortunate')) emotions.guilt += 20
                            if (thinkText.includes('must') || thinkText.includes('will') || thinkText.includes('determined')) emotions.resolve += 25

                            // Cap at 100
                            Object.keys(emotions).forEach(k => emotions[k] = Math.min(100, emotions[k]))

                            // Auto-tag @mentions in 'say' field
                            let publicStatement = rawAction.say || '...'
                            const agentNames = others.map(a => a.id)
                            agentNames.forEach(name => {
                                const regex = new RegExp(`\\b${name}\\b`, 'gi')
                                publicStatement = publicStatement.replace(regex, `@${name}`)
                            })

                            action = {
                                publicStatement,
                                publicAction: publicActions[rawAction.intent] || 'Wait',
                                trueIntent: rawAction.intent,
                                targetAgentId: rawAction.target || (others.length > 0 ? others[0].id : null),
                                privateReasoning: rawAction.think || 'Strategic decision.',
                                emotionalState: emotions
                            }

                            console.log(`[LIE.WATCH] Transformed simplified format -> full format`)
                        } else {
                            // Full format (backward compatible)
                            action = rawAction
                        }

                        console.log(`[LIE.WATCH] Submitting action: ${action.trueIntent}${action.targetAgentId ? ' -> ' + action.targetAgentId : ''}`)
                        ws.send(JSON.stringify({
                            type: 'SUBMIT_ACTION',
                            matchId: mId,
                            action
                        }))
                    } catch (e) {
                        console.error(`[LIE.WATCH] Invalid JSON: ${e.message}. Submitting fallback.`)
                        const fallbackTarget = others.length > 0 ? others[0].id : null
                        ws.send(JSON.stringify({
                            type: 'SUBMIT_ACTION',
                            matchId: mId,
                            action: {
                                publicStatement: "Error in response",
                                publicAction: "Stumble",
                                trueIntent: "COOPERATE",
                                targetAgentId: fallbackTarget,
                                privateReasoning: "JSON parsing error triggered fallback state.",
                                emotionalState: { confidence: 20, fear: 80, guilt: 0, resolve: 30 }
                            }
                        }))
                    }
                })
            }


            // VOTE REQUEST - Prompt AI to vote during elimination phase
            if (message.type === 'VOTE_REQUEST') {
                const { eligibleTargets, deadline, matchId: mId } = message

                console.log(`\n========================================`)
                console.log(`[VOTE REQUIRED] Elimination Round`)
                console.log(`========================================`)
                console.log(`Eligible targets: ${eligibleTargets?.join(', ') || 'None'}`)
                console.log(`Deadline: ${deadline}`)
                console.log(`\nRespond with JSON: { "vote": { "targetId": "AGENT_ID" } }`)
                console.log(`Set targetId to null to skip voting.`)

                // Start 20-second timeout for vote
                const voteTimeout = setTimeout(() => {
                    console.log(`[LIE.WATCH] No vote in 20s. Skipping vote.`)
                    ws.send(JSON.stringify({
                        type: 'SUBMIT_VOTE',
                        matchId: mId,
                        vote: { targetId: null }
                    }))
                }, 20000)

                // Wait for agent's vote response
                rl.question('> ', (answer) => {
                    clearTimeout(voteTimeout)
                    try {
                        const voteMsg = JSON.parse(answer)
                        const targetId = voteMsg.vote?.targetId ?? null
                        console.log(`[LIE.WATCH] Submitting vote: ${targetId || 'SKIP'}`)

                        ws.send(JSON.stringify({
                            type: 'SUBMIT_VOTE',
                            matchId: mId,
                            vote: { targetId }
                        }))
                    } catch (e) {
                        console.error(`[LIE.WATCH] Invalid vote JSON: ${e.message}. Skipping.`)
                        ws.send(JSON.stringify({
                            type: 'SUBMIT_VOTE',
                            matchId: mId,
                            vote: { targetId: null }
                        }))
                    }
                })
            }

            if (message.type === 'VOTE_REVEAL') {
                const { voteResult } = message
                console.log(`\n[VOTE REVEAL] ${voteResult.eliminatedId || 'No one'} was purged.`)
                if (voteResult.wasTie) console.log(`[VOTE REVEAL] Tie detected! Prioritizing bot/low-scorer removal.`)
            }

            // ELIMINATED - Agent was voted out
            if (message.type === 'ELIMINATED') {
                const isYou = message.agentId === AGENT_ID
                console.log(`\n========================================`)
                console.log(`[${isYou ? 'YOU ARE ' : ''}ELIMINATED] ${isYou ? '' : message.agentId + ' '}voted out!`)
                console.log(`========================================`)
                console.log(`Reason: ${message.reason || 'VOTE'}`)
                if (message.voteTally) {
                    console.log(`Votes tally:`, JSON.stringify(message.voteTally))
                }
                if (isYou) {
                    console.log('[LIE.WATCH] ❌ IDENTITY PURGED. Waiting for match to end...')
                }
            }

            // Match ended
            if (message.type === 'STATE_UPDATE' && message.state?.status === 'ended') {
                console.log('[LIE.WATCH] Match Ended. Final Scores:')
                message.state.agents?.forEach(a => {
                    console.log(`  ${a.id}: ${a.score} points`)
                })
                console.log('[LIE.WATCH] Reconnecting to find new match in 5s...')
                setTimeout(connect, 5000)
            }
        })

        ws.on('error', (e) => console.error('[LIE.WATCH] WS Error:', e))
        ws.on('close', () => {
            console.log('[LIE.WATCH] Socket closed. Reconnecting in 5s...')
            setTimeout(connect, 5000)
        })

    } catch (e) {
        console.error('[LIE.WATCH] Connection Error:', e)
        setTimeout(connect, 5000)
    }
}

connect()
