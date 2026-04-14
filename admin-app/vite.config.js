import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  // Load .env from the project root (one level up); empty prefix loads all variables.
  const env = loadEnv(mode, path.resolve(__dirname, '..'), '')

  const port = parseInt(env.ADMIN_PORT || process.env.ADMIN_PORT || '3001')
  const backendProxy = env.BACKEND_PROXY_URL || process.env.BACKEND_PROXY_URL || 'http://localhost:18000'

  return {
    plugins: [react()],
    server: {
      host: true,  // bind 0.0.0.0 so LAN clients can reach the dev server
      port,
      proxy: {
        '/api': backendProxy
      }
    }
  }
})
