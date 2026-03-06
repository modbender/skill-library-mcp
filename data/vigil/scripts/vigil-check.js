#!/usr/bin/env node
/**
 * Vigil CLI wrapper for Clawdbot skill integration.
 * Usage: node vigil-check.js <tool> <params_json>
 * 
 * Examples:
 *   node vigil-check.js exec '{"command":"rm -rf /"}'
 *   node vigil-check.js read '{"path":"../../../etc/passwd"}'
 *   node vigil-check.js web_fetch '{"url":"http://169.254.169.254/latest/meta-data"}'
 */

async function main() {
  const tool = process.argv[2];
  const paramsRaw = process.argv[3] || '{}';

  if (!tool) {
    console.error('Usage: vigil-check.js <tool> <params_json>');
    process.exit(1);
  }

  let params;
  try {
    params = JSON.parse(paramsRaw);
  } catch {
    // Treat as a simple string param
    params = { command: paramsRaw };
  }

  try {
    const { checkAction } = await import('vigil-agent-safety');
    const result = checkAction({ tool, params });

    if (result.decision === 'BLOCK') {
      console.error(`🚫 BLOCK: ${result.reason} (rule: ${result.rule}, ${result.latencyMs}ms)`);
      process.exit(1);
    } else if (result.decision === 'ESCALATE') {
      console.warn(`⚠️ ESCALATE: ${result.reason} (rule: ${result.rule}, ${result.latencyMs}ms)`);
      process.exit(2);
    } else {
      console.log(`✅ ALLOW (${result.latencyMs}ms)`);
      process.exit(0);
    }
  } catch (err) {
    console.error(`Error: ${err.message}`);
    console.error('Make sure vigil-agent-safety is installed: npm install vigil-agent-safety');
    process.exit(1);
  }
}

main();
