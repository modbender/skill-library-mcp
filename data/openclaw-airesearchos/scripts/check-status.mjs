#!/usr/bin/env node

/**
 * check-status.mjs — Check AIresearchOS research status and fetch report if complete.
 *
 * Outputs a structured JSON result to stdout. No natural-language prompts.
 * Reads API key from AIRESEARCHOS_API_KEY env var (injected by OpenClaw at runtime).
 * Never accepts secrets as CLI arguments.
 *
 * Exit codes:
 *   0 — completed (report JSON on stdout)
 *   2 — still processing (status JSON on stdout)
 *   1 — failed/timeout/error (error JSON on stdout)
 *
 * Usage:
 *   node check-status.mjs --id <REQUEST_ID> --base-url <URL> [--api-path /api/v1]
 *
 * Environment:
 *   AIRESEARCHOS_API_KEY — Bearer token for /api/v1 endpoints (optional for /api/x402)
 */

import { parseArgs } from 'node:util'

const { values: args } = parseArgs({
  options: {
    id: { type: 'string' },
    'base-url': { type: 'string' },
    'api-path': { type: 'string', default: '/api/v1' },
  },
})

const requestId = args.id
const baseUrl = (args['base-url'] || '').replace(/\/+$/, '')
const apiPath = args['api-path'] || '/api/v1'

if (!requestId || !baseUrl) {
  process.stdout.write(JSON.stringify({
    action: 'error',
    error: 'missing_args',
    message: '--id and --base-url are required',
  }) + '\n')
  process.exit(1)
}

const statusUrl = `${baseUrl}${apiPath}/research/${requestId}`
const outputUrl = `${baseUrl}${apiPath}/research/${requestId}/output`

async function main() {
  const headers = {}

  // Read API key from environment (injected by OpenClaw, never from CLI args)
  const apiKey = process.env.AIRESEARCHOS_API_KEY
  if (apiKey && apiPath === '/api/v1') {
    headers['Authorization'] = `Bearer ${apiKey}`
  }

  // Check status
  const statusResponse = await fetch(statusUrl, { headers })

  if (!statusResponse.ok) {
    const body = await statusResponse.text()
    process.stdout.write(JSON.stringify({
      action: 'error',
      error: 'status_request_failed',
      httpStatus: statusResponse.status,
      body,
    }) + '\n')
    process.exit(1)
  }

  const data = await statusResponse.json()

  // Terminal: completed
  if (data.status === 'completed') {
    try {
      const outputResponse = await fetch(outputUrl, { headers })
      if (outputResponse.ok) {
        const report = await outputResponse.text()
        process.stdout.write(JSON.stringify({
          action: 'completed',
          id: requestId,
          report: JSON.parse(report),
        }) + '\n')
        process.exit(0)
      }
    } catch {
      // Fall back to inline report if output endpoint fails
    }

    // Inline fallback
    process.stdout.write(JSON.stringify({
      action: 'completed',
      id: requestId,
      report: data,
    }) + '\n')
    process.exit(0)
  }

  // Terminal: failed or timeout
  if (data.status === 'failed' || data.status === 'timeout') {
    process.stdout.write(JSON.stringify({
      action: 'failed',
      id: requestId,
      status: data.status,
      error: data.error || `Research ${data.status}`,
    }) + '\n')
    process.exit(1)
  }

  // Still processing
  process.stdout.write(JSON.stringify({
    action: 'pending',
    id: requestId,
    status: data.status,
    progress: data.progress || null,
    currentStep: data.currentStep || null,
  }) + '\n')
  process.exit(2)
}

main().catch((err) => {
  process.stdout.write(JSON.stringify({
    action: 'error',
    error: 'network_error',
    message: err.message || 'Unknown error',
  }) + '\n')
  process.exit(1)
})
