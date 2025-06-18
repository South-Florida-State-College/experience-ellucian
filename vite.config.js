import { defineConfig } from 'vite';
import basicSsl from '@vitejs/plugin-basic-ssl';

export default defineConfig({
  plugins: [basicSsl()],
  server: {
    port: 3000,
    https: true
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
}); 