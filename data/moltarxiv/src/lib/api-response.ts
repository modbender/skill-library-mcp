import { NextResponse } from 'next/server'
import { ZodError } from 'zod'
import { AuthError } from './auth'

export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: {
    code: string
    message: string
    details?: unknown
  }
  meta?: {
    page?: number
    limit?: number
    total?: number
    hasMore?: boolean
  }
}

/**
 * Create a successful API response
 */
export function success<T>(data: T, meta?: ApiResponse['meta']): NextResponse {
  return NextResponse.json({
    success: true,
    data,
    meta
  } satisfies ApiResponse<T>)
}

/**
 * Create a paginated success response
 */
export function paginated<T>(
  data: T[],
  page: number,
  limit: number,
  total: number
): NextResponse {
  return success(data, {
    page,
    limit,
    total,
    hasMore: page * limit < total
  })
}

/**
 * Create an error API response
 */
export function error(
  message: string,
  code: string = 'ERROR',
  status: number = 400,
  details?: unknown
): NextResponse {
  return NextResponse.json(
    {
      success: false,
      error: {
        code,
        message,
        details
      }
    } satisfies ApiResponse,
    { status }
  )
}

/**
 * Handle API errors uniformly
 */
export function handleError(err: unknown): NextResponse {
  console.error('API Error:', err)
  
  // Auth errors
  if (err instanceof AuthError) {
    return error(err.message, 'AUTH_ERROR', err.status)
  }
  
  // Validation errors
  if (err instanceof ZodError) {
    return error(
      'Validation failed',
      'VALIDATION_ERROR',
      400,
      err.errors.map(e => ({
        field: e.path.join('.'),
        message: e.message
      }))
    )
  }
  
  // Prisma errors
  if (typeof err === 'object' && err !== null && 'code' in err) {
    const prismaError = err as { code: string; meta?: unknown }
    
    switch (prismaError.code) {
      case 'P2002':
        return error('A record with this value already exists', 'DUPLICATE_ERROR', 409)
      case 'P2025':
        return error('Record not found', 'NOT_FOUND', 404)
      case 'P2003':
        return error('Related record not found', 'REFERENCE_ERROR', 400)
      default:
        break
    }
  }
  
  // Rate limit errors
  if (err instanceof Error && err.message.includes('Rate limit')) {
    return error(err.message, 'RATE_LIMIT_ERROR', 429)
  }
  
  // Generic errors
  if (err instanceof Error) {
    return error(
      process.env.NODE_ENV === 'development' ? err.message : 'Internal server error',
      'INTERNAL_ERROR',
      500
    )
  }
  
  return error('An unexpected error occurred', 'UNKNOWN_ERROR', 500)
}

/**
 * Rate limit exceeded error
 */
export function rateLimitExceeded(resetAt: Date): NextResponse {
  return NextResponse.json(
    {
      success: false,
      error: {
        code: 'RATE_LIMIT_EXCEEDED',
        message: 'Too many requests. Please try again later.',
        details: { resetAt: resetAt.toISOString() }
      }
    } satisfies ApiResponse,
    {
      status: 429,
      headers: {
        'Retry-After': Math.ceil((resetAt.getTime() - Date.now()) / 1000).toString(),
        'X-RateLimit-Reset': resetAt.toISOString()
      }
    }
  )
}

/**
 * Not found error
 */
export function notFound(resource: string = 'Resource'): NextResponse {
  return error(`${resource} not found`, 'NOT_FOUND', 404)
}

/**
 * Unauthorized error
 */
export function unauthorized(message: string = 'Unauthorized'): NextResponse {
  return error(message, 'UNAUTHORIZED', 401)
}

/**
 * Forbidden error
 */
export function forbidden(message: string = 'Forbidden'): NextResponse {
  return error(message, 'FORBIDDEN', 403)
}
