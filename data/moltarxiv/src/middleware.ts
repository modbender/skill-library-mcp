import { NextRequest, NextResponse } from 'next/server'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET,POST,PATCH,PUT,DELETE,OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
  'Access-Control-Max-Age': '86400',
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  if (pathname.startsWith('/@')) {
    const handle = pathname.slice(2)
    if (handle) {
      const url = request.nextUrl.clone()
      url.pathname = `/agents/${handle}`
      return NextResponse.redirect(url)
    }
  }

  if (pathname.startsWith('/api/v1/')) {
    if (request.method === 'OPTIONS') {
      return new NextResponse(null, {
        status: 204,
        headers: corsHeaders,
      })
    }

    const response = NextResponse.next()
    for (const [key, value] of Object.entries(corsHeaders)) {
      response.headers.set(key, value)
    }
    return response
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/api/v1/:path*', '/@:path*'],
}
