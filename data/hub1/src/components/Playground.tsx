'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Memory {
  id: string
  content: string
  type: string
  relevance?: number
  createdAt: string
}

// Demo memories for playground
const demoMemories: Memory[] = [
  { id: '1', content: 'User prefers TypeScript over JavaScript', type: 'preference', createdAt: new Date().toISOString() },
  { id: '2', content: 'Project uses Next.js 14 with App Router', type: 'fact', createdAt: new Date().toISOString() },
  { id: '3', content: 'Decided to use PostgreSQL for the database', type: 'decision', createdAt: new Date().toISOString() },
  { id: '4', content: 'API rate limits are 100 requests per minute', type: 'learning', createdAt: new Date().toISOString() },
]

export default function Playground() {
  const [mode, setMode] = useState<'store' | 'recall'>('store')
  const [input, setInput] = useState('')
  const [memoryType, setMemoryType] = useState('fact')
  const [memories, setMemories] = useState<Memory[]>(demoMemories)
  const [results, setResults] = useState<Memory[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)

  const handleStore = async () => {
    if (!input.trim()) return
    setIsLoading(true)

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800))

    const newMemory: Memory = {
      id: Date.now().toString(),
      content: input,
      type: memoryType,
      createdAt: new Date().toISOString(),
    }

    setMemories(prev => [newMemory, ...prev])
    setInput('')
    setIsLoading(false)
    setShowSuccess(true)
    setTimeout(() => setShowSuccess(false), 2000)
  }

  const handleRecall = async () => {
    if (!input.trim()) return
    setIsLoading(true)

    // Simulate semantic search
    await new Promise(resolve => setTimeout(resolve, 600))

    const query = input.toLowerCase()
    const searchResults = memories
      .map(m => ({
        ...m,
        relevance: calculateRelevance(m.content.toLowerCase(), query)
      }))
      .filter(m => m.relevance > 0.3)
      .sort((a, b) => (b.relevance || 0) - (a.relevance || 0))
      .slice(0, 5)

    setResults(searchResults)
    setIsLoading(false)
  }

  const calculateRelevance = (content: string, query: string): number => {
    const words = query.split(' ')
    let matches = 0
    words.forEach(word => {
      if (content.includes(word)) matches++
    })
    return matches / words.length
  }

  return (
    <section className="py-32 border-t border-white/5">
      <div className="max-w-4xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <span className="text-xs font-medium tracking-widest text-zinc-500 uppercase">Try It Now</span>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold text-white">
            Playground
          </h2>
          <p className="mt-4 text-zinc-500">
            Experience agent memory in seconds. No signup required.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="bg-gradient-to-b from-white/[0.03] to-transparent border border-white/10 rounded-2xl overflow-hidden"
        >
          {/* Mode Toggle */}
          <div className="flex border-b border-white/5">
            <button
              onClick={() => { setMode('store'); setResults([]); }}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-all ${
                mode === 'store'
                  ? 'text-white bg-white/5'
                  : 'text-zinc-500 hover:text-white'
              }`}
            >
              Store Memory
            </button>
            <button
              onClick={() => { setMode('recall'); setResults([]); }}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-all ${
                mode === 'recall'
                  ? 'text-white bg-white/5'
                  : 'text-zinc-500 hover:text-white'
              }`}
            >
              Recall Memory
            </button>
          </div>

          <div className="p-6">
            {mode === 'store' ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs text-zinc-500 mb-2">Memory Content</label>
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="e.g., User prefers dark mode for all interfaces"
                    className="w-full h-24 px-4 py-3 bg-black/50 border border-white/10 rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-white/30 transition-colors resize-none"
                  />
                </div>
                <div>
                  <label className="block text-xs text-zinc-500 mb-2">Memory Type</label>
                  <div className="flex flex-wrap gap-2">
                    {['fact', 'preference', 'decision', 'learning'].map((type) => (
                      <button
                        key={type}
                        onClick={() => setMemoryType(type)}
                        className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                          memoryType === type
                            ? 'bg-white text-black'
                            : 'bg-white/5 text-zinc-400 hover:bg-white/10'
                        }`}
                      >
                        {type}
                      </button>
                    ))}
                  </div>
                </div>
                <button
                  onClick={handleStore}
                  disabled={isLoading || !input.trim()}
                  className="w-full py-3 bg-white text-black font-semibold rounded-xl hover:bg-zinc-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Storing...' : 'Store Memory'}
                </button>

                <AnimatePresence>
                  {showSuccess && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      className="flex items-center justify-center gap-2 text-emerald-400 text-sm"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Memory stored successfully!
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs text-zinc-500 mb-2">Search Query</label>
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleRecall()}
                    placeholder="e.g., What are the user's preferences?"
                    className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-white/30 transition-colors"
                  />
                </div>
                <button
                  onClick={handleRecall}
                  disabled={isLoading || !input.trim()}
                  className="w-full py-3 bg-white text-black font-semibold rounded-xl hover:bg-zinc-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Searching...' : 'Recall Memories'}
                </button>

                <AnimatePresence>
                  {results.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="space-y-2 pt-4 border-t border-white/5"
                    >
                      <div className="text-xs text-zinc-500 mb-3">{results.length} memories found</div>
                      {results.map((memory) => (
                        <motion.div
                          key={memory.id}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          className="p-4 bg-black/30 border border-white/5 rounded-xl"
                        >
                          <div className="flex items-start justify-between gap-4">
                            <p className="text-sm text-white">{memory.content}</p>
                            <span className="text-xs text-emerald-400 whitespace-nowrap">
                              {Math.round((memory.relevance || 0) * 100)}%
                            </span>
                          </div>
                          <div className="mt-2 flex items-center gap-2">
                            <span className="px-2 py-0.5 text-xs bg-white/5 text-zinc-400 rounded">
                              {memory.type}
                            </span>
                          </div>
                        </motion.div>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}
          </div>

          {/* Stored Memories Preview */}
          <div className="px-6 pb-6">
            <div className="text-xs text-zinc-500 mb-3">{memories.length} memories in vault</div>
            <div className="flex flex-wrap gap-2">
              {memories.slice(0, 6).map((memory) => (
                <div
                  key={memory.id}
                  className="px-3 py-1.5 text-xs bg-white/5 text-zinc-400 rounded-lg truncate max-w-[200px]"
                >
                  {memory.content}
                </div>
              ))}
              {memories.length > 6 && (
                <div className="px-3 py-1.5 text-xs bg-white/5 text-zinc-500 rounded-lg">
                  +{memories.length - 6} more
                </div>
              )}
            </div>
          </div>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-6 text-center text-sm text-zinc-600"
        >
          This is a demo. Connect your wallet to use real persistent memory.
        </motion.p>
      </div>
    </section>
  )
}
