import { QdrantClient } from '@qdrant/js-client-rest'

const COLLECTION_NAME = 'memories'
const VECTOR_SIZE = 1536 // text-embedding-3-small dimension

let client: QdrantClient | null = null

export function getQdrantClient(): QdrantClient {
  if (!client) {
    client = new QdrantClient({
      url: process.env.QDRANT_URL,
      apiKey: process.env.QDRANT_API_KEY,
    })
  }
  return client
}

export async function ensureCollection(): Promise<void> {
  const qdrant = getQdrantClient()

  const collections = await qdrant.getCollections()
  const exists = collections.collections.some((c) => c.name === COLLECTION_NAME)

  if (!exists) {
    await qdrant.createCollection(COLLECTION_NAME, {
      vectors: {
        size: VECTOR_SIZE,
        distance: 'Cosine',
      },
    })
    // Collection created silently
  }
}

export async function upsertVector(
  id: string,
  vector: number[],
  payload: Record<string, unknown>
): Promise<void> {
  const qdrant = getQdrantClient()

  await qdrant.upsert(COLLECTION_NAME, {
    wait: true,
    points: [
      {
        id,
        vector,
        payload,
      },
    ],
  })
}

export async function searchVectors(
  vector: number[],
  agentId: string,
  limit: number = 5,
  filter?: { type?: string }
): Promise<Array<{ id: string; score: number; payload: Record<string, unknown> }>> {
  const qdrant = getQdrantClient()

  const mustConditions: Array<{ key: string; match: { value: string } }> = [
    { key: 'agentId', match: { value: agentId } },
  ]

  if (filter?.type) {
    mustConditions.push({ key: 'type', match: { value: filter.type } })
  }

  const results = await qdrant.search(COLLECTION_NAME, {
    vector,
    limit,
    filter: {
      must: mustConditions,
    },
    with_payload: true,
  })

  return results.map((result) => ({
    id: result.id as string,
    score: result.score,
    payload: result.payload as Record<string, unknown>,
  }))
}

export async function deleteVector(id: string): Promise<void> {
  const qdrant = getQdrantClient()

  await qdrant.delete(COLLECTION_NAME, {
    wait: true,
    points: [id],
  })
}

export async function deleteAgentVectors(agentId: string): Promise<void> {
  const qdrant = getQdrantClient()

  await qdrant.delete(COLLECTION_NAME, {
    wait: true,
    filter: {
      must: [{ key: 'agentId', match: { value: agentId } }],
    },
  })
}
