#!/usr/bin/env node
/**
 * claw402 query script — uses the claw402 SDK for x402 V2 payment flow.
 *
 * GET:  node query.mjs <path> [key=value ...]
 * POST: node query.mjs <path> --post '<json-body>'
 *
 * Examples:
 *   node query.mjs /api/v1/nofx/netflow/top-ranking limit=20 duration=1h
 *   node query.mjs /api/v1/ai/openai/chat --post '{"messages":[{"role":"user","content":"Hello"}]}'
 */

import { Claw402 } from 'claw402'

const [,, path, ...rest] = process.argv

if (!path) {
  console.error(JSON.stringify({ error: 'Usage: node query.mjs <path> [key=value ...] | --post <json>' }))
  process.exit(1)
}

const privateKey = process.env.WALLET_PRIVATE_KEY
if (!privateKey) {
  console.error(JSON.stringify({ error: 'WALLET_PRIVATE_KEY environment variable is required' }))
  process.exit(1)
}

const gateway = process.env.CLAW402_GATEWAY ?? 'https://claw402.ai'
const client = new Claw402({ privateKey, baseUrl: gateway })

// Detect POST mode: node query.mjs <path> --post '<json>'
const isPost = rest[0] === '--post'

try {
  let data
  if (isPost) {
    const bodyStr = rest.slice(1).join(' ')
    if (!bodyStr) {
      console.error(JSON.stringify({ error: '--post requires a JSON body argument' }))
      process.exit(1)
    }
    const body = JSON.parse(bodyStr)
    const url = `${gateway}${path}`
    data = await client._post(path, body)
    console.log(JSON.stringify({ status: 200, url, data }, null, 2))
  } else {
    // Parse key=value params
    const params = {}
    for (const arg of rest) {
      const idx = arg.indexOf('=')
      if (idx > 0) params[arg.slice(0, idx)] = arg.slice(idx + 1)
    }
    const qs = new URLSearchParams(params).toString()
    const url = `${gateway}${path}${qs ? '?' + qs : ''}`
    data = await client._get(path, params)
    console.log(JSON.stringify({ status: 200, url, data }, null, 2))
  }
} catch (err) {
  console.error(JSON.stringify({ error: String(err), path }))
  process.exit(1)
}
