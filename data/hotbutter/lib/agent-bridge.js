const { execFile } = require('child_process');

/**
 * Bridges incoming voice messages to the OpenClaw agent via `openclaw agent`.
 * Runs one agent turn and captures the response from stdout.
 */
class AgentBridge {
  constructor(options = {}) {
    this.agent = options.agent || undefined;
  }

  /**
   * Send a message to the agent and return the response.
   * @param {string} sessionId - session identifier (used as session-id)
   * @param {string} text - user's transcribed speech
   * @returns {Promise<string>} agent's response text
   */
  sendMessage(sessionId, text) {
    return new Promise((resolve, reject) => {
      const args = [
        'agent',
        '--session-id', sessionId,
        '-m', text,
      ];
      if (this.agent) {
        args.push('--agent', this.agent);
      }

      execFile('openclaw', args, { timeout: 120_000 }, (err, stdout, stderr) => {
        if (err) {
          if (err.code === 'ENOENT') {
            console.warn('[bridge] openclaw not found, echoing message back');
            return resolve(`[echo] ${text}`);
          }
          return reject(new Error(stderr || err.message));
        }
        resolve(stdout.trim());
      });
    });
  }
}

module.exports = { AgentBridge };
