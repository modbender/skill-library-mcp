// worker.js — Worker agent: listens for tasks, claims subtasks, submits results
import { createSwarmAgent, sendProtocolMessage, onProtocolMessage } from './agent.js';
import { createClaim, createResult, MessageType } from './protocol.js';

/**
 * Create and start a Worker agent.
 * @param {string} privateKey - Wallet private key
 * @param {object} opts - { env, dbPath, onTask, onPayment, autoClaimSubtask }
 */
export async function createWorker(privateKey, opts = {}) {
  const { agent, address } = await createSwarmAgent(privateKey, opts);

  const receivedTasks = new Map();  // taskId -> task msg
  const payments = new Map();       // `${taskId}:${subtaskId}` -> payment msg

  // Listen for tasks
  onProtocolMessage(agent, MessageType.TASK, async (msg, ctx) => {
    receivedTasks.set(msg.id, msg);
    opts.onTask?.(msg, ctx);
  });

  // Listen for payment confirmations
  onProtocolMessage(agent, MessageType.PAYMENT, async (msg, ctx) => {
    const key = `${msg.taskId}:${msg.subtaskId}`;
    payments.set(key, msg);
    opts.onPayment?.(msg, ctx);
  });

  return {
    agent,
    address,
    receivedTasks,
    payments,

    /** Claim a subtask in a group conversation */
    async claimSubtask(conversation, { taskId, subtaskId }) {
      const msg = createClaim({ taskId, subtaskId, worker: address });
      await sendProtocolMessage(conversation, msg);
      return msg;
    },

    /** Submit a result for a subtask */
    async submitResult(conversation, { taskId, subtaskId, result }) {
      const msg = createResult({ taskId, subtaskId, worker: address, result });
      await sendProtocolMessage(conversation, msg);
      return msg;
    },
  };
}
