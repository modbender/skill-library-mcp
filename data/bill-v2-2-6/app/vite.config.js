import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 8005,
    host: '0.0.0.0',
    allowedHosts: true
  }
})
