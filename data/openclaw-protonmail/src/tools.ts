/**
 * OpenClaw Tool Definitions for ProtonMail Skill
 * 
 * Registers tool functions that OpenClaw can invoke.
 */

import type { ProtonMailSkill } from './index';

export function registerTools(skill: ProtonMailSkill) {
  // TODO: Register tools with OpenClaw's tool registry
  // This will depend on OpenClaw's skill API
  
  // Example tool structure (adjust to match OpenClaw's actual API):
  /*
  registerTool({
    name: 'protonmail-list-inbox',
    description: 'List recent emails from ProtonMail inbox',
    parameters: {
      limit: { type: 'number', description: 'Max emails to return', default: 10 },
      unreadOnly: { type: 'boolean', description: 'Only unread emails', default: false }
    },
    handler: async (params) => {
      return skill.listInbox(params.limit, params.unreadOnly);
    }
  });
  */
}

// Tool definitions for documentation
export const TOOL_DEFINITIONS = {
  'protonmail-list-inbox': {
    description: 'List recent emails from inbox',
    parameters: {
      limit: { type: 'number', optional: true, default: 10 },
      unreadOnly: { type: 'boolean', optional: true, default: false }
    }
  },
  'protonmail-search': {
    description: 'Search emails by query',
    parameters: {
      query: { type: 'string', required: true },
      limit: { type: 'number', optional: true, default: 10 }
    }
  },
  'protonmail-read': {
    description: 'Read a specific email by ID',
    parameters: {
      messageId: { type: 'string', required: true }
    }
  },
  'protonmail-send': {
    description: 'Send a new email',
    parameters: {
      to: { type: 'string', required: true },
      subject: { type: 'string', required: true },
      body: { type: 'string', required: true },
      cc: { type: 'string', optional: true },
      bcc: { type: 'string', optional: true }
    }
  },
  'protonmail-reply': {
    description: 'Reply to an email thread',
    parameters: {
      messageId: { type: 'string', required: true },
      body: { type: 'string', required: true }
    }
  }
};
