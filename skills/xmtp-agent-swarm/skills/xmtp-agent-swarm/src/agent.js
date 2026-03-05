// agent.js — Core XMTP agent for the swarm protocol
import { Agent, createUser, createSigner, filter, encodeText } from '@xmtp/agent-sdk';
import { parseMessage } from './protocol.js';

/**
 * Create an XMTP swarm agent from a private key.
 * @param {string} privateKey - Hex private key (0x...)
 * @param {object} opts - Options: { dbPath, env }
 * @returns {{ agent: Agent, address: string }}
 */
export async function createSwarmAgent(privateKey, opts = {}) {
  const user = createUser(privateKey);
  const signer = createSigner(user);
  const address = user.account.address;

  const agent = await Agent.create(signer, {
    env: opts.env || 'dev',
    dbPath: opts.dbPath || null, // in-memory by default
  });

  return { agent, address, user };
}

/**
 * Create a swarm group conversation (the agent must be started first or client available).
 * @param {Agent} agent - The XMTP agent
 * @param {string[]} memberAddresses - Ethereum addresses of other members
 * @param {string} name - Group name
 */
export async function createSwarmGroup(agent, memberAddresses, name = 'Swarm') {
  const group = await agent.createGroupWithAddresses(memberAddresses, {
    name,
    description: 'Agent Swarm task group',
  });
  return group;
}

/**
 * Send a protocol message (JSON) to a conversation.
 */
export async function sendProtocolMessage(conversation, msg) {
  await conversation.send(encodeText(JSON.stringify(msg)));
}

/**
 * Register a handler for protocol messages of a specific type.
 * @param {Agent} agent - The XMTP agent
 * @param {string} type - Message type to handle (e.g. 'task', 'claim')
 * @param {function} handler - async (parsedMsg, ctx) => void
 */
export function onProtocolMessage(agent, type, handler) {
  agent.on('text', async (ctx) => {
    // Skip own messages
    if (filter.fromSelf(ctx.message, ctx.client)) return;
    const parsed = parseMessage(ctx.message.content);
    if (parsed && parsed.type === type) {
      await handler(parsed, ctx);
    }
  });
}

export { Agent, createUser, createSigner, filter };
