import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  poweredByHeader: false,
  devIndicators: false,
  outputFileTracingExcludes: {
    "/*": [
      "data/**/*",
      "data-v2/**/*",
      "documents/**/*",
      "html_lore/**/*",
      "app_static/**/*",
      "content/**/*",
      "meta/**/*",
      ".mimosa/**/*",
      ".cursor/**/*",
    ],
  },
};

export default nextConfig;
