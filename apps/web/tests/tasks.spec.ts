import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
const password = "Task browser passphrase 2026";
async function enter(page: Page) {
  const email = `tasks-${crypto.randomUUID()}@example.com`;
  await page.goto("/signup");
  await page.getByLabel("Your name").fill("Task User");
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
  await expect(
    page.getByRole("button", { name: "Add task", exact: true }),
  ).toBeVisible();
}
async function add(page: Page, title: string, daily = false) {
  await page.getByRole("button", { name: "Add task", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Add a task", exact: true });
  await dialog.getByLabel("Task title", { exact: true }).fill(title);
  if (daily) await dialog.getByLabel("Task type").selectOption("daily");
  else {
    await dialog.getByLabel("Deadline", { exact: true }).selectOption("date");
    await dialog
      .locator('input[name="due_date"]')
      .fill(new Date().toISOString().slice(0, 10));
  }
  await dialog.getByRole("button", { name: "Save task", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await expect(
    page.getByRole("article", { name: title, exact: true }),
  ).toBeVisible();
}

test("task and daily habit journey, categories, history and responsive dashboard", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await enter(page);
  await page
    .getByRole("button", { name: "Manage categories", exact: true })
    .click();
  let dialog = page.getByRole("dialog", {
    name: "Manage categories",
    exact: true,
  });
  await dialog.getByLabel("Category name").fill("Work");
  await dialog
    .getByRole("button", { name: "Add category", exact: true })
    .click();
  await expect(
    dialog.locator(".category-list > li > span").filter({ hasText: /^Work$/ }),
  ).toBeVisible();
  await dialog.getByRole("button", { name: "Close", exact: true }).click();
  await add(page, "Prepare report");
  let row = page.getByRole("article", { name: "Prepare report", exact: true });
  await row.getByRole("button", { name: "Edit", exact: true }).click();
  dialog = page.getByRole("dialog", { name: "Edit task", exact: true });
  await dialog
    .getByLabel("Task title", { exact: true })
    .fill("Prepare final report");
  await dialog.getByLabel("Description").fill("Careful notes for the project");
  await dialog.getByLabel("Priority", { exact: true }).selectOption("high");
  await dialog
    .getByLabel("Category", { exact: true })
    .selectOption({ label: "Work" });
  await dialog.getByLabel("Estimated minutes").fill("30");
  await dialog.getByRole("button", { name: "Save task", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await add(page, "Read every day", true);
  const habit = page.getByRole("article", {
    name: "Read every day",
    exact: true,
  });
  await habit.getByRole("button", { name: "Complete", exact: true }).click();
  await expect(habit).not.toBeVisible();
  await page
    .getByRole("navigation", { name: "Task views" })
    .getByRole("button", { name: "Daily habits", exact: true })
    .click();
  await expect(habit).toContainText("Current streak 1");
  await expect(
    habit.getByRole("button", { name: "Done today", exact: true }),
  ).toBeDisabled();
  await habit
    .getByRole("button", { name: "Read every day", exact: true })
    .click();
  dialog = page.getByRole("dialog");
  await expect(dialog.getByText(/Daily credit:/)).toBeVisible();
  await dialog.getByRole("button", { name: "Close", exact: true }).click();
  await page
    .getByRole("navigation", { name: "Task views" })
    .getByRole("button", { name: "All tasks", exact: true })
    .click();
  await page
    .getByRole("searchbox", { name: "Search tasks" })
    .fill("final report");
  await page.getByRole("button", { name: "Search", exact: true }).click();
  row = page.getByRole("article", {
    name: "Prepare final report",
    exact: true,
  });
  await expect(row).toBeVisible();
  await expect(habit).not.toBeVisible();
  await page.getByText("Filters and sorting", { exact: true }).click();
  await page.getByLabel("Filter priority").selectOption("high");
  await expect(row).toBeVisible();
  await row.getByRole("button", { name: "Complete", exact: true }).click();
  await expect(row).not.toBeVisible();
  await page
    .getByRole("navigation", { name: "Task views" })
    .getByRole("button", { name: "Completed", exact: true })
    .click();
  await expect(row).toBeVisible();
  await row
    .getByRole("button", { name: "Prepare final report", exact: true })
    .click();
  dialog = page.getByRole("dialog");
  await expect(dialog.getByText(/One-time completion/)).toBeVisible();
  await expect(dialog.getByText("Careful notes for the project")).toBeVisible();
  await dialog.getByRole("button", { name: "Close", exact: true }).click();
  await row.getByRole("button", { name: "Reopen", exact: true }).click();
  await expect(row).not.toBeVisible();
  await page
    .getByRole("navigation", { name: "Task views" })
    .getByRole("button", { name: "Today", exact: true })
    .click();
  await expect(row).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.screenshot({
    path: "test-results/tasks-desktop.png",
    fullPage: true,
  });
  for (const width of [360, 768]) {
    await page.setViewportSize({ width, height: 1000 });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    await page.screenshot({
      path: `test-results/tasks-${width}.png`,
      fullPage: true,
    });
  }
  await row.getByRole("button", { name: "Delete", exact: true }).click();
  dialog = page.getByRole("dialog", { name: "Delete this task?", exact: true });
  await dialog.getByRole("button", { name: "Keep task", exact: true }).click();
  await expect(row).toBeVisible();
  await row.getByRole("button", { name: "Delete", exact: true }).click();
  await dialog
    .getByRole("button", { name: "Confirm delete", exact: true })
    .click();
  await expect(row).not.toBeVisible();
  await page
    .getByRole("button", { name: "Manage categories", exact: true })
    .click();
  dialog = page.getByRole("dialog", { name: "Manage categories", exact: true });
  await dialog
    .getByRole("button", { name: "Rename Work", exact: true })
    .click();
  await dialog.getByLabel("Category name").fill("Projects");
  await dialog
    .getByRole("button", { name: "Rename category", exact: true })
    .click();
  await expect(
    dialog
      .locator(".category-list > li > span")
      .filter({ hasText: /^Projects$/ }),
  ).toBeVisible();
  await dialog
    .getByRole("button", { name: "Delete Projects", exact: true })
    .click();
  await dialog
    .getByRole("button", { name: "Confirm category delete", exact: true })
    .click();
  await expect(
    dialog
      .locator(".category-list > li > span")
      .filter({ hasText: /^Projects$/ }),
  ).not.toBeVisible();
  await dialog.getByRole("button", { name: "Close", exact: true }).click();
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page).toHaveURL(/\/login$/);
});

test("task privacy, bounded pagination and failed save stays honest", async ({
  page,
  browser,
}) => {
  await enter(page);
  await add(page, "Private task");
  const row = page.getByRole("article", { name: "Private task", exact: true });
  await page.route("**/api/tasks/*/complete", (route) => route.abort());
  await row.getByRole("button", { name: "Complete", exact: true }).click();
  await expect(
    page
      .getByRole("region", { name: "Task list", exact: true })
      .getByRole("alert"),
  ).toContainText("Unable to connect");
  await expect(row).toBeVisible();
  await page.unroute("**/api/tasks/*/complete");
  const data = await (await page.request.get("/api/tasks")).json();
  const id = data.items[0].id;
  const csrf = (await (await page.request.get("/api/auth/csrf")).json())
    .csrf_token;
  for (let i = 0; i < 11; i++)
    expect(
      (
        await page.request.post("/api/tasks", {
          headers: { Origin: "http://127.0.0.1:3100", "X-CSRF-Token": csrf },
          data: { title: `Extra ${i}` },
        })
      ).status(),
    ).toBe(201);
  await page.getByRole("link", { name: "All tasks", exact: true }).click();
  await expect(page.getByRole("article")).toHaveCount(10);
  await page.getByRole("button", { name: "Next", exact: true }).click();
  await expect(page.getByRole("article")).toHaveCount(2);
  await page.getByRole("button", { name: "Previous", exact: true }).click();
  await expect(page.getByRole("article")).toHaveCount(10);
  const other = await browser.newContext({ baseURL: "http://127.0.0.1:3100" });
  const another = await other.newPage();
  await enter(another);
  await expect(
    another.getByRole("article", { name: "Private task", exact: true }),
  ).toHaveCount(0);
  expect((await another.request.get(`/api/tasks/${id}`)).status()).toBe(404);
  await other.close();
});
