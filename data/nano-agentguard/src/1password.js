/**
 * 1Password Provider for AgentGuard
 *
 * Uses 1Password CLI (op) as credential source
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

class OnePasswordProvider {
  constructor(options = {}) {
    this.account = options.account || process.env.OP_ACCOUNT || null;
    this.vault = options.vault || 'Private'; // Default vault
    this.opPath = options.opPath || 'op';
    this.socketDir = options.socketDir || process.env.OPENCLAW_TMUX_SOCKET_DIR || '/tmp/openclaw-tmux-sockets';
    this.session = null;
  }

  /**
   * Check if op CLI is available
   */
  isAvailable() {
    try {
      execSync(`${this.opPath} --version`, { encoding: 'utf8' });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get current signed-in account
   */
  async whoami() {
    try {
      const result = this.execOp('whoami');
      return JSON.parse(result);
    } catch {
      return null;
    }
  }

  /**
   * Execute op command (via tmux for auth)
   */
  execOp(command, input = null) {
    const accountFlag = this.account ? ` --account ${this.account}` : '';

    if (process.env.AGENTGUARD_USE_TMUX === 'true') {
      return this.execViaTmux(`op ${command}${accountFlag}`, input);
    }

    try {
      const options = {
        encoding: 'utf8',
        env: { ...process.env, OP_ACCOUNT: this.account }
      };

      if (input) {
        options.input = input;
      }

      return execSync(`op ${command}${accountFlag}`, options);
    } catch (e) {
      throw new Error(`1Password CLI error: ${e.message}`);
    }
  }

  /**
   * Execute via tmux (for interactive auth)
   */
  execViaTmux(command, input = null) {
    const session = `op-${Date.now()}`;
    const socket = path.join(this.socketDir, `op-${Date.now()}.sock`);

    // Ensure socket dir exists
    if (!fs.existsSync(this.socketDir)) {
      fs.mkdirSync(this.socketDir, { recursive: true });
    }

    try {
      // Create tmux session
      execSync(`tmux -S "${socket}" new -d -s ${session}`, { encoding: 'utf8' });

      // Run command
      execSync(`tmux -S "${socket}" send-keys -t ${session} -- '${command}' Enter`, { encoding: 'utf8' });

      // Wait for output
      execSync('sleep 2');

      // Capture output
      const output = execSync(`tmux -S "${socket}" capture-pane -p -J -t ${session} -S -200`, { encoding: 'utf8' });

      // Cleanup
      execSync(`tmux -S "${socket}" kill-session -t ${session}`, { encoding: 'utf8' });

      return output;
    } catch (e) {
      // Cleanup on error
      try {
        execSync(`tmux -S "${socket}" kill-session -t ${session} 2>/dev/null`);
      } catch {}

      throw new Error(`tmux execution error: ${e.message}`);
    }
  }

  /**
   * Get a secret from 1Password
   */
  async get(itemTitle, field = 'password') {
    try {
      const result = this.execOp(`item get "${itemTitle}" --fields label=${field}`);
      return result.trim();
    } catch (e) {
      throw new Error(`Failed to get secret "${itemTitle}": ${e.message}`);
    }
  }

  /**
   * Get a secret by reference (op://vault/item/field)
   */
  async getByRef(reference) {
    try {
      const result = this.execOp(`read "${reference}"`);
      return result.trim();
    } catch (e) {
      throw new Error(`Failed to read reference "${reference}": ${e.message}`);
    }
  }

  /**
   * Store a secret in 1Password
   */
  async store(itemTitle, value, options = {}) {
    const vault = options.vault || this.vault;
    const field = options.field || 'password';
    const category = options.category || 'Password';
    const username = options.username || '';
    const url = options.url || '';

    try {
      // Build create command
      let cmd = `item create --vault "${vault}" --category ${category} --title "${itemTitle}" "${field}=${value}"`;

      if (username) {
        cmd += ` --username "${username}"`;
      }
      if (url) {
        cmd += ` --url "${url}"`;
      }

      const result = this.execOp(cmd);
      return { success: true, itemTitle, vault };
    } catch (e) {
      // If item exists, update it
      if (e.message.includes('already exists')) {
        return this.update(itemTitle, value, { field });
      }
      throw new Error(`Failed to store secret "${itemTitle}": ${e.message}`);
    }
  }

  /**
   * Update an existing secret
   */
  async update(itemTitle, value, options = {}) {
    const field = options.field || 'password';

    try {
      this.execOp(`item edit "${itemTitle}" "${field}=${value}"`);
      return { success: true, itemTitle, updated: true };
    } catch (e) {
      throw new Error(`Failed to update secret "${itemTitle}": ${e.message}`);
    }
  }

  /**
   * Delete a secret
   */
  async delete(itemTitle, vault = null) {
    const vaultFlag = vault ? ` --vault "${vault}"` : '';
    try {
      this.execOp(`item delete "${itemTitle}"${vaultFlag} --archive`);
      return { success: true, itemTitle };
    } catch (e) {
      throw new Error(`Failed to delete secret "${itemTitle}": ${e.message}`);
    }
  }

  /**
   * List items in vault
   */
  async listItems(vault = null) {
    const vaultFlag = vault ? ` --vault "${vault}"` : '';
    try {
      const result = this.execOp(`item list${vaultFlag}`);
      return result.trim().split('\n').slice(1).map(line => {
        const parts = line.split(/\s+/);
        return {
          id: parts[0],
          title: parts[1],
          vault: parts[2]
        };
      });
    } catch (e) {
      throw new Error(`Failed to list items: ${e.message}`);
    }
  }

  /**
   * Get AgentGuard master password from 1Password
   */
  async getMasterPassword() {
    return this.get('AgentGuard Master Password', 'password');
  }

  /**
   * Store AgentGuard master password in 1Password
   */
  async storeMasterPassword(password) {
    return this.store('AgentGuard Master Password', password, {
      vault: this.vault,
      category: 'Password',
      username: 'agentguard'
    });
  }

  /**
   * Get agent credential from 1Password
   */
  async getAgentCredential(agentId, key) {
    const itemTitle = `AgentGuard: ${agentId} - ${key}`;
    return this.get(itemTitle, 'credential');
  }

  /**
   * Store agent credential in 1Password
   */
  async storeAgentCredential(agentId, key, value) {
    const itemTitle = `AgentGuard: ${agentId} - ${key}`;
    return this.store(itemTitle, value, {
      vault: this.vault,
      category: 'API Credential',
      username: agentId
    });
  }

  /**
   * Generate a reference for use in op inject
   */
  getReference(agentId, key) {
    return `op://${this.vault}/AgentGuard: ${agentId} - ${key}/credential`;
  }
}

module.exports = OnePasswordProvider;
