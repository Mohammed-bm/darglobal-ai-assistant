import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: [['babel-plugin-react-compiler']],
      },
    }),
    tailwindcss(),
  ],
  server: {
    // lets the UI call /query, /items and /ingest without localhost:8000
    proxy: {
      '/ingest': 'http://localhost:8000',
      '/items': 'http://localhost:8000',
      '/query': 'http://localhost:8000',
    },
  },
})