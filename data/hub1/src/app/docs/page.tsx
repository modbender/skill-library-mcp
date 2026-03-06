'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import Logo from '@/components/Logo'

const codeExamples = {
  curl: {
    store: `curl -X POST https://openclawdy.xyz/api/memory/store \\
  -H "X-Agent-Address: 0xYourWallet" \\
  -H "X-Agent-Signature: 0xSignature" \\
  -H "X-Agent-Timestamp: 1234567890" \\
  -H "Content-Type: application/json" \\
  -d '{
    "content": "User prefers TypeScript",
    "type": "preference"
  }'`,
    recall: `curl -X POST https://openclawdy.xyz/api/memory/recall \\
  -H "X-Agent-Address: 0xYourWallet" \\
  -H "X-Agent-Signature: 0xSignature" \\
  -H "X-Agent-Timestamp: 1234567890" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "programming preferences",
    "limit": 5
  }'`,
  },
  typescript: {
    store: `import { createWalletClient, http } from 'viem'
import { privateKeyToAccount } from 'viem/accounts'
import { base } from 'viem/chains'

const account = privateKeyToAccount('0xYourPrivateKey')
const timestamp = Date.now().toString()
const message = \`OpenClawdy Auth\\nTimestamp: \${timestamp}\`

const signature = await account.signMessage({ message })

const response = await fetch('https://openclawdy.xyz/api/memory/store', {
  method: 'POST',
  headers: {
    'X-Agent-Address': account.address,
    'X-Agent-Signature': signature,
    'X-Agent-Timestamp': timestamp,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content: 'User prefers TypeScript',
    type: 'preference',
  }),
})

const data = await response.json()
console.log(data)`,
    recall: `const response = await fetch('https://openclawdy.xyz/api/memory/recall', {
  method: 'POST',
  headers: {
    'X-Agent-Address': account.address,
    'X-Agent-Signature': signature,
    'X-Agent-Timestamp': timestamp,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'programming preferences',
    limit: 5,
  }),
})

const data = await response.json()
// Returns memories sorted by relevance
data.data.forEach(memory => {
  console.log(\`[\${memory.relevance}] \${memory.content}\`)
})`,
  },
  python: {
    store: `import requests
from eth_account import Account
from eth_account.messages import encode_defunct
import time

private_key = "0xYourPrivateKey"
account = Account.from_key(private_key)

timestamp = str(int(time.time() * 1000))
message = f"OpenClawdy Auth\\nTimestamp: {timestamp}"
signature = account.sign_message(encode_defunct(text=message))

response = requests.post(
    "https://openclawdy.xyz/api/memory/store",
    headers={
        "X-Agent-Address": account.address,
        "X-Agent-Signature": signature.signature.hex(),
        "X-Agent-Timestamp": timestamp,
        "Content-Type": "application/json",
    },
    json={
        "content": "User prefers TypeScript",
        "type": "preference",
    }
)

print(response.json())`,
    recall: `response = requests.post(
    "https://openclawdy.xyz/api/memory/recall",
    headers={
        "X-Agent-Address": account.address,
        "X-Agent-Signature": signature.signature.hex(),
        "X-Agent-Timestamp": timestamp,
        "Content-Type": "application/json",
    },
    json={
        "query": "programming preferences",
        "limit": 5,
    }
)

data = response.json()
for memory in data["data"]:
    print(f"[{memory['relevance']}] {memory['content']}")`,
  },
}

