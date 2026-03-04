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
};

/** Validate a task message */
export function validateTask(msg) {
  return msg?.type === MessageType.TASK && msg.id && msg.title && Array.isArray(msg.subtasks);
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

/** Try to parse a JSON protocol message from text. Returns null if not valid JSON or not a protocol msg. */
export function parseMessage(text) {
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
  return msg?.type === MessageType.LISTING && msg.taskId && msg.title && msg.requestor;
}

/** Validate a profile message */
export function validateProfile(msg) {
  return msg?.type === MessageType.PROFILE && msg.agent && Array.isArray(msg.skills);
}

/** Validate a bid message */
export function validateBid(msg) {
  return msg?.type === MessageType.BID && msg.taskId && msg.worker && msg.price;
}
