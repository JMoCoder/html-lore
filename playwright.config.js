const { defineConfig, devices } = require("@playwright/test");

const browserChannel = process.env.PLAYWRIGHT_BROWSER_CHANNEL;

module.exports = defineConfig({
  testDir: "./tests/e2e",
  timeout: 30_000,
  workers: 1,
  expect: {
    timeout: 5_000,
  },
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: "http://127.0.0.1:8090",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "off",
    serviceWorkers: "block",
    launchOptions: {
      args: ["--no-sandbox"],
    },
  },
  webServer: {
    command: "python3 -m http.server 8090 --directory docs",
    url: "http://127.0.0.1:8090/demo/",
    reuseExistingServer: true,
    timeout: 10_000,
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        ...(browserChannel ? { channel: browserChannel } : {}),
      },
    },
  ],
});
