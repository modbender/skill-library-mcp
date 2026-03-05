'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ConnectButton } from '@rainbow-me/rainbowkit'
import { useAccount, useSignMessage } from 'wagmi'
import Logo from '@/components/Logo'

interface Memory {
  id: string
  content: string
  type: string
  tags: string[]
  createdAt: string
}

interface AgentStats {
  address: string
  tier: string
  memoriesStored: number
  recallsToday: number
  limits: {
    maxMemories: number
    maxRecallsPerDay: number
  }
}

interface Session {
  token: string
  expiresAt: number
  address: string
}

const STORAGE_KEY_SESSION = 'openclawdy_session'
const STORAGE_KEY_MEMORIES = 'openclawdy_memories'
const STORAGE_KEY_STATS = 'openclawdy_stats'

// Session management
function getSession(address: string): Session | null {
  if (typeof window === 'undefined') return null
  try {
    const stored = localStorage.getItem(STORAGE_KEY_SESSION)
    if (!stored) return null
    const session = JSON.parse(stored) as Session
    // Validate session is for this address and not expired
    if (session.address?.toLowerCase() !== address?.toLowerCase()) return null
    if (session.expiresAt < Date.now()) return null
    return session
  } catch {
    return null
  }
}

function saveSession(session: Session): void {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(STORAGE_KEY_SESSION, JSON.stringify(session))
  } catch {}
}

function clearSession(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(STORAGE_KEY_SESSION)
}

// Cache management
function getCachedMemories(address: string): Memory[] {
  if (typeof window === 'undefined') return []
  try {
    const stored = localStorage.getItem(`${STORAGE_KEY_MEMORIES}_${address.toLowerCase()}`)
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

function saveCachedMemories(address: string, memories: Memory[]): void {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(`${STORAGE_KEY_MEMORIES}_${address.toLowerCase()}`, JSON.stringify(memories))
  } catch {}
}

function getCachedStats(address: string): AgentStats | null {
  if (typeof window === 'undefined') return null
  try {
    const stored = localStorage.getItem(`${STORAGE_KEY_STATS}_${address.toLowerCase()}`)
    return stored ? JSON.parse(stored) : null
  } catch {
    return null
  }
}

function saveCachedStats(address: string, stats: AgentStats): void {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(`${STORAGE_KEY_STATS}_${address.toLowerCase()}`, JSON.stringify(stats))
  } catch {}
}

