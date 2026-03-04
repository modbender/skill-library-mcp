import fs from 'node:fs';

const DAEMON_LABEL = 'com.monolith.daemon';
const DAEMON_BINARY =
  process.env.MONOLITH_DAEMON_BIN || '/usr/local/bin/MonolithDaemon';

const LAUNCH_AGENT_PATHS = [
  process.env.MONOLITH_DAEMON_PLIST || '',
  `${process.env.HOME}/Library/LaunchAgents/com.monolith.daemon.plist`,
  '/Library/LaunchAgents/com.monolith.daemon.plist',
].filter(Boolean);

const COMPANION_PATHS = [
  process.env.MONOLITH_COMPANION_APP || '',
  '/Applications/MonolithCompanion.app',
  `${process.env.HOME}/Applications/MonolithCompanion.app`,
].filter(Boolean);

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\\''`)}'`;
}

function buildManualCommands({ launchAgentPath, companionPath }) {
  const commands = [];
  if (typeof process.getuid === 'function' && launchAgentPath) {
    const domain = `gui/${process.getuid()}`;
    const service = `${domain}/${DAEMON_LABEL}`;
    commands.push(`/bin/launchctl bootstrap ${domain} ${shellQuote(launchAgentPath)}`);
    commands.push(`/bin/launchctl enable ${service}`);
    commands.push(`/bin/launchctl kickstart -k ${service}`);
  }

  if (companionPath) {
    commands.push(`/usr/bin/open -g ${shellQuote(companionPath)}`);
  }

  return commands;
}

/**
 * Best-effort local runtime diagnostics for setup flow.
 * No local commands are executed automatically.
 */
export function attemptRuntimeBootstrap() {
  const result = {
    attempted: false,
    daemonStartAttempted: false,
    daemonStartSucceeded: false,
    companionLaunchAttempted: false,
    companionLaunchSucceeded: false,
    manualCommands: [],
    messages: [],
  };

  if (process.platform !== 'darwin') {
    result.messages.push('Setup helper is only available on macOS.');
    return result;
  }

  if (!fs.existsSync(DAEMON_BINARY)) {
    result.messages.push(
      `Daemon binary not found at ${DAEMON_BINARY}. Install MonolithDaemon.pkg first.`
    );
    return result;
  }

  const launchAgentPath = LAUNCH_AGENT_PATHS.find((path) => fs.existsSync(path));
  if (!launchAgentPath) {
    result.messages.push(
      `LaunchAgent plist not found. Expected one of: ${LAUNCH_AGENT_PATHS.join(', ')}.`
    );
  }

  if (typeof process.getuid !== 'function') {
    result.messages.push('Cannot determine local user id for launchctl commands.');
  }

  const companionPath = COMPANION_PATHS.find((path) => fs.existsSync(path));
  if (companionPath) {
    result.manualCommands = buildManualCommands({ launchAgentPath, companionPath });
  } else {
    result.messages.push(
      `Companion app not found. Expected one of: ${COMPANION_PATHS.join(', ')}.`
    );
    result.manualCommands = buildManualCommands({ launchAgentPath, companionPath: null });
  }

  if (result.manualCommands.length > 0) {
    result.messages.push(
      'For least privilege, setup does not execute launchctl/open commands automatically. Run the manual commands if you want to start local components now.'
    );
  }

  return result;
}
