const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  timeout: 30_000,
  expect: {
    timeout: 5_000,
  },
  fullyParallel: true,
  retries: 0,
  use: {
    baseURL: 'http://127.0.0.1:8003',
    headless: true,
    trace: 'on-first-retry',
  },
  reporter: [
    ['list'],
    ['html', { outputFolder: '../reports/frontend/playwright-html', open: 'never' }],
    ['json', { outputFile: '../reports/frontend/playwright-report.json' }],
    ['junit', { outputFile: '../reports/frontend/playwright-junit.xml' }],
  ],
  webServer: {
    command: '../.venv/Scripts/python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8003',
    cwd: '..',
    url: 'http://127.0.0.1:8003/health',
    reuseExistingServer: true,
    timeout: 120_000,
    env: {
      PYTHONPATH: '.',
    },
  },
});
