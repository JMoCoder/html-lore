import { networkInterfaces } from "node:os";
import type { NextConfig } from "next";

function localDevOrigins() {
  const hosts = new Set(["127.0.0.1"]);
  for (const nets of Object.values(networkInterfaces())) {
    for (const net of nets ?? []) {
      if ((net.family === "IPv4" || net.family === 4) && !net.internal) {
        hosts.add(net.address);
      }
    }
  }
  return [...hosts];
}

const nextConfig: NextConfig = {
  output: "standalone",
  poweredByHeader: false,
  devIndicators: false,
  allowedDevOrigins: localDevOrigins(),
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
