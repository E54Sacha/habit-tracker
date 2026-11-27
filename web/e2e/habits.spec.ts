import { expect, test } from "@playwright/test";

// Next.js keeps the previous page hidden in the DOM after a navigation, so look inside the visible <main> only.
const board = (page: import("@playwright/test").Page) => page.locator("main:visible");

test("sign up, create a habit, tick it, log out and back in", async ({ page }) => {
  const email = `e2e-${Date.now()}@example.com`;
  const password = "e2e-password-123";

  await page.goto("/");
  await page.getByRole("link", { name: "Create an account" }).click();
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Create account" }).click();

  await expect(page).toHaveURL(/\/habits$/);
  await expect(board(page).getByText("No habits yet.")).toBeVisible();

  await board(page).getByLabel("New habit").fill("Read 10 pages");
  await board(page).getByRole("button", { name: "Add habit" }).click();
  const tick = board(page).getByRole("button", { name: /Read 10 pages:/ });
  await expect(tick).toHaveAttribute("aria-pressed", "false");

  await tick.click();
  await expect(tick).toHaveAttribute("aria-pressed", "true");
  await expect(board(page).getByText("All done for today.")).toBeVisible();
  await expect(board(page).getByText("1 day in a row")).toBeVisible();

  await page.getByRole("button", { name: "Log out" }).click();
  await expect(page).toHaveURL(/\/$/);
  await page.goto("/habits");
  await expect(page).toHaveURL(/\/login$/); // logged out: the habits page is closed

  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page).toHaveURL(/\/habits$/);
  await expect(board(page).getByRole("button", { name: /Read 10 pages:/ })).toHaveAttribute("aria-pressed", "true");
});

test("try as a guest shows a filled demo account", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Try it as a guest" }).click();
  await expect(page).toHaveURL(/\/habits$/);
  await expect(board(page).getByText("You’re using a demo account", { exact: false })).toBeVisible();
  await expect(board(page).getByRole("listitem")).toHaveCount(4);
  await expect(board(page).getByText(/23 days in a row/)).toBeVisible();
});
