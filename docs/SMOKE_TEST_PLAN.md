# Manual Smoke Test Plan

This checklist covers all major user-facing functionality. Run it against staging or production
before a release, or after significant changes.

## Prerequisites

- A running instance of the site (dev: `python3 manage.py runserver localhost:8000`)
- At least one active Campaign exists in the database
- Test data loaded: `python3 manage.py loaddata startingdata` (optional but helpful)
- PayPal sandbox account configured for donation tests (or skip PayPal step and verify pending state only)
- Two browser windows/incognito sessions available for multi-user testing

---

## 1. Campaign & Fundraiser Browsing (No Login Required)

### 1a. Root / Campaign List
- [ ] Visit `/` — page loads without errors
- [ ] Active campaigns are displayed
- [ ] Clicking a campaign navigates to its campaign page

### 1b. Campaign Home Page
- [ ] Visit `/team_fundraising/` — redirects to the latest active campaign
- [ ] Visit `/team_fundraising/<campaign_id>/` — page loads
- [ ] Fundraisers are listed with names, photos, and totals
- [ ] Campaign total raised is displayed
- [ ] Recent donations are displayed (up to 5)
- [ ] "Sign Up" / "Donate" call-to-action buttons are visible

### 1c. Fundraiser Page
- [ ] Click a fundraiser from the campaign page
- [ ] Fundraiser name, team, goal, photo, and message are displayed
- [ ] Progress bar / total raised is shown
- [ ] List of donations is shown (non-anonymous donors visible, anonymous shown as "Anonymous")
- [ ] "Donate" button is visible and links to `/team_fundraising/donation/<fundraiser_id>/`
- [ ] "Edit Fundraiser" link is NOT visible when not logged in

### 1d. About Page
- [ ] Visit `/team_fundraising/about/<campaign_id>/` — page loads with campaign info

---

## 2. Donor Donation Flow (No Login Required)

### 2a. Donation Form
- [ ] Click "Donate" from a fundraiser page
- [ ] Donation form loads at `/team_fundraising/donation/<fundraiser_id>/`
- [ ] Pre-set amount buttons are shown
- [ ] "Other" amount field appears (or is available to select)
- [ ] Required fields: Name, Email, Amount
- [ ] Optional fields: Message, Anonymous checkbox, Tax receipt fields (name, address, city, province, country, postal code)
- [ ] Submit with missing required fields → validation errors shown, no donation created

### 2b. Valid Donation Submission
- [ ] Fill in Name, Email, select an amount
- [ ] Submit form → redirected to PayPal form page
- [ ] "Thank you for your donation" message is shown
- [ ] A pending Donation record exists in Django admin at `/admin/`

### 2c. Anonymous Donation
- [ ] Check "Anonymous" checkbox on donation form
- [ ] Submit → after payment completes, donor name does NOT appear on fundraiser page

### 2d. Custom Amount
- [ ] Select "Other" amount option
- [ ] Enter a custom numeric amount → form submits successfully
- [ ] Enter a non-numeric value → validation error shown

### 2e. PayPal Flow (requires sandbox)
- [ ] On PayPal form page, click the PayPal button
- [ ] Redirected to PayPal sandbox login/payment
- [ ] Complete sandbox payment
- [ ] Redirected back to fundraiser page
- [ ] Donation now shows as "paid" in Django admin
- [ ] Donor total raised updated on fundraiser page
- [ ] Donor receives confirmation email (check sandbox inbox or Django logs)
- [ ] Fundraiser owner receives notification email

---

## 3. New User Signup

### 3a. Signup Form Loads
- [ ] Visit `/team_fundraising/accounts/signup/<campaign_id>/`
- [ ] Form shows: Email, Username, Password, Password confirm, ReCAPTCHA
- [ ] Form shows: Fundraiser name, Team (optional), Goal, Photo (optional), Message (optional)

### 3b. Valid New User Signup
- [ ] Fill in all required fields with a unique username/email
- [ ] Complete ReCAPTCHA (or confirm it is bypassed in dev/test mode)
- [ ] Submit → user is logged in automatically
- [ ] Redirected to fundraiser page with success message
- [ ] New fundraiser appears on campaign page
- [ ] Signup confirmation email is sent to the provided email address (check logs in dev)

