// protocol.js — Message types and parsing for the XMTP agent swarm protocol

export const MessageType = {
  TASK: 'task',
  CLAIM: 'claim',
  RESULT: 'result',
  PAYMENT: 'payment',
  ACK: 'ack',
  LISTING: 'listing',
  PROFILE: 'profile',
  BID: 'bid',
  BID_ACCEPT: 'bid_accept',
  PROGRESS: 'progress',
  CANCEL: 'cancel',
  ESCROW_CREATED: 'escrow_created',
  ESCROW_RELEASED: 'escrow_released',
  REPUTATION_QUERY: 'reputation_query',
  REPUTATION: 'reputation',
  DELIVERABLE_SUBMITTED: 'deliverable_submitted',
  VERIFICATION_RESULT: 'verification_result',
  CRITERIA_SET: 'criteria_set',
  // Multi-bid negotiation
  BID_COUNTER: 'bid_counter',
  BID_WITHDRAW: 'bid_withdraw',
  // Subcontracting
  SUBTASK_DELEGATION: 'subtask_delegation',
};

// ─── Input Limits ───
export const LIMITS = {
  MAX_TITLE: 200,
  MAX_DESCRIPTION: 5000,
  MAX_RESULT: 50000,
  MAX_SKILL_NAME: 50,
  MAX_SKILLS: 20,
  MAX_ID: 100,
  MAX_MESSAGE_SIZE: 100000, // 100KB total message size
};

/** Validate a string field doesn't exceed max length */
function validString(val, maxLen) {
  return typeof val === 'string' && val.length <= maxLen;
}

/** Validate a skill name: alphanumeric, hyphens, underscores only */
function validSkillName(name) {
  return typeof name === 'string' && name.length <= LIMITS.MAX_SKILL_NAME && /^[a-zA-Z0-9_-]+$/.test(name);
}

/** Validate a skills array */
function validSkills(arr) {
  return Array.isArray(arr) && arr.length <= LIMITS.MAX_SKILLS && arr.every(validSkillName);
}

/** Validate a task message */
export function validateTask(msg) {
  return msg?.type === MessageType.TASK
    && msg.id && validString(msg.id, LIMITS.MAX_ID)
    && msg.title && validString(msg.title, LIMITS.MAX_TITLE)
    && Array.isArray(msg.subtasks);
}

/** Validate a claim message */
export function validateClaim(msg) {
  return msg?.type === MessageType.CLAIM && msg.taskId && msg.subtaskId && msg.worker;
}

/** Validate a result message */
export function validateResult(msg) {
  return msg?.type === MessageType.RESULT && msg.taskId && msg.subtaskId && msg.worker && msg.result;
}

/** Validate a payment message */
export function validatePayment(msg) {
  return msg?.type === MessageType.PAYMENT && msg.taskId && msg.worker && msg.txHash;
}

/** Try to parse a JSON protocol message from text. Returns null if not valid JSON or not a protocol msg.
 *  SECURITY: Rejects oversized messages to prevent memory exhaustion. */
export function parseMessage(text) {
  if (typeof text !== 'string' || text.length > LIMITS.MAX_MESSAGE_SIZE) return null;
  try {
    const msg = JSON.parse(text);
    if (msg && typeof msg.type === 'string') return msg;
  } catch { /* not JSON, ignore */ }
  return null;
}

/** Serialize a protocol message to JSON string */
export function serialize(msg) {
  return JSON.stringify(msg);
}

/** Create a task message */
export function createTask({ id, title, description, budget, subtasks, requirements }) {
  return { type: MessageType.TASK, id, title, description, budget, subtasks, requirements };
}

/** Create a claim message */
export function createClaim({ taskId, subtaskId, worker }) {
  return { type: MessageType.CLAIM, taskId, subtaskId, worker };
}

/** Create a result message */
export function createResult({ taskId, subtaskId, worker, result }) {
  return { type: MessageType.RESULT, taskId, subtaskId, worker, result };
}

