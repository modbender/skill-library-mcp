#!/usr/bin/env node

/**
 * 环境变量配置 - 读取 .env / .env.local 获取 LLM 等配置
 */

import * as fs from 'fs'
import * as path from 'path'

const ROOT_DIR = path.join(__dirname, '..', '..')
const ENV_FILE = path.join(ROOT_DIR, '.env')
const ENV_LOCAL_FILE = path.join(ROOT_DIR, '.env.local')
const ENV_EXAMPLE_FILE = path.join(ROOT_DIR, '.env.example')

function parseEnvFile(filePath: string): Record<string, string> {
  const result: Record<string, string> = {}
  if (!fs.existsSync(filePath)) return result
  try {
    const content = fs.readFileSync(filePath, 'utf-8')
    for (const line of content.split('\n')) {
      const trimmed = line.trim()
      if (trimmed && !trimmed.startsWith('#')) {
        const eq = trimmed.indexOf('=')
        if (eq > 0) {
          const key = trimmed.slice(0, eq).trim()
          let val = trimmed.slice(eq + 1).trim()
          if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
            val = val.slice(1, -1)
          }
          result[key] = val
        }
      }
    }
  } catch {
    // ignore
  }
  return result
}

/**
 * 加载 .env 和 .env.local（.env.local 优先），若无则尝试 .env.example
 */
export function loadEnv(): Record<string, string> {
  const env = parseEnvFile(ENV_FILE)
  const local = parseEnvFile(ENV_LOCAL_FILE)
  const example = parseEnvFile(ENV_EXAMPLE_FILE)
  const proc: Record<string, string> = {}
  for (const [k, v] of Object.entries(process.env)) {
    if (v !== undefined) proc[k] = v
  }
  return { ...example, ...env, ...local, ...proc }
}

export interface LLMEnvConfig {
  provider: string
  apiKey: string
  baseUrl: string
  model: string
  temperature: number
  maxTokens: number
}

/**
 * 从 env 获取 LLM 配置（优先 .env，其次 .env.example）
 */
export function getLLMConfigFromEnv(): LLMEnvConfig {
  const env = loadEnv()
  return {
    provider: env.LLM_PROVIDER || 'deepseek',
    apiKey: env.LLM_API_KEY || env.DEEPSEEK_API_KEY || env.OPENAI_API_KEY || env.CLAUDE_API_KEY || env.GEMINI_API_KEY || '',
    baseUrl: env.LLM_BASE_URL || 'https://api.deepseek.com',
    model: env.LLM_MODEL || env.DEEPSEEK_MODAL || env.GEMINI_MODAL || 'DeepSeek-V3.2',
    temperature: parseFloat(env.LLM_TEMPERATURE || '0.8') || 0.8,
    maxTokens: parseInt(env.LLM_MAX_TOKENS || '500', 10) || 500,
  }
}
