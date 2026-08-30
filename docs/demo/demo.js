const NOTES = [
  {
    id: "about/htmlore-2.html",
    title: "HTMlore 2.0",
    summary: "自托管 HTML 知识工作台：导入、筛选、阅读、编辑、分享。没有数据库，也没有应用内登录或 AI。",
    collection: "Reading",
    tags: ["HTMlore", "2.0"],
    sourceType: "html",
    favorite: true,
    archived: false,
    created: "2026-08-29T00:00:00.000Z",
    updated: "2026-08-29T00:00:00.000Z",
  },
  {
    id: "reading/knowledge-workspace.html",
    title: "Knowledge Workspace Design Notes",
    summary: "HTML notes work best when each page is treated as a durable knowledge asset with metadata, source context, and a stable URL.",
    collection: "Reading",
    tags: ["Design", "HTML"],
    sourceType: "html",
    favorite: false,
    archived: false,
    created: "2026-05-29T03:26:34.680Z",
    updated: "2026-05-29T03:26:34.680Z",
  },
  {
    id: "imported/docker-network.html",
    title: "Docker Network Quick Notes",
    summary: "Bridge networks, published ports, and service discovery notes for Docker.",
    collection: "Dev",
    tags: ["Docker", "Network"],
    sourceType: "imported",
    favorite: false,
    archived: false,
    created: "2026-05-20T08:00:00.000Z",
    updated: "2026-05-20T08:00:00.000Z",
  },
  {
    id: "imported/react-server-components.html",
    title: "React Server Components in App Router",
    summary: "Imported English note for mixed-language grids, collection badges, and reading-time estimation.",
    collection: "Dev",
    tags: ["React", "Next.js"],
    sourceType: "imported",
    favorite: false,
    archived: false,
    created: "2026-06-10T09:15:00.000Z",
    updated: "2026-06-10T09:15:00.000Z",
  },
  {
    id: "generated/2026/05/mcp-security.html",
    title: "MCP Server 安全模型",
    summary: "介绍 MCP Server 的信任边界、权限、工具调用风险与部署建议。",
    collection: "Dev",
    tags: ["MCP", "Security"],
    sourceType: "html",
    favorite: true,
    archived: false,
    created: "2026-05-18T10:00:00.000Z",
    updated: "2026-05-18T10:00:00.000Z",
  },
  {
    id: "generated/2026/08/offline-first-notes.html",
    title: "Offline-First 阅读体验笔记",
    summary: "收藏态卡片、较长摘要段落，以及 PWA shell 缓存策略的简要记录。",
    collection: "Reading",
    tags: ["PWA", "Reading"],
    sourceType: "html",
    favorite: true,
    archived: false,
    created: "2026-08-15T14:00:00.000Z",
    updated: "2026-08-26T02:00:00.000Z",
  },
];

const I18N = {
  "zh-CN": {
    banner: "静态预览 · 2.0.4 · 无后端 / 无登录 / 无 AI",
    library: "资料库",
    collections: "集合",
    tags: "标签",
    all: "全部笔记",
    recent: "最近",
    favorites: "收藏",
    imported: "已导入",
    archived: "已归档",
    search: "搜索笔记…",
    themeLight: "切换为亮色",
    themeDark: "切换为暗色",
    back: "工作台",
    empty: "没有符合当前筛选的笔记。",
    sort: {
      "created-newest": "最近创建",
      "created-oldest": "最早创建",
      newest: "最近更新",
      oldest: "最早更新",
      "title-az": "标题 A → Z",
      "title-za": "标题 Z → A",
    },
  },
  en: {
    banner: "Static preview · 2.0.4 · no backend / no login / no AI",
    library: "Library",
    collections: "Collections",
    tags: "Tags",
    all: "All notes",
    recent: "Recent",
    favorites: "Favorites",
    imported: "Imported",
    archived: "Archived",
    search: "Search notes…",
    themeLight: "Switch to light",
    themeDark: "Switch to dark",
    back: "Workspace",
    empty: "No notes match the current filters.",
    sort: {
      "created-newest": "Recently created",
      "created-oldest": "Oldest created",
      newest: "Recently updated",
      oldest: "Oldest updated",
      "title-az": "Title A → Z",
      "title-za": "Title Z → A",
    },
  },
  ja: {
    banner: "静的プレビュー · 2.0.4 · バックエンド / ログイン / AI なし",
    library: "ライブラリ",
    collections: "コレクション",
    tags: "タグ",
    all: "すべてのノート",
    recent: "最近",
    favorites: "お気に入り",
    imported: "インポート済み",
    archived: "アーカイブ",
    search: "ノートを検索…",
    themeLight: "ライトモード",
    themeDark: "ダークモード",
    back: "ワークスペース",
    empty: "条件に合うノートがありません。",
    sort: {
      "created-newest": "作成が新しい順",
      "created-oldest": "作成が古い順",
      newest: "更新が新しい順",
      oldest: "更新が古い順",
      "title-az": "タイトル A → Z",
      "title-za": "タイトル Z → A",
    },
  },
};

