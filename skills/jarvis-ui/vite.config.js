import { defineConfig } from 'vite';

export default defineConfig({
  root: '.',
  server: {
    port: 8001,
    host: true,
    allowedHosts: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:9999',
        changeOrigin: true,
      },
    },
  },
  assetsInclude: ['**/*.glb', '**/*.gltf'],
});
