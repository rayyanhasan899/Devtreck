import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./release-tests",
  workers: 1,
  retries: 0,
  timeout: 60000,
  use: {
    baseURL: "https://localhost:8443",
    ignoreHTTPSErrors: true, // Only the loopback synthetic stack's private CA.
    trace: "retain-on-failure",
  },
  reporter: "list",
});
