# HTMlore

Languages: [English](README.md) | [中文](README.zh-CN.md) | [日本語](README.ja.md)

Deployment: [Self-hosted Docker and security baseline](DEPLOYMENT.md)

HTMlore は、HTML 形式のナレッジファイルを保存、閲覧、読書し、将来的には AI と対話するためのセルフホスト型ナレッジワークスペースです。内容をデータベース中心のノートアプリに閉じ込めず、移植可能なファイルとして保持したいユーザー向けに設計されています。

長期的な方向性は、Web ファーストの個人ナレッジライブラリです。HTML ノートをインポートまたは生成し、コレクションとタグで整理し、洗練されたカードワークスペースで読み、PWA としてインストールし、将来的には AI サービスを接続して、自分のライブラリに対する分類、検索、要約、多ターン会話を行えるようにします。

## Why HTMlore

多くのナレッジツールは、内容を不透明なデータベース行として保存するか、Markdown 執筆を中心にしています。HTMlore は別の方針を取ります:

- **HTML ファイルを永続的なコンテンツ層にします。** ノートは確認、コピー、アーカイブ、バックアップでき、一般的な Web インフラで配信できます。
- **YAML サイドカーメタデータで整理情報を明示します。** タイトル、概要、コレクション、タグ、お気に入り、アーカイブ、ソース情報はコンテンツとは別に保存されます。
- **Web アプリを主クライアントにします。** 別のデスクトップアプリではなく、ブラウザーとモバイル PWA を主な利用形態にします。
- **AI は任意のサービス層です。** 現在のアプリには AI ワークフロー用 UI とコンテキスト設計がありますが、認証情報とモデル呼び出しは静的フロントエンドには保存しません。

## 0.9.x Current Scope

現在の `0.9.x` ラインは、ローカル、プライベートネットワーク、セルフホストでの実運用を対象にしています。Docker デプロイ、内蔵ログイン、HTML インポート、メタデータ永続化、フィルター、読書、アーカイブ、公開共有に加え、最初のサーバー側 AI ワークフローを含みます。

現在実装済み:

- `docker compose up -d --build` による単一コンテナ Docker デプロイ。
- Docker イメージに `GET /api/health` を使うヘルスチェックを内蔵。
- HttpOnly session Cookie とバックエンド設定のテストユーザー認証情報を使う内蔵ログイン画面。
- `app_static/` から生成される静的優先フロントエンド。
- 実際のノートブック運用向けバックエンド API。
- HTML アップロードと `data/content` へのインポート。
- YAML メタデータの `data/meta` への永続化。
- インポート、メタデータ変更、状態変更後の `public/` 自動再ビルド。
- ライブラリ、コレクション、タグ、お気に入り、検索、並び替えを備えたカードワークスペース。
- OR/AND 一致を選べる複数タグフィルター。
- iframe 読書、原文アクセス、コピー/共有、お気に入り/アーカイブ、メタデータ編集を備えたリーダー。
- アーカイブされていないノートでは、HTML ソース編集と保守的なビジュアルファイル編集を利用できます。テキスト編集、文字色/背景色、太字/斜体/下線/取り消し線、undo/redo、保存前の共有安全チェック、折りたたみ可能な編集パネルを含みます。
- アーカイブ済みノートの編集ロックと完全削除。
- セルフホスト向けマルチユーザーログイン。ユーザー名は大文字小文字を区別せず、ノートブックデータはユーザーごとに分離されます。
- `data/users.json` にユーザーアカウントを保存し、パスワードはハッシュで保存します。
- 追加ユーザーのノートブックは `data/users/<data_id>/` に保存されます。
- ライブラリ、コレクション、タグのサイドバー表示管理。
- ワークスペース、コレクション、タグ、リーダー、手動選択ノートを扱うグローバル AI サイドバー。
- OpenAI-compatible エンドポイント向けのサーバー側 AI プロバイダー設定。API key はバックエンド環境変数からのみ読み取り、ブラウザー設定 API では送信も取得もできません。
- ナレッジベース Q&A beta。コンテキスト検索、現在コンテキストの概要、直近会話に基づく追問理解、Markdown 回答表示、ソース表示、会話永続化、現在コンテキストの最新会話復元、コンテキスト別履歴を備えます。
- ナレッジベース Q&A ランタイムは planner、search planner、answer、verifier、reviewer の段階に分割され、agent/prompt trace も公開されます。今後の統一マルチエージェント backend への拡張とデバッグのためです。
- AI 回答の strict / content expansion モード。strict は選択中のノートブックコンテキストだけで回答し、expansion は外部検索アダプター設定時に明示的な外部ソースを扱います。
- AI 実行履歴、軽量非同期の生成履歴、失敗した会話生成ジョブの再試行、Settings 内のグローバル会話管理。
- AI 会話から HTML ノートを生成する beta 機能。PM/UX/Coder/QA/Reviewer の段階的グラフを使います。
- HTML、Markdown、テキスト資料アップロードから HTML ノートを生成する beta 機能。安全なテキスト抽出後に HTML 生成グラフを再利用します。
- キーワード検索を実装済みで、短い質問のクエリ拡張、複数ノート間の証拠バランス、検索カバレッジ診断に対応します。軽量ローカル vector index をサポートし、embedding model または vector index が未設定の場合はキーワード検索へ自動フォールバックします。
- プロンプト長、未対応リクエスト、秘密情報らしき出力、共有向け HTML 安全レビューに対する AI ガードレール。
- AI プロバイダー、データ、ユーザー、アカウントセキュリティ、AI 会話履歴、プロジェクト情報、更新情報の設定セクション。
- PWA manifest と Service Worker。
- 中国語、英語、日本語のシステム UI。
- ライト/ダークテーマ切り替えとリサイズ可能なサイドバー。
- `GET /api/version` と GitHub releases/tags による更新ヒント。
- 任意の Caddy Basic Auth 公開デプロイ例。

