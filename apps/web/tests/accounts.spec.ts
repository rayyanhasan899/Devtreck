import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
const password = "Browser test passphrase 2026";
const email = () => `browser-${crypto.randomUUID()}@example.com`;
async function signup(page: Page, address: string) {
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Browser User");
  await page.getByLabel("Email address").fill(address);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page
    .getByRole("button", { name: "Create account", exact: true })
    .click();
  await expect(page).toHaveURL(/registered=true/);
}
async function login(page: Page, address: string, secret = password) {
  await page.getByLabel("Email address").fill(address);
  await page.getByLabel("Password", { exact: true }).fill(secret);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page).toHaveURL(/\/app$/);
}

test("desktop account lifecycle and accessible settings", async ({ page }) => {
  const address = email();
  await signup(page, address);
  await login(page, address);
  await page.getByRole("link", { name: "Settings", exact: true }).click();
  await page.getByLabel("Your name").fill("Updated User");
  await page.getByLabel("Time zone", { exact: true }).fill("Asia/Karachi");
  await page.getByLabel("Appearance").selectOption("dark");
  await page.getByRole("button", { name: "Save preferences" }).click();
  await expect(page.getByRole("status")).toContainText("Changes saved");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.reload();
  await expect(page.getByLabel("Your name")).toHaveValue("Updated User");
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.screenshot({
    path: "test-results/settings-desktop.png",
    fullPage: true,
  });
  await page
    .getByRole("button", { name: "Delete my account", exact: true })
    .click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).not.toBeVisible();
  const newAddress = email();
  await page.getByLabel("Email address", { exact: true }).fill(newAddress);
  await page.getByLabel("Current password for email change").fill(password);
  await page.getByRole("button", { name: "Update email" }).click();
  await expect(page).toHaveURL(/reason=updated/);
  await login(page, newAddress);
  await page.getByRole("link", { name: "Settings", exact: true }).click();
  await page.getByLabel("Current password", { exact: true }).fill(password);
  await page
    .getByLabel("New password", { exact: true })
    .fill(password + " changed");
  await page
    .getByRole("button", { name: "Change password", exact: true })
    .click();
  await expect(page).toHaveURL(/reason=updated/);
  await login(page, newAddress, password + " changed");
  await page.getByRole("link", { name: "Settings", exact: true }).click();
  await page
    .getByRole("button", { name: "Delete my account", exact: true })
    .click();
  await page
    .getByLabel("Confirm your current password")
    .fill(password + " changed");
  await page.getByRole("checkbox").check();
  await page
    .getByRole("button", { name: "Permanently delete account", exact: true })
    .click();
  await expect(page).toHaveURL(/reason=deleted/);
  await page.goto("/app/settings");
  await expect(page).toHaveURL(/\/login/);
});

test("protected navigation invalid login and revoked session", async ({
  page,
  context,
  playwright,
}) => {
  await page.goto("/app/settings");
  await expect(page).toHaveURL(/\/login/);
  await page.getByLabel("Email address").fill("unknown@example.com");
  await page.getByLabel("Password", { exact: true }).fill("wrong");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.locator("p[role=alert]")).toContainText("incorrect");
  const address = email();
  await signup(page, address);
  await login(page, address);
  const request = await playwright.request.newContext({
    baseURL: "http://127.0.0.1:3100",
    storageState: await context.storageState(),
  });
  const token = (await (await request.get("/api/auth/csrf")).json()).csrf_token;
  expect(
    (
      await request.post("/api/auth/logout", {
        headers: { Origin: "http://127.0.0.1:3100", "X-CSRF-Token": token },
      })
    ).status(),
  ).toBe(204);
  await request.dispose();
  await page.evaluate(() => window.dispatchEvent(new Event("focus")));
  await expect(page).toHaveURL(/reason=expired/);
  await expect(page.getByRole("status")).toContainText("session has ended");
});

test("mobile keyboard navigation logout and network failure", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/signup");
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Skip to content" }),
  ).toBeFocused();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  const address = email();
  await signup(page, address);
  await login(page, address);
  await page.getByRole("link", { name: "Settings", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Account settings", exact: true }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: "test-results/settings-mobile.png",
    fullPage: true,
  });
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.setViewportSize({ width: 768, height: 1024 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: "test-results/settings-tablet.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.route("**/api/users/me", (route) =>
    route.request().method() === "PATCH" ? route.abort() : route.continue(),
  );
  await page.getByLabel("Your name").fill("Unsaved Name");
  await page.getByRole("button", { name: "Save preferences" }).click();
  await expect(page.locator("p[role=alert]")).toContainText(
    "Unable to connect",
  );
  await page.unroute("**/api/users/me");
  await page.reload();
  await expect(page.getByLabel("Your name")).toHaveValue("Browser User");
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page).toHaveURL(/\/login$/);
  await page.goto("/app");
  await expect(page).toHaveURL(/\/login/);
});
