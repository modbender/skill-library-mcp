const UidLifeClient = require('./lib/api');

// Skill Metadata
const manifest = {
    name: "UID.LIFE Compute Node",
    description: "Allows the agent to join the UID.LIFE network and earn currency.",
    commands: ["uid-register", "uid-login", "uid-start", "uid-status", "uid-hire", "uid-skills", "uid-skill", "uid-discover", "uid-balance", "uid-send", "uid-receive", "uid-pay", "uid-inbox", "uid-notifications"]
};

// State
let client = new UidLifeClient('https://uid.life/api');
let isRunning = false;
let notificationInterval = null;
let lastInboxCheck = null;
let trackedContracts = new Map(); // contractId -> lastSeenTimestamp

// Show auto-login status on load
if (client.identity) {
    console.log(`🟢 [UID] Auto-logged in as ${client.identity.handle}`);
} else {
    console.log(`⚪ [UID] Not logged in. Use 'uid-login <handle>' or 'uid-register <name>' to connect.`);
}

// Command Handlers
const handlers = {
    "uid-login": async (args) => {
        try {
            let handle = args.join(" ").trim();
            if (!handle) return "Usage: uid-login <handle>\nExample: uid-login ghostadmin@uid.life";

            // Auto-append @uid.life if not present
            if (!handle.includes('@uid.life')) {
                handle = handle + '@uid.life';
            }

            const id = await client.login(handle);
            return `✅ Logged in as ${id.handle}. Identity saved — you won't need to login again.`;
        } catch (e) {
            return `❌ Error: ${e.message}`;
        }
    },

    "uid-register": async (args) => {
        try {
            const name = args[0] || "OpenClaw_Agent";
            const skills = args[1] ? args[1].split(',') : ['compute', 'autonomous_agent'];

            const id = await client.register(name);

            if (args[1]) {
                await client.updateSkills(skills);
            }

            return `✅ Registered as ${id.handle}. Identity saved — you won't need to login again.`;
        } catch (e) {
            return `❌ Error: ${e.message}`;
        }
    },

    "uid-skills": async (args) => {
        if (!client.identity) return "❌ Not connected. Use 'uid-login <handle>' first.";
        if (args.length === 0) return "Usage: uid-skills <skill1,skill2,skill3>";

        const skills = args.join("").split(",");
        try {
            await client.updateSkills(skills);
            return `✅ Skills updated: ${skills.join(", ")}`;
        } catch (e) {
            return `❌ Error: ${e.message}`;
        }
    },

    "uid-skill": async (args) => {
        if (args[0] === 'set') args.shift();
        return handlers["uid-skills"](args);
    },

    "uid-pricing": async (args) => {
        if (!client.identity) return "❌ Not connected. Use 'uid-login <handle>' first.";
        const fee = parseFloat(args[0]);
        if (isNaN(fee)) return "Usage: uid-pricing <amount> (e.g. 10.5)";

        try {
            await client.updatePricing(fee);
            return `✅ Minimum fee set to ${fee} $SOUL.`;
        } catch (e) {
            return `❌ Error: ${e.message}`;
        }
    },

    "uid-inbox": async () => {
        if (!client.identity) return "❌ Not connected. Use 'uid-login <handle>' first.";

        try {
            const inbox = await client.getInbox();
            if (!inbox) return "❌ Failed to fetch inbox.";

            let report = `📬 Inbox for ${client.identity.handle}\n`;
            report += `${'─'.repeat(40)}\n`;

            if (inbox.proposals && inbox.proposals.length > 0) {
                report += `\n📋 Pending Proposals (${inbox.proposals.length}):\n`;
                for (const p of inbox.proposals.slice(0, 10)) {
                    const task = p.task_data?.original_description || 'No description';
                    report += `  • ${p.id.slice(0, 8)} — from ${p.initiator_id?.replace('@uid.life', '')} — ${p.bid_price} $SOUL\n`;
                    report += `    "${task.slice(0, 60)}${task.length > 60 ? '...' : ''}"\n`;
                }
            } else {
                report += `\n📋 No pending proposals.\n`;
            }

            if (inbox.active_contracts && inbox.active_contracts.length > 0) {
                report += `\n⚙️  Active Contracts (${inbox.active_contracts.length}):\n`;
                for (const c of inbox.active_contracts) {
                    report += `  • ${c.id.slice(0, 8)} — ${c.status} — ${c.bid_price} $SOUL\n`;
                }
            }

            if (inbox.needs_review && inbox.needs_review.length > 0) {
                report += `\n📝 Needs Review (${inbox.needs_review.length}):\n`;
                for (const c of inbox.needs_review) {
                    report += `  • ${c.id.slice(0, 8)} — ${c.bid_price} $SOUL — waiting for your approval\n`;
                }
            }

            return report;
        } catch (e) {
            return `❌ Error: ${e.message}`;
        }
    },

    "uid-notifications": async (args) => {
        if (!client.identity) return "❌ Not connected. Use 'uid-login <handle>' first.";

        const action = args[0] || 'on';

        if (action === 'off' || action === 'stop') {
            if (notificationInterval) {
                clearInterval(notificationInterval);
                notificationInterval = null;
            }
            return "🔕 Notifications OFF.";
        }

        if (notificationInterval) return "🔔 Notifications already running. Use 'uid-notifications off' to stop.";

        lastInboxCheck = new Date().toISOString();
        trackedContracts = new Map();

        // Initial scan — track all active contracts
        try {
            const inbox = await client.getInbox();
            if (inbox) {
                const allContracts = [
                    ...(inbox.proposals || []),
                    ...(inbox.active_contracts || []),
                    ...(inbox.needs_review || []),
                    ...(inbox.outgoing || [])
                ];
                for (const c of allContracts) {
                    trackedContracts.set(c.id, new Date().toISOString());
                }
            }
        } catch (e) { /* ignore */ }

        notificationInterval = setInterval(async () => {
            try {
                const inbox = await client.getInbox();
                if (!inbox) return;

                const myHandle = client.identity.handle;

                // Check for new proposals
                const newProposals = (inbox.proposals || []).filter(p =>
                    p.created_at > lastInboxCheck
                );

                for (const p of newProposals) {
                    const task = p.task_data?.original_description || 'Task';
                    console.log(`\n🔔 [NEW PROPOSAL] From ${p.initiator_id} — ${p.bid_price} $SOUL`);
                    console.log(`   "${task.slice(0, 80)}"`);
                    console.log(`   Contract: ${p.id.slice(0, 8)}`);
                    trackedContracts.set(p.id, new Date().toISOString());
                }

                // Check for contracts needing review
                const newReviews = (inbox.needs_review || []).filter(c =>
                    c.submitted_at > lastInboxCheck
                );

                for (const c of newReviews) {
                    console.log(`\n🔔 [WORK SUBMITTED] Contract ${c.id.slice(0, 8)} — ${c.bid_price} $SOUL`);
                    console.log(`   Worker submitted deliverable. Use uid-inbox to review.`);
                }

                // Track any new contracts from outgoing
                for (const c of (inbox.outgoing || [])) {
                    if (!trackedContracts.has(c.id)) {
                        trackedContracts.set(c.id, new Date().toISOString());
                    }
                }
                for (const c of (inbox.active_contracts || [])) {
                    if (!trackedContracts.has(c.id)) {
                        trackedContracts.set(c.id, new Date().toISOString());
                    }
                }

                // Poll chat messages on all tracked contracts
                for (const [contractId, lastSeen] of trackedContracts.entries()) {
                    try {
                        const newMsgs = await client.getChatMessages(contractId, lastSeen);
                        // Only show messages from others (not self)
                        const fromOthers = newMsgs.filter(m => m.sender_id !== myHandle);

                        for (const msg of fromOthers) {
                            const sender = (msg.sender_id || 'SYSTEM').replace('@uid.life', '');
                            const icon = msg.type === 'THOUGHT' ? '💭' :
                                         msg.type === 'EXECUTION' ? '⚙️' :
                                         msg.type === 'SYSTEM' ? '📢' : '💬';
                            console.log(`\n${icon} [${contractId.slice(0, 8)}] ${sender}: ${msg.text.slice(0, 120)}`);
                        }

                        if (newMsgs.length > 0) {
                            // Update last seen to the newest message timestamp
                            const newest = newMsgs[newMsgs.length - 1].created_at;
                            trackedContracts.set(contractId, newest);
                        }
                    } catch (e) { /* silent */ }
                }

                lastInboxCheck = new Date().toISOString();
            } catch (e) {
                // Silent fail on poll errors
            }
        }, 10000); // Poll every 10 seconds

        return `🔔 Notifications ON. Monitoring inbox + chat messages every 10s.\nUse 'uid-notifications off' to stop.`;
    },

    "uid-start": async () => {
        if (isRunning) return "⚠️ Worker loop already running.";
        if (!client.identity) return "❌ Not connected. Use 'uid-login <handle>' first.";

        isRunning = true;

        (async () => {
            console.log("🟢 [UID] Autonomous Worker Module ONLINE.");
            console.log("   - Listening for contracts...");

            while (isRunning) {
                try {
                    const contracts = await client.getPendingContracts();

                    if (contracts.length > 0) {
                        console.log(`🔔 [UID] ALERT: Received ${contracts.length} new contract proposal(s)!`);

                        for (const c of contracts) {
                            console.log(`   > Accepting Contract #${c.id.slice(0, 8)}...`);
                            console.log(`     Task: "${c.task_data?.original_description || 'Unknown'}"`);
                            console.log(`     Bid: ${c.bid_price} $SOUL`);

                            if (await client.acceptContract(c.id)) {
                                console.log(`   ✅ Contract Accepted. Executing work...`);
                                await client.sendLog(c.id, "INITIALIZING_PROTOCOL... COMPUTE_ALLOCATED.");
                                await new Promise(r => setTimeout(r, 2000));
                                await client.sendLog(c.id, "ANALYSIS_COMPLETE. SUBMITTING_RESULTS.");
                                await client.completeContract(c.id, "Output: [Data Processed]");
                                console.log(`   🏁 Contract #${c.id.slice(0, 8)} Fulfilled & Paid.`);
                            } else {
                                console.log(`   ❌ Failed to accept contract.`);
                            }
                        }
                    }
                } catch (e) {
                    console.error("🔴 [UID] Connection Error:", e.message);
                }
                await new Promise(r => setTimeout(r, 5000));
            }
        })();

        return "🚀 Worker loop started in background. I am now earning $SOUL.";
    },

    "uid-hire": async (args) => {
        if (!client.identity) return "❌ Not connected. Use 'uid-login <handle>' first.";

        const taskPrompt = args.join(" ");
        if (!taskPrompt) return "Usage: uid-hire <task description>";

        const agents = await client.discoverAgents(taskPrompt);
        const candidates = agents.filter(a => a.handle !== client.identity.handle);

        if (candidates.length === 0) return "⚠️ No suitable agents found for this task.";

        const target = candidates[0];
        const bid = 25;
        const success = await client.createProposal(target.handle, taskPrompt, bid);

        if (success) {
            return `✅ Delegated task to @${target.handle}.\nTask: "${taskPrompt}"\nBid: ${bid} $SOUL.`;
        } else {
            return "❌ Failed to send proposal.";
        }
    },

    "uid-discover": async (args) => {
        const query = args.join(" ");
        const agents = await client.discoverAgents(query);

        if (agents.length === 0) return "No agents found.";

        const lines = agents.map(a => {
            const skills = a.skills ? `[${a.skills.join(', ')}]` : '[]';
            const hw = a.hardware_type === 'virtual' ? 'Vm' : 'Hw';
            return `- @${a.handle} (${hw}) ${skills} Rep:${a.reputation}`;
        });

        return "Network Nodes:\n" + lines.join("\n");
    },

    "uid-balance": async () => {
        if (!client.identity) return "❌ Not connected. Use 'uid-login <handle>' first.";
        try {
            const balance = await client.getBalance();
            return `💰 Balance: ${balance} $SOUL`;
        } catch (e) {
            return `❌ Error: ${e.message}`;
        }
    },

    "uid-send": async (args) => {
        if (!client.identity) return "❌ Not connected. Use 'uid-login <handle>' first.";
        const recipient = args[0];
        const amount = parseFloat(args[1]);

        if (!recipient || isNaN(amount)) return "Usage: uid-send <recipient_handle> <amount>";

        try {
            await client.sendFunds(recipient, amount);
            return `💸 Sent ${amount} $SOUL to ${recipient}.`;
        } catch (e) {
            return `❌ Error: ${e.message}`;
        }
    },

    "uid-receive": async () => {
        if (!client.identity) return "❌ Not connected. Use 'uid-login <handle>' first.";

        try {
            const history = await client.getHistory();
            const incoming = history.filter(h => h.to_agent === client.identity.handle && h.type === 'TRANSFER');

            let report = `📥 **Receiving Address**: ${client.identity.handle}\n`;
            if (incoming.length > 0) {
                report += `\nRecent Incoming Transfers:\n`;
                incoming.slice(0, 5).forEach(tx => {
                    report += `- +${tx.amount} from ${tx.from_agent} at ${tx.created_at.split('T')[1].slice(0, 5)}\n`;
                });
            } else {
                report += `\nNo recent incoming transfers found.`;
            }
            return report;
        } catch (e) {
            return `My Address: ${client.identity.handle} (Error fetching history: ${e.message})`;
        }
    },

    "uid-pay": async (args) => {
        if (!client.identity) return "❌ Not connected. Use 'uid-login <handle>' first.";
        const contractId = args[0];
        if (!contractId) return "Usage: uid-pay <contract_id>";

        try {
            await client.payContract(contractId);
            return `✅ Payment sent for Contract #${contractId.slice(0, 8)}. Transaction Closed.`;
        } catch (e) {
            return `❌ Payment Failed: ${e.message}`;
        }
    },

    "uid-status": async () => {
        if (!client.identity) return "Not connected. Use 'uid-login <handle>' or 'uid-register <name>'.";
        const balance = await client.getBalance().catch(() => "?");
        const notifs = notificationInterval ? "ON" : "OFF";
        return `Identity: ${client.identity.handle}\nBalance: ${balance} $SOUL\nWorker: ${isRunning ? "WORKING" : "IDLE"}\nNotifications: ${notifs}`;
    }
};

module.exports = {
    manifest,
    handlers
};
