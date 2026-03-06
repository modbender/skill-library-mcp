/**
 * ACP Job Handler
 *
 * Initializes the Virtuals ACP SDK alongside Express, listens for jobs
 * via WebSocket, and executes real inference through Windfall's pipeline.
 *
 * Payment is skipped — ACP escrow handles it. Rate limits are bypassed —
 * ACP has economic rate limiting via escrow.
 *
 * Job lifecycle state machine:
 *   onNewTask(job, phase=REQUEST)     → job.accept() + job.createRequirement()
 *   onNewTask(job, phase=TRANSACTION) → parseRequirement → executeInference → job.deliver(result)
 *   onEvaluate(job)                   → log completion
 */

import AcpClient, {
  AcpContractClientV2,
  baseAcpConfigV2,
  AcpJobPhases,
} from '@virtuals-protocol/acp-node';
import { v4 as uuid } from 'uuid';
import { config } from '../config';
import { classifyEngagement } from './engagement-classifier';
import { getCached, setCached } from './cache';
import { routeRequest } from './spatial-router';
import { callOpenRouter, getModelPrice } from './openrouter-proxy';
import { getEnergyForNode } from './energy-oracle';
import { logRequest, logRevenue } from './free-tier';
import { queueAttestation } from './eas-attestation';
import { RoutingMode } from '../types';

let acpClient: AcpClient | null = null;

/**
 * Parse the buyer's requirement into an OpenAI-compatible messages array.
 *
 * Handles three formats:
 * 1. JSON with `messages` array (OpenAI-compatible)
 * 2. JSON with `prompt` string
 * 3. Plain text string
 */
function parseRequirement(content: string): {
  messages: Array<{ role: string; content: string }>;
  model?: string;
  mode?: RoutingMode;
  temperature?: number;
  max_tokens?: number;
} {
  try {
    const parsed = JSON.parse(content);

    // OpenAI-compatible: { messages: [...], model?, mode?, ... }
    if (Array.isArray(parsed.messages) && parsed.messages.length > 0) {
      return {
        messages: parsed.messages,
        model: parsed.model,
        mode: parsed.mode,
        temperature: parsed.temperature,
        max_tokens: parsed.max_tokens,
      };
    }

    // Simple prompt object: { prompt: "..." }
    if (typeof parsed.prompt === 'string') {
      return {
        messages: [{ role: 'user', content: parsed.prompt }],
        model: parsed.model,
        mode: parsed.mode,
      };
    }

    // Fallback: treat entire JSON as prompt
    return {
      messages: [{ role: 'user', content: content }],
    };
  } catch {
    // Plain text string
    return {
      messages: [{ role: 'user', content: content }],
    };
  }
}

/**
 * Execute real inference through Windfall's pipeline.
 * Calls the same pure functions as the HTTP inference route.
 */
