import { describe, expect, it, vi } from "vitest";
import { cachedManifest, invalidateManifestCache } from "@/server/manifest-cache";
import type { Manifest } from "@/server/types";

function stubManifest(title: string): Manifest {
  return {
    version: 2,
    generated_at: "2026-09-04T00:00:00.000Z",
    site: { title, layout: "cards" },
    items: [],
    collections: [],
    tags: [],
  };
}

describe("manifest cache", () => {
  it("reuses the built manifest until writes invalidate it", () => {
    invalidateManifestCache();
    let builds = 0;
    const build = () => {
      builds += 1;
      return stubManifest(`build-${builds}`);
    };
    expect(cachedManifest("k", build).site.title).toBe("build-1");
    expect(cachedManifest("k", build).site.title).toBe("build-1");
    expect(builds).toBe(1);
    invalidateManifestCache();
    expect(cachedManifest("k", build).site.title).toBe("build-2");
    expect(builds).toBe(2);
  });
});

describe("manifest-cache 跨 runtime 实例共享", () => {
  it("一个模块实例失效后，另一个实例的缓存条目必须过期", async () => {
    const a = await import("@/server/manifest-cache");
    vi.resetModules(); // simulate bundler re-instantiating for a second runtime
    const b = await import("@/server/manifest-cache");

    let builds = 0;
    const key = "test-key";
    a.cachedManifest(key, () => ({ builds: ++builds } as never));

    a.invalidateManifestCache();
    b.cachedManifest(key, () => ({ builds: ++builds } as never));

    expect(builds).toBe(2); // before fix: b misses invalidation and hits stale cache (builds === 1)
  });
});
