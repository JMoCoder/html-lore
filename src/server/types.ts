export type Item = {
  id: string;
  title: string;
  summary: string;
  path: string;
  source_type: string;
  source_url: string | null;
  collection: string;
  tags: string[];
  status: string;
  review_status: string;
  favorite: boolean;
  archived: boolean;
  pinned: boolean;
  created: string;
  updated: string;
  cover: string | null;
  open_mode: string;
  agent: Record<string, unknown>;
};

export type Manifest = {
  version: number;
  generated_at: string;
  site: { title: string; layout: string };
  items: Item[];
  collections: { id: string; name: string; count: number }[];
  tags: { name: string; count: number }[];
};

export type ItemQuery = {
  q: string;
  library: string;
  collection: string;
  tags: string[];
  tagMatch: string;
  favorite: boolean | null;
  archived: boolean | null;
  sort: string;
  limit: number | null;
};

export type AuthenticatedUser = {
  username: string;
  dataId: string;
  role: string;
};
