import { test, expect } from '@playwright/test';

test('drag and drop displays results', async ({ page }) => {
  await page.goto('/');
  
  await expect(page.locator('h1')).toHaveText('Diamond Solver Pro');
  
  await page.route('http://localhost:4000/upload', async route => {
    const json = { part1: 12345, part2: 67890 };
    await route.fulfill({ json });
  });

  await page.setInputFiles('input[type="file"]', {
    name: 'seed.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from('Blueprint 1: 4 2 3 14 2 7 1 5 3')
  });

  await expect(page.getByText('Part 1 Score')).toBeVisible();
  await expect(page.getByText('12345')).toBeVisible();
  await expect(page.getByText('Part 2 Score')).toBeVisible();
  await expect(page.getByText('67890')).toBeVisible();
});

test('displays error message when API returns 400', async ({ page }) => {
  await page.goto('/');
  
  await page.route('http://localhost:4000/upload', async route => {
    await route.fulfill({
      status: 400,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Error parsing line 1: Expected 10 integers' })
    });
  });

  await page.setInputFiles('input[type="file"]', {
    name: 'bad_seed.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from('Blueprint 1: 4 2 3 14 2 7 1 5')
  });

  await expect(page.getByText('Error parsing line 1: Expected 10 integers')).toBeVisible();
  await expect(page.getByText('Part 1 Score')).not.toBeVisible();
});

test('displays server error when API returns 500', async ({ page }) => {
  await page.goto('/');
  
  await page.route('http://localhost:4000/upload', async route => {
    await route.fulfill({
      status: 500,
      contentType: 'text/plain',
      body: 'Internal Server Error'
    });
  });

  await page.setInputFiles('input[type="file"]', {
    name: 'seed.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from('Blueprint 1: 4 2 3 14 2 7 1 5 3')
  });

  await expect(page.getByText('Internal Server Error')).toBeVisible();
  await expect(page.getByText('Part 1 Score')).not.toBeVisible();
});

test('displays error message when non-txt file is uploaded', async ({ page }) => {
  await page.goto('/');
  
  await page.route('http://localhost:4000/upload', async route => {
    await route.fulfill({
      status: 400,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Invalid file type. Only .txt files are allowed.' })
    });
  });

  await page.setInputFiles('input[type="file"]', {
    name: 'image.png',
    mimeType: 'image/png',
    buffer: Buffer.from('fake image data')
  });

  await expect(page.getByText('Invalid file type. Only .txt files are allowed.')).toBeVisible();
  await expect(page.getByText('Part 1 Score')).not.toBeVisible();
});

test('displays loading spinner while request is in progress', async ({ page }) => {
  await page.goto('/');
  
  let resolveResponse: any;
  const responsePromise = new Promise(resolve => {
    resolveResponse = resolve;
  });

  await page.route('http://localhost:4000/upload', async route => {
    await responsePromise;
    const json = { part1: 12345, part2: 67890 };
    await route.fulfill({ json });
  });

  await page.setInputFiles('input[type="file"]', {
    name: 'seed.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from('Blueprint 1: 4 2 3 14 2 7 1 5 3')
  });

  // Verify loader is visible (it has class animate-spin)
  await expect(page.locator('.animate-spin')).toBeVisible();

  // Resolve the mock response
  resolveResponse();

  // Verify results are visible and loader is gone
  await expect(page.getByText('Part 1 Score')).toBeVisible();
  await expect(page.locator('.animate-spin')).not.toBeVisible();
});


