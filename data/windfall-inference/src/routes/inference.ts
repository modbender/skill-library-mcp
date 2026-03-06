import { Router, Request, Response } from 'express';
import { v4 as uuid } from 'uuid';
import { config } from '../config';
import { InferenceRequest, RoutingMode, InferenceResponse } from '../types';
import { routeRequest, isLocalNode } from '../services/spatial-router';
import { callOpenRouter, getModelPrice, isPremiumModel } from '../services/openrouter-proxy';
import { checkFreeTier, consumeFreeTier, logRequest, logRevenue } from '../services/free-tier';
import { extractWalletFromHeaders, verifyOnchainPayment, PaymentResult } from '../services/payment';
import { getEnergyForNode } from '../services/energy-oracle';
import { queueAttestation } from '../services/eas-attestation';
import { extractApiKey, validateApiKey, canMakeRequest, deductRequest } from '../services/api-keys';
import { classifyEngagement, EngagementClassification } from '../services/engagement-classifier';
import { getCached, setCached, recordCacheSavings, shouldBypassCache } from '../services/cache';
import { buildPaymentRequired, encodePaymentRequiredHeader, decodePaymentSignature, encodePaymentResponseHeader, verifyAndSettleX402 } from '../services/x402';
import { getWalletSession } from '../services/sessions';

// Validate Ethereum address format (0x + 40 hex chars)
function isValidAddress(addr: any): addr is string {
  return typeof addr === 'string' && /^0x[a-fA-F0-9]{40}$/.test(addr);
}

const router = Router();