/** Create a payment message */
export function createPayment({ taskId, subtaskId, worker, txHash, amount, escrowContract }) {
  const msg = { type: MessageType.PAYMENT, taskId, subtaskId, worker, txHash, amount };
  if (escrowContract) msg.escrowContract = escrowContract;
  return msg;
}

/** Create a listing message (for the bulletin board) */
export function createListing({ taskId, title, description, budget, skills_needed, requestor, expires }) {
  return { type: MessageType.LISTING, taskId, title, description, budget, skills_needed: skills_needed || [], requestor, expires: expires || null };
}

/** Create a profile message */
export function createProfileMsg({ agent, skills, rates, availability }) {
  return { type: MessageType.PROFILE, agent, skills: skills || [], rates: rates || {}, availability: availability || 'active' };
}

/** Create a bid message */
export function createBid({ taskId, worker, price, estimatedTime }) {
  return { type: MessageType.BID, taskId, worker, price, estimatedTime: estimatedTime || null };
}

/** Validate a listing message */
export function validateListing(msg) {
  return msg?.type === MessageType.LISTING
    && msg.taskId && validString(msg.taskId, LIMITS.MAX_ID)
    && msg.title && validString(msg.title, LIMITS.MAX_TITLE)
    && msg.requestor
    && (!msg.skills_needed || validSkills(msg.skills_needed));
}

/** Validate a profile message */
export function validateProfile(msg) {
  return msg?.type === MessageType.PROFILE
    && msg.agent
    && Array.isArray(msg.skills) && validSkills(msg.skills);
}

/** Validate a bid message */
export function validateBid(msg) {
  return msg?.type === MessageType.BID
    && msg.taskId && validString(msg.taskId, LIMITS.MAX_ID)
    && msg.worker
    && msg.price && !isNaN(parseFloat(msg.price)) && parseFloat(msg.price) > 0;
}

/** Create a reputation query message */
export function createReputationQuery({ agent, escrowContract }) {
  return { type: MessageType.REPUTATION_QUERY, agent, escrowContract };
}

/** Validate a reputation query */
export function validateReputationQuery(msg) {
  return msg?.type === MessageType.REPUTATION_QUERY && msg.agent;
}

/** Validate a reputation response */
export function validateReputation(msg) {
  return msg?.type === MessageType.REPUTATION && msg.address && typeof msg.trustScore === 'number';
}

// ─── Multi-Bid Negotiation ───

/** Create a counter-offer to a bid */
export function createBidCounter({ taskId, worker, counterPrice, message }) {
  return { type: MessageType.BID_COUNTER, taskId, worker, counterPrice, message: message || null };
}

/** Validate a bid counter message */
export function validateBidCounter(msg) {
  return msg?.type === MessageType.BID_COUNTER
    && msg.taskId && validString(msg.taskId, LIMITS.MAX_ID)
    && msg.worker
    && msg.counterPrice && !isNaN(parseFloat(msg.counterPrice));
}

/** Create a bid withdrawal */
export function createBidWithdraw({ taskId, worker }) {
  return { type: MessageType.BID_WITHDRAW, taskId, worker };
}

/** Validate a bid withdrawal */
export function validateBidWithdraw(msg) {
  return msg?.type === MessageType.BID_WITHDRAW
    && msg.taskId && validString(msg.taskId, LIMITS.MAX_ID)
    && msg.worker;
}

// ─── Subcontracting ───

/** Create a subtask delegation message */
export function createSubtaskDelegation({ parentTaskId, subtaskId, delegatedListingId, worker }) {
  return { type: MessageType.SUBTASK_DELEGATION, parentTaskId, subtaskId, delegatedListingId, worker };
}

/** Validate a subtask delegation */
export function validateSubtaskDelegation(msg) {
  return msg?.type === MessageType.SUBTASK_DELEGATION
    && msg.parentTaskId && msg.subtaskId && msg.worker;
}
