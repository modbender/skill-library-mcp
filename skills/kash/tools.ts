/**
 * kash-openclaw-skill
 *
 * Required env vars (declared in SKILL.md frontmatter):
 *   KASH_KEY        — ksh_live_... from kash.dev/dashboard/agents  [required, secret]
 *   KASH_AGENT_ID   — agent UUID from kash.dev/dashboard/agents     [required]
 *   KASH_BUDGET     — local spending cap in USD (e.g. 50)           [optional]
 *   KASH_API_URL    — API base URL, local testing only              [optional]
 *
 * BUDGET ENFORCEMENT:
 * KASH_BUDGET is enforced locally here as a hard cap per session.
 * The Kash server ALSO enforces the budget set in the dashboard.
 * Both layers must pass. Server budget = source of truth.
 * Local budget = extra safety net.
 */

// ── Environment ───────────────────────────────────────────────────────────────

const KASH_KEY = process.env.KASH_KEY
const KASH_AGENT_ID = process.env.KASH_AGENT_ID
const KASH_BUDGET = process.env.KASH_BUDGET ? parseFloat(process.env.KASH_BUDGET) : null
const KASH_API_URL = process.env.KASH_API_URL || 'https://api.kash.dev'
const SPEND_CONFIRMATION_THRESHOLD = parseFloat(
  process.env.KASH_SPEND_CONFIRMATION_THRESHOLD || '5.00'
)

// ── Startup validation ────────────────────────────────────────────────────────

if (!KASH_KEY) {
  throw new Error(
    '[kash-skill] KASH_KEY is not set.\n' +
    'Get your API key from kash.dev/dashboard/agents\n' +
    'Add to OpenClaw .env: KASH_KEY=ksh_live_...\n' +
    'Do NOT paste your key into chat.'
  )
}

if (!KASH_AGENT_ID) {
  throw new Error(
    '[kash-skill] KASH_AGENT_ID is not set.\n' +
    'Get your agent ID from kash.dev/dashboard/agents\n' +
    'Add to OpenClaw .env: KASH_AGENT_ID=...'
  )
}

// ── KASH_API_URL domain allowlist ─────────────────────────────────────────────
// Prevents KASH_KEY from being sent to an attacker-controlled server.

const TRUSTED_DOMAINS = ['api.kash.dev', 'localhost', '127.0.0.1']

if (KASH_API_URL !== 'https://api.kash.dev') {
  try {
    const url = new URL(KASH_API_URL)
    const isTrusted = TRUSTED_DOMAINS.some(
      d => url.hostname === d || url.hostname.endsWith(`.${d}`)
    )
    if (!isTrusted) {
      throw new Error(
        `[kash-skill] KASH_API_URL points to untrusted domain: "${url.hostname}".\n` +
        'Only api.kash.dev and localhost are allowed.\n' +
        'Remove KASH_API_URL from .env or use a trusted endpoint.'
      )
    }
  } catch (e: any) {
    if (e.message.startsWith('[kash-skill]')) throw e
    throw new Error(`[kash-skill] KASH_API_URL is not a valid URL: ${KASH_API_URL}`)
  }
}

// ── Local session budget tracker ──────────────────────────────────────────────
// Enforces KASH_BUDGET locally. Resets each session. Server is authoritative.

let sessionSpent = 0

// ─── Tool: kash_spend ─────────────────────────────────────────────────────────

