import { defineConfig } from 'vite'
import path from 'path'

export default defineConfig({
  root: '.',
  build: {
    outDir: '../dist/web',
    emptyOutDir: true
  }
})
