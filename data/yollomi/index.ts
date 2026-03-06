export type YollomiGenerateInput = {
  type: 'image' | 'video'
  modelId: string
  prompt?: string
  imageUrl?: string
  aspectRatio?: '1:1' | '16:9' | '9:16'
  numOutputs?: number
  // allow any additional model-specific fields
  [key: string]: unknown
}

export type YollomiGenerateOutput =
  | { images: string[]; remainingCredits?: number; [key: string]: unknown }
  | { video: string; remainingCredits?: number; [key: string]: unknown }

function requireEnv(name: string): string {
  const v = process.env[name]
  if (!v) throw new Error(`Missing required env: ${name}`)
  return v
}

function isHttpUrl(u: string): boolean {
  try {
    const url = new URL(u)
    return url.protocol === 'http:' || url.protocol === 'https:'
  } catch {
    return false
  }
}

async function fetchWithTimeout(input: RequestInfo, init: RequestInit, timeoutMs = 120000) {
  const controller = new AbortController()
  const t = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const resp = await fetch(input, { ...init, signal: controller.signal })
    return resp
  } finally {
    clearTimeout(t)
  }
}

export async function generate(params: YollomiGenerateInput): Promise<YollomiGenerateOutput> {
  const apiKey = requireEnv('YOLLOMI_API_KEY')
  const baseUrl = 'https://yollomi.com'

  if (params.type === "video") {
    throw new Error("Video generation is temporarily disabled. Please use image generation only.")
  }

  if (params.imageUrl && !isHttpUrl(params.imageUrl)) {
    throw new Error("imageUrl must be an http(s) URL")
  }

  const resp = await fetchWithTimeout(`${baseUrl}/api/v1/generate`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  })

  const text = await resp.text()
  if (!resp.ok) {
    // Keep errors readable; avoid dumping huge HTML.
    const snippet = text.length > 2000 ? text.slice(0, 2000) + '…' : text
    throw new Error(`Yollomi API error ${resp.status}: ${snippet}`)
  }

  try {
    return JSON.parse(text) as YollomiGenerateOutput
  } catch {
    throw new Error('Yollomi API returned non-JSON response')
  }
}

// OpenClaw tool export (convention)
export const tools = {
  'yollomi.generate': generate,
}