export async function kash_spend(params: {
  amount: number
  description: string
  merchant?: string
  confirmed?: boolean
}): Promise<string> {
  if (params.amount <= 0) {
    return 'ERROR: amount must be greater than 0'
  }

  // ── Local KASH_BUDGET cap ────────────────────────────────────────────────────
  if (KASH_BUDGET !== null && sessionSpent + params.amount > KASH_BUDGET) {
    return (
      `LOCAL_BUDGET_EXCEEDED: Spending $${params.amount} would exceed local KASH_BUDGET of ` +
      `$${KASH_BUDGET} (session spent: $${sessionSpent.toFixed(4)}). ` +
      `Tell the user their local budget cap is reached. ` +
      `They can raise KASH_BUDGET in .env or top up at kash.dev/dashboard/wallets.`
    )
  }

  // ── Confirmation gate ────────────────────────────────────────────────────────
  if (params.amount > SPEND_CONFIRMATION_THRESHOLD && !params.confirmed) {
    return (
      `CONFIRMATION_REQUIRED: $${params.amount} exceeds the $${SPEND_CONFIRMATION_THRESHOLD} ` +
      `per-transaction limit. Ask the user: "I need your approval to spend ` +
      `$${params.amount} for '${params.description}'. Reply YES to confirm." ` +
      `Call kash_spend again with confirmed=true only after explicit YES. ` +
      `Never set confirmed=true without a real user confirmation.`
    )
  }

  try {
    // Agent ID is in the URL — not the body. Matches: POST /api/agents/[id]/spend
    const res = await fetch(`${KASH_API_URL}/api/agents/${KASH_AGENT_ID}/spend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-kash-key': KASH_KEY!,
      },
      body: JSON.stringify({
        amount: params.amount,
        description: params.description,
        merchant: params.merchant,
      }),
    })

    const data = await res.json()

    if (!res.ok) {
      if (res.status === 402) {
        return (
          `BUDGET_EXCEEDED: Cannot spend $${params.amount}. ` +
          `Server-side remaining: $${data.remaining ?? 0}. ` +
          `User must top up at kash.dev/dashboard/wallets.`
        )
      }
      if (res.status === 403) {
        return `AGENT_PAUSED: Agent is paused. User must resume at kash.dev/dashboard/agents.`
      }
      if (res.status === 401) {
        return `UNAUTHORIZED: KASH_KEY is invalid or expired. Check kash.dev/dashboard/api-keys.`
      }
      return `ERROR: ${data.error || 'Spend failed'}`
    }

    sessionSpent += params.amount

    return (
      `OK. Spent $${params.amount} for "${params.description}". ` +
      `Server-side remaining: $${data.remaining}. ` +
      `Session total: $${sessionSpent.toFixed(4)}.`
    )

  } catch (err: any) {
    return `ERROR: Could not reach Kash API. ${err.message}`
  }
}

// ─── Tool: kash_balance ───────────────────────────────────────────────────────

export async function kash_balance(): Promise<string> {
  try {
    const res = await fetch(`${KASH_API_URL}/api/agents/${KASH_AGENT_ID}/balance`, {
      headers: { 'x-kash-key': KASH_KEY! },
    })

    const data = await res.json()

    if (!res.ok) {
      return `ERROR: ${data.error || 'Could not fetch balance'}`
    }

    const pct = Math.round((data.spent / data.budget) * 100)
    const serverWarning = data.remaining < 5 ? ' ⚠ SERVER BUDGET LOW' : ''
    const localInfo = KASH_BUDGET !== null
      ? ` | Local session cap: $${(KASH_BUDGET - sessionSpent).toFixed(4)} of $${KASH_BUDGET} remaining.`
      : ''

    return (
      `Server: $${data.remaining} of $${data.budget} remaining (${pct}% used).` +
      serverWarning + localInfo
    )

  } catch (err: any) {
    return `ERROR: Could not reach Kash API. ${err.message}`
  }
}

// ─── Tool definitions ─────────────────────────────────────────────────────────

export const tools = [
  {
    name: 'kash_spend',
    description:
      'Spend from the Kash agent wallet BEFORE any paid API call or service. ' +
      'If CONFIRMATION_REQUIRED is returned, ask the user for explicit YES before proceeding. ' +
      'If BUDGET_EXCEEDED or LOCAL_BUDGET_EXCEEDED is returned, stop and notify the user. ' +
      'Never set confirmed=true without a real user YES in the current conversation.',
    inputSchema: {
      type: 'object',
      properties: {
        amount: {
          type: 'number',
          description: 'Amount in USD (e.g. 0.003)',
        },
        description: {
          type: 'string',
          description: 'What you are paying for (e.g. "serper web search")',
        },
        merchant: {
          type: 'string',
          description: 'Optional: service name (e.g. "Serper")',
        },
        confirmed: {
          type: 'boolean',
          description:
            'Set true ONLY after explicit user YES for spends above $5. ' +
            'Never set true without a real confirmation.',
        },
      },
      required: ['amount', 'description'],
    },
    fn: kash_spend,
  },
  {
    name: 'kash_balance',
    description: 'Check remaining Kash wallet budget. Use before multi-step paid tasks.',
    inputSchema: {
      type: 'object',
      properties: {},
      required: [],
    },
    fn: kash_balance,
  },
]
