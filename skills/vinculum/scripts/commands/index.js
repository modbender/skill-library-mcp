/**
 * Command router for Vinculum skill
 * Parses /link commands and routes to handlers
 */

const init = require('./init');
const join = require('./join');
const status = require('./status');
const toggle = require('./toggle');
const peers = require('./peers');
const activity = require('./activity');
const config = require('./config');
const admin = require('./admin');
const relay = require('./relay');

/**
 * Parse and route a /link command
 * @param {string} input - Full command string (e.g., "/link status")
 * @param {Object} context - Execution context
 * @returns {Promise<string>} Response message
 */
async function handleCommand(input, context) {
  // Parse the command
  const parts = input.trim().split(/\s+/);
  const base = parts[0]; // "/link"
  const subcommand = parts[1] || '';
  const args = parts.slice(2);
  
  // Route to handler
  switch (subcommand.toLowerCase()) {
    // No subcommand - quick status
    case '':
      return status.quickStatus(context);
    
    // Setup commands
    case 'init':
      return init.initNamespace(context);
    
    case 'join':
      return join.joinNamespace(args[0], context);
    
    case 'invite':
      return init.generateInvite(context);
    
    case 'leave':
      return init.leaveNamespace(context);
    
    // Toggle commands
    case 'on':
      return toggle.enable(context);
    
    case 'off':
      return toggle.disable(context);
    
    // Status commands
    case 'status':
      return status.detailedStatus(context);
    
    // Awareness commands
    case 'peers':
    case 'drones':
      return peers.listPeers(context);
    
    case 'activity':
      return activity.listActivity(args[0], context);
    
    case 'decisions':
      return activity.listDecisions(context);
    
    // Config commands
    case 'config':
      if (args.length === 0) {
        return config.showConfig(context);
      }
      return config.setConfig(args[0], args.slice(1).join(' '), context);
    
    // Manual sync commands
    case 'push':
      return toggle.forcePush(context);
    
    case 'pull':
      return toggle.forcePull(context);
    
    case 'share':
      // Join remaining args as the text to share
      const text = args.join(' ').replace(/^["']|["']$/g, '');
      return activity.shareNote(text, context);
    
    // Relay commands
    case 'relay':
      return handleRelayCommand(args, context);
    
    // Admin commands
    case 'logs':
      return admin.showLogs(context);
    
    case 'reset':
      return admin.reset(context);
    
    case 'destroy':
      return admin.destroy(context);
    
    case 'debug':
      return admin.debug(context);

    case 'help':
      return showHelp();
    
    // Unknown command
    default:
      return `❓ Unknown command: \`/link ${subcommand}\`

**Core Commands**
\`/link\` — Quick status
\`/link init\` — Create new collective
\`/link join <code>\` — Join collective
\`/link on|off\` — Enable/disable

**Relay**
\`/link relay\` — Relay status
\`/link relay start|stop\` — Control relay
\`/link relay peer <url>\` — Add peer

**Collective**
\`/link drones\` — List drones
\`/link activity\` — Recent activity
\`/link share "text"\` — Share a thought

**Config**
\`/link config\` — Show config
\`/link config <key> <value>\` — Set config

Use \`/link help\` for full documentation.`;
  }
}

/**
 * Handle relay subcommands
 */
async function handleRelayCommand(args, context) {
  const subCmd = (args[0] || '').toLowerCase();
  const subArgs = args.slice(1);

  switch (subCmd) {
    case '':
    case 'status':
      return relay.relayStatus(context);
    
    case 'start':
      return relay.startRelay(context);
    
    case 'stop':
      return relay.stopRelay(context);
    
    case 'restart':
      return relay.restartRelay(context);
    
    case 'logs':
      return relay.relayLogs(subArgs[0], context);
    
    case 'port':
      return relay.setRelayPort(subArgs[0], context);
    
    case 'peer':
    case 'add':
      return relay.addPeer(subArgs[0], context);
    
    case 'remove':
      return relay.removePeer(subArgs[0], context);
    
    case 'peers':
    case 'list':
      return relay.listPeers(context);
    
    default:
      return `❓ Unknown relay command: \`${subCmd}\`

**Relay Commands**
\`/link relay\` — Show relay status
\`/link relay start\` — Start Vinculum relay
\`/link relay stop\` — Stop relay
\`/link relay restart\` — Restart relay
\`/link relay logs [n]\` — Show last n logs
\`/link relay port <port>\` — Set relay port
\`/link relay peer <url>\` — Add remote peer
\`/link relay remove <url>\` — Remove peer
\`/link relay peers\` — List configured peers`;
  }
}

/**
 * Show full help
 */
function showHelp() {
  return `📖 **Vinculum Help**

*Shared consciousness for Clawdbot instances*

**Getting Started**
1. \`/link relay start\` — Start Vinculum relay
2. \`/link init\` — Create a collective
3. Share the pairing code with other drones
4. \`/link join <code>\` — Other drones join

**Collective Setup**
\`/link init\` — Create new collective
\`/link join <code>\` — Join with invite code
\`/link invite\` — Generate new invite
\`/link leave\` — Leave collective

**Relay (Vinculum Core)**
\`/link relay start\` — Start relay daemon
\`/link relay stop\` — Stop relay
\`/link relay status\` — Relay health
\`/link relay peer <url>\` — Add remote peer

**Control**
\`/link on\` — Enable link
\`/link off\` — Disable link
\`/link status\` — Detailed status

**Collective Mind**
\`/link share "text"\` — Share a thought
\`/link activity\` — View activity
\`/link drones\` — See connected drones
\`/link decisions\` — Shared decisions

**Configuration**
\`/link config\` — View all settings
\`/link config share-activity on|off\`
\`/link config share-memory on|off\`
\`/link config share-decisions on|off\`
\`/link config sync-interval <sec>\`
\`/link config drone-name <name>\`

**Admin**
\`/link logs\` — View link logs
\`/link reset\` — Reset link state
\`/link debug\` — Debug info

*Resistance is futile.*`;
}

module.exports = {
  handleCommand
};