export default function DocsPage() {
  const [selectedLang, setSelectedLang] = useState<'curl' | 'typescript' | 'python'>('typescript')
  const [copiedCode, setCopiedCode] = useState<string | null>(null)

  const copyCode = (code: string, id: string) => {
    navigator.clipboard.writeText(code)
    setCopiedCode(id)
    setTimeout(() => setCopiedCode(null), 2000)
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-white/5 bg-black/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <a href="/">
            <Logo />
          </a>
          <nav className="flex items-center gap-6">
            <a href="/" className="text-sm text-zinc-400 hover:text-white transition-colors">Home</a>
            <a href="/dashboard" className="text-sm text-zinc-400 hover:text-white transition-colors">Dashboard</a>
            <a href="https://x.com/openclawdy" target="_blank" className="text-sm text-zinc-400 hover:text-white transition-colors">Twitter</a>
          </nav>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-4xl font-bold mb-4">Documentation</h1>
          <p className="text-zinc-500 mb-12">
            Learn how to integrate OpenClawdy into your agents.
          </p>

          {/* Quick Start */}
          <section className="mb-16">
            <h2 className="text-2xl font-semibold mb-6">Quick Start</h2>

            <div className="space-y-6">
              <div className="p-6 bg-white/[0.02] border border-white/5 rounded-xl">
                <h3 className="font-medium mb-3">1. Authentication</h3>
                <p className="text-zinc-500 text-sm mb-4">
                  OpenClawdy uses wallet signatures for authentication. Sign a message with your agent&apos;s wallet to authenticate requests.
                </p>
                <pre className="p-4 bg-black rounded-lg text-sm text-zinc-400 overflow-x-auto">
{`Message format:
OpenClawdy Auth
Timestamp: {unix_timestamp_ms}`}
                </pre>
              </div>

              <div className="p-6 bg-white/[0.02] border border-white/5 rounded-xl">
                <h3 className="font-medium mb-3">2. Required Headers</h3>
                <pre className="p-4 bg-black rounded-lg text-sm text-zinc-400 overflow-x-auto">
{`X-Agent-Address: 0x...      # Your wallet address
X-Agent-Signature: 0x...    # Signed message
X-Agent-Timestamp: 123...   # Timestamp used in message`}
                </pre>
              </div>
            </div>
          </section>

          {/* Code Examples */}
          <section className="mb-16">
            <h2 className="text-2xl font-semibold mb-6">Code Examples</h2>

            {/* Language Selector */}
            <div className="flex gap-2 mb-6">
              {(['typescript', 'python', 'curl'] as const).map((lang) => (
                <button
                  key={lang}
                  onClick={() => setSelectedLang(lang)}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                    selectedLang === lang
                      ? 'bg-white text-black'
                      : 'bg-white/5 text-zinc-400 hover:bg-white/10'
                  }`}
                >
                  {lang === 'typescript' ? 'TypeScript' : lang === 'python' ? 'Python' : 'cURL'}
                </button>
              ))}
            </div>

            <div className="space-y-6">
              {/* Store Example */}
              <div className="border border-white/5 rounded-xl overflow-hidden">
                <div className="flex items-center justify-between px-4 py-3 bg-white/[0.02] border-b border-white/5">
                  <span className="text-sm font-medium">Store Memory</span>
                  <button
                    onClick={() => copyCode(codeExamples[selectedLang].store, 'store')}
                    className="text-xs text-zinc-500 hover:text-white transition-colors"
                  >
                    {copiedCode === 'store' ? 'Copied!' : 'Copy'}
                  </button>
                </div>
                <pre className="p-4 bg-black text-sm text-zinc-400 overflow-x-auto">
                  {codeExamples[selectedLang].store}
                </pre>
              </div>

              {/* Recall Example */}
              <div className="border border-white/5 rounded-xl overflow-hidden">
                <div className="flex items-center justify-between px-4 py-3 bg-white/[0.02] border-b border-white/5">
                  <span className="text-sm font-medium">Recall Memory</span>
                  <button
                    onClick={() => copyCode(codeExamples[selectedLang].recall, 'recall')}
                    className="text-xs text-zinc-500 hover:text-white transition-colors"
                  >
                    {copiedCode === 'recall' ? 'Copied!' : 'Copy'}
                  </button>
                </div>
                <pre className="p-4 bg-black text-sm text-zinc-400 overflow-x-auto">
                  {codeExamples[selectedLang].recall}
                </pre>
              </div>
            </div>
          </section>

          {/* API Reference */}
          <section className="mb-16">
            <h2 className="text-2xl font-semibold mb-6">API Reference</h2>

            <div className="border border-white/5 rounded-xl overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/5 bg-white/[0.02]">
                    <th className="px-4 py-3 text-left text-xs font-medium text-zinc-500 uppercase">Method</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-zinc-500 uppercase">Endpoint</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-zinc-500 uppercase">Description</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {[
                    ['POST', '/api/memory/store', 'Store a new memory'],
                    ['POST', '/api/memory/recall', 'Semantic search memories'],
                    ['GET', '/api/memory/list', 'List all memories'],
                    ['GET', '/api/memory/{id}', 'Get specific memory'],
                    ['DELETE', '/api/memory/{id}', 'Delete a memory'],
                    ['GET', '/api/memory/vault', 'Export all memories'],
                    ['DELETE', '/api/memory/vault', 'Clear entire vault'],
                    ['GET', '/api/agent/stats', 'Usage statistics'],
                  ].map(([method, path, desc], i) => (
                    <tr key={i}>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 text-xs font-medium rounded ${
                          method === 'POST' ? 'bg-blue-400/10 text-blue-400' :
                          method === 'DELETE' ? 'bg-red-400/10 text-red-400' :
                          'bg-emerald-400/10 text-emerald-400'
                        }`}>
                          {method}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-mono text-sm text-zinc-300">{path}</td>
                      <td className="px-4 py-3 text-sm text-zinc-500">{desc}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Memory Types */}
          <section className="mb-16">
            <h2 className="text-2xl font-semibold mb-6">Memory Types</h2>

            <div className="grid sm:grid-cols-2 gap-4">
              {[
                { type: 'fact', desc: 'Objective information', example: 'Project uses Next.js 14' },
                { type: 'preference', desc: 'User/agent preferences', example: 'User prefers dark mode' },
                { type: 'decision', desc: 'Past decisions made', example: 'Chose PostgreSQL over MongoDB' },
                { type: 'learning', desc: 'Lessons learned', example: 'This API requires auth header' },
                { type: 'history', desc: 'Historical events', example: 'Deployed v2.1 on Jan 15' },
                { type: 'context', desc: 'General context', example: 'Working on e-commerce project' },
              ].map((item) => (
                <div key={item.type} className="p-4 bg-white/[0.02] border border-white/5 rounded-xl">
                  <div className="font-medium text-white mb-1">{item.type}</div>
                  <div className="text-sm text-zinc-500 mb-2">{item.desc}</div>
                  <div className="text-xs text-zinc-600 italic">&quot;{item.example}&quot;</div>
                </div>
              ))}
            </div>
          </section>

          {/* OpenClaw Skill */}
          <section>
            <h2 className="text-2xl font-semibold mb-6">OpenClaw Skill</h2>

            <div className="p-6 bg-white/[0.02] border border-white/5 rounded-xl">
              <p className="text-zinc-500 mb-4">
                Install OpenClawdy as an OpenClaw skill for seamless integration:
              </p>
              <pre className="p-4 bg-black rounded-lg text-sm text-emerald-400 overflow-x-auto">
                openclaw skill install openclawdy
              </pre>
              <p className="mt-4 text-sm text-zinc-600">
                Or add to your agent config:
              </p>
              <pre className="mt-2 p-4 bg-black rounded-lg text-sm text-zinc-400 overflow-x-auto">
{`skills:
  - url: https://openclawdy.xyz/SKILL.md
    name: openclawdy`}
              </pre>
            </div>
          </section>
        </motion.div>
      </div>
    </div>
  )
}