### 3c. Duplicate Username / Wrong Password
- [ ] Submit signup form with an existing username but wrong password → error shown
- [ ] Submit signup form with an existing username and correct password → logs in existing user, creates new fundraiser

### 3d. Validation Errors
- [ ] Submit with missing required fields → appropriate field errors shown
- [ ] Submit with mismatched passwords → error shown
- [ ] Submit with invalid email → error shown

---

## 4. Existing User: Login, Logout, and Adding a New Campaign

### 4a. Login
- [ ] Visit `/team_fundraising/accounts/login/`
- [ ] Enter valid credentials → redirected (to update_fundraiser or next URL)
- [ ] Enter invalid credentials → error message shown

### 4b. Logout
- [ ] Click logout → session ends, redirected to logged-out page
- [ ] Visiting a login-required page after logout → redirected to login

### 4c. Existing Logged-In User Adds Another Campaign Fundraiser
- [ ] While logged in, visit `/team_fundraising/accounts/signup/<different_campaign_id>/`
- [ ] Username and email are pre-filled and read-only
- [ ] Fill in fundraiser details and submit
- [ ] New Fundraiser created for the same User under the new Campaign
- [ ] Confirmation email sent

### 4d. One-Click Signup
- [ ] While logged in, visit `/team_fundraising/accounts/signup_logged_in/<campaign_id>/`
- [ ] System auto-creates a new Fundraiser copying previous campaign's data
- [ ] Redirected to update_fundraiser with confirmation message
- [ ] New fundraiser visible on campaign page

---

## 5. Fundraiser Page Management (Login Required)

### 5a. Update Fundraiser
- [ ] While logged in, visit `/team_fundraising/accounts/update_fundraiser/`
- [ ] Form shows current fundraiser data (name, team, goal, photo, message)
- [ ] User email field is editable
- [ ] Edit name, team, goal, or message → save → changes reflected on fundraiser page
- [ ] Upload a new photo → thumbnail auto-generated, new photo shown on fundraiser page
- [ ] All fields are disabled if the campaign is inactive

### 5b. Edit Link on Fundraiser Page
- [ ] While logged in and viewing your own fundraiser page, "Edit Fundraiser" link is visible
- [ ] Clicking it takes you to `/team_fundraising/accounts/update_fundraiser/`
- [ ] While logged in and viewing ANOTHER user's fundraiser, "Edit Fundraiser" is NOT visible

---

## 6. Password Management

### 6a. Change Password (Logged In)
- [ ] Visit `/team_fundraising/accounts/change_password/`
- [ ] Enter wrong current password → error shown
- [ ] Enter correct current password + new password (×2) → success
- [ ] Remain logged in after change
- [ ] Redirected to update_fundraiser page

### 6b. Password Reset (Not Logged In)
- [ ] Visit `/team_fundraising/accounts/password_reset/`
- [ ] Enter email address → "email sent" confirmation page shown
- [ ] Check email for reset link (or check Django logs in dev)
- [ ] Follow reset link → reset confirm page loads
- [ ] Enter new password (×2) → success page with login link
- [ ] Log in with new password → works
- [ ] Old password no longer works

---

## 7. Admin / Staff Functions

### 7a. Django Admin
- [ ] Log in as a staff/superuser at `/admin/`
- [ ] Campaign, Fundraiser, Donation models are accessible
- [ ] Can view and modify records

### 7b. Donation Report CSV
- [ ] As staff user, visit `/admin/donation_report_csv/<campaign_id>/`
- [ ] CSV file is downloaded
- [ ] CSV contains correct columns: donor name, email, amount, address, date, etc.
- [ ] Only "paid" donations are included
- [ ] Non-staff user visiting this URL → 403 or redirect to login

---

## Notes

- **PayPal IPN in dev**: IPN callbacks won't fire in local dev unless using ngrok or similar.
  You can manually set `payment_status='paid'` in the Django admin to simulate a completed payment.
- **Emails in dev**: If AWS credentials are not set, emails are skipped and logged at DEBUG level.
  Check server logs or use Django's console email backend to verify email content.
- **ReCAPTCHA in dev/test**: Automatically disabled when `TESTING=True` or via `TEST_WITHOUT_CAPTCHA` setting.
- **Photo uploads**: Requires `media/photos/` and `media/photos_small/` directories to exist (auto-created on startup).
- **Cache**: Campaign home page is cached for 60 seconds — changes may not appear immediately.