const SORTS = ["created-newest", "created-oldest", "newest", "oldest", "title-az", "title-za"];
const MONTH_MS = 1000 * 60 * 60 * 24 * 30;

const state = {
  library: "all",
  collection: "",
  tags: [],
  query: "",
  sort: "created-newest",
  locale: localStorage.getItem("htmlore-demo-locale") || "zh-CN",
  theme: localStorage.getItem("htmlore-demo-theme") || "light",
};

function t() {
  return I18N[state.locale] || I18N["zh-CN"];
}

function isImported(note) {
  return note.sourceType === "imported" || note.id.startsWith("imported/");
}

function counts() {
  const visible = NOTES.filter((note) => !note.archived);
  return {
    all: visible.length,
    recent: visible.filter((note) => Date.now() - Date.parse(note.updated) <= MONTH_MS).length,
    favorites: visible.filter((note) => note.favorite).length,
    imported: visible.filter(isImported).length,
    archived: NOTES.filter((note) => note.archived).length,
  };
}

function filterNotes() {
  const query = state.query.trim().toLowerCase();
  const filtered = NOTES.filter((note) => {
    if (state.library === "archived") {
      if (!note.archived) return false;
    } else if (note.archived) {
      return false;
    }
    if (state.library === "favorites" && !note.favorite) return false;
    if (state.library === "imported" && !isImported(note)) return false;
    if (state.library === "recent" && Date.now() - Date.parse(note.updated) > MONTH_MS) return false;
    if (state.collection && note.collection !== state.collection) return false;
    if (state.tags.length && !state.tags.every((tag) => note.tags.includes(tag))) return false;
    if (!query) return true;
    return `${note.title} ${note.summary} ${note.collection} ${note.tags.join(" ")}`.toLowerCase().includes(query);
  });

  return filtered.sort((a, b) => {
    const titleOrder = a.title.localeCompare(b.title, "zh");
    const newestUpdated = b.updated.localeCompare(a.updated);
    if (state.sort === "created-oldest") return a.created.localeCompare(b.created) || titleOrder;
    if (state.sort === "oldest") return a.updated.localeCompare(b.updated) || titleOrder;
    if (state.sort === "newest") return newestUpdated || titleOrder;
    if (state.sort === "title-az") return titleOrder || newestUpdated;
    if (state.sort === "title-za") return b.title.localeCompare(a.title, "zh") || newestUpdated;
    return b.created.localeCompare(a.created) || titleOrder;
  });
}

function formatDate(value) {
  return new Intl.DateTimeFormat(state.locale, { year: "numeric", month: "short", day: "numeric" }).format(new Date(value));
}

function readId() {
  const hash = decodeURIComponent(location.hash.slice(1));
  return hash.startsWith("/read/") ? hash.slice("/read/".length) : "";
}

function applyTheme() {
  document.documentElement.classList.toggle("dark", state.theme === "dark");
  localStorage.setItem("htmlore-demo-theme", state.theme);
}