現在の制限または未実装:

- AI 機能は beta であり、ホスト型/クラウド製品化の前にセルフホスト検証を優先しています。
- 外部 Web 検索はアダプターを用意していますが、既定プロバイダーは同梱していません。
- vector / hybrid 検索にはサーバー側の embedding model 設定が必要です。未設定の場合、HTMlore はキーワード検索を使い続けます。
- PDF 資料解析は意図的に後回しにしています。
- AI による再分類、再タグ付けなどのバッチ処理。
- クラウド同期またはホスト型サブスクリプションサービス。
- 完全なバックアップ/復元と WebDAV 実行。
- コレクション/タグの一括リネーム、統合、削除。

## Quick Docker Start

既定の Docker パスはローカル PC、NAS、LAN サーバー、プライベート VPS 向けです。token も Caddy も必須ではありません。

任意のローカル既定値は `.env.example` に記載しています。compose の既定値と同じで、ローカルまたはプライベートネットワークでのテスト用途です。

```bash
git clone https://github.com/JMoCoder/html_lore.git
cd html_lore
docker compose up -d --build
```

開く:

```text
http://localhost:8080
```

既定のローカル/テストログイン:

```text
Username: admin
Password: test-password
```

同じネットワーク上の別デバイスからは:

```text
http://your-host-ip:8080
```

ランタイムデータは Git には保存されません:

```text
data/content             既定管理者のインポート/生成 HTML
data/meta                既定管理者の YAML メタデータとランタイム設定
data/users.json          セルフホストログインユーザー。パスワードはハッシュ保存
data/users/<data_id>/    追加ユーザーの HTML、メタデータ、ジョブ、public 出力
public                   既定管理者の生成済み Web アプリ出力
```

env から作成される最初の管理者は、既存デプロイとの互換性のためルートの `data/content`、`data/meta`、`public` を引き続き使用します。あとから追加したユーザーは `data/users/<data_id>/` に分離されます。

セルフホストユーザーを追加します:

```bash
docker compose run --rm html-lore \
  html-lore user-add \
  --users-file /data/users.json \
  --username alice \
  --password "change-this-password"
```

ユーザー名は大文字小文字を区別せずに照合されます。パスワードは大文字小文字を区別し、平文ではなく PBKDF2 ハッシュとして保存されます。

