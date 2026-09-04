import { describe, expect, it } from "vitest";
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
