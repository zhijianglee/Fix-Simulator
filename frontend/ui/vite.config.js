import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API calls to the backend Flask server
      '/send_message': { target: 'http://127.0.0.1:5031', changeOrigin: true },
      '/retrieve_orders_by_client_comp_id': { target: 'http://127.0.0.1:5031', changeOrigin: true },
      '/fix message/parse_to_json': { target: 'http://127.0.0.1:5031', changeOrigin: true },
      '/orders': { target: 'http://127.0.0.1:5031', changeOrigin: true }
    }
  },
});