既定の認証情報のまま compose スタックを公開インターネットに出さないでください。公開デプロイでは `HTML_LORE_AUTH_USERNAME`、`HTML_LORE_AUTH_PASSWORD`、`HTML_LORE_SESSION_SECRET` を変更し、HTTPS の背後に置いてください。env のユーザー名/パスワードは `data/users.json` が存在しない場合に最初の管理者を作成するためだけに使われ、その後は `users.json` が正になります。Caddy Basic Auth 例と本番向け env テンプレートとして `compose.prod.yml`、`.env.secure.example`、`deploy/caddy-basic-auth.Caddyfile` を用意しています。

## Update Existing Docker Deployment

HTMlore はホストを自動更新しません。アプリは GitHub releases/tags から更新ヒントを表示するだけです。

更新前に `data/` をバックアップします:

```bash
cp -a data "data.backup.$(date +%Y%m%d-%H%M%S)"
```

変更内容を確認します:

```bash
git fetch
git log --oneline HEAD..origin/main
git diff --stat HEAD..origin/main
```

更新を適用します:

```bash
git pull --ff-only
docker compose up -d --build
docker compose logs -f
```

## Static Build

既存のコンテンツとメタデータから静的サイトを生成することもできます:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
html-lore build --content examples/content --meta examples/meta --out public
python -m http.server 8080 --directory public
```

`http://localhost:8080` を開きます。

静的モードは読み取り専用公開、GitHub Pages のようなホスティング、生成アプリの確認に適しています。実際のアップロードとメタデータ永続化には、バックエンド API または既定の Docker デプロイが必要です。

## Data Model

HTML ファイルはコンテンツディレクトリに保存されます:

```text
content/
  generated/2026/05/mcp-security.html
  imported/docker-network.html
  reading/knowledge-workspace.html
```

任意のメタデータは同じパス構造で `meta/items/` に保存されます:

```yaml
id: generated/2026/05/mcp-security.html
title: MCP Server Security Model
summary: Trust boundaries, permissions, tool-call risks, and deployment notes.
source_type: topic
collection: AI
tags:
  - MCP
  - Security
favorite: true
pinned: true
open_mode: iframe
agent:
  generated: true
  job_id: job_demo
```

メタデータは HTML ドキュメントから抽出した値を上書きします。メタデータがない場合、HTMlore はタイトル、概要、コレクション、ソース種別、タイムスタンプ、レビュー状態を推測します。

## Backend API

バックエンド API は Docker デプロイに含まれます。任意の `agent` extra で手動起動することもできます:

```bash
pip install -e ".[agent]"
HTML_LORE_CONTENT=data/content \
HTML_LORE_META=data/meta \
HTML_LORE_PUBLIC=public \
html-lore serve-api --host 127.0.0.1 --port 8787
```

実装済みエンドポイント:

- `GET /api/health`
- `GET /api/version`
- `GET /api/manifest`
- `GET /api/navigation`
- `PUT /api/navigation`
- `GET /api/items`
- `GET /api/search`
- `GET /api/items/{id}`
- `GET /api/items/{id}/content`
- `GET /api/items/{id}/raw`
- `POST /api/rebuild`
- `GET /api/rebuild/{job_id}`
- `PATCH /api/items/{id}/metadata`
- `PATCH /api/items/{id}/state`
- `POST /api/uploads/html`
- `GET /api/uploads/{upload_id}`
- `DELETE /api/items/{id}`
- `GET /api/ai/providers`
- `PUT /api/ai/providers`
- `GET /api/ai/status`
- `POST /api/ai/test-provider`
- `POST /api/ai/context/resolve`
- `POST /api/ai/conversations`
- `GET /api/ai/conversations`
- `GET /api/ai/conversations/latest`
- `GET /api/ai/conversations/{conversation_id}`
- `DELETE /api/ai/conversations/{conversation_id}`
- `GET /api/ai/conversations/{conversation_id}/messages`
- `POST /api/ai/conversations/{conversation_id}/messages`
- `POST /api/ai/conversations/{conversation_id}/generate-note`
- `POST /api/ai/conversations/{conversation_id}/generate-note/jobs`
- `POST /api/ai/material-runs`
- `POST /api/ai/material-jobs`
- `GET /api/ai/runs`
- `GET /api/ai/runs/{run_id}`
- `GET /api/ai/jobs`
- `GET /api/ai/jobs/{job_id}`
- `POST /api/ai/jobs/{job_id}/retry`
- `DELETE /api/ai/jobs/{job_id}`

