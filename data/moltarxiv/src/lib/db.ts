import { PrismaClient, Prisma } from '@prisma/client'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
  prismaMiddlewareApplied?: boolean
}

const rawDatabaseUrl = process.env.DATABASE_URL || process.env.DIRECT_URL

function normalizeDatabaseUrl(url: string): string {
  try {
    const parsed = new URL(url)
    const isSupabaseHost = parsed.hostname.endsWith('.supabase.co')
    if (isSupabaseHost && parsed.port === '5432') {
      parsed.port = '6543'
    }

    const port = parsed.port
    const isSupabasePooled = port === '6543'

    if (isSupabasePooled && !parsed.searchParams.has('pgbouncer')) {
      parsed.searchParams.set('pgbouncer', 'true')
    }

    if (!parsed.searchParams.has('connection_limit')) {
      parsed.searchParams.set('connection_limit', isSupabasePooled ? '1' : '5')
    }

    if (isSupabasePooled && !parsed.searchParams.has('pool_timeout')) {
      parsed.searchParams.set('pool_timeout', '0')
    }

    if (isSupabasePooled && !parsed.searchParams.has('statement_cache_size')) {
      parsed.searchParams.set('statement_cache_size', '0')
    }

    return parsed.toString()
  } catch {
    return url
  }
}

const databaseUrl = rawDatabaseUrl ? normalizeDatabaseUrl(rawDatabaseUrl) : ''

if (!databaseUrl) {
  throw new Error('DATABASE_URL or DIRECT_URL must be set')
}

if (process.env.NODE_ENV === 'production') {
  try {
    const parsed = new URL(databaseUrl)
    if (parsed.port === '5432') {
      console.warn('[db] Using direct (non-pooled) database port in production. This can cause max client errors.')
    }
  } catch {
    // ignore
  }
}

const prisma = globalForPrisma.prisma ?? new PrismaClient({
  datasources: {
    db: {
      url: databaseUrl,
    },
  },
  log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
})

function isTransientDbError(err: unknown): boolean {
  if (err instanceof Prisma.PrismaClientKnownRequestError) {
    return ['P1001', 'P1002', 'P1008', 'P1017'].includes(err.code)
  }

  if (err instanceof Prisma.PrismaClientInitializationError) {
    return true
  }

  if (err instanceof Prisma.PrismaClientRustPanicError) {
    return true
  }

  if (err instanceof Error) {
    const message = err.message.toLowerCase()
    return (
      message.includes('timeout') ||
      message.includes('timed out') ||
      message.includes('maxclientsinsessionmode') ||
      message.includes('too many clients') ||
      message.includes('connection terminated') ||
      message.includes('connection reset') ||
      message.includes('econnreset') ||
      message.includes('econnrefused') ||
      message.includes('could not connect')
    )
  }

  return false
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

if (!globalForPrisma.prismaMiddlewareApplied) {
  prisma.$use(async (params, next) => {
    const maxRetries = 5
    let attempt = 0

    while (true) {
      try {
        return await next(params)
      } catch (err) {
        if (attempt < maxRetries && isTransientDbError(err)) {
          attempt += 1
          await sleep(100 * attempt)
          continue
        }
        throw err
      }
    }
  })

  globalForPrisma.prismaMiddlewareApplied = true
}

export const db = prisma

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma
// Trigger redeploy Sun Feb  1 19:55:04 IST 2026
