import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "declare-render/browser": path.resolve(__dirname, "../../declare-renderer/src/browser.ts"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:3001",
        changeOrigin: true,
      },
      "/picui-free": {
        target: "https://free.picui.cn",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/picui-free/, ""),
      },
      "/picui-cn": {
        target: "https://picui.cn",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/picui-cn/, ""),
      },
    },
  },
});
