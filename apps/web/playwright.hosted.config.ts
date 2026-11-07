import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./hosted-tests",
  workers: 1,
  retries: 0,
  timeout: 120000,
  use: { baseURL: "https://devtreck.vercel.app", trace: "retain-on-failure" },
  reporter: "list",
});