// OpenAI-compatible POST /v1/chat/completions
router.post('/v1/chat/completions', async (req: Request, res: Response) => {
  const startTime = Date.now();
  const requestId = uuid();

  try {
    const body = req.body as InferenceRequest & {
      x_wallet_address?: string;
      x_payment_tx?: string;
    };

    if (!body.messages || !Array.isArray(body.messages) || body.messages.length === 0) {
      return res.status(400).json({ error: 'messages array is required' });
    }

    // --- Authentication: API Key > Wallet > None ---

    const apiKey = extractApiKey(req.headers as Record<string, string | string[] | undefined>);
    let auth = apiKey ? validateApiKey(apiKey) : { authenticated: false, method: 'none' as const };

    // SIWA/SIWE: If no API key, check for wallet session token
    let agentSession: { walletAddress: string; isAgent: boolean } | null = null;
    if (!auth.authenticated) {
      const authHeader = req.headers['authorization'] || req.headers['Authorization'];
      const bearerStr = typeof authHeader === 'string' ? authHeader : Array.isArray(authHeader) ? authHeader[0] : '';
      if (bearerStr.startsWith('Bearer ') && !bearerStr.startsWith('Bearer wf_')) {
        const sessionToken = bearerStr.slice(7);
        const session = getWalletSession(sessionToken);
        if (session) {
          agentSession = {
            walletAddress: session.walletAddress,
            isAgent: session.isAgent || false,
          };
        }
      }
    }

    // Resolve wallet address (from agent session, API key, headers, or body)
    const rawWallet =
      agentSession?.walletAddress ||
      auth.walletAddress ||
      (isValidAddress(body.x_wallet_address) ? body.x_wallet_address.toLowerCase() : null) ||
      extractWalletFromHeaders(req.headers as Record<string, string | string[] | undefined>) ||
      (isValidAddress(req.headers['x-wallet-address']) ? (req.headers['x-wallet-address'] as string).toLowerCase() : null) ||
      null;
    const walletAddress = rawWallet;

    // --- Engagement Classification (always runs) ---

    const engagement: EngagementClassification = classifyEngagement({
      keyId: auth.keyId?.toString() || walletAddress || requestId,
      messages: body.messages,
      priorityHeader: req.headers['x-priority'] as string | undefined,
      userSpecifiedModel: body.model,
    });

    // Model selection: user's choice > engagement auto-select
    const model = body.model && body.model !== 'auto' ? body.model : engagement.autoModel;
    const price = getModelPrice(model);

    // Routing mode: default to greenest — users can override with x-routing-mode header or body.mode
    const mode: RoutingMode = (['cheapest', 'greenest', 'balanced'].includes(body.mode || '')
      ? body.mode
      : 'greenest') as RoutingMode;

    const finalPrice = mode === 'greenest' ? price * (1 + config.greenSurcharge) : price;

    // --- Cache Check (before payment, before routing) ---

    const bypassCache = shouldBypassCache(req.headers as Record<string, string | string[] | undefined>);

    // Scope cache per API key, wallet, or anonymous session
    const keyScope = auth.keyId
      ? `key:${auth.keyId}`
      : walletAddress
        ? `wallet:${walletAddress}`
        : `anon:${requestId}`;

    if (!bypassCache) {
      const cached = getCached(body.messages, model, keyScope);
      if (cached) {
        // Cache hit — free response
        const energyData = getEnergyForNode(config.nodeId);

        const cachedResponse: InferenceResponse = {
          ...cached.response,
          windfall: {
            node: config.nodeId,
            location: config.nodeLocation,
            mode,
            energyPricePerKwh: energyData?.pricePerKwh || 0,
            carbonIntensityGCO2: energyData?.carbonIntensity || 0,
            renewablePercent: energyData?.renewablePercent || 0,
            curtailmentActive: energyData?.curtailmentActive || false,
            costUsd: 0,
            cached: true,
            engagement: engagement.level,
            savedUsd: finalPrice,
          },
        };

        // Track savings
        recordCacheSavings(cached.cacheKey, finalPrice);

        // Log as cache hit (no payment deducted)
        logRequest({
          id: requestId,
          walletAddress: walletAddress || 'cache_hit',
          nodeId: config.nodeId,
          model,
          mode,
          inputTokens: cached.response.usage?.prompt_tokens || 0,
          outputTokens: cached.response.usage?.completion_tokens || 0,
          energyPriceKwh: energyData?.pricePerKwh || 0,
          carbonIntensity: energyData?.carbonIntensity || 0,
          costUsd: 0,
          paymentMethod: 'cache_hit',
          responseTimeMs: Date.now() - startTime,
        });

        res.set('X-Windfall-Cache', 'HIT');
        res.set('X-Windfall-Mode', mode);
        res.set('X-Windfall-Model', model);
        res.set('X-Windfall-Engagement', engagement.level);
        res.set('X-Windfall-Node', config.nodeId);
        res.set('X-Windfall-Cost', '$0.0000');
        res.set('X-Windfall-Saved', `$${finalPrice.toFixed(4)}`);
        return res.json(cachedResponse);
      }
    }

    // --- Payment Resolution ---

    let payment: PaymentResult = { method: 'none', walletAddress: walletAddress || 'unknown', amountUsd: 0 };

    // Verify proxied requests come from known peer node IPs only
    const proxyNodeId = req.headers['x-proxied-from'] as string;
    const clientIp = req.ip || req.socket?.remoteAddress || '';
    const isProxied = req.headers['x-payment-verified'] === 'true'
      && proxyNodeId
      && config.nodes.some(n => n.id === proxyNodeId && clientIp.includes(n.ip));
    if (isProxied) {
      payment = { method: 'free_tier', walletAddress: walletAddress || 'proxied', amountUsd: 0 };
    } else if (agentSession) {
      // Agent/wallet session auth — check free tier for the session wallet
      const freeTier = checkFreeTier(agentSession.walletAddress);
      if (freeTier.allowed) {
        payment = { method: 'free_tier', walletAddress: agentSession.walletAddress, amountUsd: 0 };
      } else {
        // Agent session with exhausted free tier needs payment
        const paymentTx = body.x_payment_tx || (req.headers['x-payment-tx'] as string) || null;
        if (paymentTx) {
          const verification = await verifyOnchainPayment(paymentTx, finalPrice);
          if (verification.valid) {
            payment = {
              method: 'eth_transfer',
              walletAddress: verification.from || agentSession.walletAddress,
              amountUsd: verification.amountUsd,
              txHash: paymentTx,
            };
          }
        }
        if (payment.method === 'none') {
          const payReqAgent = buildPaymentRequired(finalPrice);
          res.set('PAYMENT-REQUIRED', encodePaymentRequiredHeader(payReqAgent));
          return res.status(402).json({
            error: 'Payment required',
            x402Version: 2,
            message: `Agent session active (${agentSession.isAgent ? 'ERC-8004' : 'wallet'}), but free tier exhausted. Pay per request via x402, tx hash, or create an API key with balance.`,
            price_usd: finalPrice,
            wallet: config.walletAddress,
            network: 'Base',
            chainId: 8453,
            accepts: ['ETH', 'USDC'],
          });
        }
      }
    } else if (auth.authenticated && auth.keyId) {
      // API key auth — check key balance/free tier
      const canPay = canMakeRequest(auth.keyId, finalPrice);
      if (canPay.allowed) {
        payment = {
          method: canPay.paymentMethod as any,
          walletAddress: walletAddress || `key:${auth.keyId}`,
          amountUsd: canPay.paymentMethod === 'free_tier' ? 0 : finalPrice,
        };
      } else {
        const paymentRequired = buildPaymentRequired(finalPrice);
        res.set('PAYMENT-REQUIRED', encodePaymentRequiredHeader(paymentRequired));
        return res.status(402).json({
          error: 'Payment required',
          message: canPay.reason,
          x402Version: 2,
          price_usd: finalPrice,
          model,
          mode,
          engagement: engagement.level,
          wallet: config.walletAddress,
          network: 'Base',
          chainId: 8453,
          accepts: ['ETH', 'USDC'],
          topup: '/topup',
          hint: 'Top up your API key balance via card at /topup, or send ETH/USDC on Base to the wallet address, or use x402 protocol',
        });
      }
    } else if (walletAddress) {
      // Wallet-based auth — check free tier or payment
      const freeTier = checkFreeTier(walletAddress);
      // x402: accept payment tx hash from body or X-Payment-TX header (ETH or USDC)
      const paymentTx = body.x_payment_tx || (req.headers['x-payment-tx'] as string) || null;
      if (freeTier.allowed) {
        payment = { method: 'free_tier', walletAddress, amountUsd: 0 };
      } else if (paymentTx) {
        const verification = await verifyOnchainPayment(paymentTx, finalPrice);
        if (verification.valid) {
          payment = {
            method: 'eth_transfer',
            walletAddress: verification.from || walletAddress,
            amountUsd: verification.amountUsd,
            txHash: paymentTx,
          };
        } else {
          const payReq = buildPaymentRequired(finalPrice);
          res.set('PAYMENT-REQUIRED', encodePaymentRequiredHeader(payReq));
          return res.status(402).json({
            error: 'Payment required',
            message: verification.error,
            x402Version: 2,
            price_usd: finalPrice,
            wallet: config.walletAddress,
            network: 'Base',
            chainId: 8453,
            accepts: ['ETH', 'USDC'],
          });
        }
      } else {
        const payReq2 = buildPaymentRequired(finalPrice);
          res.set('PAYMENT-REQUIRED', encodePaymentRequiredHeader(payReq2));
          return res.status(402).json({
          error: 'Payment required',
          x402Version: 2,
          price_usd: finalPrice,
          model,
          mode,
          engagement: engagement.level,
          wallet: config.walletAddress,
          network: 'Base',
          chainId: 8453,
          accepts: ['ETH', 'USDC'],
          free_tier_remaining: 0,
          hint: 'Get an API key at POST /api/keys, include X-Payment-TX header with a Base tx hash, or use x402 protocol',
        });
      }
    } else {
      // --- x402 Protocol: check for payment-signature header ---
      const x402Header = (req.headers['payment-signature'] || req.headers['x-payment']) as string | undefined;
      if (x402Header) {
        const paymentPayload = decodePaymentSignature(x402Header);
        if (paymentPayload) {
          const x402Result = await verifyAndSettleX402(paymentPayload, finalPrice);
          if (x402Result.valid) {
            payment = {
              method: 'x402',
              walletAddress: x402Result.payer || 'x402',
              amountUsd: finalPrice,
              txHash: x402Result.txHash,
            };
            // Set wallet address from x402 payer for logging
            if (x402Result.payer) {
              (req as any)._x402Payer = x402Result.payer;
              (req as any)._x402TxHash = x402Result.txHash;
            }
          } else {
            // x402 payment failed — return 402 with PAYMENT-REQUIRED header
            const paymentRequired = buildPaymentRequired(finalPrice);
            res.set('PAYMENT-REQUIRED', encodePaymentRequiredHeader(paymentRequired));
            return res.status(402).json({
              error: 'x402 payment failed',
              message: x402Result.error,
              x402Version: 2,
              price_usd: finalPrice,
              model,
              mode,
              payTo: config.walletAddress,
              network: 'Base (eip155:8453)',
              asset: config.usdcAddress,
            });
          }
        }
      }

      // No auth method provided — return 402 with x402 PAYMENT-REQUIRED header
      if (payment.method === 'none') {
        const paymentRequired = buildPaymentRequired(finalPrice);
        res.set('PAYMENT-REQUIRED', encodePaymentRequiredHeader(paymentRequired));
        return res.status(402).json({
          error: 'Payment required',
          x402Version: 2,
          price_usd: finalPrice,
          model,
          mode,
          wallet: config.walletAddress,
          network: 'Base',
          chainId: 8453,
          accepts: ['ETH', 'USDC'],
          methods: {
            x402: 'Send request with PAYMENT-SIGNATURE header (base64 JSON). x402 clients handle this automatically.',
            credits: 'Add Authorization: Bearer wf_YOUR_KEY header. Get a key at POST /api/keys (25-100 free requests based on onchain identity)',
            manual: 'Add X-Wallet-Address and X-Payment-TX headers with a Base tx hash (ETH or USDC)',
          },
        });
      }
    }

    // --- Route the request ---

    const routing = routeRequest(mode);

    // If routed to a different node, deduct payment FIRST then proxy
    if (!isLocalNode(routing.nodeId)) {
      // Deduct payment on entry node before proxying
      if (!isProxied) {
        if (auth.authenticated && auth.keyId) {
          const directCost = isPremiumModel(model) ? 0.008 : 0.006;
          const savedUsd = Math.max(0, directCost - finalPrice);
          deductRequest(auth.keyId, finalPrice, savedUsd, payment.method);
        } else if (payment.method === 'free_tier' && walletAddress) {
          consumeFreeTier(walletAddress);
        }
      }

      try {
        const proxyHeaders: Record<string, string> = {
          'Content-Type': 'application/json',
          'X-Proxied-From': config.nodeId,
          'X-Payment-Verified': 'true',
        };
        if (walletAddress) proxyHeaders['X-Wallet-Address'] = walletAddress;

        const proxyRes = await fetch(`http://${routing.nodeIp}:${config.port}/v1/chat/completions`, {
          method: 'POST',
          headers: proxyHeaders,
          body: JSON.stringify({ ...body, model, _payment_verified: true }),
          signal: AbortSignal.timeout(60000),
        });

        const proxyData = await proxyRes.json();
        return res.status(proxyRes.status).json(proxyData);
      } catch (proxyErr) {
        console.error(`[inference] Proxy to ${routing.nodeId} failed, falling back to local:`, proxyErr);
      }
    }

    // --- Execute locally via OpenRouter ---

    const cappedMaxTokens = body.max_tokens !== undefined
      ? Math.min(body.max_tokens, 8192)
      : undefined;

    const { response: openRouterRes, latencyMs } = await callOpenRouter({
      model,
      messages: body.messages,
      temperature: body.temperature,
      max_tokens: cappedMaxTokens,
    });

    const responseTimeMs = Date.now() - startTime;
    const energyData = getEnergyForNode(config.nodeId) || routing.energyData;

    // --- Cache the response ---

    if (!bypassCache) {
      setCached(body.messages, model, keyScope, openRouterRes, finalPrice);
    }

    // --- Build response ---

    const windfallResponse: InferenceResponse = {
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
      },
    };

    // --- Deduct payment (skip for proxied requests — entry node handles billing) ---

    if (!isProxied) {
      if (auth.authenticated && auth.keyId) {
        const directCost = isPremiumModel(model) ? 0.008 : 0.006;
        const savedUsd = Math.max(0, directCost - finalPrice);
        deductRequest(auth.keyId, finalPrice, savedUsd, payment.method);
      } else if (payment.method === 'free_tier' && walletAddress) {
        consumeFreeTier(walletAddress);
      }
    }

    // Log request
    logRequest({
      id: requestId,
      walletAddress: payment.walletAddress,
      nodeId: config.nodeId,
      model: openRouterRes.model || model,
      mode,
      inputTokens: openRouterRes.usage?.prompt_tokens || 0,
      outputTokens: openRouterRes.usage?.completion_tokens || 0,
      energyPriceKwh: energyData.pricePerKwh,
      carbonIntensity: energyData.carbonIntensity,
      costUsd: finalPrice,
      paymentMethod: payment.method,
      responseTimeMs,
    });

    // Log revenue if paid
    if (payment.method !== 'free_tier' && payment.method !== 'none' && payment.method !== 'cache_hit') {
      logRevenue(payment.walletAddress, finalPrice, payment.method, payment.txHash);
    }

    // Queue attestation
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

    // Response headers
    res.set('X-Windfall-Cache', 'MISS');
    res.set('X-Windfall-Mode', mode);
    res.set('X-Windfall-Model', openRouterRes.model || model);
    res.set('X-Windfall-Engagement', engagement.level);
    res.set('X-Windfall-Node', config.nodeId);
    res.set('X-Windfall-Cost', `$${finalPrice.toFixed(4)}`);

    // x402: Set PAYMENT-RESPONSE header if payment was via x402
    if (payment.method === 'x402' && (req as any)._x402TxHash) {
      res.set('PAYMENT-RESPONSE', encodePaymentResponseHeader({
        success: true,
        transaction: (req as any)._x402TxHash,
        network: 'eip155:8453',
        payer: (req as any)._x402Payer,
      }));
    }

    return res.json(windfallResponse);
  } catch (err: any) {
    console.error(`[inference] Error processing request ${requestId}:`, err);
    return res.status(500).json({
      error: 'Internal server error',
      request_id: requestId,
    });
  }
});

export default router;
