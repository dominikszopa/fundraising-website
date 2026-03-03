/**
 * Smoke tests for the fundraising website.
 *
 * Mirrors the manual smoke test plan in docs/SMOKE_TEST_PLAN.md.
 *
 * Prerequisites:
 *   1. Django server running with PLAYWRIGHT_TESTING=true:
 *        PLAYWRIGHT_TESTING=true python3 manage.py runserver localhost:8000
 *   2. Install Playwright: npm install && npx playwright install chromium
 *   3. Run tests: npm run test:e2e
 */
import { test, expect } from '@playwright/test';
import { TEST_USER, PW_USER, TEST_USER_AUTH, PW_USER_AUTH, ADMIN_AUTH } from './global-setup';

const CAMPAIGN_ID = 1;
const FUNDRAISER_ID = 1; // "First Fundraiser" from startingdata fixture

// ── Helper ──────────────────────────────────────────────────────────────────

/** Enable the signup submit button (it is disabled until reCAPTCHA fires;
 *  reCAPTCHA is removed server-side when PLAYWRIGHT_TESTING=true). */
async function enableSignupButton(page: import('@playwright/test').Page) {
  await page.evaluate(() => {
    const btn = document.getElementById('signup-submit-btn') as HTMLButtonElement | null;
    if (btn) btn.disabled = false;
  });
}

// ── 1. Campaign & Fundraiser Browsing (anonymous) ────────────────────────────

test.describe('1. Campaign & Fundraiser Browsing', () => {
  test('root page loads', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('body')).toBeVisible();
    // Should not show a server error
    await expect(page.locator('body')).not.toContainText('Server Error');
  });

  test('campaign home page shows fundraisers and totals', async ({ page }) => {
    await page.goto(`/team_fundraising/${CAMPAIGN_ID}/`);
    await expect(page.locator('h3')).toContainText('Fundraising Campaign');
    // Total raised widget
    await expect(page.locator('#raised')).toBeVisible();
    // At least one fundraiser card
    await expect(page.locator('[data-filter-item]').first()).toBeVisible();
    // CTA for anonymous visitor
    await expect(page.locator('a:has-text("Create a fundraiser page")')).toBeVisible();
  });

  test('fundraiser search filters cards', async ({ page }) => {
    await page.goto(`/team_fundraising/${CAMPAIGN_ID}/`);
    await page.fill('#search', 'First Fundraiser');
    // At least the matching card remains visible
    await expect(page.locator('[data-filter-name*="first fundraiser"]')).toBeVisible();
    // A card that does NOT match should be hidden
    const allCards = page.locator('[data-filter-item]');
    const count = await allCards.count();
    if (count > 1) {
      const hiddenCards = page.locator('[data-filter-item].hidden');
      await expect(hiddenCards.first()).toBeVisible({ visible: false });
    }
  });

  test('fundraiser page shows info and Donate button', async ({ page }) => {
    await page.goto(`/team_fundraising/fundraiser/${FUNDRAISER_ID}/`);
    await expect(page.locator('h2')).toContainText('First Fundraiser');
    await expect(page.locator('#raised')).toBeVisible();
    await expect(page.locator('.donate-button')).toBeVisible();
    // Edit button must NOT be visible to anonymous users
    await expect(page.locator('a.btn-secondary:has-text("Edit")')).not.toBeVisible();
  });

  test('about page loads', async ({ page }) => {
    await page.goto(`/team_fundraising/about/${CAMPAIGN_ID}/`);
    await expect(page.locator('body')).toBeVisible();
    await expect(page.locator('body')).not.toContainText('Server Error');
  });
});

// ── 2. Donation Flow (anonymous) ─────────────────────────────────────────────

