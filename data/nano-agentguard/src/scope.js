/**
 * Scope - Permission Management
 *
 * Defines operation levels and approval requirements
 */

// Permission levels hierarchy
const LEVELS = {
  read: 1,
  write: 2,
  admin: 3,
  dangerous: 4
};

// Dangerous operations that require human approval
const DANGEROUS_OPERATIONS = new Set([
  'send_message',
  'send_email',
  'financial_transaction',
  'delete_data',
  'modify_config',
  'access_credential',
  'external_api_call',
  'file_write',
  'exec_command',
  'create_agent',
  'delete_agent'
]);

// Read-only operations (always auto-approved for read+ level)
const READ_OPERATIONS = new Set([
  'read_file',
  'list_files',
  'get_credential_metadata',
  'list_agents',
  'get_agent_info',
  'read_audit_log'
]);

class Scope {
  constructor(registry) {
    this.registry = registry;
  }

  /**
   * Check if operation is allowed for agent
   * Returns: { allowed: boolean, requiresApproval: boolean, reason: string }
   */
  async check(agentId, operation, context = {}) {
    const agent = await this.registry.get(agentId);
    const level = LEVELS[agent.permissions.level] || 0;
    const dangerousPolicy = agent.permissions.dangerous || 'require-approval';

    // Check if operation is dangerous
    const isDangerous = DANGEROUS_OPERATIONS.has(operation) || context.isDangerous === true;
    const isRead = READ_OPERATIONS.has(operation) || context.isRead === true;

    // Read operations: always allowed for read+ level
    if (isRead && level >= LEVELS.read) {
      return {
        allowed: true,
        requiresApproval: false,
        reason: 'Read operation auto-approved'
      };
    }

    // Dangerous operations policy
    if (isDangerous) {
      if (dangerousPolicy === 'never-allow') {
        return {
          allowed: false,
          requiresApproval: false,
          reason: 'Dangerous operations disabled for this agent'
        };
      }

      if (dangerousPolicy === 'require-approval') {
        return {
          allowed: true,
          requiresApproval: true,
          reason: 'Dangerous operation requires human approval'
        };
      }

      if (dangerousPolicy === 'auto-approve' && level >= LEVELS.dangerous) {
        return {
          allowed: true,
          requiresApproval: false,
          reason: 'Agent has dangerous auto-approve permission'
        };
      }
    }

    // Level-based check
    if (level >= LEVELS.write && !isDangerous) {
      return {
        allowed: true,
        requiresApproval: false,
        reason: 'Operation within permission level'
      };
    }

    // Default: deny
    return {
      allowed: false,
      requiresApproval: false,
      reason: 'Operation not permitted for this agent'
    };
  }

  /**
   * Set permission level for agent
   */
  async setLevel(agentId, level) {
    if (!LEVELS[level]) {
      throw new Error(`Invalid permission level: ${level}`);
    }

    return this.registry.update(agentId, {
      permissions: {
        ...((await this.registry.get(agentId)).permissions),
        level
      }
    });
  }

  /**
   * Set dangerous operation policy
   */
  async setDangerousPolicy(agentId, policy) {
    const validPolicies = ['require-approval', 'auto-approve', 'never-allow'];
    if (!validPolicies.includes(policy)) {
      throw new Error(`Invalid dangerous policy: ${policy}`);
    }

    return this.registry.update(agentId, {
      permissions: {
        ...((await this.registry.get(agentId)).permissions),
        dangerous: policy
      }
    });
  }

  /**
   * Get permission info for agent
   */
  async getInfo(agentId) {
    const agent = await this.registry.get(agentId);
    return {
      level: agent.permissions.level,
      dangerous: agent.permissions.dangerous,
      levelRank: LEVELS[agent.permissions.level] || 0
    };
  }

  /**
   * List all available operations
   */
  static listOperations() {
    return {
      read: Array.from(READ_OPERATIONS),
      dangerous: Array.from(DANGEROUS_OPERATIONS)
    };
  }
}

module.exports = Scope;
module.exports.LEVELS = LEVELS;
module.exports.DANGEROUS_OPERATIONS = DANGEROUS_OPERATIONS;
module.exports.READ_OPERATIONS = READ_OPERATIONS;
