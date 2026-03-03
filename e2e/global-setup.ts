/**
 * Playwright global setup.
 *
 * Runs once before all tests. Creates test users in the DB with known
 * credentials and saves authenticated browser state (cookies) to files
 * so that tests can skip the login flow when testing authenticated pages.
 *
 * Requires the Django server to be running at BASE_URL with PLAYWRIGHT_TESTING=true.
 */
import { chromium, FullConfig } from '@playwright/test';
import { execSync } from 'child_process';
import { mkdirSync } from 'fs';
import * as path from 'path';

const AUTH_DIR = path.join(__dirname, 'auth');

export const TEST_USER = { username: 'smoke_test_user', password: 'SmokeTest123!', email: 'smoke@test.com' };
export const PW_USER = { username: 'smoke_pw_user', password: 'SmokePw123!', email: 'pwuser@test.com' };
export const ADMIN_USER = { username: 'smoke_admin', password: 'SmokeAdmin123!', email: 'admin@test.com' };

export const TEST_USER_AUTH = path.join(AUTH_DIR, 'smoke_test_user.json');
export const PW_USER_AUTH = path.join(AUTH_DIR, 'smoke_pw_user.json');
export const ADMIN_AUTH = path.join(AUTH_DIR, 'smoke_admin.json');


function createTestData() {
  const script = `
from django.contrib.auth.models import User
from team_fundraising.models import Campaign, Donation, Fundraiser

# ── Fixture data (replaces loaddata startingdata, safe to run repeatedly) ──

# Campaign pk=1 must exist for CAMPAIGN_ID constant in tests
# Use update_or_create so that existing records get the correct values (e.g. active=True)
campaign, _ = Campaign.objects.update_or_create(
    pk=1,
    defaults={
        'name': 'Fundraising Campaign',
        'goal': 10000,
        'campaign_message': 'Test campaign.',
        'default_fundraiser_message': 'Welcome to my fundraising page!',
        'default_fundraiser_amount': 0,
        'active': True,
    },
)

# "first" user — used as the owner of Fundraiser pk=1
first_user, created = User.objects.get_or_create(username='first', defaults={'email': 'name@email.com'})
if created:
    first_user.set_password('FirstUser123!')
    first_user.save()

# Fundraiser pk=1 "First Fundraiser" — referenced by FUNDRAISER_ID constant in tests
# Use update_or_create so that existing records get the correct values
fundraiser, _ = Fundraiser.objects.update_or_create(
    pk=1,
    defaults={
        'campaign': campaign,
        'user': first_user,
        'name': 'First Fundraiser',
        'goal': 200,
        'message': 'Welcome to my fundraising page!',
    },
)

# At least one paid donation so the fundraiser page is non-empty
Donation.objects.get_or_create(
    pk=2,
    defaults={
        'fundraiser': fundraiser,
        'name': 'First Donation',
        'amount': 50.0,
        'email': 'email@domain.com',
        'payment_status': 'paid',
    },
)

# ── Smoke-test users (recreated fresh every run) ──
# Delete fundraisers first to satisfy the FK constraint before deleting users.

for username in ('smoke_test_user', 'smoke_pw_user', 'smoke_admin'):
    Fundraiser.objects.filter(user__username=username).delete()
    User.objects.filter(username=username).delete()

user = User.objects.create_user('smoke_test_user', 'smoke@test.com', 'SmokeTest123!')
Fundraiser.objects.create(campaign=campaign, user=user, name='Smoke Test Fundraiser', goal=500)

pw_user = User.objects.create_user('smoke_pw_user', 'pwuser@test.com', 'SmokePw123!')
Fundraiser.objects.create(campaign=campaign, user=pw_user, name='PW Test Fundraiser', goal=300)

User.objects.create_superuser('smoke_admin', 'admin@test.com', 'SmokeAdmin123!')

print('Test data ready')
`;

  execSync('poetry run python3 manage.py shell', {
    input: script,
    stdio: ['pipe', 'inherit', 'inherit'],
    env: { ...process.env, PLAYWRIGHT_TESTING: 'true' },
  });
}

async function saveAuthState(
  baseURL: string,
  loginPath: string,
  username: string,
  password: string,
  waitForPath: string | RegExp,
  outFile: string,
) {
  const browser = await chromium.launch();
  const context = await browser.newContext({ baseURL });
  const page = await context.newPage();

  await page.goto(loginPath);
  await page.fill('#id_username', username);
  await page.fill('#id_password', password);
  await page.click('input[type="submit"]');
  await page.waitForURL(waitForPath);

  await context.storageState({ path: outFile });
  await browser.close();
}

export default async function globalSetup(config: FullConfig) {
  const baseURL = config.projects[0]?.use?.baseURL ?? 'http://localhost:8000';

  console.log('[global-setup] Setting up test data...');
  createTestData();

  mkdirSync(AUTH_DIR, { recursive: true });

  console.log('[global-setup] Saving auth state for smoke_test_user...');
  await saveAuthState(
    baseURL,
    '/team_fundraising/accounts/login/',
    TEST_USER.username,
    TEST_USER.password,
    /update_fundraiser/,
    TEST_USER_AUTH,
  );

  console.log('[global-setup] Saving auth state for smoke_pw_user...');
  await saveAuthState(
    baseURL,
    '/team_fundraising/accounts/login/',
    PW_USER.username,
    PW_USER.password,
    /update_fundraiser/,
    PW_USER_AUTH,
  );

  console.log('[global-setup] Saving auth state for smoke_admin (via /admin/login/)...');
  await saveAuthState(
    baseURL,
    '/admin/login/',
    ADMIN_USER.username,
    ADMIN_USER.password,
    /\/admin\/$/,
    ADMIN_AUTH,
  );

  console.log('[global-setup] Done.\n');
}
