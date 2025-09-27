import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  return {
    plugins: [react()],
    server: {
      host: '127.0.0.1',
      port: Number(env.VITE_DEV_PORT ?? 5173),
      proxy: {
        '/api': {
          target: env.VITE_API_BASE ?? 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false
        }
      }
    }
  };
});
