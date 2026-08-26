# HTMlore 2.0

当前稳定版是 **1.x**，在 `main` 分支。本分支 `next` 是 2.0 重写：**换栈做减法**，去掉知识库问答和 HTML 生成，先把阅读 / 筛选 / 分享的界面做对。

```bash
npm install
npm run dev
```

打开：

- 工作台 `http://localhost:3000`
- 登录 `http://localhost:3000/login`
- 阅读 `http://localhost:3000/read/mcp-security`
- 安全分享 `http://localhost:3000/share/mcp-security`

现在是 **mock 数据原型**，没有真实登录、磁盘和 AI。1.x 实现见 `main` 或 tag `v1.2.5`。GA 时会把当时的 `main` 改名为 `legacy`，再把 `next` 改名为 `main`。
