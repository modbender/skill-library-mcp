// board.js — Public task board: XMTP group-based discovery for agents
import { createSwarmGroup, sendProtocolMessage, onProtocolMessage } from './agent.js';
import { MessageType, serialize } from './protocol.js';

/**
 * Create a new bulletin board (XMTP group conversation).
 * The board ID should be published so other agents can join.
 * @param {Agent} agent - XMTP agent (must be started)
 * @returns {object} group conversation representing the board
 */
export async function createBoard(agent) {
  const group = await agent.createGroupWithAddresses([], {
    name: 'Agent Swarm Board',
    description: 'Public task board for agent discovery. Post listings, find work.',
  });
  return group;
}

/**
 * Join an existing bulletin board by group ID.
 * @param {Agent} agent - XMTP agent
 * @param {string} boardId - The group conversation ID
 */
export async function joinBoard(agent, boardId) {
  // XMTP agent SDK: sync conversations and find the group
  await agent.conversations.sync();
  const conversations = await agent.conversations.list();
  const board = conversations.find(c => c.id === boardId);
  if (!board) {
    throw new Error(`Board ${boardId} not found. Make sure the agent has been added to the group.`);
  }
  return board;
}

/**
 * Post a task listing to the bulletin board.
 * @param {object} board - The board group conversation
 * @param {object} task - { taskId, title, description, budget, skills_needed, requestor, expires }
 */
export async function postListing(board, task) {
  const msg = {
    type: MessageType.LISTING,
    taskId: task.taskId,
    title: task.title,
    description: task.description || '',
    budget: task.budget,
    skills_needed: task.skills_needed || [],
    requestor: task.requestor,
    expires: task.expires || null,
  };
  await sendProtocolMessage(board, msg);
  return msg;
}

/**
 * Post a worker profile to the bulletin board.
 * @param {object} board - The board group conversation
 * @param {object} profile - { agent, skills, rates, availability }
 */
export async function postProfile(board, profile) {
  const msg = {
    type: MessageType.PROFILE,
    agent: profile.agent,
    skills: profile.skills || [],
    rates: profile.rates || {},
    availability: profile.availability || 'active',
  };
  await sendProtocolMessage(board, msg);
  return msg;
}

/**
 * Listen for new listings on the board.
 * @param {Agent} agent - The XMTP agent
 * @param {function} callback - async (listing) => void
 */
export function onListing(agent, callback) {
  onProtocolMessage(agent, MessageType.LISTING, callback);
}

/**
 * Listen for bids on the board.
 * @param {Agent} agent - The XMTP agent
 * @param {function} callback - async (bid) => void
 */
export function onBid(agent, callback) {
  onProtocolMessage(agent, MessageType.BID, callback);
}

/**
 * Post a bid on a listing.
 * @param {object} board - The board group conversation
 * @param {object} bid - { taskId, worker, price, estimatedTime }
 */
export async function postBid(board, bid) {
  const msg = {
    type: MessageType.BID,
    taskId: bid.taskId,
    worker: bid.worker,
    price: bid.price,
    estimatedTime: bid.estimatedTime || null,
  };
  await sendProtocolMessage(board, msg);
  return msg;
}
