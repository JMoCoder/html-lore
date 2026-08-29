export type LibraryFilter = "all" | "recent" | "favorites" | "imported" | "archived";
export type SortMode = "created-newest" | "created-oldest" | "newest" | "oldest" | "title-az" | "title-za";

export type Note = {
  id: string;
  slug: string;
  title: string;
  summary: string;
  collection: string;
  tags: string[];
  favorite: boolean;
  archived: boolean;
  imported: boolean;
  pinned: boolean;
  created: string;
  updated: string;
  shareToken?: string;
  html: string;
};

function page(title: string, body: string, lang = "zh-CN"): string {
  return `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><title>${title}</title>
<style>
  body{margin:0;padding:48px 28px 72px;font:17px/1.7 ui-sans-serif,system-ui,sans-serif;color:#1a221e;background:#fbf9f4;}
  h1{font:600 2rem/1.2 "Iowan Old Style",Georgia,serif;margin:0 0 12px;letter-spacing:-0.03em;}
  p{margin:0 0 1em;max-width:42rem;}
  h2{font-size:1.05rem;margin:1.8em 0 .6em;}
  code{font:13px/1.5 ui-monospace,Menlo,monospace;background:#ece7dc;padding:.1em .35em;border-radius:4px;}
</style></head><body><article><h1>${title}</h1>${body}</article></body></html>`;
}

export const notes: Note[] = [
  {
    id: "generated/2026/05/mcp-security.html",
    slug: "mcp-security",
    title: "MCP Server 安全模型",
    summary: "信任边界、权限、工具调用风险与部署建议。",
    collection: "AI",
    tags: ["MCP", "Security"],
    favorite: true,
    archived: false,
    imported: false,
    pinned: true,
    created: "2026-05-29",
    updated: "2026-05-29",
    shareToken: "mcp-security",
    html: page(
      "MCP Server 安全模型",
      "<p>MCP Server 的主要风险来自工具调用权限、文件系统访问、网络访问和凭据暴露。部署时应默认最小权限，并把可执行工具和数据访问范围拆开配置。</p><h2>部署建议</h2><p>优先在受控网络中运行，限制环境变量、日志输出和命令执行能力。对外开放前应增加认证、审计和速率限制。</p>",
    ),
  },
  {
    id: "imported/docker-network.html",
    slug: "docker-network",
    title: "Docker Network Quick Notes",
    summary: "Bridge 网络、发布端口与服务发现。",
    collection: "Ops",
    tags: ["Docker", "Network"],
    favorite: false,
    archived: false,
    imported: true,
    pinned: false,
    created: "2026-04-12",
    updated: "2026-04-12",
    shareToken: "docker-network",
    html: page(
      "Docker Network Quick Notes",
      "<p>Docker bridge networks give containers private service discovery while published ports expose selected services to the host network.</p><h2>Useful commands</h2><p><code>docker network inspect</code> helps verify aliases, subnets, and connected containers.</p>",
      "en",
    ),
  },
  {
    id: "reading/knowledge-workspace.html",
    slug: "knowledge-workspace",
    title: "Knowledge Workspace Design Notes",
    summary: "把每一页 HTML 当作可长期保存的知识资产。",
    collection: "Reading",
    tags: ["Design", "HTML"],
    favorite: true,
    archived: false,
    imported: false,
    pinned: false,
    created: "2026-06-02",
    updated: "2026-06-02",
    html: page(
      "Knowledge Workspace Design Notes",
      "<p>HTML notes work best when each page is treated as a durable knowledge asset with metadata, source context, and a stable URL.</p>",
      "en",
    ),
  },
  {
    id: "generated/2026/05/mcp-docker-agent.html",
    slug: "mcp-docker-agent",
    title: "MCP Docker Agent Notes",
    summary: "在 Docker 本地服务中部署 MCP agent。",
    collection: "AI",
    tags: ["MCP", "Docker"],
    favorite: false,
    archived: false,
    imported: false,
    pinned: false,
    created: "2026-05-18",
    updated: "2026-05-18",
    html: page(
      "MCP Docker Agent Notes",
      "<p>MCP agent deployment notes for Docker-based local services. Keep the agent on a private network and expose only a reverse-proxied HTTP endpoint.</p>",
    ),
  },
  {
    id: "imported/caddy-share-headers.html",
    slug: "caddy-share-headers",
    title: "Caddy 分享页响应头",
    summary: "CSP、frame-ancestors 与缓存策略，避免把私有笔记送进 CDN。",
    collection: "Ops",
    tags: ["Caddy", "Share"],
    favorite: false,
    archived: false,
    imported: true,
    pinned: false,
    created: "2026-07-03",
    updated: "2026-07-03",
    html: page(
      "Caddy 分享页响应头",
      "<p>公开分享链接必须能在无 Cookie 的窗口打开。对 <code>/share/*</code> 关闭 Full Route Cache，并明确写出 CSP。</p>",
    ),
  },
  {
    id: "reading/editorial-chrome.html",
    slug: "editorial-chrome",
    title: "编辑气质的工作台 Chrome",
    summary: "侧栏比内容更暗，品牌色不上导航，卡片不要堆操作按钮。",
    collection: "Reading",
    tags: ["Design", "UI"],
    favorite: true,
    archived: false,
    imported: false,
    pinned: false,
    created: "2026-08-20",
    updated: "2026-08-20",
    shareToken: "editorial-chrome",
    html: page(
      "编辑气质的工作台 Chrome",
      "<p>阅读优先：卡片网格和 iframe 占满注意力。侧栏是暗一层的索引，不是第三个产品。</p><p>强调色只出现在当前筛选、主按钮和收藏态。</p>",
    ),
  },
  {
    id: "imported/yaml-sidecar.html",
    slug: "yaml-sidecar",
    title: "YAML 旁车元数据",
    summary: "标题、集合、标签与正文分离，HTML 文件保持可携带。",
    collection: "Reading",
    tags: ["Metadata", "YAML"],
    favorite: false,
    archived: false,
    imported: true,
    pinned: false,
    created: "2026-03-21",
    updated: "2026-03-21",
    html: page(
      "YAML 旁车元数据",
      "<p>组织方式写在 sidecar 里，而不是写进数据库行。没有 sidecar 时从 HTML 推断标题与摘要。</p>",
    ),
  },
  {
    id: "archived/old-inbox.html",
    slug: "old-inbox",
    title: "早期收件箱草稿",
    summary: "已归档。编辑锁定，仅供回看。",
    collection: "Inbox",
    tags: ["Archive"],
    favorite: false,
    archived: true,
    imported: true,
    pinned: false,
    created: "2025-11-08",
    updated: "2025-11-08",
    html: page(
      "早期收件箱草稿",
      "<p>归档笔记不再出现在默认资料库里。2.0 原型用这条演示归档筛选。</p>",
    ),
  },
];

export function getNote(slug: string): Note | undefined {
  return notes.find((note) => note.slug === slug || note.id === slug);
}

export function getNoteByShareToken(token: string): Note | undefined {
  return notes.find((note) => note.shareToken === token);
}
