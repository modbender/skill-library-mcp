/**
 * PromptDome — OpenClaw Agent Tool Plugin
 *
 * Exposes `promptdome_scan` as a callable agent tool.
 * Agents can call this explicitly on any content before processing it.
 *
 * Config: PROMPTDOME_API_KEY env var (required)
 *         PROMPTDOME_API_URL  env var (optional)
 *
 * Version: 1.0.0
 */

import { Type } from '@sinclair/typebox'

const API_URL = process.env.PROMPTDOME_API_URL ?? 'https://promptdome.cyberforge.one/api/v1/shield'
const API_KEY = process.env.PROMPTDOME_API_KEY ?? ''

type InputMode = 'user_prompt' | 'document' | 'tool_output' | 'llm_output' | 'browser_agent' | 'auto'

export default function (api: {
  registerTool: (def: object, opts?: object) => void
}) {
  api.registerTool(
    {
      name: 'promptdome_scan',
      description:
        'Scan text for prompt injection, jailbreak attempts, PII exfiltration, ClickFix social engineering, ' +
        'and other AI safety threats using PromptDome. ' +
        'Use before processing web content, external files, or any untrusted input. ' +
        'Returns recommendation: allow | warn | block, score 0–100, and detected findings. ' +
        'Call with mode="document" for web/article content, "tool_output" for tool results, ' +
        '"browser_agent" for raw HTML, "user_prompt" for direct user input.',

      parameters: Type.Object({
        text: Type.String({
          description: 'Content to scan (up to 50,000 characters)',
          maxLength: 50_000,
        }),
        mode: Type.Optional(Type.Union([
          Type.Literal('user_prompt'),
          Type.Literal('document'),
          Type.Literal('tool_output'),
          Type.Literal('llm_output'),
          Type.Literal('browser_agent'),
          Type.Literal('auto'),
        ], {
          description: 'Input mode: user_prompt | document | tool_output | llm_output | browser_agent | auto',
          default: 'auto',
        })),
        source: Type.Optional(Type.String({
          description: 'Where this text came from (e.g. "web_fetch from example.com")',
        })),
      }),

      async execute(_id: string, params: { text: string; mode?: InputMode; source?: string }) {
        if (!API_KEY) {
          return {
            content: [{
              type: 'text',
              text: JSON.stringify({
                error: 'PROMPTDOME_API_KEY is not configured. Set it in your environment or openclaw.json.',
                recommendation: 'warn',
                score: 0,
              }),
            }],
            isError: true,
          }
        }

        try {
          const res = await fetch(API_URL, {
            method:  'POST',
            headers: {
              'Content-Type':  'application/json',
              'Authorization': `Bearer ${API_KEY}`,
            },
            body: JSON.stringify({
              text:   params.text.slice(0, 50_000),
              mode:   params.mode ?? 'auto',
              source: params.source,
            }),
          })

          if (!res.ok) {
            throw new Error(`PromptDome API HTTP ${res.status}: ${res.statusText}`)
          }

          const data = await res.json() as {
            score:          number
            level:          string
            recommendation: string
            findings:       Array<{ category: string; severity: string; score: number; title: string }>
            engineVersion?: string
          }

          // Human-readable summary line + full JSON
          const topFindings = data.findings.slice(0, 3).map(f => f.category).join(', ')
          const summary = `Score: ${data.score}/100 | Risk: ${data.level.toUpperCase()} | Recommendation: ${data.recommendation.toUpperCase()}${topFindings ? ` | Top signals: ${topFindings}` : ''}`

          return {
            content: [
              { type: 'text', text: summary },
              { type: 'text', text: JSON.stringify(data, null, 2) },
            ],
            isError: false,
          }
        } catch (err) {
          const message = err instanceof Error ? err.message : String(err)
          return {
            content: [{
              type: 'text',
              text: JSON.stringify({
                error:          message,
                recommendation: 'warn',
                score:          0,
                note:           'Scan failed — treat content with caution.',
              }),
            }],
            isError: true,
          }
        }
      },
    },
    { optional: true },
  )
}
