import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
async function enter(page: Page) {
  const email = `productive-${crypto.randomUUID()}@example.com`;
  const password = "Productivity test passphrase";
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Focused User");
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
}
test("planning checklists and focus persist without completing tasks", async ({
  page,
  browser,
}) => {
  await enter(page);
  const csrf = (await (await page.request.get("/api/auth/csrf")).json())
    .csrf_token;
  const headers = { Origin: "http://127.0.0.1:3100", "X-CSRF-Token": csrf };
  const parent = await (
    await page.request.post("/api/tasks", {
      headers,
      data: {
        title: "Study chapter",
        task_type: "daily",
        priority: "high",
        estimated_minutes: 25,
      },
    })
  ).json();
  await page.request.post("/api/tasks", {
    headers,
    data: { title: "Review notes", task_type: "daily", priority: "low" },
  });
  await page.getByRole("link", { name: "Daily plan", exact: true }).click();
  await expect(
    page.locator(".plan-items strong").filter({ hasText: /^Study chapter$/ }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Make priority Study chapter", exact: true })
    .click();
  await expect(
    page.getByRole("button", {
      name: "Top priority Study chapter",
      exact: true,
    }),
  ).toHaveAttribute("aria-pressed", "true");
  await page
    .getByRole("button", { name: "Move Study chapter down", exact: true })
    .click();
  await page.reload();
  await expect(page.locator(".plan-items > li").first()).toContainText(
    "Review notes",
  );
  await expect(page.getByText(/tasks without estimates/)).toBeVisible();
  await page.getByRole("link", { name: "All tasks", exact: true }).click();
  await page
    .getByRole("article", { name: "Study chapter", exact: true })
    .getByRole("button", { name: "Study chapter", exact: true })
    .click();
  const dialog = page.getByRole("dialog");
  const checklist = dialog.getByRole("region", {
    name: "Task checklist",
    exact: true,
  });
  await checklist.getByLabel("New checklist item").fill("Read section");
  await checklist
    .getByRole("button", { name: "Add checklist item", exact: true })
    .click();
  await expect(
    checklist.getByRole("checkbox", { name: "Read section", exact: true }),
  ).toBeVisible();
  await checklist.getByLabel("New checklist item").fill("Write notes");
  await checklist
    .getByRole("button", { name: "Add checklist item", exact: true })
    .click();
  await expect(
    checklist.getByRole("checkbox", { name: "Write notes", exact: true }),
  ).toBeVisible();
  await checklist
    .getByRole("checkbox", { name: "Read section", exact: true })
    .click();
  await expect(
    checklist.getByRole("checkbox", { name: "Read section", exact: true }),
  ).toBeChecked();
  await checklist
    .getByRole("checkbox", { name: "Write notes", exact: true })
    .click();
  await expect(
    checklist.getByRole("checkbox", { name: "Read section", exact: true }),
  ).toBeChecked();
  await expect(
    checklist.getByRole("checkbox", { name: "Write notes", exact: true }),
  ).toBeChecked();
  await expect(checklist.getByRole("heading")).toContainText("2 of 2 complete");
  await checklist
    .getByRole("button", { name: "Move Write notes up", exact: true })
    .click();
  await expect(checklist.locator("li").first()).toContainText("Write notes");
  await checklist.getByRole("button",{name:"Edit Read section",exact:true}).click();
  await checklist.getByLabel("Edit checklist item").fill("Review section");
  await checklist.getByRole("button",{name:"Save checklist item",exact:true}).click();
  await expect(checklist.getByRole("checkbox",{name:"Review section",exact:true})).toBeChecked();
  await checklist.getByRole("button",{name:"Delete Review section",exact:true}).click();
  await checklist.getByRole("button",{name:"Keep item",exact:true}).click();
  await checklist.getByRole("button",{name:"Delete Review section",exact:true}).click();
  await checklist.getByRole("button",{name:"Confirm item delete",exact:true}).click();
  await expect(checklist.getByRole("checkbox",{name:"Review section",exact:true})).toHaveCount(0);
  await dialog.getByRole("button", { name: "Close", exact: true }).click();
  await expect(
    page.getByRole("article", { name: "Study chapter", exact: true }),
  ).toContainText("Checklist: 1 of 1 complete");
  await page.getByRole("link", { name: "Focus", exact: true }).click();
  await page
    .getByLabel("Associated task", { exact: true })
    .selectOption(parent.id);
  await page.getByLabel("Focus minutes").fill("1");
  await page.getByRole("button", { name: "Start focus", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Pause", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Pause", exact: true }).click();
  await expect(page.getByText("Paused — take your time.")).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("button", { name: "Resume", exact: true }),
  ).toBeVisible();
  const other = await browser.newContext({
    baseURL: "http://127.0.0.1:3100",
    storageState: await page.context().storageState(),
  });
  const tab = await other.newPage();
  await tab.goto("/app/focus");
  await expect(
    tab.getByRole("button", { name: "Resume", exact: true }),
  ).toBeVisible();
  await tab.getByRole("button", { name: "Resume", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Pause", exact: true }),
  ).toBeVisible({ timeout: 10000 });
  await page.getByRole("button", { name: "Stop session", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Start focus", exact: true }),
  ).toBeVisible();
  await expect(page.locator(".focus-history")).toContainText("stopped");
  await other.close();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.screenshot({
    path: "test-results/focus-desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 360, height: 900 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: "test-results/focus-mobile.png",
    fullPage: true,
  });
  const saved = await (
    await page.request.get(`/api/tasks/${parent.id}`)
  ).json();
  expect(saved.status).toBe("pending");
  expect(saved.streak.today_completed).toBe(false);
  await page.getByLabel("Session type", { exact: true }).selectOption("break");
  await page.getByRole("button", { name: "Start break", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Stop session", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Stop session", exact: true }).click();
});
