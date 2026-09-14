import type { Manifest } from "@/server/types";

type CacheEntry = { manifest: Manifest; generation: number };
type CacheState = { cache: Map<string, CacheEntry>; generation: number };

const globalForCache = globalThis as typeof globalThis & {
  __htmlLoreManifestCache?: CacheState;
};

// Critical: both server runtimes must share one cache object, not module closures.
const state: CacheState = (globalForCache.__htmlLoreManifestCache ??= {
  cache: new Map(),
  generation: 0,
});

export function invalidateManifestCache() {
  state.generation += 1;
  state.cache.clear();
}

export function manifestCacheKey(contentDir: string, metaDir: string | null, siteTitle: string) {
  return `${contentDir}\0${metaDir ?? ""}\0${siteTitle}`;
}

export function cachedManifest(key: string, build: () => Manifest): Manifest {
  const hit = state.cache.get(key);
  if (hit && hit.generation === state.generation) {
    return hit.manifest;
  }
  const manifest = build();
  state.cache.set(key, { manifest, generation: state.generation });
  return manifest;
}
