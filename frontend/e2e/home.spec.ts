import { test, expect } from '@playwright/test';

test('drag and drop displays results', async ({ page }) => {
  await page.goto('/');
  
  // Wait for the h1 to ensure page load
  await expect(page.locator('h1')).toHaveText('Diamond Solver Pro');
  
  // Mock the fetch to http://localhost:8000/upload
  await page.route('http://localhost:8000/upload', async route => {
    const json = { part1: 12345, part2: 67890 };
    await route.fulfill({ json });
  });

  // Set file directly into the hidden file input
  await page.setInputFiles('input[type="file"]', {
    name: 'seed.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from('Blueprint 1: 4 2 3 14 2 7 1 5 3')
  });

  // Verify the UI updates
  await expect(page.getByText('Part 1 Score')).toBeVisible();
  await expect(page.getByText('12345')).toBeVisible();
  await expect(page.getByText('Part 2 Score')).toBeVisible();
  await expect(page.getByText('67890')).toBeVisible();
});