export default function Dashboard() {
  const { address, isConnected } = useAccount()
  const { signMessageAsync } = useSignMessage()

  const [session, setSession] = useState<Session | null>(null)
  const [memories, setMemories] = useState<Memory[]>([])
  const [stats, setStats] = useState<AgentStats | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isSigningIn, setIsSigningIn] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<string | null>(null)
  const [newMemory, setNewMemory] = useState('')
  const [newMemoryType, setNewMemoryType] = useState('fact')
  const [showAddModal, setShowAddModal] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const initRef = useRef(false)

  // Initialize on wallet connect
  useEffect(() => {
    if (!isConnected || !address) {
      setSession(null)
      setMemories([])
      setStats(null)
      initRef.current = false
      return
    }

    if (initRef.current) return
    initRef.current = true

    // Load cached data immediately
    const cachedMemories = getCachedMemories(address)
    const cachedStats = getCachedStats(address)
    if (cachedMemories.length > 0) setMemories(cachedMemories)
    if (cachedStats) setStats(cachedStats)

    // Check for existing session
    const existingSession = getSession(address)
    if (existingSession) {
      setSession(existingSession)
      // Fetch fresh data with existing session
      fetchDataWithSession(existingSession)
    } else {
      // Need to create new session
      createSession()
    }
  }, [address, isConnected])

  // Create session (sign once)
  const createSession = async () => {
    if (!address) return

    setIsSigningIn(true)
    setError(null)

    try {
      const timestamp = Date.now().toString()
      const message = `OpenClawdy Auth\nTimestamp: ${timestamp}`

      const signature = await signMessageAsync({ message })

      const res = await fetch('/api/auth/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address, signature, timestamp }),
      })

      const data = await res.json()

      if (data.success) {
        const newSession: Session = {
          token: data.data.token,
          expiresAt: data.data.expiresAt,
          address: address.toLowerCase(),
        }
        saveSession(newSession)
        setSession(newSession)

        // Update stats from session response
        if (data.data.agent) {
          const newStats: AgentStats = {
            address: data.data.agent.address,
            tier: data.data.agent.tier,
            memoriesStored: data.data.agent.memoriesStored,
            recallsToday: data.data.agent.recallsToday,
            limits: { maxMemories: 1000, maxRecallsPerDay: 100 },
          }
          setStats(newStats)
          saveCachedStats(address, newStats)
        }

        // Fetch memories
        fetchDataWithSession(newSession)
      } else {
        setError(data.error || 'Failed to create session')
      }
    } catch (err) {
      // User rejected signature or other error
      setError('Sign in cancelled')
    }

    setIsSigningIn(false)
  }

  // Fetch data with session
  const fetchDataWithSession = async (sess: Session) => {
    if (!address) return

    setIsLoading(true)

    try {
      // Fetch memories
      const memoriesRes = await fetch('/api/memory/list', {
        headers: { Authorization: `Bearer ${sess.token}` },
      })
      const memoriesData = await memoriesRes.json()

      if (memoriesData.success) {
        setMemories(memoriesData.data || [])
        saveCachedMemories(address, memoriesData.data || [])
      } else if (memoriesRes.status === 401) {
        // Session expired, need to re-authenticate
        clearSession()
        setSession(null)
        createSession()
        return
      }

      // Fetch stats
      const statsRes = await fetch('/api/agent/stats', {
        headers: { Authorization: `Bearer ${sess.token}` },
      })
      const statsData = await statsRes.json()

      if (statsData.success) {
        setStats(statsData.data)
        saveCachedStats(address, statsData.data)
      }
    } catch {
      setError('Failed to load data')
    }

    setIsLoading(false)
  }

  // Store memory with optimistic UI
  const storeMemory = async () => {
    if (!newMemory.trim() || !session || !address) return

    const content = newMemory.trim()
    const type = newMemoryType

    // Optimistic update - show immediately
    const tempId = `temp-${Date.now()}`
    const optimisticMemory: Memory = {
      id: tempId,
      content,
      type,
      tags: [],
      createdAt: new Date().toISOString(),
    }

    // Instant UI update
    setMemories((prev) => [optimisticMemory, ...prev])
    setNewMemory('')
    setShowAddModal(false)
    if (stats) {
      setStats({ ...stats, memoriesStored: stats.memoriesStored + 1 })
    }

    // Background API call
    try {
      const res = await fetch('/api/memory/store', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.token}`,
        },
        body: JSON.stringify({ content, type }),
      })

      const data = await res.json()

      if (data.success) {
        // Replace optimistic entry with real data
        setMemories((prev) => {
          const updated = prev.map((m) => (m.id === tempId ? data.data : m))
          saveCachedMemories(address, updated)
          return updated
        })
        if (stats) {
          const updatedStats = { ...stats, memoriesStored: stats.memoriesStored + 1 }
          saveCachedStats(address, updatedStats)
        }
      } else if (res.status === 401) {
        // Rollback and handle session expiry
        setMemories((prev) => prev.filter((m) => m.id !== tempId))
        if (stats) setStats({ ...stats, memoriesStored: stats.memoriesStored })
        clearSession()
        setSession(null)
        setError('Session expired. Please sign in again.')
      } else {
        // Rollback on error
        setMemories((prev) => prev.filter((m) => m.id !== tempId))
        if (stats) setStats({ ...stats, memoriesStored: stats.memoriesStored })
        setError(data.error || 'Failed to store memory')
      }
    } catch {
      // Rollback on network error
      setMemories((prev) => prev.filter((m) => m.id !== tempId))
      if (stats) setStats({ ...stats, memoriesStored: stats.memoriesStored })
      setError('Failed to store memory')
    }
  }

  // Delete memory with optimistic UI
  const deleteMemory = async (id: string) => {
    if (!session || !address) return

    // Find the memory to delete (for potential rollback)
    const memoryToDelete = memories.find((m) => m.id === id)
    if (!memoryToDelete) return

    // Optimistic update - remove immediately
    setMemories((prev) => prev.filter((m) => m.id !== id))
    if (stats) {
      setStats({ ...stats, memoriesStored: Math.max(0, stats.memoriesStored - 1) })
    }

    // Background API call
    try {
      const res = await fetch(`/api/memory/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${session.token}` },
      })

      const data = await res.json()

      if (data.success) {
        // Persist to cache
        setMemories((prev) => {
          saveCachedMemories(address, prev)
          return prev
        })
        if (stats) {
          const updatedStats = { ...stats, memoriesStored: Math.max(0, stats.memoriesStored - 1) }
          saveCachedStats(address, updatedStats)
        }
      } else if (res.status === 401) {
        // Rollback and handle session expiry
        setMemories((prev) => [memoryToDelete, ...prev])
        if (stats) setStats({ ...stats, memoriesStored: stats.memoriesStored })
        clearSession()
        setSession(null)
        setError('Session expired. Please sign in again.')
      } else {
        // Rollback on error
        setMemories((prev) => [memoryToDelete, ...prev])
        if (stats) setStats({ ...stats, memoriesStored: stats.memoriesStored })
        setError('Failed to delete memory')
      }
    } catch {
      // Rollback on network error
      setMemories((prev) => [memoryToDelete, ...prev])
      if (stats) setStats({ ...stats, memoriesStored: stats.memoriesStored })
      setError('Failed to delete memory')
    }
  }

  // Refresh data
  const handleRefresh = () => {
    if (session) {
      fetchDataWithSession(session)
    }
  }

  // Retry sign in
  const handleRetrySignIn = () => {
    setError(null)
    createSession()
  }

  const filteredMemories = memories.filter((m) => {
    const matchesSearch = !searchQuery || m.content.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = !filterType || m.type === filterType
    return matchesSearch && matchesType
  })

  const memoryTypes = ['fact', 'preference', 'decision', 'learning', 'history', 'context']

  // Not connected state
  if (!isConnected) {
    return (
      <div className="min-h-screen bg-black text-white flex flex-col">
        <header className="border-b border-white/5 bg-black/50 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <a href="/"><Logo /></a>
            <ConnectButton />
          </div>
        </header>
        <div className="flex-1 flex items-center justify-center px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center text-center max-w-md"
          >
            <div className="w-20 h-20 mb-6 rounded-2xl bg-white/5 flex items-center justify-center">
              <svg className="w-10 h-10 text-zinc-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a2.25 2.25 0 00-2.25-2.25H15a3 3 0 11-6 0H5.25A2.25 2.25 0 003 12m18 0v6a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 18v-6m18 0V9M3 12V9m18 0a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 9m18 0V6a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 6v3" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold mb-2">Connect Your Wallet</h1>
            <p className="text-zinc-500 mb-8">
              Your wallet address is your agent identity. Connect to access your memory vault.
            </p>
            <div className="flex justify-center">
              <ConnectButton />
            </div>
          </motion.div>
        </div>
      </div>
    )
  }

  // Signing in state
  if (isSigningIn) {
    return (
      <div className="min-h-screen bg-black text-white flex flex-col">
        <header className="border-b border-white/5 bg-black/50 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <a href="/"><Logo /></a>
            <ConnectButton />
          </div>
        </header>
        <div className="flex-1 flex items-center justify-center px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center text-center max-w-md"
          >
            <div className="w-16 h-16 border-2 border-white/20 border-t-white rounded-full animate-spin mb-6" />
            <h2 className="text-xl font-semibold mb-2">Sign to Continue</h2>
            <p className="text-zinc-500">
              Please sign the message in your wallet to authenticate. You only need to do this once.
            </p>
          </motion.div>
        </div>
      </div>
    )
  }

  // No session state (sign in required)
  if (!session && !isSigningIn) {
    return (
      <div className="min-h-screen bg-black text-white flex flex-col">
        <header className="border-b border-white/5 bg-black/50 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <a href="/"><Logo /></a>
            <ConnectButton />
          </div>
        </header>
        <div className="flex-1 flex items-center justify-center px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center text-center max-w-md"
          >
            <div className="w-20 h-20 mb-6 rounded-2xl bg-white/5 flex items-center justify-center">
              <svg className="w-10 h-10 text-zinc-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold mb-2">Sign In Required</h1>
            <p className="text-zinc-500 mb-6">
              {error || 'Sign a message to access your memory vault. You only need to sign once.'}
            </p>
            <button
              onClick={handleRetrySignIn}
              className="px-6 py-3 bg-white text-black font-medium rounded-full hover:bg-zinc-200 transition-all"
            >
              Sign In
            </button>
          </motion.div>
        </div>
      </div>
    )
  }

  // Main dashboard
  return (
    <div className="min-h-screen bg-black text-white">
      <header className="border-b border-white/5 bg-black/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <a href="/"><Logo /></a>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 bg-white text-black text-sm font-medium rounded-full hover:bg-zinc-200 transition-all"
            >
              + Add Memory
            </button>
            <ConnectButton />
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats */}
        {stats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
          >
            <div className="p-4 bg-white/[0.02] border border-white/5 rounded-xl">
              <div className="text-2xl font-bold">{stats.memoriesStored}</div>
              <div className="text-xs text-zinc-500">Memories Stored</div>
            </div>
            <div className="p-4 bg-white/[0.02] border border-white/5 rounded-xl">
              <div className="text-2xl font-bold">{stats.recallsToday}</div>
              <div className="text-xs text-zinc-500">Recalls Today</div>
            </div>
            <div className="p-4 bg-white/[0.02] border border-white/5 rounded-xl">
              <div className="text-2xl font-bold capitalize">{stats.tier}</div>
              <div className="text-xs text-zinc-500">Current Tier</div>
            </div>
            <div className="p-4 bg-white/[0.02] border border-white/5 rounded-xl">
              <div className="text-2xl font-bold">
                {stats.limits.maxMemories === -1 ? '∞' : stats.limits.maxMemories}
              </div>
              <div className="text-xs text-zinc-500">Memory Limit</div>
            </div>
          </motion.div>
        )}

        {/* Search & Filter */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search memories..."
              className="w-full px-4 py-3 bg-white/[0.02] border border-white/10 rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-white/30 transition-colors"
            />
          </div>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setFilterType(null)}
              className={`px-3 py-2 text-xs font-medium rounded-lg transition-all ${
                !filterType ? 'bg-white text-black' : 'bg-white/5 text-zinc-400 hover:bg-white/10'
              }`}
            >
              All
            </button>
            {memoryTypes.map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`px-3 py-2 text-xs font-medium rounded-lg transition-all ${
                  filterType === type ? 'bg-white text-black' : 'bg-white/5 text-zinc-400 hover:bg-white/10'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* Loading */}
        {isLoading && memories.length === 0 && (
          <div className="text-center py-12">
            <div className="w-8 h-8 border-2 border-white/20 border-t-white rounded-full animate-spin mx-auto" />
            <p className="text-sm text-zinc-500 mt-4">Loading memories...</p>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && memories.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-16"
          >
            <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-white/5 flex items-center justify-center">
              <svg className="w-8 h-8 text-zinc-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">No memories yet</h3>
            <p className="text-zinc-500 mb-6 max-w-sm mx-auto">
              Start building your agent's memory vault by adding your first memory.
            </p>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-6 py-3 bg-white text-black font-medium rounded-full hover:bg-zinc-200 transition-all"
            >
              + Add First Memory
            </button>
          </motion.div>
        )}

        {/* Memories List */}
        {memories.length > 0 && (
          <>
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-zinc-500">
                {filteredMemories.length} {filteredMemories.length === 1 ? 'memory' : 'memories'}
                {filterType && ' (filtered)'}
              </p>
              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="text-sm text-zinc-500 hover:text-white transition-colors flex items-center gap-1 disabled:opacity-50"
              >
                <svg className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                {isLoading ? 'Syncing...' : 'Refresh'}
              </button>
            </div>

            <div className="grid gap-4">
              <AnimatePresence>
                {filteredMemories.map((memory) => (
                  <motion.div
                    key={memory.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="p-4 bg-white/[0.02] border border-white/5 rounded-xl hover:border-white/10 transition-all group"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <p className="text-white">{memory.content}</p>
                        <div className="mt-2 flex items-center gap-2">
                          <span className="px-2 py-0.5 text-xs bg-white/5 text-zinc-400 rounded">
                            {memory.type}
                          </span>
                          <span className="text-xs text-zinc-600">
                            {new Date(memory.createdAt).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={() => deleteMemory(memory.id)}
                        className="p-2 text-zinc-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            {filteredMemories.length === 0 && (
              <div className="text-center py-12 text-zinc-500">
                No memories match your search
              </div>
            )}
          </>
        )}
      </div>

      {/* Add Memory Modal */}
      <AnimatePresence>
        {showAddModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setShowAddModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-zinc-900 border border-white/10 rounded-2xl p-6 w-full max-w-md"
            >
              <h3 className="text-lg font-semibold mb-4">Add New Memory</h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs text-zinc-500 mb-2">Content</label>
                  <textarea
                    value={newMemory}
                    onChange={(e) => setNewMemory(e.target.value)}
                    placeholder="What should your agent remember?"
                    className="w-full h-24 px-4 py-3 bg-black/50 border border-white/10 rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-white/30 transition-colors resize-none"
                  />
                </div>

                <div>
                  <label className="block text-xs text-zinc-500 mb-2">Type</label>
                  <div className="flex flex-wrap gap-2">
                    {memoryTypes.map((type) => (
                      <button
                        key={type}
                        onClick={() => setNewMemoryType(type)}
                        className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                          newMemoryType === type
                            ? 'bg-white text-black'
                            : 'bg-white/5 text-zinc-400 hover:bg-white/10'
                        }`}
                      >
                        {type}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    onClick={() => setShowAddModal(false)}
                    className="flex-1 py-3 border border-white/10 rounded-xl text-white font-medium hover:bg-white/5 transition-all"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={storeMemory}
                    disabled={!newMemory.trim()}
                    className="flex-1 py-3 bg-white text-black font-medium rounded-xl hover:bg-zinc-200 transition-all disabled:opacity-50"
                  >
                    Store Memory
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Toast */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-4 right-4 px-4 py-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm max-w-sm"
          >
            {error}
            <button onClick={() => setError(null)} className="ml-2 text-red-300 hover:text-red-200">×</button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
