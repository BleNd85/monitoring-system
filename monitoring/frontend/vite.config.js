import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/collector': {
        target: import.meta.env?.VITE_COLLECTOR_URL || 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/collector/, ''),
      },
      proxy: {
        '/alerter': {
          target: import.meta.env?.VITE_ALERTER_URL || 'http://localhost:8002',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/alerter/, ''),
        }
      }
    }
  }
})
