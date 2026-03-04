// requestor.js — Requestor agent: posts tasks, tracks claims/results, pays workers
import { createSwarmAgent, createSwarmGroup, sendProtocolMessage, onProtocolMessage } from './agent.js';
import { createTask, createPayment, MessageType } from './protocol.js';
import { transferUSDC, loadWallet } from './wallet.js';

/**
 * Create and start a Requestor agent.
 * @param {string} privateKey - Wallet private key
 * @param {object} opts - { env, dbPath, onClaim, onResult }
 */
export async function createRequestor(privateKey, opts = {}) {
  const { agent, address } = await createSwarmAgent(privateKey, opts);

  // State: track tasks, claims, results
  const tasks = new Map();   // taskId -> task msg
  const claims = new Map();  // `${taskId}:${subtaskId}` -> worker address
  const results = new Map(); // `${taskId}:${subtaskId}` -> result

  // Listen for claims
  onProtocolMessage(agent, MessageType.CLAIM, async (msg, ctx) => {
    const key = `${msg.taskId}:${msg.subtaskId}`;
    if (!claims.has(key)) {
      claims.set(key, msg.worker);
      opts.onClaim?.(msg);
    }
  });

  // Listen for results
  onProtocolMessage(agent, MessageType.RESULT, async (msg, ctx) => {
    const key = `${msg.taskId}:${msg.subtaskId}`;
    results.set(key, msg);
    opts.onResult?.(msg, ctx);
  });

  return {
    agent,
    address,
    tasks,
    claims,
    results,

    /** Create a swarm group and invite workers */
    async createGroup(workerAddresses, name) {
      return createSwarmGroup(agent, workerAddresses, name);
    },

    /** Post a task to a group conversation */
    async postTask(conversation, taskDef) {
      const msg = createTask(taskDef);
      tasks.set(msg.id, msg);
      await sendProtocolMessage(conversation, msg);
      return msg;
    },

    /** Pay a worker and send confirmation via XMTP */
    async payWorker(conversation, { taskId, subtaskId, worker, amount }) {
      const wallet = loadWallet(privateKey);
      const txHash = await transferUSDC(wallet, worker, amount);
      const payMsg = createPayment({ taskId, subtaskId, worker, txHash, amount });
      await sendProtocolMessage(conversation, payMsg);
      return payMsg;
    },

    /** Send a payment confirmation without actual transfer (for demos) */
    async sendPaymentConfirmation(conversation, { taskId, subtaskId, worker, txHash, amount }) {
      const payMsg = createPayment({ taskId, subtaskId, worker, txHash: txHash || '0xdemo', amount });
      await sendProtocolMessage(conversation, payMsg);
      return payMsg;
    },
  };
}
