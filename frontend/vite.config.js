import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Pokédex Tracker',
        short_name: 'Pokédex',
        description: 'Track your caught Pokémon across multiple games',
        theme_color: '#e53e3e',
        background_color: '#111827',
        display: 'standalone',
        icons: [
          { src: 'pwa-64x64.png',            sizes: '64x64',    type: 'image/png' },
          { src: 'pwa-192x192.png',           sizes: '192x192',  type: 'image/png' },
          { src: 'pwa-512x512.png',           sizes: '512x512',  type: 'image/png' },
          { src: 'maskable-icon-512x512.png', sizes: '512x512',  type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,json,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\//,
            handler: 'NetworkFirst',
            options: { cacheName: 'external' },
          },
        ],
      },
    }),
  ],
  base: process.env.VITE_BASE_URL || '/',
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.BACKEND_URL || 'http://localhost:3000',
        changeOrigin: true,
      },
    },
  },
})
