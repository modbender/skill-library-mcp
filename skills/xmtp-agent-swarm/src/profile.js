// profile.js — Worker profiles: advertise skills and rates over XMTP
import { sendProtocolMessage } from './agent.js';
import { MessageType } from './protocol.js';

/**
 * Create a profile object for a worker agent.
 * @param {string} agentAddress - Worker's wallet address
 * @param {object} opts - { skills, rates, description }
 * @returns {object} profile object
 */
export function createProfile(agentAddress, { skills = [], rates = {}, description = '' } = {}) {
  return {
    agent: agentAddress,
    skills,
    rates,
    description,
    availability: 'active',
    updatedAt: new Date().toISOString(),
  };
}

/**
 * Broadcast a profile to the bulletin board.
 * @param {object} board - The board group conversation
 * @param {object} profile - Profile object from createProfile
 */
export async function broadcastProfile(board, profile) {
  const msg = {
    type: MessageType.PROFILE,
    agent: profile.agent,
    skills: profile.skills,
    rates: profile.rates,
    availability: profile.availability || 'active',
  };
  await sendProtocolMessage(board, msg);
  return msg;
}

/**
 * Find workers on the board matching a skill.
 * Scans recent profile messages in the board conversation.
 * Returns an array of profile messages that advertise the given skill.
 *
 * Note: this reads cached/synced messages. The board conversation
 * must have been synced recently for fresh results.
 *
 * @param {object} board - The board group conversation
 * @param {string} skillNeeded - Skill string to match (e.g. "backend", "code-review")
 * @returns {object[]} array of matching profile messages
 */
export async function findWorkers(board, skillNeeded) {
  await board.sync();
  const messages = await board.messages({ limit: 100 });
  const profiles = new Map(); // agent -> latest profile

  for (const m of messages) {
    try {
      const parsed = JSON.parse(m.content);
      if (parsed.type === MessageType.PROFILE && Array.isArray(parsed.skills)) {
        // Keep the latest profile per agent
        profiles.set(parsed.agent, parsed);
      }
    } catch { /* not JSON, skip */ }
  }

  const needle = skillNeeded.toLowerCase();
  return [...profiles.values()].filter(p =>
    p.skills.some(s => s.toLowerCase() === needle) &&
    p.availability !== 'offline'
  );
}
