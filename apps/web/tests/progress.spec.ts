import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("progress displays verified rewards, honest rates, recovery and responsive activity", async ({
  page,
}) => {
  const email = `progress-${crypto.randomUUID()}@example.com`;
  const password = "Progress test passphrase";
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Progress User");
  await page.getByLabel("Email address").fill(email);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page
    .getByRole("button", { name: "Create account", exact: true })
    .click();
  await expect(page).toHaveURL(/registered=true/);
  await page.getByLabel("Email address").fill(email);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page).toHaveURL(/\/app$/);
  await page.getByRole("link", { name: "Progress", exact: true }).click();
  await expect(page.getByText("0 XP", { exact: true })).toBeVisible();
  await expect(
    page.getByText("No task completions recorded in this period."),
  ).toBeVisible();
  await expect(page.getByLabel("Today", { exact: true })).toContainText(
    "Unavailable",
  );
  const csrf = (await (await page.request.get("/api/auth/csrf")).json())
    .csrf_token;
  const headers = { Origin: "http://127.0.0.1:3100", "X-CSRF-Token": csrf };
  const task = await (
    await page.request.post("/api/tasks", {
      headers,
      data: { title: "Meaningful habit", task_type: "daily" },
    })
  ).json();
  await page.request.post(`/api/tasks/${task.id}/complete`, { headers });
  await page.getByRole("button", { name: "Refresh progress" }).click();
  await expect(page.getByText("5 XP", { exact: true })).toBeVisible();
  await expect(page.getByLabel("Today", { exact: true })).toContainText("100%");
  await expect(
    page.getByRole("article").filter({ hasText: "First completion" }),
  ).toContainText("Earned");
  await page.request.post(`/api/tasks/${task.id}/reopen`, { headers });
  await page.request.post(`/api/tasks/${task.id}/complete`, { headers });
  await page.reload();
  await expect(page.getByText("5 XP", { exact: true })).toBeVisible();
  await page.route("**/api/progress", (route) => route.abort());
  await page.getByRole("button", { name: "Refresh progress" }).click();
  await expect(page.locator(".progress-page [role=alert]")).toContainText(
    "Could not load progress",
  );
  await page.unroute("**/api/progress");
  await page.getByRole("button", { name: "Refresh progress" }).click();
  await expect(page.locator(".progress-page [role=alert]")).toHaveCount(0);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.screenshot({
    path: "test-results/progress-desktop.png",
    fullPage: true,
  });
  for (const width of [360, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
  }
  await page.setViewportSize({ width: 360, height: 900 });
  await page.screenshot({
    path: "test-results/progress-mobile.png",
    fullPage: true,
  });
  await page.request.delete(`/api/tasks/${task.id}?confirm=true`, { headers });
  await page.getByRole("button", { name: "Refresh progress" }).click();
  await expect(page.getByLabel("Today", { exact: true })).toContainText(
    "Unavailable",
  );
  await expect(page.getByText("5 XP", { exact: true })).toBeVisible();
});
