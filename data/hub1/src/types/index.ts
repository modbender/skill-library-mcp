export type MemoryType = 'fact' | 'preference' | 'decision' | 'learning' | 'history' | 'context'

export interface StoreMemoryRequest {
  content: string
  type?: MemoryType
  tags?: string[]
  metadata?: Record<string, unknown>
}

export interface RecallMemoryRequest {
  query: string
  limit?: number
  type?: MemoryType
}

export interface MemoryResponse {
  id: string
  content: string
  type: MemoryType
  tags: string[]
  relevance?: number
  createdAt: string
}

export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: string
  usage?: {
    memoriesStored: number
    recallsToday: number
    tier: string
  }
}
