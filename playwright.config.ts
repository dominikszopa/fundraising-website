import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright smoke test configuration.
 *
 * The Django dev server is started automatically before tests and stopped after.
 * Just run:
 *   npm run test:e2e
 *
 * To target a different environment (server must be running manually):
 *   BASE_URL=https://staging.example.com npm run test:e2e
 */
export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  expect: { timeout: 10_000 },

  // Run tests sequentially to avoid DB conflicts from concurrent signups/updates
  fullyParallel: false,
  workers: 1,

  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [['html', { open: 'never' }], ['list']],

  use: {
    baseURL: process.env.BASE_URL ?? 'http://127.0.0.1:8000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    launchOptions: {
      slowMo: process.env.SLOWMO ? parseInt(process.env.SLOWMO) : 0,
    },
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 13'] },
    },
  ],

  globalSetup: './e2e/global-setup.ts',

  // Start Django automatically; reuse a running server in dev, always fresh in CI
  webServer: {
    command: 'bash e2e/start-server.sh',
    url: 'http://127.0.0.1:8000/',
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
  },
});
