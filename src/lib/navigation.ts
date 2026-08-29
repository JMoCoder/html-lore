export type NavConfig = {
  library: Record<string, { visible: boolean }>;
  collections: Record<string, { visible: boolean }>;
  tags: Record<string, { visible: boolean }>;
};

export function isNavVisible(config: NavConfig | null | undefined, section: keyof NavConfig, name: string): boolean {
  if (!config) return true;
  return config[section][name]?.visible ?? true;
}

export function emptyNavConfig(): NavConfig {
  return { library: {}, collections: {}, tags: {} };
}

export function setNavVisible(
  config: NavConfig,
  section: keyof NavConfig,
  name: string,
  visible: boolean,
): NavConfig {
  return {
    ...config,
    [section]: {
      ...config[section],
      [name]: { visible },
    },
  };
}