API は現在のフロントエンドワークフローをカバーします: アップロード、一覧、検索、フィルター、読書、メタデータ編集、お気に入り、アーカイブ、アーカイブ解除、アーカイブ済みノートの完全削除、サイドバー表示設定の永続化、再ビルド Job、バージョン確認、AI provider status、ナレッジベース Q&A、会話履歴、beta AI ノート生成 Job。

## AI Configuration

AI 認証情報はサーバー側に置きます。フロントエンド設定ページでは provider、base URL、model、embedding model 参照を設定できますが、API key を送信または読み取ることはできません。デプロイ環境で次のように設定します:

```bash
HTML_LORE_AI_ENABLED=true
HTML_LORE_AI_PROVIDER=openai-compatible
HTML_LORE_AI_BASE_URL=https://your-newapi.example.com/v1
HTML_LORE_AI_MODEL=gpt-5.5
HTML_LORE_AI_EMBEDDING_MODEL=baai/bge-m3
HTML_LORE_AI_RETRIEVAL_MODE=hybrid
HTML_LORE_AI_API_KEY=replace-with-your-server-side-key
```

デプロイ時の注意:

- `HTML_LORE_AI_API_KEY` はサーバー側の chat / embedding 呼び出しだけに使います。フロントエンド設定ファイルに書かないでください。
- `HTML_LORE_AI_EMBEDDING_MODEL` は vector / hybrid 検索を有効にします。embedding model または index が利用できない場合、HTMlore はキーワード検索へフォールバックします。
- `HTML_LORE_AI_QA_ENGINE=auto` がデフォルトの Q&A engine mode です。
  LangGraph ワークフローを優先し、LangGraph が利用できない場合は
  `agent_runtime` へフォールバックします。開発時に LangGraph を強制する場合は
  `HTML_LORE_AI_QA_ENGINE=langgraph`、安定した runtime fallback を使う場合は
  `HTML_LORE_AI_QA_ENGINE=agent_runtime` を設定します。
- Tavily 外部検索を有効にする場合は、別のサーバー側 key を使います。
- smoke-test コマンドは実際の provider 呼び出しを行います。その環境の model と key が正しいことを確認してから実行してください。

外部拡張モードでは、Tavily を制御された Web 検索 provider として利用できます:

```bash
HTML_LORE_AI_EXTERNAL_SEARCH=tavily
HTML_LORE_AI_EXTERNAL_SEARCH_API_KEY=replace-with-your-tavily-key
HTML_LORE_AI_EXTERNAL_SEARCH_MAX_RESULTS=5
HTML_LORE_AI_EXTERNAL_SEARCH_DEPTH=basic
HTML_LORE_AI_EXTERNAL_SEARCH_AUTO_PARAMETERS=false
```

HTMlore は既定では Tavily の生成 answer を使いません。Tavily は外部証拠検索として扱い、最終回答はナレッジ Q&A workflow が組み立てます。検索は低コストの `basic` から開始し、時事性の高い質問や金融質問では topic / time range を切り替えます。ユーザーの質問から country ヒントを推定でき、ユーザーが深い調査や複数ソース比較を明示した場合、または運用者が明示設定した場合のみ `advanced` に昇格します。
`联网搜索` のような短い追問は、検索計画の前に直近のユーザー質問を継承し、以前の assistant 回答本文をそのまま検索クエリへ混ぜないようにしています。

vector / hybrid 検索は、現在のユーザー metadata ディレクトリに軽量ローカル index を保存します。例: `meta/ai/vector_index.json`。マルチユーザーデプロイでは、対応する `users/{data_id}/meta/ai/vector_index.json` に保存されます。これにより、同じアプリケーションプロセスを共有しつつ、各ユーザーのワークスペースを論理的に分離できます。

