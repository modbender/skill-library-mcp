import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'framer-motion'],
          markdown: ['react-markdown', 'rehype-prism-plus'],
        },
      },
    },
  },
  server: {
    open: true,
    port: 5173,
  },
})
