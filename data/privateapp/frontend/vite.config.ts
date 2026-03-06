import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In dev, proxy /api and /app to the FastAPI backend.
// In production, `npm run build` outputs to ../static/dist/
// and FastAPI serves that directory.
export default defineConfig({
  plugins: [react()],
  publicDir: 'public',
  build: {
    outDir: '../static/dist',
    emptyOutDir: true,
    // Disable crossorigin attribute on script/link tags
    // (causes CORS issues behind reverse proxies like Tailscale)
    modulePreload: false,
  },
  // Prevent Vite from adding crossorigin to script tags
  html: {
    cspNonce: undefined,
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8800',
      '/app': 'http://localhost:8800',
      '/manifest.json': 'http://localhost:8800',
      '/sw.js': 'http://localhost:8800',
    },
  },
})
