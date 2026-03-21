const fs = require('fs');
const path = require('path');
const { test, expect } = require('@playwright/test');

const RAW_COVERAGE_DIR = path.resolve(__dirname, '../../../reports/frontend/.raw-coverage');

function ensureCoverageDir() {
  fs.mkdirSync(RAW_COVERAGE_DIR, { recursive: true });
}

function toSafeFileName(value) {
  return value.replace(/[^a-zA-Z0-9_-]/g, '_');
}

let coverageClient = null;

test.beforeEach(async ({ page }) => {
  ensureCoverageDir();
  coverageClient = await page.context().newCDPSession(page);
  await coverageClient.send('Profiler.enable');
  await coverageClient.send('Profiler.startPreciseCoverage', {
    callCount: true,
    detailed: true,
  });
});

test.afterEach(async ({}, testInfo) => {
  if (!coverageClient) {
    return;
  }

  const coverage = await coverageClient.send('Profiler.takePreciseCoverage');
  await coverageClient.send('Profiler.stopPreciseCoverage');
  await coverageClient.send('Profiler.disable');

  const payload = {
    title: testInfo.title,
    workerIndex: testInfo.workerIndex,
    scripts: coverage.result || [],
  };

  const fileName = [
    toSafeFileName(testInfo.title),
    String(testInfo.workerIndex),
    String(Date.now()),
  ].join('-') + '.json';

  fs.writeFileSync(path.join(RAW_COVERAGE_DIR, fileName), JSON.stringify(payload, null, 2), 'utf8');
  coverageClient = null;
});

test.describe('Website core functionality', () => {
  test('home page renders key sections', async ({ page }) => {
    await page.goto('/');

    await expect(page).toHaveTitle(/Empower Hub 360 NC/i);
    await expect(page.locator('nav.navbar')).toBeVisible();
    await expect(page.locator('#services')).toBeVisible();
    await expect(page.locator('#contact-form')).toBeVisible();
  });

  test('health endpoint returns healthy', async ({ request }) => {
    const response = await request.get('/health');
    const payload = await response.json();

    expect(response.status()).toBe(200);
    expect(payload).toEqual({ status: 'healthy' });
  });

  test('mobile menu opens and closes', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/');

    const menuButton = page.locator('.mobile-menu');
    const navLinks = page.locator('.nav-links');

    await menuButton.click();
    await expect(navLinks).toHaveClass(/active/);

    await page.locator('body').click({ position: { x: 10, y: 10 } });
    await expect(navLinks).not.toHaveClass(/active/);
  });

  test('solutions tabs switch active panel', async ({ page }) => {
    await page.goto('/');

    const developersTab = page.locator('.tab-btn[data-tab="developers"]');
    const developersPanel = page.locator('#developers');
    const enterprisePanel = page.locator('#enterprise');

    await developersTab.click();

    await expect(developersTab).toHaveClass(/active/);
    await expect(developersPanel).toHaveClass(/active/);
    await expect(enterprisePanel).not.toHaveClass(/active/);
  });

  test('contact form submission shows success feedback', async ({ page }) => {
    await page.route('**/api/v1/consulting/consultation', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          request_id: 'test-id',
          status: 'submitted',
          message: "We'll contact you within 24 hours",
        }),
      });
    });

    await page.goto('/');

    await page.fill('#contact-form input[name="name"]', 'Test User');
    await page.fill('#contact-form input[name="email"]', 'test@example.com');
    await page.fill('#contact-form input[name="company"]', 'Example Co');
    await page.selectOption('#contact-form select[name="service_type"]', 'automation');
    await page.fill('#contact-form textarea[name="message"]', 'Need automation setup.');

    const submitButton = page.locator('#contact-form button[type="submit"]');
    await submitButton.click();

    await expect(submitButton).toHaveText('✓ Sent!');
    await expect(page.locator('#toast-container .toast')).toBeVisible();
  });

  test('chat widget sends message and renders bot response', async ({ page }) => {
    await page.route('**/api/v1/chatbot/chat', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: 'Mock assistant response',
          context: 'general',
          status: 'success',
        }),
      });
    });

    await page.goto('/');

    await page.click('#chat-trigger');
    await page.fill('#chat-input', 'Hello AI');
    await page.click('.chat-send');

    await expect(page.locator('.chat-msg.user .msg-bubble').last()).toHaveText('Hello AI');
    await expect(page.locator('.chat-msg.bot .msg-bubble').last()).toHaveText('Mock assistant response');
  });
});
