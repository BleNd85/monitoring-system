import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/collector': {
          target: env.VITE_COLLECTOR_URL || 'http://localhost:8001',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/collector/, ''),
        },
        '/alerter': {
          target: env.VITE_ALERTER_URL || 'http://localhost:8002',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/alerter/, ''),
        }
      }
    }
  }
})