import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '127.0.0.1',
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://127.0.0.1:8005',
        ws: true,
      },
      '/static': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true,
      },
      '/evidence': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true,
      },
      '/oiml_evidence': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true,
      },
    },
  },
});
