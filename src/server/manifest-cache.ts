import type { Manifest } from "@/server/types";

const cache = new Map<string, { manifest: Manifest; generation: number }>();
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
  if (hit && hit.generation === generation) {
    return hit.manifest;
  }
  const manifest = build();
  cache.set(key, { manifest, generation });
  return manifest;
}
