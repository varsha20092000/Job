import { defineConfig } from 'vite'

export default defineConfig({
  root: '.',
  base: '/',
  build: {
    outDir: 'static/js',
    emptyOutDir: true,
  }
})