async function executeInference(
  requirement: string,
  clientAddress: string,
  jobId: number,
): Promise<string> {
  const startTime = Date.now();
  const requestId = uuid();

  const parsed = parseRequirement(requirement);
  const messages = parsed.messages;

  // 1. Engagement classification → model selection
  const engagement = classifyEngagement({
    keyId: `acp:${clientAddress}`,
    messages,
    userSpecifiedModel: parsed.model,
  });

  const model = parsed.model && parsed.model !== 'auto'
    ? parsed.model
    : engagement.autoModel;

  const mode: RoutingMode = (['cheapest', 'greenest', 'balanced'].includes(parsed.mode || '')
    ? parsed.mode
    : 'greenest') as RoutingMode;

  const price = getModelPrice(model);
  const finalPrice = mode === 'greenest' ? price * (1 + config.greenSurcharge) : price;

  // 2. Cache check (scope: acp:{clientAddress})
  const keyScope = `acp:${clientAddress.toLowerCase()}`;

  const cached = getCached(messages, model, keyScope);
  if (cached) {
    const energyData = getEnergyForNode(config.nodeId);

    logRequest({
      id: requestId,
      walletAddress: clientAddress.toLowerCase(),
      nodeId: config.nodeId,
      model,
      mode,
      inputTokens: cached.response.usage?.prompt_tokens || 0,
      outputTokens: cached.response.usage?.completion_tokens || 0,
      energyPriceKwh: energyData?.pricePerKwh || 0,
      carbonIntensity: energyData?.carbonIntensity || 0,
      costUsd: 0,
      paymentMethod: 'acp_cache_hit',
      responseTimeMs: Date.now() - startTime,
    });

    console.log(`[acp] Job #${jobId} cache HIT for ${clientAddress.slice(0, 10)}...`);

    return JSON.stringify({
      ...cached.response,
      windfall: {
        node: config.nodeId,
        mode,
        costUsd: 0,
        cached: true,
        engagement: engagement.level,
        acpJobId: jobId,
      },
    });
  }

  // 3. Route request → energy data
  const routing = routeRequest(mode);
  const energyData = getEnergyForNode(config.nodeId) || routing.energyData;

  // 4. Call OpenRouter
  const cappedMaxTokens = parsed.max_tokens !== undefined
    ? Math.min(parsed.max_tokens, 8192)
    : undefined;

  const { response: openRouterRes, latencyMs } = await callOpenRouter({
    model,
    messages: messages as Array<{ role: 'system' | 'user' | 'assistant'; content: string }>,
    temperature: parsed.temperature,
    max_tokens: cappedMaxTokens,
  });

  const responseTimeMs = Date.now() - startTime;

  // 5. Cache the response
  setCached(messages, model, keyScope, openRouterRes, finalPrice);

  // 6. Log request with paymentMethod: 'acp'
  logRequest({
    id: requestId,
    walletAddress: clientAddress.toLowerCase(),
    nodeId: config.nodeId,
    model: openRouterRes.model || model,
    mode,
    inputTokens: openRouterRes.usage?.prompt_tokens || 0,
    outputTokens: openRouterRes.usage?.completion_tokens || 0,
    energyPriceKwh: energyData.pricePerKwh,
    carbonIntensity: energyData.carbonIntensity,
    costUsd: finalPrice,
    paymentMethod: 'acp',
    responseTimeMs,
  });

  // Log revenue (ACP escrow handles actual payment, but track for stats)
  logRevenue(clientAddress.toLowerCase(), finalPrice, 'acp');

  // 7. Queue EAS attestation
  queueAttestation({
    timestamp: Math.floor(Date.now() / 1000),
    nodeId: config.nodeId,
    lat: config.nodeLat,
    lon: config.nodeLon,
    energyPricePerKwh: energyData.pricePerKwh,
    carbonIntensity: energyData.carbonIntensity,
    curtailmentActive: energyData.curtailmentActive,
    model: openRouterRes.model || model,
    responseHash: requestId,
    requestCount: 1,
  });

  console.log(
    `[acp] Job #${jobId} inference complete: ` +
    `model=${openRouterRes.model || model}, ` +
    `tokens=${openRouterRes.usage?.total_tokens || 0}, ` +
    `latency=${latencyMs}ms, ` +
    `cost=$${finalPrice.toFixed(4)}, ` +
    `client=${clientAddress.slice(0, 10)}...`
  );

  // Return full response as JSON deliverable
  return JSON.stringify({
    ...openRouterRes,
    windfall: {
      node: config.nodeId,
      location: config.nodeLocation,
      mode,
      energyPricePerKwh: energyData.pricePerKwh,
      carbonIntensityGCO2: energyData.carbonIntensity,
      renewablePercent: energyData.renewablePercent,
      curtailmentActive: energyData.curtailmentActive,
      costUsd: finalPrice,
      cached: false,
      engagement: engagement.level,
      acpJobId: jobId,
    },
  });
}

/**
 * Extract the buyer's original inference requirement from the job.
 *
 * At TRANSACTION phase, memos typically are:
 *   [0] Buyer's initiation (contains the original JSON requirement)
 *   [1] Provider's acceptance
 *   [2] Provider's requirement description
 *   [3] Buyer's payment approval ("Approved")
 *
 * We want memo[0] — the buyer's first memo — NOT latestMemo (which is "Approved").
 */
function extractRequirementContent(job: any): string | null {
  // Walk memos forward to find the FIRST memo from the buyer (client)
  if (job.memos?.length) {
    for (let i = 0; i < job.memos.length; i++) {
      const memo = job.memos[i];
      if (memo.content && memo.senderAddress?.toLowerCase() === job.clientAddress?.toLowerCase()) {
        return memo.content;
      }
    }
    // Fallback: first memo with content (should be the initiation)
    if (job.memos[0]?.content) {
      return job.memos[0].content;
    }
  }

  return null;
}

// Keywords that indicate a non-inference request (trading, swapping, fund transfers)
const REJECT_KEYWORDS = [
  'swap', 'trade', 'transfer', 'send tokens', 'send eth', 'send usdc',
  'buy token', 'sell token', 'yield farm', 'stake', 'unstake', 'bridge',
  'approve token', 'mint nft', 'deploy contract',
];

/**
 * Validate whether a requirement looks like a valid inference request.
 * Returns null if valid, or a rejection reason string if invalid.
 */