vector index のメンテナンスはバックエンド用の機能であり、通常のワークスペースボタンとしては表示しません。ノートを編集、アーカイブ、完全削除した場合、HTMlore は対応する古い vector を削除します。運用者は必要に応じて CLI からローカル index を確認、整理、再構築できます:

```bash
html-lore ai-vector-index stats
html-lore ai-vector-index prune
html-lore ai-vector-index rebuild
html-lore ai-vector-index smoke-test
```

`smoke-test` は、現在のサーバー設定の provider と embedding model を使って実際に 1 回 embedding リクエストを送ります。その環境で model と key が意図した設定であることを確認してから実行してください。

開発テストでは `HTML_LORE_AI_PROVIDER=fake` を使い、実際のモデルリクエストなしで UI と会話フローを確認できます。公開ステータスは `has_api_key` のみを返し、秘密値は返しません。

## Security Model

既定の Docker モードはローカル、LAN、プライベートセルフホスト向けです。既定のローカル/テストログインは `admin` / `test-password` で、開発用 session secret を使用します。ブラウザーは最初にログイン画面を表示し、ログイン後は HttpOnly session Cookie を使用します。登録は無効です。公開デプロイでは既定のユーザー名、パスワード、session secret を必ず変更してください。セルフホストユーザーは `data/users.json` に保存され、追加ユーザーごとのノートブックデータは `data/users/<data_id>/` に分離保存されます。

HTMlore を公開インターネットに出す場合:

- HTTPS の背後に置く。
- 内蔵ログインを有効にするか、同等の認証境界を前段に置く。
- HTTPS で配信する場合は `HTML_LORE_SESSION_SECURE=true` を設定する。
- スクリプト、自動化、またはリバースプロキシ API アクセス用に `HTML_LORE_API_TOKEN` を設定する。
- 長期 API token をフロントエンド JavaScript に埋め込まない。
- アップグレード前とスキーマ変更リリース前に `data/` をバックアップする。

再利用可能な安全基線と Caddy Basic Auth 例は [DEPLOYMENT.md](DEPLOYMENT.md) を参照してください。

## Roadmap

近い将来のバックエンド/ノートブック機能:

- コレクションとタグの一括操作。
- バックアップと復元フロー。
- WebDAV 設定の実行。
- より堅牢なインポート検証と重複処理。
- SQLite FTS や Pagefind などの検索バックエンド移行。

AI 機能:

- Q&A 検索品質を改善し、実際の vector-store backend を追加する。
- content expansion モード向けの設定可能な外部検索 provider を追加する。
- beta のマルチエージェント HTML 生成グラフを改善し、planning、coding、QA、review を実モデル協調へ進める。
- AI による分類、タグ付け、要約、整理 Job。
- 破壊的な AI バッチ操作に対するユーザー確認と監査履歴。

将来のプロダクト方向:

- ホスト型同期とクロスデバイス利用。
- ユーザーアカウントとアカウントセキュリティ。
- 商用 AI/クラウドサービス連携。
- より良いモバイル PWA フロー。
- ローカル優先のデータ所有権を保ちながら、任意のコラボレーション機能を提供。

## Repository Layout

```text
app_static/        ビルド出力へコピーされる静的ワークスペース UI
html_lore/        Python ビルダー、manifest ロジック、バックエンド API
examples/          サンプルコンテンツとメタデータ
tests/             ビルダーとバックエンド API のテスト
deploy/            任意のデプロイ例
docs/              GitHub Pages ホームページと読み取り専用 Demo
documents/         ローカル計画ドキュメント、Git では無視
```

## Development

```bash
pip install -e ".[dev,agent]"
pytest
python tests/run_smoke.py
npm ci
npm run test:e2e
html-lore build --content examples/content --meta examples/meta --out public
```

`npm run test:e2e` はローカルにインストール済みの Chrome channel を使います。CI では `npm run test:e2e:ci` と Playwright 管理の Chromium を使います。GitHub Actions は `develop`、`main`、Pull Request で pytest、Playwright Demo チェック、`docker compose config` を実行します。

## License

MIT
