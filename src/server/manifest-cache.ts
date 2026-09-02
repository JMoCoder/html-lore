import type { Manifest } from "@/server/types";

const TTL_MS = 3000;
const cache = new Map<string, { manifest: Manifest; expiresAt: number; generation: number }>();
let generation = 0;

export function invalidateManifestCache() {
  generation += 1;
  cache.clear();
}

export function manifestCacheKey(contentDir: string, metaDir: string | null, siteTitle: string) {
  return `${contentDir}\0${metaDir ?? ""}\0${siteTitle}`;
}

export function cachedManifest(key: string, build: () => Manifest): Manifest {
  const hit = cache.get(key);
  if (hit && hit.generation === generation && hit.expiresAt > Date.now()) {
    return hit.manifest;
  }
  const manifest = build();
  cache.set(key, { manifest, expiresAt: Date.now() + TTL_MS, generation });
  return manifest;
}
