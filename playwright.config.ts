import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright smoke test configuration.
 *
 * Before running tests, start the Django server with captcha disabled:
 *   PLAYWRIGHT_TESTING=true python3 manage.py runserver localhost:8000
 *
 * Run tests:
 *   npm run test:e2e
 *
 * To target a different environment:
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
    baseURL: process.env.BASE_URL ?? 'http://localhost:8000',
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
  ],

  globalSetup: './e2e/global-setup.ts',
});
