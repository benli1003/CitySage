import { defineConfig } from 'vite';
  import react from '@vitejs/plugin-react-swc';
  import path from "path";

  export default defineConfig(({ mode }) => ({
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      host: "::",
      port: 8080,
      proxy: mode === 'development' ? {
        "/api": {
          target: "http://18.191.243.194:5050",
          changeOrigin: true,
          secure: false
        }
      } : undefined
    },
    define: {
      __API_URL__: mode === 'production'
        ? '""'
        : '""'
    },
    optimizeDeps: {
      exclude: ['lovable-tagger']
    },
    plugins: [react()]
  }));