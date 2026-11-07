import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("local production HTTPS account task habit plan focus and reward journey", async ({
  page,
  browser,
}) => {
  const origin = "https://localhost:8443";
  const email = `release-${crypto.randomUUID()}@example.com`;
  const password = "Synthetic release passphrase";
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Release Check");
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
  const cookie = (await page.context().cookies()).find(
    (c) => c.name === "devtreck_session",
  );
  expect(cookie?.secure).toBe(true);
  expect(cookie?.httpOnly).toBe(true);
  expect(cookie?.sameSite).toBe("Strict");
  const csrf = (await (await page.request.get("/api/auth/csrf")).json())
    .csrf_token;
  const headers = { Origin: origin, "X-CSRF-Token": csrf };
  const habit = await (
    await page.request.post("/api/tasks", {
      headers,
      data: { title: "Release habit", task_type: "daily" },
    })
  ).json();
  expect(habit.id).toBeTruthy();
  const one = await (
    await page.request.post("/api/tasks", {
      headers,
      data: { title: "Release milestone" },
    })
  ).json();
  expect(
    (
      await page.request.post(`/api/tasks/${one.id}/complete`, { headers })
    ).status(),
  ).toBe(200);
  expect(
    (
      await page.request.post(`/api/tasks/${habit.id}/complete`, { headers })
    ).status(),
  ).toBe(200);
  const child = await (
    await page.request.post(`/api/tasks/${habit.id}/checklist`, {
      headers,
      data: { title: "Review" },
    })
  ).json();
  expect(child.id).toBeTruthy();
  await page.getByRole("link", { name: "Daily plan", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Plan your day", exact: true }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Focus", exact: true }).click();
  await page.getByRole("button", { name: "Start focus", exact: true }).click();
  await page.getByRole("button", { name: "Pause", exact: true }).click();
  await page.reload();
  await expect(
    page.getByRole("button", { name: "Resume", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Stop session", exact: true }).click();
  await page.getByRole("link", { name: "Progress", exact: true }).click();
  await expect(page.getByText("15 XP", { exact: true })).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.screenshot({
    path: "test-results/release-desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 360, height: 900 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: "test-results/release-mobile.png",
    fullPage: true,
  });
  const foreign = await browser.newContext({
    baseURL: origin,
    ignoreHTTPSErrors: true,
  });
  expect((await foreign.request.get(`/api/tasks/${habit.id}`)).status()).toBe(
    401,
  );
  await foreign.close();
  expect(
    (
      await page.request.post("/api/tasks", {
        headers: { Origin: "https://evil.example", "X-CSRF-Token": csrf },
        data: { title: "Rejected" },
      })
    ).status(),
  ).toBe(403);
  expect(
    (
      await page.request.post("/api/tasks", {
        headers: { Origin: origin },
        data: { title: "Rejected" },
      })
    ).status(),
  ).toBe(403);
  const ready = await page.request.get("/ready");
  expect(ready.status()).toBe(200);
  expect(ready.headers()["x-content-type-options"]).toBe("nosniff");
  expect(ready.headers()["strict-transport-security"]).toContain("max-age=");
  expect((await page.request.get("/api/../docs")).status()).toBe(404);
  expect(
    (
      await page.request.delete("/api/users/me", {
        headers,
        data: { current_password: password, confirm: true },
      })
    ).status(),
  ).toBe(204);
  await page.reload();
  await expect(page).toHaveURL(/\/login/);
});