function validateRequirement(content: string): string | null {
  if (!content || content.trim().length === 0) {
    return 'Empty requirement. Send JSON with messages array, e.g. {"messages":[{"role":"user","content":"Hello"}]}';
  }

  // Check for non-inference requests (trading, swapping, etc.)
  const lower = content.toLowerCase();
  for (const keyword of REJECT_KEYWORDS) {
    if (lower.includes(keyword)) {
      return `Windfall is an LLM inference service only. Cannot perform: "${keyword}". Send a chat completion request with a messages array.`;
    }
  }

  // Try parsing as JSON to validate structure
  try {
    const parsed = JSON.parse(content);
    if (parsed.messages && Array.isArray(parsed.messages)) {
      if (parsed.messages.length === 0) {
        return 'Messages array is empty. Provide at least one message.';
      }
      // Validate each message has role and content
      for (const msg of parsed.messages) {
        if (!msg.role || !msg.content) {
          return 'Each message must have "role" and "content" fields.';
        }
      }
    }
    // JSON with prompt field is also valid
    if (parsed.prompt !== undefined && typeof parsed.prompt !== 'string') {
      return 'The "prompt" field must be a string.';
    }
  } catch {
    // Plain text is fine — will be treated as a user message
  }

  return null;
}

/**
 * Start the ACP handler. Initializes the SDK with WebSocket connection
 * and registers onNewTask/onEvaluate callbacks.
 */
export async function startAcpHandler(): Promise<void> {
  if (!config.acpEnabled) return;

  if (!config.acpWalletKey || !config.acpAgentWallet) {
    console.warn('[acp] ACP_ENABLED=true but ACP_WALLET_KEY or ACP_AGENT_WALLET is missing. Skipping.');
    return;
  }

  try {
    console.log('[acp] Initializing ACP handler...');

    const contractClient = await AcpContractClientV2.build(
      config.acpWalletKey as `0x${string}`,
      config.acpEntityId,
      config.acpAgentWallet as `0x${string}`,
      baseAcpConfigV2,
    );

    acpClient = new AcpClient({
      acpContractClient: contractClient,

      onNewTask: async (job, memoToSign) => {
        const phase = job.phase;
        console.log(`[acp] onNewTask: job #${job.id}, phase=${phase}, client=${job.clientAddress?.slice(0, 10)}...`);

        try {
          if (phase === AcpJobPhases.REQUEST) {
            // Phase REQUEST: Validate the requirement, then accept or reject.
            const initContent = extractRequirementContent(job);
            const rejectReason = initContent ? validateRequirement(initContent) : null;

            if (rejectReason) {
              console.log(`[acp] Job #${job.id} REJECTED: ${rejectReason}`);
              await job.reject(rejectReason);
              return;
            }

            await job.accept('Windfall inference service ready');
            await job.createRequirement(
              'OpenAI-compatible LLM inference. Send JSON with messages array, or plain text prompt.'
            );
            console.log(`[acp] Job #${job.id} accepted + requirement created`);

          } else if (phase === AcpJobPhases.TRANSACTION) {
            // Phase TRANSACTION: Buyer has paid. Execute real inference and deliver.
            const requirement = extractRequirementContent(job);

            if (!requirement) {
              console.error(`[acp] Job #${job.id}: no requirement content found in memos`);
              await job.deliver(JSON.stringify({
                error: 'No inference requirement found in job memos',
                hint: 'Send JSON with messages array, e.g. {"messages":[{"role":"user","content":"Hello"}]}',
              }));
              return;
            }

            console.log(`[acp] Job #${job.id} executing inference...`);
            const result = await executeInference(
              requirement,
              job.clientAddress,
              job.id,
            );

            await job.deliver(result);
            console.log(`[acp] Job #${job.id} delivered`);

          } else {
            console.log(`[acp] Job #${job.id}: unhandled phase ${phase}, ignoring`);
          }
        } catch (err: any) {
          console.error(`[acp] Job #${job.id} error in phase ${phase}:`, err.message);

          // Deliver error payload so buyer can reject cleanly
          try {
            if (phase === AcpJobPhases.TRANSACTION) {
              await job.deliver(JSON.stringify({
                error: 'Inference execution failed',
                message: err.message?.slice(0, 500),
              }));
            }
          } catch (deliverErr: any) {
            console.error(`[acp] Job #${job.id} failed to deliver error:`, deliverErr.message);
          }
        }
      },

      onEvaluate: (job) => {
        console.log(
          `[acp] onEvaluate: job #${job.id} completed, ` +
          `client=${job.clientAddress?.slice(0, 10)}...`
        );
      },
    });

    await acpClient.init(true);

    console.log(`[acp] ACP handler started — listening for jobs as ${config.acpAgentWallet.slice(0, 10)}...`);
  } catch (err: any) {
    console.error('[acp] Failed to start ACP handler:', err.message);
    // Non-fatal: server continues without ACP
  }
}
