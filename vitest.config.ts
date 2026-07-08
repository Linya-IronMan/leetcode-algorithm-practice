import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      'scripts/**', // 排除脚手架与模板目录
    ],
  },
});
