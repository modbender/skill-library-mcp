/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      // Make the public API path match the docs (/v1/*) while keeping Next.js under /api/*
      { source: '/health', destination: '/api/health' },
      { source: '/v1/:path*', destination: '/api/v1/:path*' }
    ];
  }
};

module.exports = nextConfig;