function applyCopy() {
  const copy = t();
  document.documentElement.lang = state.locale;
  document.querySelector("[data-i18n=banner]").textContent = copy.banner;
  document.querySelector("[data-i18n=library]").textContent = copy.library;
  document.querySelector("[data-i18n=collections]").textContent = copy.collections;
  document.querySelector("[data-i18n=tags]").textContent = copy.tags;
  document.getElementById("search").placeholder = copy.search;
  document.getElementById("back").textContent = copy.back;
  document.getElementById("empty").textContent = copy.empty;
  document.getElementById("theme").textContent = state.theme === "dark" ? copy.themeLight : copy.themeDark;
  document.getElementById("lang").value = state.locale;

  const sort = document.getElementById("sort");
  sort.innerHTML = SORTS.map((value) => `<option value="${value}">${copy.sort[value]}</option>`).join("");
  sort.value = state.sort;

  const n = counts();
  document.querySelectorAll("[data-library]").forEach((btn) => {
    const id = btn.dataset.library;
    btn.textContent = `${copy[id]}  ${n[id]}`;
    btn.setAttribute("aria-current", state.library === id && !state.collection ? "true" : "false");
  });
}

function groupCounts(key) {
  const map = new Map();
  NOTES.filter((note) => !note.archived).forEach((note) => {
    const values = key === "tags" ? note.tags : [note.collection];
    values.filter(Boolean).forEach((name) => map.set(name, (map.get(name) || 0) + 1));
  });
  return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0], "zh"));
}

function renderNav(id, entries, active, onClick) {
  const root = document.getElementById(id);
  root.innerHTML = "";
  entries.forEach(([name, count]) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "nav-btn";
    btn.textContent = `${name}  ${count}`;
    btn.setAttribute("aria-current", active === name ? "true" : "false");
    btn.addEventListener("click", () => onClick(name));
    root.appendChild(btn);
  });
}

function renderGrid() {
  const notes = filterNotes();
  const grid = document.getElementById("grid");
  const empty = document.getElementById("empty");
  grid.innerHTML = "";
  empty.hidden = notes.length > 0;
  notes.forEach((note) => {
    const card = document.createElement("a");
    card.className = "card";
    card.href = `#/read/${note.id}`;
    card.innerHTML = `
      <div class="card-meta">${note.collection}${note.favorite ? " · ★" : ""}</div>
      <h2>${note.title}</h2>
      <p>${note.summary}</p>
      <div class="card-foot">${formatDate(note.updated)} · ${note.tags.join(" · ")}</div>
    `;
    grid.appendChild(card);
  });
}

function render() {
  applyTheme();
  applyCopy();
  renderNav("collections", groupCounts("collection"), state.collection, (name) => {
    state.collection = state.collection === name ? "" : name;
    state.library = "all";
    render();
  });
  renderNav("tags", groupCounts("tags"), state.tags[0] || "", (name) => {
    state.tags = state.tags[0] === name ? [] : [name];
    render();
  });
  renderGrid();

  const id = readId();
  const note = NOTES.find((item) => item.id === id);
  document.getElementById("workspace").classList.toggle("hidden", Boolean(note));
  document.getElementById("reader").classList.toggle("open", Boolean(note));
  if (note) {
    document.getElementById("reader-title").textContent = note.title;
    document.getElementById("frame").src = `content/${note.id}`;
    document.title = `${note.title} · HTMlore`;
  } else {
    document.getElementById("frame").src = "about:blank";
    document.title = "HTMlore 2.0 · Demo";
  }
}

document.querySelectorAll("[data-library]").forEach((btn) => {
  btn.addEventListener("click", () => {
    state.library = btn.dataset.library;
    state.collection = "";
    render();
  });
});
document.getElementById("search").addEventListener("input", (event) => {
  state.query = event.target.value;
  render();
});
document.getElementById("sort").addEventListener("change", (event) => {
  state.sort = event.target.value;
  render();
});
document.getElementById("lang").addEventListener("change", (event) => {
  state.locale = event.target.value;
  localStorage.setItem("htmlore-demo-locale", state.locale);
  render();
});
document.getElementById("theme").addEventListener("click", () => {
  state.theme = state.theme === "dark" ? "light" : "dark";
  render();
});
document.getElementById("back").addEventListener("click", () => {
  location.hash = "#/";
});
window.addEventListener("hashchange", render);

if (!location.hash) location.hash = "#/";
render();