test.describe('2. Donation Flow', () => {
  test('donation form shows amount options and required fields', async ({ page }) => {
    await page.goto(`/team_fundraising/donation/${FUNDRAISER_ID}/`);
    // Preset amounts
    for (const amount of ['10', '25', '50', '100']) {
      await expect(page.locator(`input[name="amount"][value="${amount}"]`)).toBeVisible();
    }
    await expect(page.locator('input[name="amount"][value="other"]')).toBeVisible();
    // Required fields
    await expect(page.locator('#id_name')).toBeVisible();
    await expect(page.locator('#id_email')).toBeVisible();
    await expect(page.locator('input[value="Donate now"]')).toBeVisible();
  });

  test('submitting empty form shows validation errors', async ({ page }) => {
    await page.goto(`/team_fundraising/donation/${FUNDRAISER_ID}/`);
    // Remove HTML5 required attributes so the form reaches the server for validation
    await page.evaluate(() => {
      document.querySelectorAll<HTMLInputElement>('input[required], textarea[required]').forEach(el => {
        el.removeAttribute('required');
      });
    });
    await page.click('input[value="Donate now"]');
    await expect(page.locator('.alert-danger').first()).toBeVisible();
    await expect(page).toHaveURL(/\/donation\//);
  });

  test('valid donation submission reaches PayPal confirmation page', async ({ page }) => {
    await page.goto(`/team_fundraising/donation/${FUNDRAISER_ID}/`);
    await page.click('input[name="amount"][value="25"]');
    await page.fill('#id_name', 'Playwright Donor');
    await page.fill('#id_email', 'playwright@test.com');
    await page.click('input[value="Donate now"]');

    // PayPal confirmation page
    await expect(page.locator('body')).toContainText('Please confirm your information');
    await expect(page.locator('body')).toContainText('25');
    await expect(page.locator('body')).toContainText('Playwright Donor');
  });

  test('custom "Other" amount is accepted', async ({ page }) => {
    await page.goto(`/team_fundraising/donation/${FUNDRAISER_ID}/`);
    await page.click('input[name="amount"][value="other"]');
    await page.fill('input[name="other_amount"]', '75');
    await page.fill('#id_name', 'Custom Amount Donor');
    await page.fill('#id_email', 'custom@test.com');
    await page.click('input[value="Donate now"]');

    await expect(page.locator('body')).toContainText('Please confirm your information');
    await expect(page.locator('body')).toContainText('75');
  });

  test('non-numeric "Other" amount shows validation error', async ({ page }) => {
    await page.goto(`/team_fundraising/donation/${FUNDRAISER_ID}/`);
    await page.click('input[name="amount"][value="other"]');
    // input[type=number] rejects non-numeric values; change to text so the browser
    // allows the value to reach the server for Django-side validation
    await page.locator('input[name="other_amount"]').evaluate((el: HTMLInputElement) => {
      el.type = 'text';
    });
    await page.fill('input[name="other_amount"]', 'notanumber');
    await page.fill('#id_name', 'Bad Donor');
    await page.fill('#id_email', 'bad@test.com');
    await page.click('input[value="Donate now"]');

    await expect(page.locator('.alert-danger').first()).toBeVisible();
    await expect(page).toHaveURL(/\/donation\//);
  });

  test('anonymous checkbox is present', async ({ page }) => {
    await page.goto(`/team_fundraising/donation/${FUNDRAISER_ID}/`);
    await expect(page.locator('#id_anonymous')).toBeVisible();
    // Can check it
    await page.check('#id_anonymous');
    await expect(page.locator('#id_anonymous')).toBeChecked();
  });
});

// ── 3. New User Signup ────────────────────────────────────────────────────────

test.describe('3. New User Signup', () => {
  test('signup form shows all required fields', async ({ page }) => {
    await page.goto(`/team_fundraising/accounts/signup/${CAMPAIGN_ID}/`);
    await expect(page.locator('#id_name')).toBeVisible();
    await expect(page.locator('#id_goal')).toBeVisible();
    await expect(page.locator('#id_email')).toBeVisible();
    await expect(page.locator('#id_username')).toBeVisible();
    await expect(page.locator('#id_password1')).toBeVisible();
    await expect(page.locator('#id_password2')).toBeVisible();
    await expect(page.locator('#signup-submit-btn')).toBeVisible();
  });

  test('valid new user signup → auto-login and success message', async ({ page }) => {
    const uniqueUser = `e2e_${Date.now()}`;
    await page.goto(`/team_fundraising/accounts/signup/${CAMPAIGN_ID}/`);

    await page.fill('#id_name', 'E2E Test Fundraiser');
    await page.fill('#id_goal', '1000');
    await page.fill('#id_email', `${uniqueUser}@test.com`);
    await page.fill('#id_username', uniqueUser);
    await page.fill('#id_password1', 'TestPass789!');
    await page.fill('#id_password2', 'TestPass789!');
    await enableSignupButton(page);
    await page.click('#signup-submit-btn');

    // Redirected to the new fundraiser page
    await expect(page).toHaveURL(/\/fundraiser\//);
    await expect(page.locator('.alert-primary')).toContainText('Thank you for signing up');
  });

  test('existing username + wrong password → clear error message', async ({ page }) => {
    await page.goto(`/team_fundraising/accounts/signup/${CAMPAIGN_ID}/`);
    await page.fill('#id_name', 'Test');
    await page.fill('#id_goal', '500');
    await page.fill('#id_email', 'x@test.com');
    await page.fill('#id_username', TEST_USER.username); // Existing username
    await page.fill('#id_password1', 'WrongPassword1!');
    await page.fill('#id_password2', 'WrongPassword1!');
    await enableSignupButton(page);
    await page.click('#signup-submit-btn');

    // The "password entered is incorrect" message is rendered via Django messages
    // as .alert-primary (not .alert-danger which is reserved for form field errors)
    await expect(page.locator('.alert-primary').filter({ hasText: 'password entered is incorrect' })).toBeVisible();
  });

  test('mismatched passwords → validation error', async ({ page }) => {
    const uniqueUser = `e2e_mismatch_${Date.now()}`;
    await page.goto(`/team_fundraising/accounts/signup/${CAMPAIGN_ID}/`);
    await page.fill('#id_name', 'Mismatch Test');
    await page.fill('#id_email', `${uniqueUser}@test.com`);
    await page.fill('#id_username', uniqueUser);
    await page.fill('#id_password1', 'TestPass789!');
    await page.fill('#id_password2', 'DifferentPass999!'); // Mismatch
    await page.evaluate(() => {
      // Remove the onsubmit JS validator (checkSignupForm returns false on mismatched passwords)
      // and HTML5 required attributes so the form reaches the server for Django-side validation.
      // Also clear goal so fundraiser_form is invalid (server-side code assumes user_form is also valid).
      const form = document.querySelector('form') as HTMLFormElement;
      if (form) form.removeAttribute('onsubmit');
      document.querySelectorAll<HTMLInputElement>('input[required], textarea[required]').forEach(el => {
        el.removeAttribute('required');
      });
      const goalInput = document.querySelector<HTMLInputElement>('input[name="goal"]');
      if (goalInput) goalInput.value = '';
    });
    await enableSignupButton(page);
    await page.click('#signup-submit-btn');

    // Server-side form field errors render as .alert-danger
    await expect(page.locator('.alert-danger').first()).toBeVisible();
    await expect(page).toHaveURL(/\/signup\//);
  });

  test('missing required fields → form stays with errors', async ({ page }) => {
    await page.goto(`/team_fundraising/accounts/signup/${CAMPAIGN_ID}/`);
    await page.evaluate(() => {
      // Remove the onsubmit JS validator and HTML5 required attributes
      // so the completely empty form reaches the server for Django-side validation.
      const form = document.querySelector('form') as HTMLFormElement;
      if (form) form.removeAttribute('onsubmit');
      document.querySelectorAll<HTMLInputElement>('input[required], textarea[required]').forEach(el => {
        el.removeAttribute('required');
      });
    });
    await enableSignupButton(page);
    await page.click('#signup-submit-btn');

    // Server-side form field errors render as .alert-danger
    await expect(page.locator('.alert-danger').first()).toBeVisible();
    await expect(page).toHaveURL(/\/signup\//);
  });
});

// ── 4. Login & Logout ─────────────────────────────────────────────────────────

test.describe('4. Login & Logout', () => {
  test('valid login redirects to update_fundraiser', async ({ page }) => {
    await page.goto('/team_fundraising/accounts/login/');
    await page.fill('#id_username', TEST_USER.username);
    await page.fill('#id_password', TEST_USER.password);
    await page.click('input[value="login"]');

    await expect(page).toHaveURL('/team_fundraising/accounts/update_fundraiser/');
  });

  test('invalid credentials → error message stays on login page', async ({ page }) => {
    await page.goto('/team_fundraising/accounts/login/');
    await page.fill('#id_username', 'nonexistentuser');
    await page.fill('#id_password', 'wrongpass');
    await page.click('input[value="login"]');

    await expect(page.locator('p')).toContainText("didn't match");
    await expect(page).toHaveURL(/\/login/);
  });

  test('logout clears session', async ({ page }) => {
    // Log in first
    await page.goto('/team_fundraising/accounts/login/');
    await page.fill('#id_username', TEST_USER.username);
    await page.fill('#id_password', TEST_USER.password);
    await page.click('input[value="login"]');
    await expect(page).toHaveURL(/update_fundraiser/);

    // Logout via nav button
    await page.locator('form[action*="logout"] button[type="submit"]').click();
    await page.waitForLoadState('networkidle');

    // Should no longer be on an authenticated page
    await expect(page).not.toHaveURL(/update_fundraiser/);
    // The "Join" / "Login" links should be visible, not "Edit"
    await expect(page.locator('a:has-text("Login")')).toBeVisible();
  });

  test('visiting login-required page while logged out redirects to login', async ({ page }) => {
    await page.goto('/team_fundraising/accounts/update_fundraiser/');
    await expect(page).toHaveURL(/\/login/);
  });
});

// ── 5. Fundraiser Management (logged in as smoke_test_user) ──────────────────

test.describe('5. Fundraiser Management', () => {
  test.use({ storageState: TEST_USER_AUTH });

  test('update_fundraiser page loads with existing fundraiser data', async ({ page }) => {
    await page.goto('/team_fundraising/accounts/update_fundraiser/');
    await expect(page.locator('#id_name')).toHaveValue('Smoke Test Fundraiser');
    await expect(page.locator('#id_goal')).toBeVisible();
    await expect(page.locator('button[type="submit"]:has-text("Save Changes")')).toBeVisible();
    await expect(page.locator('a:has-text("Change Password")')).toBeVisible();
  });

  test('saving changes redirects to fundraiser page with success message', async ({ page }) => {
    await page.goto('/team_fundraising/accounts/update_fundraiser/');
    await page.fill('#id_name', 'Smoke Test Fundraiser Updated');
    await page.click('button[type="submit"]:has-text("Save Changes")');

    await expect(page).toHaveURL(/\/fundraiser\//);
    await expect(page.locator('.alert-primary')).toContainText('Your information was updated');

    // Restore original name
    await page.goto('/team_fundraising/accounts/update_fundraiser/');
    await page.fill('#id_name', 'Smoke Test Fundraiser');
    await page.click('button[type="submit"]:has-text("Save Changes")');
  });

  test('Edit button is visible on own fundraiser page', async ({ page }) => {
    await page.goto(`/team_fundraising/${CAMPAIGN_ID}/`);
    await page.locator('[data-filter-name*="smoke test fundraiser"]').click();
    await expect(page).toHaveURL(/\/fundraiser\//);
    await expect(page.locator('a.btn-secondary:has-text("Edit")')).toBeVisible();
  });

  test('Edit button is NOT visible on another user\'s fundraiser page', async ({ page }) => {
    await page.goto(`/team_fundraising/fundraiser/${FUNDRAISER_ID}/`); // "First Fundraiser", owned by a different user
    await expect(page.locator('a.btn-secondary:has-text("Edit")')).not.toBeVisible();
  });

  test('campaign home page shows "Edit my profile" for logged-in user', async ({ page }) => {
    await page.goto(`/team_fundraising/${CAMPAIGN_ID}/`);
    await expect(page.locator('a:has-text("Edit my profile")')).toBeVisible();
    // "Create a fundraiser page" should NOT be shown when logged in
    await expect(page.locator('a:has-text("Create a fundraiser page")')).not.toBeVisible();
  });
});

// ── 6. Password Management ───────────────────────────────────────────────────

test.describe('6. Password Management', () => {
  test.use({ storageState: PW_USER_AUTH });

  test('wrong current password → error stays on change_password page', async ({ page }) => {
    await page.goto('/team_fundraising/accounts/change_password/');
    await expect(page.locator('h3')).toContainText('Change Password');
    await page.fill('#id_old_password', 'WrongOldPassword!');
    await page.fill('#id_new_password1', 'NewPass789!');
    await page.fill('#id_new_password2', 'NewPass789!');
    await page.click('input[value="Change Password"]');

    // Stays on change_password page (no redirect on error)
    await expect(page).toHaveURL(/\/change_password/);
  });

  test('valid password change → success message on update_fundraiser page', async ({ page }) => {
    await page.goto('/team_fundraising/accounts/change_password/');
    await page.fill('#id_old_password', PW_USER.password);
    await page.fill('#id_new_password1', 'SmokePwNew456!');
    await page.fill('#id_new_password2', 'SmokePwNew456!');
    await page.click('input[value="Change Password"]');

    await expect(page).toHaveURL(/\/update_fundraiser/);
    await expect(page.locator('.alert-primary')).toContainText('Your password has been updated');
  });
});

// ── 7. Password Reset (unauthenticated) ──────────────────────────────────────

test.describe('7. Password Reset', () => {
  test('password reset form accepts an email and shows confirmation', async ({ page }) => {
    await page.goto('/team_fundraising/accounts/password_reset/');
    await expect(page.locator('#id_email')).toBeVisible();

    await page.fill('#id_email', TEST_USER.email);
    await page.click('input[type="submit"], button[type="submit"]');

    await expect(page).toHaveURL(/\/password_reset\/done/);
  });
});

// ── 8. Admin & Staff Functions ────────────────────────────────────────────────

test.describe('8. Admin - unauthenticated', () => {
  test('donation CSV redirects non-staff to admin login', async ({ page }) => {
    await page.goto(`/admin/donation_report_csv/${CAMPAIGN_ID}/`);
    await expect(page).toHaveURL(/\/admin\/login\//);
  });
});

test.describe('8. Admin - staff', () => {
  test.use({ storageState: ADMIN_AUTH });

  test('Django admin panel is accessible for staff', async ({ page }) => {
    await page.goto('/admin/');
    await expect(page).toHaveURL('/admin/');
    await expect(page.locator('#content h1')).toContainText('Site administration');
  });

  test('Campaign model is visible in admin', async ({ page }) => {
    await page.goto('/admin/team_fundraising/');
    await expect(page.locator('body')).toContainText('Campaigns');
  });

  test('donation CSV report returns CSV content', async ({ page }) => {
    const response = await page.request.get(`/admin/donation_report_csv/${CAMPAIGN_ID}/`);
    expect(response.status()).toBe(200);
    const contentType = response.headers()['content-type'];
    expect(contentType).toContain('text/csv');
  });
});
