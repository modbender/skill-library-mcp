#!/usr/bin/env node

/**
 * x402-request.mjs — x402 payment helper for AIresearchOS OpenClaw skill
 *
 * Makes an HTTP request. If 402 is returned, signs a USDC payment on Base
 * mainnet and retries with the payment header. Outputs the response body
 * to stdout and status/errors to stderr.
 *
 * Usage:
 *   node x402-request.mjs --url <URL> [--method POST] [--body <JSON>] [--max-payment <USDC>]
 *
 * Environment:
 *   AIRESEARCHOS_WALLET_KEY — EVM private key (0x-prefixed hex)
 */

import { parseArgs } from 'node:util'
import { privateKeyToAccount } from 'viem/accounts'
import { ExactEvmScheme } from '@x402/evm/exact/client'
import { encodePaymentSignatureHeader } from '@x402/core/http'

const { values: args } = parseArgs({
  options: {
    url: { type: 'string' },
    method: { type: 'string', default: 'POST' },
    body: { type: 'string', default: '' },
    'max-payment': { type: 'string', default: '1.00' },
  },
})

const url = args.url
const method = args.method || 'POST'
const body = args.body || ''
const maxPaymentUsd = parseFloat(args['max-payment'] || '1.00')

if (!url) {
  process.stderr.write(JSON.stringify({ error: 'missing_url', message: '--url is required' }) + '\n')
  process.exit(1)
}

const walletKey = process.env.AIRESEARCHOS_WALLET_KEY
if (!walletKey || !walletKey.startsWith('0x')) {
  process.stderr.write(JSON.stringify({
    error: 'missing_wallet_key',
    message: 'AIRESEARCHOS_WALLET_KEY env var must be set to a 0x-prefixed private key',
  }) + '\n')
  process.exit(1)
}

async function main() {
  const account = privateKeyToAccount(walletKey)
  const evmScheme = new ExactEvmScheme(account)

  // Step 1: Initial request (expects 402)
  const headers = { 'Content-Type': 'application/json' }
  const fetchOpts = { method, headers }
  if (body && method !== 'GET') {
    fetchOpts.body = body
  }

  process.stderr.write(JSON.stringify({ step: 'requesting', url, wallet: account.address }) + '\n')

  const initialResponse = await fetch(url, fetchOpts)

  // If not 402, pass through directly
  if (initialResponse.status !== 402) {
    const responseBody = await initialResponse.text()
    if (initialResponse.ok) {
      process.stdout.write(responseBody)
      process.exit(0)
    } else {
      process.stderr.write(JSON.stringify({
        error: 'request_failed',
        status: initialResponse.status,
        body: responseBody,
      }) + '\n')
      process.exit(1)
    }
  }

  // Step 2: Parse payment requirements from 402 response
  let paymentRequired
  try {
    paymentRequired = await initialResponse.json()
  } catch {
    process.stderr.write(JSON.stringify({ error: 'invalid_402_response', message: 'Could not parse 402 response body' }) + '\n')
    process.exit(1)
  }

  if (!paymentRequired.accepts || !paymentRequired.accepts.length) {
    process.stderr.write(JSON.stringify({ error: 'no_payment_options', message: 'Server returned 402 but no payment options' }) + '\n')
    process.exit(1)
  }

  const req = paymentRequired.accepts[0]
  const version = paymentRequired.x402Version
  const requiredUsd = parseInt(req.amount) / 1_000_000

  process.stderr.write(JSON.stringify({
    step: 'payment_required',
    price_usdc: requiredUsd,
    pay_to: req.payTo,
    network: req.network,
  }) + '\n')

  // Step 3: Check max payment safety
  if (requiredUsd > maxPaymentUsd) {
    process.stderr.write(JSON.stringify({
      error: 'payment_exceeds_max',
      required: req.amount,
      required_usdc: requiredUsd,
      max: String(Math.round(maxPaymentUsd * 1_000_000)),
      max_usdc: maxPaymentUsd,
    }) + '\n')
    process.exit(1)
  }

  // Step 4: Sign payment
  process.stderr.write(JSON.stringify({ step: 'signing_payment' }) + '\n')

  let encodedPayment
  try {
    const { x402Version, payload: innerPayload } = await evmScheme.createPaymentPayload(version, req)
    const paymentPayload = {
      x402Version,
      accepted: req,
      payload: innerPayload,
    }
    encodedPayment = encodePaymentSignatureHeader(paymentPayload)
  } catch (err) {
    process.stderr.write(JSON.stringify({
      error: 'payment_failed',
      message: err.message || 'Failed to sign payment',
    }) + '\n')
    process.exit(1)
  }

  // Step 5: Retry with payment header
  process.stderr.write(JSON.stringify({ step: 'submitting_with_payment' }) + '\n')

  const paidHeaders = {
    'Content-Type': 'application/json',
    'X-Payment': encodedPayment,
  }
  const paidOpts = { method, headers: paidHeaders }
  if (body && method !== 'GET') {
    paidOpts.body = body
  }

  const paidResponse = await fetch(url, paidOpts)
  const responseBody = await paidResponse.text()

  if (paidResponse.ok) {
    const settlement = paidResponse.headers.get('X-Payment-Response')
    process.stderr.write(JSON.stringify({
      step: 'complete',
      status: paidResponse.status,
      settled: !!settlement,
    }) + '\n')
    process.stdout.write(responseBody)
    process.exit(0)
  } else {
    process.stderr.write(JSON.stringify({
      error: 'paid_request_failed',
      status: paidResponse.status,
      body: responseBody,
    }) + '\n')
    process.exit(1)
  }
}

main().catch((err) => {
  process.stderr.write(JSON.stringify({
    error: 'network_error',
    message: err.message || 'Unknown error',
  }) + '\n')
  process.exit(1)
})
