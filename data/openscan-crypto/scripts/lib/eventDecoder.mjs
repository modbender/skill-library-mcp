/**
 * Event log decoder — decodes EVM event logs using a signature database
 * Ported from explorer: src/utils/eventDecoder.ts (viem-free)
 */

import { readFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { decodeValue } from "./abiDecoder.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
let eventsDb = null;

async function loadEventsDb() {
  if (eventsDb) return eventsDb;
  const raw = await readFile(join(__dirname, "events.json"), "utf-8");
  eventsDb = JSON.parse(raw);
  return eventsDb;
}

/**
 * Parse event signature to extract param types
 */
function parseEventSignature(signature) {
  const match = signature.match(/^(\w+)\((.*)\)$/);
  if (!match) return { name: signature, params: [] };
  const name = match[1];
  const paramsStr = match[2] || "";
  if (!paramsStr) return { name, params: [] };

  const params = [];
  let depth = 0, current = "";
  for (const char of paramsStr) {
    if (char === "(") { depth++; current += char; }
    else if (char === ")") { depth--; current += char; }
    else if (char === "," && depth === 0) {
      if (current) params.push(current.trim());
      current = "";
    } else { current += char; }
  }
  if (current) params.push(current.trim());
  return { name, params };
}

/** Known parameter names for common events */
const PARAM_NAMES = {
  Transfer: ["from", "to", "value"],
  Approval: ["owner", "spender", "value"],
  ApprovalForAll: ["owner", "operator", "approved"],
  Swap: ["sender", "amount0In", "amount1In", "amount0Out", "amount1Out", "to"],
  Mint: ["sender", "amount0", "amount1"],
  Burn: ["sender", "amount0", "amount1", "to"],
  Sync: ["reserve0", "reserve1"],
  Deposit: ["sender", "owner", "assets", "shares"],
  Withdraw: ["sender", "receiver", "owner", "assets", "shares"],
  OwnershipTransferred: ["previousOwner", "newOwner"],
};

function getParamName(eventName, index) {
  const names = PARAM_NAMES[eventName];
  return names?.[index] || `param${index}`;
}

/**
 * Decode an event log
 * @param {string[]} topics - Log topics
 * @param {string} data - Log data hex
 * @returns {Object|null} Decoded event with name, signature, params
 */
export async function decodeEventLog(topics, data) {
  if (!topics || topics.length === 0) return null;

  const topic0 = topics[0];
  const db = await loadEventsDb();
  const eventInfo = db[topic0.toLowerCase()] || db[topic0];
  if (!eventInfo) return null;

  const { name, params: paramTypes } = parseEventSignature(eventInfo.event);
  const indexedCount = topics.length - 1;

  const decoded = [];
  let topicIdx = 1;
  let dataOffset = 0;
  const cleanData = (data && data !== "0x") ? (data.startsWith("0x") ? data.slice(2) : data) : "";

  for (let i = 0; i < paramTypes.length; i++) {
    const type = paramTypes[i];

    if (topicIdx <= indexedCount && topicIdx < topics.length) {
      // Indexed param from topics
      decoded.push({
        name: getParamName(name, i),
        type,
        value: decodeValue(topics[topicIdx], type),
        indexed: true,
      });
      topicIdx++;
    } else {
      // Non-indexed param from data
      const chunk = cleanData.slice(dataOffset, dataOffset + 64);
      decoded.push({
        name: getParamName(name, i),
        type,
        value: chunk ? decodeValue(`0x${chunk}`, type) : "",
        indexed: false,
      });
      dataOffset += 64;
    }
  }

  return {
    name,
    fullSignature: eventInfo.event,
    type: eventInfo.type,
    description: eventInfo.description,
    topic0,
    params: decoded,
  };
}

/**
 * Look up event info by topic0 (without decoding params)
 */
export async function lookupEvent(topic0) {
  const db = await loadEventsDb();
  return db[topic0.toLowerCase()] || db[topic0] || null;
}

/**
 * Format a decoded value for human display
 */
export function formatDecodedValue(value, type) {
  if (!value) return "";
  if (type.startsWith("uint") || type.startsWith("int")) {
    try {
      const num = BigInt(value);
      if (num > BigInt(1e15)) {
        const ethValue = Number(num) / 1e18;
        if (ethValue >= 0.0001 && ethValue < 1e15) {
          return `${num.toString()} (≈${ethValue.toFixed(6)} if 18 decimals)`;
        }
      }
      return num.toLocaleString();
    } catch { return value; }
  }
  return value;
}
