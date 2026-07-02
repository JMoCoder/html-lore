const i18n = {
  en: {
    appLanguage: "en",
    sidebarAria: "Library navigation",
    readerAria: "Reader",
    readerFrameTitle: "HTML knowledge item",
    closeReader: "Close reader",
    home: "Home",
    collapseSidebar: "Collapse sidebar",
    expandSidebar: "Expand sidebar",
    resizeSidebar: "Resize sidebar",
    userMenu: "User menu",
    subscriptionStatus: "Subscription",
    subscriptionSelfHosted: "Self-hosted",
    aiCreditsBalance: "AI credits",
    agentStatus: "Agent status",
    aiReady: "AI ready",
    uploadAvatar: "Upload avatar",
    avatarOptions: "Avatar options",
    importHtmlFile: "Import HTML file",
    collapseNavSection: "Collapse {name}",
    expandNavSection: "Expand {name}",
    language: "Language",
    toggleTheme: "Toggle dark and light mode",
    openGlobalAi: "Open AI assistant",
    closeGlobalAi: "Close AI assistant",
    globalAiPanel: "Global AI assistant",
    resizeAiPanel: "Resize AI panel",
    resizeAiComposer: "Resize AI input area",
    globalAiAssistant: "Global AI",
    aiConversation: "Knowledge Q&A",
    aiContext: "Context",
    aiCurrentContext: "Current context",
    aiContextGlobal: "All notes",
    aiContextLibrary: "Library: {name}",
    aiContextCollection: "Collection: {name}",
    aiContextTag: "Tag: {name}",
    aiContextReader: "Current topic: {title}",
    aiContextSearch: "Search results: {query}",
    aiContextCollections: "Collections: {names}",
    aiContextTags: "Tags ({mode}): {names}",
    aiContextManualItems: "Selected files: {titles}",
    aiContextManualCount: "Selected {count} notes",
    aiContextTagSummary: "{first} and {count} tags",
    tagMatchModeAnyLabel: "OR",
    tagMatchModeAllLabel: "AND",
    aiContextFavoritesOnly: "Favorites only",
    aiContextArchivedHidden: "Archived excluded",
    aiContextArchivedShown: "Archived included",
    aiWelcome: "This AI panel will answer questions against the current workspace context. Connect Agent Server later to enable real responses.",
    aiUserPlaceholder: "User question",
    aiAssistantPlaceholder: "AI response placeholder. No request was sent.",
    aiReplying: "Replying...",
    aiContentExpansion: "Expand",
    aiDeepResearch: "Research",
    aiDeepResearchSoon: "Research is planned for the AI generation workflow.",
    staticDemoUnavailable: "Demo mode only previews the interface. This action is unavailable.",
    aiPanelComingSoon: "Conversation and note generation are in development.",
    aiNewConversation: "New conversation",
    aiConversationHistory: "Conversation history",
    aiConversationHistoryEmpty: "No conversation history yet.",
    aiConversationHistoryFailed: "Conversation history could not be loaded.",
    aiConversationHistoryAll: "AI conversations",
    aiConversationHistoryAllIntro: "Review, reopen, and delete all AI knowledge-base conversations.",
    aiConversationHistoryUnavailable: "Conversation management requires the backend server.",
    refreshConversations: "Refresh conversations",
    openConversationContext: "Open",
    deleteConversation: "Delete",
    deleteConversationConfirm: "Delete this AI conversation history?",
    aiConversationDeleted: "Conversation deleted.",
    aiChatPlaceholder: "Ask about the current notes or request a new HTML note...",
    aiProviderUnavailable: "AI provider is not configured on the server.",
    aiMessageFailed: "AI request failed.",
    aiSources: "Sources",
    aiSourceLocal: "Local",
    aiSourceExternal: "External",
    generateHtmlNote: "Generate note",
    generateNoteDialog: "Generate note",
    generateNoteIntro: "Create an HTML note from the current AI conversation and selected workspace context.",
    generateTheme: "Theme",
    generateTargetUse: "Purpose",
    generateStylePreference: "Style preference",
    generateAudience: "Audience",
    generateReferenceDefault: "Default",
    generateShareSafetyHint: "Share-target notes are reviewed with the public share safety rules. Static, self-contained output is more likely to pass.",
    generateDefault: "Default",
    generateDark: "Dark",
    generateLight: "Light",
    generatePersonal: "Personal",
    generateShare: "Share",
    generateMinimal: "Minimal",
    generateBusiness: "Business",
    generateTech: "Tech",
    generateRetro: "Retro",
    generateMagazine: "Magazine",
    generateReport: "Report",
    generateWebpage: "Webpage",
    generatePpt: "PPT",
    generateNoteSubmit: "Generate note",
    generateNoteRunning: "Generating note...",
    generateNoteCreated: "Generated note: {title}",
    generateNoteNeedsAgent: "AI note generation requires the backend server.",
    generateNoteFailed: "Note generation failed.",
    send: "Send",
    settings: "Settings",
    settingsTitle: "Settings",
    closeSettings: "Close settings",
    settingsSections: "Settings sections",
    basicSettings: "Basic settings",
    basicSettingsIntro: "Configure interface preferences stored in this browser.",
    interfaceTheme: "Theme settings",
    themeSettingsComingSoon: "Theme color controls will be added here later.",
    languageSetting: "Language",
    themeSystem: "System",
    themeLight: "Light",
    themeDark: "Dark",
    libraryManagement: "Library",
    collectionManagement: "Collections",
    tagManagement: "Tags",
    libraryManagementIntro: "Library filters are fixed system views. You can choose whether each view appears in the sidebar.",
    collectionManagementIntro: "Hide collections from the sidebar now. Add, rename, merge, and delete need a metadata writer because collections are stored on items.",
    tagManagementIntro: "Hide tags from the sidebar now. Add, rename, merge, and delete need a metadata writer because tags are stored on items.",
    managementStaticNote: "Static mode can only control sidebar visibility. Structural changes must update item metadata through Agent Server or a metadata editor.",
    addCollection: "Add collection",
    addTag: "Add tag",
    rename: "Rename",
    merge: "Merge",
    delete: "Delete",
    requiresWriter: "Requires metadata writer",
    visible: "Visible",
    aiProviders: "AI providers",
    aiRunHistory: "AI runs",
    aiRunHistoryIntro: "Review recent AI generation runs without exposing prompts, source text, or API keys.",
    aiGenerationHistory: "AI generation history",
    aiGenerationHistoryIntro: "Review generated note jobs, open finished notes, retry failures, or manage history.",
    aiGenerationHistoryDetails: "Details",
    aiGenerationHistoryMore: "More",
    aiGenerationHistoryMorePlaceholder: "More generation details will be designed here.",
    aiGenerationHistoryOpenItem: "Open note",
    aiGenerationHistoryDeleteConfirm: "Delete or cancel this generation job?",
    aiGenerationHistoryGeneratedAt: "Generated: {date}",
    aiGenerationDetailTitle: "AI generation details",
    aiGenerationDetailEyebrow: "LangGraph workflow",
    aiGenerationDetailCurrentStage: "Current stage",
    aiGenerationDetailStarted: "Started",
    aiGenerationDetailUpdated: "Updated",
    aiGenerationDetailCompleted: "Completed",
    aiGenerationDetailMessage: "Message",
    aiGenerationDetailError: "Error",
    aiGenerationDetailSummary: "Summary",
    aiGenerationDetailCurrentAction: "Current action",
    aiGenerationDetailInputSummary: "Input summary",
    aiGenerationDetailOutputSummary: "Output summary",
    aiGenerationDetailQualityScore: "Quality score",
    aiGenerationDetailUsage: "Usage",
    aiGenerationDetailWarnings: "Warnings",
    aiGenerationDetailMetadata: "Metadata",
    aiGenerationDetailNoStage: "No workflow stage has been recorded yet.",
    aiGenerationDetailNoData: "No detailed record yet.",
    aiGenerationDefaultSkills: "Default skills",
    aiGenerationEnhancedSkills: "Enhanced skills",
    aiGenerationSkillTriggeredBy: "Triggered by",
    aiGenerationDetailLoading: "Loading generation details...",
    aiGenerationDetailLoadFailed: "Generation details could not be loaded.",
    aiGenerationDetailCreated: "Created",
    refreshAiJobs: "Refresh generation history",
    aiRunHistoryEmpty: "No AI runs yet.",
    aiRunHistoryUnavailable: "AI run history requires the backend server.",
    aiRunHistoryFailed: "AI run history could not be loaded.",
    refreshAiRuns: "Refresh runs",
    aiJobQueue: "Generation history",
    aiJobQueueEmpty: "No generation history yet.",
    aiJobQueued: "AI job queued: {jobId}",
    aiJobRetry: "Retry",
    aiJobNotRetryable: "This AI job cannot be retried.",
    aiJobRetrying: "Retrying AI job: {jobId}",
    aiJobCompleted: "AI job completed.",
    aiJobFailed: "AI job failed: {message}",
    aiJobCurrentStage: "Current stage",
    aiJobTrace: "Process",
    aiJobChecklist: "Checklist",
    aiJobSkills: "Skills",
    aiJobArtifacts: "Agent outputs",
    aiRunHtmlGeneration: "Generated from conversation",
    aiRunMaterialGeneration: "Generated from uploaded material",
    aiRunKnowledgeQa: "Knowledge Q&A",
    aiRunUnknownKind: "AI run",
    aiRunStatusCompleted: "Completed",
    aiRunStatusFailed: "Failed",
    aiRunStatusRunning: "Running",
    aiRunStatusPending: "Pending",
    aiRunStatusRetrying: "Retrying",
    aiRunStatusWarning: "Warning",
    aiGenerationStageParsing: "Parsing",
    aiGenerationStageAnalyzing: "Analyzing",
    aiGenerationStagePlanning: "Planning",
    aiGenerationStageWriting: "Writing",
    aiGenerationStageDesigning: "Designing",
    aiGenerationStageCoding: "Writing code",
    aiGenerationStageVerifying: "Verifying",
    aiGenerationStageSafety: "Safety review",
    aiGenerationStageFinalizing: "Finalizing",
    aiGenerationStageWritingFile: "Writing file",
    aiRunNodeCount: "{count} steps",
    aiRunDuration: "{duration}",
    aiRunCompletedAt: "Completed: {date}",
    aiRunGeneratedAt: "Generated: {date}",
    aiRunItem: "Item: {id}",
    aiRunError: "Error: {message}",
    aiRunErrorLabel: "Error:",
    aiRunRetryable: "Retryable",
    aiRunNotCancellable: "Not cancellable",
    aiRunDetails: "Details",
    aiRunHideDetails: "Hide",
    aiRunDetailsLoading: "Loading run details...",
    aiRunDetailsFailed: "Run details could not be loaded.",
    aiRunSpec: "Spec",
    aiRunUsage: "Usage",
    aiRunBudget: "Budget",
    aiRunNodes: "Steps",
    aiRunNoDetailData: "No detail data recorded.",
    aiRunInputTokens: "Input tokens: {count}",
    aiRunOutputTokens: "Output tokens: {count}",
    aiRunTotalTokens: "Total tokens: {count}",
    aiKnowledgeAssistant: "AI knowledge assistant",
    aiKnowledgeAssistantIntro: "Prepare an AI job to reclassify, retag, or review all knowledge items in the library. This module is a placeholder until database write support is implemented.",
    assistantOperation: "Operation",
    assistantClassify: "Reclassify collections",
    assistantTag: "Retag items",
    assistantReview: "Mark review status",
    assistantCustom: "Custom prompt",
    assistantPrompt: "Prompt",
    assistantPromptPlaceholder: "Describe how AI should reorganize or tag the knowledge base.",
    assistantImpactNote: "This type of operation may rewrite existing database metadata. The real submit flow must show a second confirmation before it runs.",
    submitAssistantJob: "Submit AI job",
    assistantConfirm: "This may affect the existing knowledge database. Continue?",
    assistantComingSoon: "Development in progress. No database changes were made.",
    developmentInProgress: "Development in progress",
    localBackupRestore: "Local backup & restore",
    localBackupIntro: "Back up local browser preferences, view state, favorites, archives, and non-sensitive settings.",
    autoBackup: "Enable automatic local backup snapshots",
    backupScopeNote: "Static mode can export browser-side state and the current manifest. Source HTML/YAML files still need filesystem or server-side backup.",
    createBackup: "Create backup",
    restoreBackup: "Restore backup",
    backupCreated: "Backup file created.",
    backupRestored: "Backup restored. Reloading workspace state.",
    backupFailed: "Backup file could not be restored.",
    webdavSettings: "WebDAV",
    webdavIntro: "Prepare remote backup settings for future Agent Server sync.",
    webdavUrl: "WebDAV URL",
    webdavUsername: "Username",
    webdavRemotePath: "Remote path",
    webdavPasswordNote: "Password or app token is not saved in this browser. Future sync should hand credentials to Agent Server over a protected connection.",
    saveWebdav: "Save WebDAV settings",
    webdavSaved: "Saved non-sensitive WebDAV settings.",
    dataExport: "Data export",
    dataExportIntro: "Export manifest data or browser preferences for inspection and migration.",
    exportManifest: "Export manifest",
    exportPreferences: "Export preferences",
    dataExportNote: "Exports are downloaded as JSON files. They do not include API keys.",
    exportCreated: "Export file created.",
    shareManagement: "Share links",
    shareManagementIntro: "Review active public note links and revoke access when a note should no longer be shared.",
    shareDialog: "Share note",
    shareSecurityNote: "Shared notes are public read-only pages. HTMlore blocks sharing when a note contains executable HTML, dangerous links, or likely secrets. External links are disabled in the shared page.",
    shareDuration: "Duration",
    shareDuration1h: "1 hour",
    shareDuration1d: "1 day",
    shareDuration7d: "7 days",
    shareDuration30d: "30 days",
    shareDurationForever: "Forever",
    shareLink: "Share link",
    shareValidUntil: "Valid until: {date}",
    shareNoExpiry: "Never expires",
    createShare: "Create share",
    updateShare: "Update share",
    copyShareLink: "Copy share link",
    revokeShare: "Revoke share",
    shareNeedsAgent: "Sharing requires the backend server.",
    shareCreated: "Share link created.",
    shareUpdated: "Share settings updated.",
    shareRevoked: "Share revoked.",
    shareCopied: "Share link copied.",
    shareLinkOneTime: "This older share was created before persistent share links were available. Revoke and create a new share if you need a copyable link.",
    shareBlocked: "This note cannot be shared because it failed the safety checks.",
    shareFailed: "Share operation failed.",
    noShares: "No shared links.",
    shareActive: "Active",
    shareExpired: "Expired",
    shareAccessCount: "{count} visits",
    userProfile: "User profile",
    userProfileIntro: "Profile details for future sync and cloud account features.",
    userProfilePlaceholder: "This area will manage display name, avatar, workspace identity, and plan information after account support is added.",
    accountSecurity: "Account & security",
    accountSecurityIntro: "Security controls for future login, devices, and credential workflows.",
    accountSecurityPlaceholder: "This area will manage password, passkeys, sessions, connected devices, and security events after account support is added.",
    userAgreement: "User agreement",
    aboutProject: "About project",
    updateDocs: "Update docs",
    aiProviderIntro: "Configure the provider and model used by the optional Agent Server.",
    provider: "Provider",
    customProvider: "Custom provider",
    currentModel: "Current model",
    apiBaseUrl: "API base URL",
    apiKey: "API key",
    apiKeyPlaceholder: "Stored only by Agent Server, not in this browser",
    newModel: "Add model",
    temperature: "Temperature",
    maxTokens: "Max tokens",
    keyStorageNote: "Security: API keys are not saved in localStorage. In static mode this form only saves non-sensitive preferences. In full mode the key is sent to the Agent Server over your protected connection and should be encrypted or stored as a server environment secret.",
    saveProviderConfig: "Save configuration",
    testConnection: "Test connection",
    settingsSavedStatic: "Saved local model preferences. API key was not stored.",
    settingsNeedsAgent: "Agent Server is not configured. API key was not sent or saved.",
    settingsSavedAgent: "Configuration sent to Agent Server.",
    settingsAgentFailed: "Agent Server did not accept the configuration.",
    termsIntro: "HTMlore is designed for personal and team knowledge assets.",
    termsPrivateUse: "Use it with content you own, have permission to process, or can lawfully store for private use.",
    termsCopyright: "Generated notes should summarize and cite sources instead of copying protected works wholesale.",
    termsSecurity: "You are responsible for protecting deployed Agent APIs, uploads, and model credentials.",
    aboutIntro: "HTMlore turns HTML files into a card-based static knowledge workspace.",
    aboutStaticFirst: "HTML and YAML files remain the knowledge source of truth; the database should only hold optional job state.",
    aboutVersion: "Current version: {version}.",
    updateAvailable: "Update available: {version}.",
    versionCurrent: "You are on the latest checked version.",
    versionCheckUnavailable: "Version check unavailable.",
    updatesIntro: "Project updates are tracked in the repository and local planning docs.",
    updatesChangelog: "Public release notes live in CHANGELOG.md.",
    updatesDocsLocal: "Product planning documents under documents/ are local-only and ignored by Git.",
    updatesNext: "Next major work: Agent Server, secure provider storage, Pagefind, and metadata editing.",
    loading: "Loading",
    items: "{count} items",
    library: "Library",
    collections: "Collections",
    tags: "Tags",
    newButton: "+ Import",
    allItems: "All Items",
    inbox: "Inbox",
    recent: "Recent",
    favorites: "Favorites",
    generated: "Generated",
    imported: "Imported",
    generatedSource: "Generated",
    importedSource: "Imported",
    archived: "Archived",
    loginEyebrow: "Private workspace",
    loginUsername: "Username",
    loginPassword: "Password",
    loginSubmit: "Sign in",
    loginNoRegister: "Registration is disabled. Use the account configured by the server administrator.",
    loginFailed: "Invalid username or password.",
    loginUnavailable: "Login service is unavailable.",
    logout: "Sign out",
    knowledgeWorkspace: "Knowledge Workspace",
    feelingLucky: "I'm feeling lucky",
    viewStyle: "View style",
    resultFilters: "Result filters",
    advancedFilters: "Tag filters",
    collectionFilters: "Collections",
    tagFilters: "Tags",
    tagFilterSelectedCount: "(Selected: {count})",
    tagMatchMode: "Tag match mode",
    tagMatchAny: "OR",
    tagMatchAll: "AND",
    sort: "Sort",
    sortNewest: "Time: new to old",
    sortOldest: "Time: old to new",
    sortTitleAz: "Title: A-Z",
    sortTitleZa: "Title: Z-A",
    cardView: "Card view",
    listView: "List view",
    hideArchived: "Hide archived items",
    showArchived: "Show archived items",
    onlyFavorites: "Only favorites",
    showAllFavorites: "Show all items",
    search: "Search",
    searchTitle: "Search: {query}",
    searchPlaceholder: "Title, summary, tag, path",
    manifestMissing: "Manifest not found. Run <code>html-lore build</code> first.",
    noMatches: "No matching HTML knowledge items.",
    newKnowledgeItem: "New Knowledge Item",
    createHtmlNote: "Create with AI",
    staticMode: "Static mode",
    agentConnected: "Agent connected",
    connectAgent: "Connect an Agent Server to create notes from this entry.",
    inputType: "Input type",
    inputAuto: "Auto",
    inputLink: "Link",
    inputFile: "File",
    inputBook: "Book",
    inputTopic: "Topic",
    newItemPlaceholder: "Describe what you want to generate",
    chooseFile: "Choose file",
    noFileSelected: "No file selected",
    fileSelected: "{name}",
    filesSelected: "{name} + {count} more",
    fileReadyStatus: "{size} selected",
    filesReadyStatus: "{count} files · {size} selected",
    fileTooLargeStatus: "{size} exceeds the {limit} upload limit",
    filesTooLargeStatus: "{size} exceeds the {limit} total upload limit",
    fileUploadStarting: "Preparing upload...",
    fileUploadingStatus: "Uploading {percent}%",
    fileUploadQueued: "Upload complete.",
    fileUploadFailedStatus: "Upload failed: {message}",
    uploadLimitUnknown: "configured limit",
    removeFile: "Remove file",
    chooseReferenceFile: "Upload style",
    referenceFileHint: "Optional style reference. Supports JPG/PNG, HTML, PDF, PPT/PPTX.",
    removeReferenceFile: "Remove reference file",
    moreSettings: "More",
    chooseFileFirst: "Choose a source file first.",
    create: "Create",
    emptyInput: "Enter a link, book, file path, or topic first.",
    agentNotConfigured: "Agent Server not configured. Set window.HTML_LORE_AGENT_URL before loading the app.",
    submittingJob: "Submitting job...",
    queuedJob: "Queued job {jobId}",
    agentUnavailable: "Agent Server is unavailable.",
    importingHtml: "Importing HTML file...",
    importHtmlDone: "Imported {title}",
    importHtmlFailed: "HTML import failed.",
    generatingMaterialNote: "Generating note from uploaded material...",
    materialNoteDone: "Generated note: {title}",
    materialNoteFailed: "Material note generation failed.",
    noSummary: "No summary yet.",
    read: "Read",
    original: "Original",
    shareAction: "Share",
    editMetadata: "Edit metadata",
    editCode: "Edit code",
    editFile: "Edit file",
    editFileComingSoon: "File editor is planned for a later version.",
    fileEditor: "Visual file editor",
    fileEditTextMode: "Text",
    fileEditElementMode: "Element",
    fileResetElement: "Reset element",
    fileSelectedElement: "Selected element",
    fileNoSelection: "Select text or an element in the preview.",
    fileTextContent: "Text content",
    fileTextColor: "Text color",
    fileBackgroundColor: "Background",
    fileTextStyle: "Text style",
    fileFontSize: "Font size",
    fileLineHeight: "Line height",
    fileFontWeight: "Weight",
    fileTextAlign: "Align",
    fileStyleInherit: "Inherit",
    alignLeft: "Left",
    alignCenter: "Center",
    alignRight: "Right",
    undo: "Undo",
    redo: "Redo",
    bold: "Bold",
    italic: "Italic",
    underline: "Underline",
    strikethrough: "Strikethrough",
    resizeEditorPanel: "Resize editor panel",
    collapseEditorPanel: "Collapse editor panel",
    expandEditorPanel: "Expand editor panel",
    fileEditorLoading: "Loading visual editor...",
    fileEditorLoaded: "Select an editable element.",
    fileEditorUnsaved: "Unsaved visual edits",
    fileEditorSaved: "Visual edits saved.",
    fileEditorSaveFailed: "Visual edits failed to save.",
    fileEditorUnsupported: "This element is not editable in visual mode.",
    fileEditorConfirmClose: "Discard unsaved visual edits?",
    metadataEditor: "Edit note metadata",
    metadataTitle: "Title",
    metadataSummary: "Summary",
    metadataCollection: "Collection",
    metadataTags: "Tags",
    metadataAddCollection: "Add collection...",
    metadataAddTag: "Add tag...",
    metadataStorageNote: "With Agent Server connected, changes are written to YAML metadata. Static mode saves local browser overrides only.",
    save: "Save",
    cancel: "Cancel",
    metadataSaved: "Metadata saved.",
    metadataSaveFailed: "Metadata save failed.",
    codeEditor: "HTML code editor",
    codeFullscreen: "Fullscreen",
    codeExitFullscreen: "Exit fullscreen",
    codeWrap: "Wrap lines",
    saveAndClose: "Save & close",
    codeLoading: "Loading source...",
    codeLoaded: "Source loaded.",
    codeUnsaved: "Unsaved changes",
    codeSaved: "HTML source saved.",
    codeSaveFailed: "HTML source save failed.",
    codeNeedsAgent: "Agent Server is required to save HTML source.",
    codeShareSafetyConfirm: "This HTML can be saved locally, but it may not pass public share safety checks.\n\nReasons: {reasons}\n\nSave anyway?",
    codeShareSafetyFailed: "Share safety precheck failed.",
    codeConfirmClose: "Discard unsaved source changes?",
    codePosition: "Line {line}, column {column}",
    stateSaveFailed: "State save failed.",
    navigationSaveFailed: "Navigation settings save failed.",
    favoriteAction: "Favorite",
    unfavoriteAction: "Remove favorite",
    archiveAction: "Archive",
    unarchiveAction: "Unarchive",
    confirmArchive: "Archive this note? Archived notes only appear in the Archived library view until restored.",
    permanentDeleteAction: "Delete permanently",
    confirmPermanentDelete: "Permanently delete this archived note? This removes the HTML file and metadata when Agent Server is connected. This cannot be undone.",
    deleteNeedsAgent: "Agent Server is required to permanently delete archived notes.",
    deleteFailed: "Permanent delete failed.",
    addToAiContext: "Add to Q&A context",
    removeFromAiContext: "Remove from Q&A context",
    item: "Item",
  },
  "zh-CN": {
    appLanguage: "zh-CN",
    sidebarAria: "知识库导航",
    readerAria: "阅读器",
    readerFrameTitle: "HTML 知识条目",
    closeReader: "关闭阅读器",
    home: "回到主页",
    collapseSidebar: "收起侧栏",
    expandSidebar: "展开侧栏",
    resizeSidebar: "调整侧栏宽度",
    userMenu: "用户菜单",
    subscriptionStatus: "订阅状态",
    subscriptionSelfHosted: "自托管",
    aiCreditsBalance: "AI 点数",
    agentStatus: "Agent 状态",
    aiReady: "AI 已就绪",
    uploadAvatar: "上传头像",
    avatarOptions: "头像选项",
    importHtmlFile: "导入HTML文件",
    collapseNavSection: "折叠{name}",
    expandNavSection: "展开{name}",
    language: "语言",
    toggleTheme: "切换暗色与亮色模式",
    openGlobalAi: "打开 AI 助理",
    closeGlobalAi: "关闭 AI 助理",
    globalAiPanel: "全局 AI 助理",
    resizeAiPanel: "调整 AI 面板宽度",
    resizeAiComposer: "调整 AI 输入区域高度",
    globalAiAssistant: "全局 AI",
    aiConversation: "知识库问答",
    aiContext: "上下文",
    aiCurrentContext: "当前上下文",
    aiContextGlobal: "全部笔记",
    aiContextLibrary: "资料库：{name}",
    aiContextCollection: "集合：{name}",
    aiContextTag: "标签：{name}",
    aiContextReader: "当前话题：{title}",
    aiContextSearch: "搜索结果：{query}",
    aiContextCollections: "集合：{names}",
    aiContextTags: "标签（{mode}）：{names}",
    aiContextManualItems: "指定文件：{titles}",
    aiContextManualCount: "自选 {count} 篇笔记",
    aiContextTagSummary: "{first} 等 {count} 个标签",
    tagMatchModeAnyLabel: "或",
    tagMatchModeAllLabel: "且",
    aiContextFavoritesOnly: "仅收藏",
    aiContextArchivedHidden: "已排除归档",
    aiContextArchivedShown: "包含归档",
    aiWelcome: "这里将针对当前工作区上下文进行 AI 问答。连接 Agent Server 后再启用真实回复。",
    aiUserPlaceholder: "用户问题",
    aiAssistantPlaceholder: "AI 回复占位。当前未发送任何请求。",
    aiReplying: "回复中...",
    aiContentExpansion: "拓展",
    aiDeepResearch: "研究",
    aiDeepResearchSoon: "研究功能将随 AI 生成工作流后续开放。",
    staticDemoUnavailable: "Demo 模式仅用于界面预览，当前操作不可用。",
    aiPanelComingSoon: "对话与生成 HTML 笔记功能开发中。",
    aiNewConversation: "新建对话",
    aiConversationHistory: "对话历史",
    aiConversationHistoryEmpty: "暂无对话历史。",
    aiConversationHistoryFailed: "对话历史加载失败。",
    aiConversationHistoryAll: "AI 会话历史",
    aiConversationHistoryAllIntro: "回顾、重新打开或删除所有知识库问答历史会话。",
    aiConversationHistoryUnavailable: "会话管理需要连接后端服务。",
    refreshConversations: "刷新会话",
    openConversationContext: "打开",
    deleteConversation: "删除",
    deleteConversationConfirm: "确认删除这条 AI 会话历史？",
    aiConversationDeleted: "会话已删除。",
    aiChatPlaceholder: "围绕当前笔记提问，或要求生成新的 HTML 笔记...",
    aiProviderUnavailable: "服务端尚未配置 AI 服务商。",
    aiMessageFailed: "AI 请求失败。",
    aiSources: "来源",
    aiSourceLocal: "本地",
    aiSourceExternal: "外部",
    generateHtmlNote: "生成笔记",
    generateNoteDialog: "生成笔记",
    generateNoteIntro: "根据当前 AI 对话和已选择的工作区上下文生成 HTML 笔记。",
    generateTheme: "主题",
    generateTargetUse: "目标用途",
    generateStylePreference: "样式偏好",
    generateAudience: "受众",
    generateReferenceDefault: "默认",
    generateShareSafetyHint: "分享用途会按公开分享安全规则预检。静态、无外部依赖的输出更容易通过。",
    generateDefault: "默认",
    generateDark: "暗色",
    generateLight: "亮色",
    generatePersonal: "自用",
    generateShare: "分享",
    generateMinimal: "简约",
    generateBusiness: "商务",
    generateTech: "科技",
    generateRetro: "复古",
    generateMagazine: "杂志",
    generateReport: "报告",
    generateWebpage: "网页",
    generatePpt: "PPT",
    generateNoteSubmit: "生成笔记",
    generateNoteRunning: "正在生成笔记...",
    generateNoteCreated: "已生成笔记：{title}",
    generateNoteNeedsAgent: "生成 AI 笔记需要连接后端服务。",
    generateNoteFailed: "笔记生成失败。",
    send: "发送",
    settings: "设置",
    settingsTitle: "设置",
    closeSettings: "关闭设置",
    settingsSections: "设置分区",
    basicSettings: "基本设置",
    basicSettingsIntro: "配置保存在当前浏览器中的界面偏好。",
    interfaceTheme: "主题设置",
    themeSettingsComingSoon: "后续会在这里加入主题色切换功能。",
    languageSetting: "语言设置",
    themeSystem: "跟随系统",
    themeLight: "亮色模式",
    themeDark: "暗色模式",
    libraryManagement: "资料库管理",
    collectionManagement: "集合管理",
    tagManagement: "标签管理",
    libraryManagementIntro: "资料库是固定系统视图。这里仅控制每个视图是否显示在左侧导航栏。",
    collectionManagementIntro: "当前可隐藏侧栏集合。新增、重命名、合并、删除需要元数据写入能力，因为集合保存在条目上。",
    tagManagementIntro: "当前可隐藏侧栏标签。新增、重命名、合并、删除需要元数据写入能力，因为标签保存在条目上。",
    managementStaticNote: "静态模式只能控制侧栏显隐。结构性变更必须通过 Agent Server 或元数据编辑器批量更新条目元数据。",
    addCollection: "新增集合",
    addTag: "新增标签",
    rename: "重命名",
    merge: "合并",
    delete: "删除",
    requiresWriter: "需要元数据写入服务",
    visible: "显示",
    aiProviders: "AI 服务商配置",
    aiRunHistory: "AI 运行记录",
    aiRunHistoryIntro: "查看最近的 AI 生成记录，不展示提示词、来源正文或 API Key。",
    aiGenerationHistory: "AI 生成历史",
    aiGenerationHistoryIntro: "查看生成笔记任务，打开已完成笔记，重试失败任务，或管理历史记录。",
    aiGenerationHistoryDetails: "详情",
    aiGenerationHistoryMore: "更多",
    aiGenerationHistoryMorePlaceholder: "更多生成详情将在这里设计。",
    aiGenerationHistoryOpenItem: "打开笔记",
    aiGenerationHistoryDeleteConfirm: "确认删除或取消这条生成任务？",
    aiGenerationHistoryGeneratedAt: "生成时间：{date}",
    aiGenerationDetailTitle: "AI 生成详情",
    aiGenerationDetailEyebrow: "LangGraph 工作流",
    aiGenerationDetailCurrentStage: "当前阶段",
    aiGenerationDetailStarted: "开始",
    aiGenerationDetailUpdated: "更新",
    aiGenerationDetailCompleted: "完成",
    aiGenerationDetailMessage: "消息",
    aiGenerationDetailError: "错误",
    aiGenerationDetailSummary: "摘要",
    aiGenerationDetailCurrentAction: "当前动作",
    aiGenerationDetailInputSummary: "输入摘要",
    aiGenerationDetailOutputSummary: "输出摘要",
    aiGenerationDetailQualityScore: "质量评分",
    aiGenerationDetailUsage: "用量统计",
    aiGenerationDetailWarnings: "警告",
    aiGenerationDetailMetadata: "元数据",
    aiGenerationDetailNoStage: "暂无工作流阶段记录。",
    aiGenerationDetailNoData: "暂无详细记录。",
    aiGenerationDefaultSkills: "默认技能",
    aiGenerationEnhancedSkills: "增强技能",
    aiGenerationSkillTriggeredBy: "触发原因",
    aiGenerationDetailLoading: "正在加载生成详情...",
    aiGenerationDetailLoadFailed: "无法加载生成详情。",
    aiGenerationDetailCreated: "创建",
    refreshAiJobs: "刷新生成历史",
    aiRunHistoryEmpty: "暂无 AI 运行记录。",
    aiRunHistoryUnavailable: "AI 运行记录需要连接后端服务。",
    aiRunHistoryFailed: "无法加载 AI 运行记录。",
    refreshAiRuns: "刷新运行记录",
    aiJobQueue: "生成历史",
    aiJobQueueEmpty: "暂无生成历史。",
    aiJobQueued: "AI 任务已加入队列：{jobId}",
    aiJobRetry: "重试",
    aiJobNotRetryable: "这个 AI 任务不能重试。",
    aiJobRetrying: "正在重试 AI 任务：{jobId}",
    aiJobCompleted: "AI 任务已完成。",
    aiJobFailed: "AI 任务失败：{message}",
    aiJobCurrentStage: "当前阶段",
    aiJobTrace: "处理过程",
    aiJobChecklist: "检查项",
    aiJobSkills: "技能",
    aiJobArtifacts: "智能体输出",
    aiRunHtmlGeneration: "根据对话生成",
    aiRunMaterialGeneration: "根据上传资料生成",
    aiRunKnowledgeQa: "知识库问答",
    aiRunUnknownKind: "AI 运行",
    aiRunStatusCompleted: "已完成",
    aiRunStatusFailed: "失败",
    aiRunStatusRunning: "运行中",
    aiRunStatusPending: "等待中",
    aiRunStatusRetrying: "重试中",
    aiRunStatusWarning: "警告",
    aiGenerationStageParsing: "解析资料",
    aiGenerationStageAnalyzing: "分析需求",
    aiGenerationStagePlanning: "规划方案",
    aiGenerationStageWriting: "撰写内容",
    aiGenerationStageDesigning: "设计样式",
    aiGenerationStageCoding: "撰写代码",
    aiGenerationStageVerifying: "验证质量",
    aiGenerationStageSafety: "安全审查",
    aiGenerationStageFinalizing: "整理交付",
    aiGenerationStageWritingFile: "写入资料库",
    aiRunNodeCount: "{count} 个步骤",
    aiRunDuration: "{duration}",
    aiRunCompletedAt: "完成时间：{date}",
    aiRunGeneratedAt: "生成时间：{date}",
    aiRunItem: "条目：{id}",
    aiRunError: "错误：{message}",
    aiRunErrorLabel: "错误：",
    aiRunRetryable: "可重试",
    aiRunNotCancellable: "不可取消",
    aiRunDetails: "详情",
    aiRunHideDetails: "收起",
    aiRunDetailsLoading: "正在加载运行详情...",
    aiRunDetailsFailed: "无法加载运行详情。",
    aiRunSpec: "配置",
    aiRunUsage: "用量",
    aiRunBudget: "预算",
    aiRunNodes: "步骤",
    aiRunNoDetailData: "暂无详情数据。",
    aiRunInputTokens: "输入 Tokens：{count}",
    aiRunOutputTokens: "输出 Tokens：{count}",
    aiRunTotalTokens: "总 Tokens：{count}",
    aiKnowledgeAssistant: "AI 知识库助理",
    aiKnowledgeAssistantIntro: "预留 AI 批量任务入口，用于对资料库全部内容重新分类、重新打标签或审核整理。数据库写入能力完成前，这里先作为模块占位。",
    assistantOperation: "任务类型",
    assistantClassify: "重新分类集合",
    assistantTag: "重新打标签",
    assistantReview: "标记审核状态",
    assistantCustom: "自定义提示词",
    assistantPrompt: "提示词",
    assistantPromptPlaceholder: "描述希望 AI 如何整理、分类或标注当前知识库。",
    assistantImpactNote: "这类操作未来会改写现有数据库元数据。真实提交前必须弹出二次确认。",
    submitAssistantJob: "提交 AI 任务",
    assistantConfirm: "这可能影响现有知识库数据库。确认继续吗？",
    assistantComingSoon: "开发中，未对数据库做任何修改。",
    developmentInProgress: "开发中",
    localBackupRestore: "本地备份与恢复",
    localBackupIntro: "备份浏览器本地偏好、视图状态、收藏、归档与非敏感设置。",
    autoBackup: "启用本地自动备份快照",
    backupScopeNote: "静态模式可导出浏览器侧状态和当前 Manifest。源 HTML/YAML 文件仍需要通过文件系统或服务端备份。",
    createBackup: "创建备份",
    restoreBackup: "恢复备份",
    backupCreated: "备份文件已创建。",
    backupRestored: "备份已恢复，工作区状态已重新加载。",
    backupFailed: "无法恢复该备份文件。",
    webdavSettings: "WebDAV 设置",
    webdavIntro: "预留远程备份配置，用于未来 Agent Server 同步。",
    webdavUrl: "WebDAV 地址",
    webdavUsername: "用户名",
    webdavRemotePath: "远程路径",
    webdavPasswordNote: "密码或应用令牌不会保存在浏览器。未来同步应通过受保护连接交给 Agent Server。",
    saveWebdav: "保存 WebDAV 设置",
    webdavSaved: "已保存非敏感 WebDAV 设置。",
    dataExport: "数据导出",
    dataExportIntro: "导出 Manifest 数据或浏览器偏好，便于检查与迁移。",
    exportManifest: "导出 Manifest",
    exportPreferences: "导出偏好",
    dataExportNote: "导出文件为 JSON，不包含 API Key。",
    exportCreated: "导出文件已创建。",
    shareManagement: "分享链接管理",
    shareManagementIntro: "查看当前公开分享链接，并在不再需要公开访问时取消分享。",
    shareDialog: "分享笔记",
    shareSecurityNote: "分享笔记是公开只读页面。若笔记包含可执行 HTML、危险链接或疑似密钥，HTMlore 会禁止分享；分享页中的外部链接会被禁用。",
    shareDuration: "有效期",
    shareDuration1h: "1小时",
    shareDuration1d: "1天",
    shareDuration7d: "7天",
    shareDuration30d: "30天",
    shareDurationForever: "永久",
    shareLink: "分享链接",
    shareValidUntil: "分享有效期至：{date}",
    shareNoExpiry: "永久有效",
    createShare: "创建分享",
    updateShare: "更新分享",
    copyShareLink: "复制分享链接",
    revokeShare: "取消分享",
    shareNeedsAgent: "分享功能需要连接后端服务。",
    shareCreated: "分享链接已创建。",
    shareUpdated: "分享设置已更新。",
    shareRevoked: "分享已取消。",
    shareCopied: "分享链接已复制。",
    shareLinkOneTime: "这条旧分享创建于可持续显示分享链接之前。若需要可复制链接，请取消分享后重新创建。",
    shareBlocked: "该笔记未通过安全检查，不能分享。",
    shareFailed: "分享操作失败。",
    noShares: "暂无分享链接。",
    shareActive: "分享中",
    shareExpired: "已失效",
    shareAccessCount: "{count} 次访问",
    userProfile: "用户资料",
    userProfileIntro: "预留未来同步与云账号能力所需的个人资料设置。",
    userProfilePlaceholder: "账号能力完成后，这里将管理显示名称、头像、工作区身份与套餐信息。",
    accountSecurity: "账户与安全",
    accountSecurityIntro: "预留未来登录、设备与凭据相关的安全控制。",
    accountSecurityPlaceholder: "账号能力完成后，这里将管理密码、通行密钥、会话、已登录设备与安全事件。",
    userAgreement: "用户协议",
    aboutProject: "关于项目",
    updateDocs: "更新文档",
    aiProviderIntro: "配置可选 Agent Server 使用的服务商与模型。",
    provider: "服务商",
    customProvider: "自定义服务商",
    currentModel: "当前模型",
    apiBaseUrl: "API 基础地址",
    apiKey: "API Key",
    apiKeyPlaceholder: "只由 Agent Server 保存，不保存在浏览器",
    newModel: "新增模型",
    temperature: "Temperature",
    maxTokens: "最大 Tokens",
    keyStorageNote: "安全说明：API Key 不会写入 localStorage。静态模式只保存非敏感偏好；Full 模式下 Key 只会通过受保护连接发送给 Agent Server，并应由服务端加密保存或作为环境变量管理。",
    saveProviderConfig: "保存配置",
    testConnection: "测试连接",
    settingsSavedStatic: "已保存本地模型偏好。API Key 未被保存。",
    settingsNeedsAgent: "尚未配置 Agent Server。API Key 没有发送，也没有保存。",
    settingsSavedAgent: "配置已发送到 Agent Server。",
    settingsAgentFailed: "Agent Server 未接受该配置。",
    termsIntro: "HTMlore 用于个人与团队知识资产管理。",
    termsPrivateUse: "请仅处理你拥有、被授权处理，或可合法用于私有保存的内容。",
    termsCopyright: "生成笔记应以总结和来源引用为主，不应整段复制受版权保护的作品。",
    termsSecurity: "你需要自行保护部署后的 Agent API、上传文件和模型凭据。",
    aboutIntro: "HTMlore 将 HTML 文件变成卡片式静态知识工作台。",
    aboutStaticFirst: "HTML 与 YAML 文件是知识真源；数据库只应保存可选任务状态。",
    aboutVersion: "当前版本：{version}。",
    updateAvailable: "发现可更新版本：{version}。",
    versionCurrent: "当前已是已检查到的最新版本。",
    versionCheckUnavailable: "版本检查不可用。",
    updatesIntro: "项目更新记录在仓库与本地规划文档中。",
    updatesChangelog: "公开发布记录保存在 CHANGELOG.md。",
    updatesDocsLocal: "documents/ 下的产品规划文档仅保存在本地，并被 Git 忽略。",
    updatesNext: "后续重点：Agent Server、安全服务商配置、Pagefind、元数据编辑。",
    loading: "加载中",
    items: "{count} 个条目",
    library: "资料库",
    collections: "集合",
    tags: "标签",
    newButton: "+ 导入",
    allItems: "全部条目",
    inbox: "收件箱",
    recent: "最近更新",
    favorites: "收藏",
    generated: "生成内容",
    imported: "导入内容",
    generatedSource: "生成",
    importedSource: "导入",
    archived: "已归档",
    loginEyebrow: "私有工作台",
    loginUsername: "用户名",
    loginPassword: "密码",
    loginSubmit: "登录",
    loginNoRegister: "当前不开放注册。请使用服务器管理员配置的账户。",
    loginFailed: "用户名或密码错误。",
    loginUnavailable: "登录服务不可用。",
    logout: "退出登录",
    knowledgeWorkspace: "知识工作台",
    feelingLucky: "手气不错",
    viewStyle: "视图样式",
    resultFilters: "结果筛选",
    advancedFilters: "标签筛选",
    collectionFilters: "集合",
    tagFilters: "标签",
    tagFilterSelectedCount: "（已选择：{count}）",
    tagMatchMode: "标签匹配模式",
    tagMatchAny: "或",
    tagMatchAll: "且",
    sort: "排序",
    sortNewest: "时间：新到旧",
    sortOldest: "时间：旧到新",
    sortTitleAz: "标题：A-Z",
    sortTitleZa: "标题：Z-A",
    cardView: "方块视图",
    listView: "横向条目视图",
    hideArchived: "排除已归档",
    showArchived: "显示已归档",
    onlyFavorites: "仅显示收藏",
    showAllFavorites: "显示全部",
    search: "搜索",
    searchTitle: "搜索：{query}",
    searchPlaceholder: "标题、摘要、标签、路径",
    manifestMissing: "未找到 Manifest。请先运行 <code>html-lore build</code>。",
    noMatches: "没有匹配的 HTML 知识条目。",
    newKnowledgeItem: "新知识条目",
    createHtmlNote: "用 AI 创建",
    staticMode: "静态模式",
    agentConnected: "Agent 已连接",
    connectAgent: "连接 Agent Server 后，可从这里创建笔记。",
    inputType: "输入类型",
    inputAuto: "自动",
    inputLink: "链接",
    inputFile: "文件",
    inputBook: "书籍",
    inputTopic: "主题",
    newItemPlaceholder: "请文字描述你想生成的内容",
    chooseFile: "选择文件",
    noFileSelected: "未选择文件",
    fileSelected: "{name}",
    filesSelected: "{name} 等 {count} 个文件",
    fileReadyStatus: "已选择 {size}",
    filesReadyStatus: "{count} 个文件 · 已选择 {size}",
    fileTooLargeStatus: "{size} 超过上传上限 {limit}",
    filesTooLargeStatus: "{size} 超过本次上传总上限 {limit}",
    fileUploadStarting: "正在准备上传...",
    fileUploadingStatus: "正在上传 {percent}%",
    fileUploadQueued: "上传完成。",
    fileUploadFailedStatus: "上传失败：{message}",
    uploadLimitUnknown: "当前配置上限",
    removeFile: "移除文件",
    chooseReferenceFile: "上传样式",
    referenceFileHint: "可选样式参考，支持 JPG/PNG、HTML、PDF、PPT/PPTX。",
    removeReferenceFile: "移除参考文件",
    moreSettings: "更多",
    chooseFileFirst: "请先选择一个资料文件。",
    create: "创建",
    emptyInput: "请先输入链接、书籍、文件路径或主题。",
    agentNotConfigured: "尚未配置 Agent Server。请在加载应用前设置 window.HTML_LORE_AGENT_URL。",
    submittingJob: "正在提交任务...",
    queuedJob: "已加入任务队列 {jobId}",
    agentUnavailable: "Agent Server 不可用。",
    importingHtml: "正在导入 HTML 文件...",
    importHtmlDone: "已导入 {title}",
    importHtmlFailed: "HTML 导入失败。",
    generatingMaterialNote: "正在根据上传资料生成笔记...",
    materialNoteDone: "已生成笔记：{title}",
    materialNoteFailed: "资料生成笔记失败。",
    noSummary: "暂无摘要。",
    read: "阅读",
    original: "原文",
    shareAction: "分享",
    editMetadata: "编辑元信息",
    editCode: "编辑代码",
    editFile: "编辑文件",
    editFileComingSoon: "文件编辑器将在后续版本实现。",
    fileEditor: "可视化文件编辑器",
    fileEditTextMode: "文本",
    fileEditElementMode: "元素",
    fileResetElement: "重置元素",
    fileSelectedElement: "选中元素",
    fileNoSelection: "请在预览中选择文本或元素。",
    fileTextContent: "文本内容",
    fileTextColor: "文字颜色",
    fileBackgroundColor: "背景色",
    fileTextStyle: "文字样式",
    fileFontSize: "字号",
    fileLineHeight: "行高",
    fileFontWeight: "字重",
    fileTextAlign: "对齐",
    fileStyleInherit: "继承",
    alignLeft: "左对齐",
    alignCenter: "居中",
    alignRight: "右对齐",
    undo: "撤销",
    redo: "重做",
    bold: "加粗",
    italic: "倾斜",
    underline: "下划线",
    strikethrough: "删除线",
    resizeEditorPanel: "调整编辑面板宽度",
    collapseEditorPanel: "收起编辑面板",
    expandEditorPanel: "展开编辑面板",
    fileEditorLoading: "正在加载可视化编辑器...",
    fileEditorLoaded: "请选择可编辑元素。",
    fileEditorUnsaved: "有未保存的可视化修改",
    fileEditorSaved: "可视化修改已保存。",
    fileEditorSaveFailed: "可视化修改保存失败。",
    fileEditorUnsupported: "该元素不支持可视化编辑。",
    fileEditorConfirmClose: "放弃未保存的可视化修改？",
    metadataEditor: "编辑笔记元信息",
    metadataTitle: "标题",
    metadataSummary: "摘要",
    metadataCollection: "集合",
    metadataTags: "标签",
    metadataAddCollection: "新增集合...",
    metadataAddTag: "新增标签...",
    metadataStorageNote: "连接 Agent Server 时会写回 YAML 元数据；静态模式仅保存浏览器本地覆盖。",
    save: "保存",
    cancel: "取消",
    metadataSaved: "元信息已保存。",
    metadataSaveFailed: "元信息保存失败。",
    codeEditor: "HTML 代码编辑器",
    codeFullscreen: "全屏",
    codeExitFullscreen: "退出全屏",
    codeWrap: "自动换行",
    saveAndClose: "保存并关闭",
    codeLoading: "正在加载源码...",
    codeLoaded: "源码已加载。",
    codeUnsaved: "有未保存的修改",
    codeSaved: "HTML 源码已保存。",
    codeSaveFailed: "HTML 源码保存失败。",
    codeNeedsAgent: "保存 HTML 源码需要连接 Agent Server。",
    codeShareSafetyConfirm: "这份 HTML 可以作为本地笔记保存，但可能无法通过公开分享安全检查。\n\n命中原因：{reasons}\n\n仍然保存？",
    codeShareSafetyFailed: "分享安全预检失败。",
    codeConfirmClose: "放弃未保存的源码修改？",
    codePosition: "第 {line} 行，第 {column} 列",
    stateSaveFailed: "状态保存失败。",
    navigationSaveFailed: "导航设置保存失败。",
    favoriteAction: "收藏",
    unfavoriteAction: "取消收藏",
    archiveAction: "归档",
    unarchiveAction: "取消归档",
    confirmArchive: "确认归档这篇笔记？归档后只会出现在资料库的“已归档”栏目，取消归档后会回到原集合与标签统计。",
    permanentDeleteAction: "永久删除",
    confirmPermanentDelete: "确认永久删除这篇已归档笔记？连接 Agent Server 时会删除 HTML 文件和元数据，此操作不可撤销。",
    deleteNeedsAgent: "永久删除已归档笔记需要连接 Agent Server。",
    deleteFailed: "永久删除失败。",
    addToAiContext: "加入知识库问答上下文",
    removeFromAiContext: "从知识库问答上下文移除",
    item: "条目",
  },
  ja: {
    appLanguage: "ja",
    sidebarAria: "ナレッジベースナビゲーション",
    readerAria: "リーダー",
    readerFrameTitle: "HTML ナレッジ項目",
    closeReader: "リーダーを閉じる",
    home: "ホームへ戻る",
    collapseSidebar: "サイドバーを折りたたむ",
    expandSidebar: "サイドバーを展開",
    resizeSidebar: "サイドバー幅を調整",
    userMenu: "ユーザーメニュー",
    subscriptionStatus: "サブスクリプション",
    subscriptionSelfHosted: "セルフホスト",
    aiCreditsBalance: "AI クレジット",
    agentStatus: "Agent 状態",
    aiReady: "AI 準備完了",
    uploadAvatar: "アバターをアップロード",
    avatarOptions: "アバター選択",
    importHtmlFile: "HTML ファイルをインポート",
    collapseNavSection: "{name}を折りたたむ",
    expandNavSection: "{name}を展開",
    language: "言語",
    toggleTheme: "ダーク/ライトモードを切り替え",
    openGlobalAi: "AI アシスタントを開く",
    closeGlobalAi: "AI アシスタントを閉じる",
    globalAiPanel: "グローバル AI アシスタント",
    resizeAiPanel: "AI パネル幅を調整",
    resizeAiComposer: "AI 入力エリアの高さを調整",
    globalAiAssistant: "グローバル AI",
    aiConversation: "ナレッジ Q&A",
    aiContext: "コンテキスト",
    aiCurrentContext: "現在のコンテキスト",
    aiContextGlobal: "すべてのノート",
    aiContextLibrary: "ライブラリ: {name}",
    aiContextCollection: "コレクション: {name}",
    aiContextTag: "タグ: {name}",
    aiContextReader: "現在のトピック: {title}",
    aiContextSearch: "検索結果: {query}",
    aiContextCollections: "コレクション: {names}",
    aiContextTags: "タグ（{mode}）: {names}",
    aiContextManualItems: "選択ファイル: {titles}",
    aiContextManualCount: "{count} 件のノートを選択",
    aiContextTagSummary: "{first} ほか {count} 件のタグ",
    tagMatchModeAnyLabel: "OR",
    tagMatchModeAllLabel: "AND",
    aiContextFavoritesOnly: "お気に入りのみ",
    aiContextArchivedHidden: "アーカイブを除外",
    aiContextArchivedShown: "アーカイブを含む",
    aiWelcome: "この AI パネルは現在のワークスペース文脈に対して質問応答する予定です。実際の応答は後で Agent Server 接続後に有効化します。",
    aiUserPlaceholder: "ユーザーの質問",
    aiAssistantPlaceholder: "AI 応答のプレースホルダーです。リクエストは送信されていません。",
    aiReplying: "返信中...",
    aiContentExpansion: "拡張",
    aiDeepResearch: "調査",
    aiDeepResearchSoon: "調査機能は AI 生成ワークフローで後日提供予定です。",
    staticDemoUnavailable: "Demo mode はインターフェースのプレビュー専用です。この操作は利用できません。",
    aiPanelComingSoon: "会話と HTML ノート生成は開発中です。",
    aiNewConversation: "新規会話",
    aiConversationHistory: "会話履歴",
    aiConversationHistoryEmpty: "会話履歴はまだありません。",
    aiConversationHistoryFailed: "会話履歴を読み込めませんでした。",
    aiConversationHistoryAll: "AI 会話履歴",
    aiConversationHistoryAllIntro: "すべてのナレッジ Q&A 会話を確認、再開、削除します。",
    aiConversationHistoryUnavailable: "会話管理にはバックエンドサーバーが必要です。",
    refreshConversations: "会話を更新",
    openConversationContext: "開く",
    deleteConversation: "削除",
    deleteConversationConfirm: "この AI 会話履歴を削除しますか？",
    aiConversationDeleted: "会話を削除しました。",
    aiChatPlaceholder: "現在のノートについて質問、または新しい HTML ノート生成を依頼...",
    aiProviderUnavailable: "サーバー側の AI プロバイダーが未設定です。",
    aiMessageFailed: "AI リクエストに失敗しました。",
    aiSources: "出典",
    aiSourceLocal: "ローカル",
    aiSourceExternal: "外部",
    generateHtmlNote: "ノートを生成",
    generateNoteDialog: "ノートを生成",
    generateNoteIntro: "現在の AI 会話と選択中のワークスペース文脈から HTML ノートを生成します。",
    generateTheme: "テーマ",
    generateTargetUse: "用途",
    generateStylePreference: "スタイル",
    generateAudience: "対象",
    generateReferenceDefault: "デフォルト",
    generateShareSafetyHint: "共有用途のノートは公開共有の安全ルールで事前確認されます。静的で自己完結した出力ほど通過しやすくなります。",
    generateDefault: "デフォルト",
    generateDark: "ダーク",
    generateLight: "ライト",
    generatePersonal: "自分用",
    generateShare: "共有",
    generateMinimal: "ミニマル",
    generateBusiness: "ビジネス",
    generateTech: "テック",
    generateRetro: "レトロ",
    generateMagazine: "マガジン",
    generateReport: "レポート",
    generateWebpage: "Web ページ",
    generatePpt: "PPT",
    generateNoteSubmit: "ノートを生成",
    generateNoteRunning: "ノートを生成中...",
    generateNoteCreated: "生成済みノート: {title}",
    generateNoteNeedsAgent: "AI ノート生成にはバックエンドサーバーが必要です。",
    generateNoteFailed: "ノート生成に失敗しました。",
    send: "送信",
    settings: "設定",
    settingsTitle: "設定",
    closeSettings: "設定を閉じる",
    settingsSections: "設定セクション",
    basicSettings: "基本設定",
    basicSettingsIntro: "このブラウザーに保存するインターフェース設定です。",
    interfaceTheme: "テーマ設定",
    themeSettingsComingSoon: "今後ここにテーマカラー切り替えを追加します。",
    languageSetting: "言語設定",
    themeSystem: "システム",
    themeLight: "ライト",
    themeDark: "ダーク",
    libraryManagement: "ライブラリ",
    collectionManagement: "コレクション",
    tagManagement: "タグ",
    libraryManagementIntro: "ライブラリは固定のシステムビューです。ここでは各ビューをサイドバーに表示するかだけを設定できます。",
    collectionManagementIntro: "現在はサイドバーのコレクション表示/非表示のみ変更できます。追加、名前変更、統合、削除にはメタデータ書き込み機能が必要です。",
    tagManagementIntro: "現在はサイドバーのタグ表示/非表示のみ変更できます。追加、名前変更、統合、削除にはメタデータ書き込み機能が必要です。",
    managementStaticNote: "静的モードではサイドバー表示のみ制御できます。構造的な変更には Agent Server またはメタデータエディターによる項目メタデータ更新が必要です。",
    addCollection: "コレクションを追加",
    addTag: "タグを追加",
    rename: "名前変更",
    merge: "統合",
    delete: "削除",
    requiresWriter: "メタデータ書き込みサービスが必要",
    visible: "表示",
    aiProviders: "AI プロバイダー設定",
    aiRunHistory: "AI 実行記録",
    aiRunHistoryIntro: "プロンプト、元テキスト、API Key を表示せず、最近の AI 生成実行を確認します。",
    aiGenerationHistory: "AI 生成履歴",
    aiGenerationHistoryIntro: "生成ノートのジョブを確認し、完了したノートを開き、失敗を再試行し、履歴を管理します。",
    aiGenerationHistoryDetails: "詳細",
    aiGenerationHistoryMore: "その他",
    aiGenerationHistoryMorePlaceholder: "生成詳細はここで設計します。",
    aiGenerationHistoryOpenItem: "ノートを開く",
    aiGenerationHistoryDeleteConfirm: "この生成ジョブを削除またはキャンセルしますか？",
    aiGenerationHistoryGeneratedAt: "生成時刻: {date}",
    aiGenerationDetailTitle: "AI 生成詳細",
    aiGenerationDetailEyebrow: "LangGraph ワークフロー",
    aiGenerationDetailCurrentStage: "現在の段階",
    aiGenerationDetailStarted: "開始",
    aiGenerationDetailUpdated: "更新",
    aiGenerationDetailCompleted: "完了",
    aiGenerationDetailMessage: "メッセージ",
    aiGenerationDetailError: "エラー",
    aiGenerationDetailSummary: "概要",
    aiGenerationDetailCurrentAction: "現在の動作",
    aiGenerationDetailInputSummary: "入力概要",
    aiGenerationDetailOutputSummary: "出力概要",
    aiGenerationDetailQualityScore: "品質スコア",
    aiGenerationDetailUsage: "使用量",
    aiGenerationDetailWarnings: "警告",
    aiGenerationDetailMetadata: "メタデータ",
    aiGenerationDetailNoStage: "ワークフロー段階はまだ記録されていません。",
    aiGenerationDetailNoData: "詳細記録はまだありません。",
    aiGenerationDefaultSkills: "デフォルトスキル",
    aiGenerationEnhancedSkills: "拡張スキル",
    aiGenerationSkillTriggeredBy: "トリガー",
    aiGenerationDetailLoading: "生成詳細を読み込み中...",
    aiGenerationDetailLoadFailed: "生成詳細を読み込めませんでした。",
    aiGenerationDetailCreated: "作成",
    refreshAiJobs: "生成履歴を更新",
    aiRunHistoryEmpty: "AI 実行はまだありません。",
    aiRunHistoryUnavailable: "AI 実行履歴にはバックエンドサーバーが必要です。",
    aiRunHistoryFailed: "AI 実行履歴を読み込めませんでした。",
    refreshAiRuns: "実行履歴を更新",
    aiJobQueue: "生成履歴",
    aiJobQueueEmpty: "生成履歴はまだありません。",
    aiJobQueued: "AI ジョブをキューに追加しました: {jobId}",
    aiJobRetry: "再試行",
    aiJobNotRetryable: "この AI ジョブは再試行できません。",
    aiJobRetrying: "AI ジョブを再試行中: {jobId}",
    aiJobCompleted: "AI ジョブが完了しました。",
    aiJobFailed: "AI ジョブに失敗しました: {message}",
    aiJobCurrentStage: "現在の段階",
    aiJobTrace: "プロセス",
    aiJobChecklist: "チェックリスト",
    aiJobSkills: "スキル",
    aiJobArtifacts: "エージェント出力",
    aiRunHtmlGeneration: "会話から生成",
    aiRunMaterialGeneration: "アップロード資料から生成",
    aiRunKnowledgeQa: "ナレッジ Q&A",
    aiRunUnknownKind: "AI 実行",
    aiRunStatusCompleted: "完了",
    aiRunStatusFailed: "失敗",
    aiRunStatusRunning: "実行中",
    aiRunStatusPending: "待機中",
    aiRunStatusRetrying: "再試行中",
    aiRunStatusWarning: "警告",
    aiGenerationStageParsing: "解析",
    aiGenerationStageAnalyzing: "分析",
    aiGenerationStagePlanning: "計画",
    aiGenerationStageWriting: "執筆",
    aiGenerationStageDesigning: "デザイン",
    aiGenerationStageCoding: "コード作成",
    aiGenerationStageVerifying: "検証",
    aiGenerationStageSafety: "安全確認",
    aiGenerationStageFinalizing: "仕上げ",
    aiGenerationStageWritingFile: "書き込み",
    aiRunNodeCount: "{count} ステップ",
    aiRunDuration: "{duration}",
    aiRunCompletedAt: "完了時刻: {date}",
    aiRunGeneratedAt: "生成時刻: {date}",
    aiRunItem: "項目: {id}",
    aiRunError: "エラー: {message}",
    aiRunErrorLabel: "エラー:",
    aiRunRetryable: "再試行可能",
    aiRunNotCancellable: "キャンセル不可",
    aiRunDetails: "詳細",
    aiRunHideDetails: "閉じる",
    aiRunDetailsLoading: "実行詳細を読み込み中...",
    aiRunDetailsFailed: "実行詳細を読み込めませんでした。",
    aiRunSpec: "設定",
    aiRunUsage: "使用量",
    aiRunBudget: "予算",
    aiRunNodes: "ステップ",
    aiRunNoDetailData: "詳細データはありません。",
    aiRunInputTokens: "入力トークン: {count}",
    aiRunOutputTokens: "出力トークン: {count}",
    aiRunTotalTokens: "合計トークン: {count}",
    aiKnowledgeAssistant: "AI ナレッジアシスタント",
    aiKnowledgeAssistantIntro: "ライブラリ全体を再分類、再タグ付け、レビュー整理する AI ジョブの入口です。データベース書き込み対応まではプレースホルダーです。",
    assistantOperation: "操作",
    assistantClassify: "コレクションを再分類",
    assistantTag: "項目を再タグ付け",
    assistantReview: "レビュー状態を設定",
    assistantCustom: "カスタムプロンプト",
    assistantPrompt: "プロンプト",
    assistantPromptPlaceholder: "AI にナレッジベースをどう整理、分類、タグ付けしてほしいかを書いてください。",
    assistantImpactNote: "この種の操作は既存データベースのメタデータを書き換える可能性があります。実行前には必ず二重確認を表示します。",
    submitAssistantJob: "AI ジョブを送信",
    assistantConfirm: "既存のナレッジデータベースに影響する可能性があります。続行しますか？",
    assistantComingSoon: "開発中です。データベースは変更していません。",
    developmentInProgress: "開発中",
    localBackupRestore: "ローカルバックアップと復元",
    localBackupIntro: "ブラウザー内の設定、表示状態、お気に入り、アーカイブ、非機密設定をバックアップします。",
    autoBackup: "ローカル自動バックアップスナップショットを有効化",
    backupScopeNote: "静的モードではブラウザー側の状態と現在の Manifest をエクスポートできます。元の HTML/YAML ファイルはファイルシステムまたはサーバー側で別途バックアップしてください。",
    createBackup: "バックアップを作成",
    restoreBackup: "バックアップを復元",
    backupCreated: "バックアップファイルを作成しました。",
    backupRestored: "バックアップを復元しました。ワークスペース状態を再読み込みしました。",
    backupFailed: "このバックアップファイルは復元できませんでした。",
    webdavSettings: "WebDAV 設定",
    webdavIntro: "将来の Agent Server 同期向けにリモートバックアップ設定を準備します。",
    webdavUrl: "WebDAV URL",
    webdavUsername: "ユーザー名",
    webdavRemotePath: "リモートパス",
    webdavPasswordNote: "パスワードやアプリトークンはブラウザーに保存しません。将来の同期では保護された接続で Agent Server に渡してください。",
    saveWebdav: "WebDAV 設定を保存",
    webdavSaved: "非機密の WebDAV 設定を保存しました。",
    dataExport: "データエクスポート",
    dataExportIntro: "Manifest データまたはブラウザー設定を検査や移行用にエクスポートします。",
    exportManifest: "Manifest をエクスポート",
    exportPreferences: "設定をエクスポート",
    dataExportNote: "エクスポートは JSON ファイルとしてダウンロードされます。API Key は含みません。",
    exportCreated: "エクスポートファイルを作成しました。",
    shareManagement: "共有リンク管理",
    shareManagementIntro: "公開共有リンクを確認し、不要になったノートの共有を取り消します。",
    shareDialog: "ノートを共有",
    shareSecurityNote: "共有ノートは公開の読み取り専用ページです。実行可能 HTML、危険なリンク、疑わしい secret が含まれる場合、HTMlore は共有を禁止します。共有ページ内の外部リンクは無効化されます。",
    shareDuration: "有効期限",
    shareDuration1h: "1時間",
    shareDuration1d: "1日",
    shareDuration7d: "7日",
    shareDuration30d: "30日",
    shareDurationForever: "無期限",
    shareLink: "共有リンク",
    shareValidUntil: "共有有効期限：{date}",
    shareNoExpiry: "無期限",
    createShare: "共有を作成",
    updateShare: "共有を更新",
    copyShareLink: "共有リンクをコピー",
    revokeShare: "共有を取り消す",
    shareNeedsAgent: "共有にはバックエンドサーバー接続が必要です。",
    shareCreated: "共有リンクを作成しました。",
    shareUpdated: "共有設定を更新しました。",
    shareRevoked: "共有を取り消しました。",
    shareCopied: "共有リンクをコピーしました。",
    shareLinkOneTime: "この古い共有は永続表示リンクに対応する前に作成されています。コピー可能なリンクが必要な場合は共有を取り消して再作成してください。",
    shareBlocked: "このノートは安全チェックに通らないため共有できません。",
    shareFailed: "共有操作に失敗しました。",
    noShares: "共有リンクはありません。",
    shareActive: "共有中",
    shareExpired: "期限切れ",
    shareAccessCount: "{count} 回アクセス",
    userProfile: "ユーザープロフィール",
    userProfileIntro: "将来の同期とクラウドアカウント向けのプロフィール設定です。",
    userProfilePlaceholder: "アカウント対応後、表示名、アバター、ワークスペース ID、プラン情報をここで管理します。",
    accountSecurity: "アカウントとセキュリティ",
    accountSecurityIntro: "将来のログイン、デバイス、認証情報向けのセキュリティ設定です。",
    accountSecurityPlaceholder: "アカウント対応後、パスワード、パスキー、セッション、ログイン済みデバイス、セキュリティイベントをここで管理します。",
    userAgreement: "利用規約",
    aboutProject: "プロジェクトについて",
    updateDocs: "更新ドキュメント",
    aiProviderIntro: "任意の Agent Server が使用するプロバイダーとモデルを設定します。",
    provider: "プロバイダー",
    customProvider: "カスタムプロバイダー",
    currentModel: "現在のモデル",
    apiBaseUrl: "API ベース URL",
    apiKey: "API Key",
    apiKeyPlaceholder: "Agent Server のみが保存し、ブラウザーには保存しません",
    newModel: "モデルを追加",
    temperature: "Temperature",
    maxTokens: "最大 Tokens",
    keyStorageNote: "セキュリティ: API Key は localStorage に保存されません。静的モードでは非機密の設定のみ保存します。Full モードでは保護された接続で Agent Server に送信し、サーバー側で暗号化保存または環境変数として管理してください。",
    saveProviderConfig: "設定を保存",
    testConnection: "接続テスト",
    settingsSavedStatic: "ローカルのモデル設定を保存しました。API Key は保存していません。",
    settingsNeedsAgent: "Agent Server が未設定です。API Key は送信も保存もされていません。",
    settingsSavedAgent: "設定を Agent Server に送信しました。",
    settingsAgentFailed: "Agent Server が設定を受け付けませんでした。",
    termsIntro: "HTMlore は個人およびチームのナレッジ資産管理向けです。",
    termsPrivateUse: "所有している、許可を得ている、または私的保存が合法なコンテンツのみ処理してください。",
    termsCopyright: "生成ノートは保護された著作物を丸ごと複製せず、要約と出典提示を中心にしてください。",
    termsSecurity: "デプロイした Agent API、アップロード、モデル認証情報の保護は利用者の責任です。",
    aboutIntro: "HTMlore は HTML ファイルをカード型の静的ナレッジワークスペースに変換します。",
    aboutStaticFirst: "HTML と YAML ファイルがナレッジの真のソースです。データベースは任意のジョブ状態のみを保持すべきです。",
    aboutVersion: "現在のバージョン: {version}。",
    updateAvailable: "利用可能な更新: {version}。",
    versionCurrent: "確認済みの最新バージョンです。",
    versionCheckUnavailable: "バージョン確認を利用できません。",
    updatesIntro: "プロジェクト更新はリポジトリとローカル計画ドキュメントで管理します。",
    updatesChangelog: "公開リリースノートは CHANGELOG.md にあります。",
    updatesDocsLocal: "documents/ 配下の製品計画ドキュメントはローカル専用で、Git から除外されます。",
    updatesNext: "次の重点: Agent Server、安全なプロバイダー保存、Pagefind、メタデータ編集。",
    loading: "読み込み中",
    items: "{count} 件",
    library: "ライブラリ",
    collections: "コレクション",
    tags: "タグ",
    newButton: "+ インポート",
    allItems: "すべて",
    inbox: "受信箱",
    recent: "最近更新",
    favorites: "お気に入り",
    generated: "生成済み",
    imported: "インポート済み",
    generatedSource: "生成",
    importedSource: "インポート",
    archived: "アーカイブ済み",
    loginEyebrow: "プライベートワークスペース",
    loginUsername: "ユーザー名",
    loginPassword: "パスワード",
    loginSubmit: "ログイン",
    loginNoRegister: "登録は無効です。サーバー管理者が設定したアカウントを使用してください。",
    loginFailed: "ユーザー名またはパスワードが正しくありません。",
    loginUnavailable: "ログインサービスを利用できません。",
    logout: "ログアウト",
    knowledgeWorkspace: "ナレッジワークスペース",
    feelingLucky: "おまかせ表示",
    viewStyle: "表示形式",
    resultFilters: "結果フィルター",
    advancedFilters: "タグフィルター",
    collectionFilters: "コレクション",
    tagFilters: "タグ",
    tagFilterSelectedCount: "（選択済み：{count}）",
    tagMatchMode: "タグ一致モード",
    tagMatchAny: "OR",
    tagMatchAll: "AND",
    sort: "並び替え",
    sortNewest: "時間: 新しい順",
    sortOldest: "時間: 古い順",
    sortTitleAz: "タイトル: A-Z",
    sortTitleZa: "タイトル: Z-A",
    cardView: "カード表示",
    listView: "横長リスト表示",
    hideArchived: "アーカイブ済みを非表示",
    showArchived: "アーカイブ済みを表示",
    onlyFavorites: "お気に入りのみ表示",
    showAllFavorites: "すべて表示",
    search: "検索",
    searchTitle: "検索: {query}",
    searchPlaceholder: "タイトル、概要、タグ、パス",
    manifestMissing: "Manifest が見つかりません。先に <code>html-lore build</code> を実行してください。",
    noMatches: "一致する HTML ナレッジ項目がありません。",
    newKnowledgeItem: "新規ナレッジ項目",
    createHtmlNote: "AI で作成",
    staticMode: "静的モード",
    agentConnected: "Agent 接続済み",
    connectAgent: "Agent Server を接続すると、ここからノートを作成できます。",
    inputType: "入力タイプ",
    inputAuto: "自動",
    inputLink: "リンク",
    inputFile: "ファイル",
    inputBook: "書籍",
    inputTopic: "トピック",
    newItemPlaceholder: "生成したい内容を文章で説明してください",
    chooseFile: "ファイルを選択",
    noFileSelected: "ファイル未選択",
    fileSelected: "{name}",
    filesSelected: "{name} ほか {count} 件",
    fileReadyStatus: "{size} を選択済み",
    filesReadyStatus: "{count} 件 · {size} を選択済み",
    fileTooLargeStatus: "{size} はアップロード上限 {limit} を超えています",
    filesTooLargeStatus: "{size} は合計アップロード上限 {limit} を超えています",
    fileUploadStarting: "アップロードを準備中...",
    fileUploadingStatus: "アップロード中 {percent}%",
    fileUploadQueued: "アップロード完了。",
    fileUploadFailedStatus: "アップロード失敗: {message}",
    uploadLimitUnknown: "設定済み上限",
    removeFile: "ファイルを削除",
    chooseReferenceFile: "スタイルをアップロード",
    referenceFileHint: "任意のスタイル参考。JPG/PNG、HTML、PDF、PPT/PPTX に対応。",
    removeReferenceFile: "参考ファイルを削除",
    moreSettings: "詳細",
    chooseFileFirst: "先に資料ファイルを選択してください。",
    create: "作成",
    emptyInput: "リンク、書籍、ファイルパス、またはトピックを入力してください。",
    agentNotConfigured: "Agent Server が設定されていません。アプリ読み込み前に window.HTML_LORE_AGENT_URL を設定してください。",
    submittingJob: "ジョブを送信中...",
    queuedJob: "ジョブをキューに追加しました {jobId}",
    agentUnavailable: "Agent Server を利用できません。",
    importingHtml: "HTML ファイルをインポート中...",
    importHtmlDone: "{title} をインポートしました",
    importHtmlFailed: "HTML インポートに失敗しました。",
    generatingMaterialNote: "アップロード資料からノートを生成中...",
    materialNoteDone: "生成済みノート: {title}",
    materialNoteFailed: "資料からのノート生成に失敗しました。",
    noSummary: "概要はまだありません。",
    read: "読む",
    original: "原文",
    shareAction: "共有",
    editMetadata: "メタデータを編集",
    editCode: "コードを編集",
    editFile: "ファイルを編集",
    editFileComingSoon: "ファイルエディターは今後のバージョンで実装予定です。",
    fileEditor: "ビジュアルファイルエディター",
    fileEditTextMode: "テキスト",
    fileEditElementMode: "要素",
    fileResetElement: "要素をリセット",
    fileSelectedElement: "選択中の要素",
    fileNoSelection: "プレビューでテキストまたは要素を選択してください。",
    fileTextContent: "テキスト内容",
    fileTextColor: "文字色",
    fileBackgroundColor: "背景",
    fileTextStyle: "文字スタイル",
    fileFontSize: "フォントサイズ",
    fileLineHeight: "行間",
    fileFontWeight: "太さ",
    fileTextAlign: "配置",
    fileStyleInherit: "継承",
    alignLeft: "左",
    alignCenter: "中央",
    alignRight: "右",
    undo: "元に戻す",
    redo: "やり直す",
    bold: "太字",
    italic: "斜体",
    underline: "下線",
    strikethrough: "取り消し線",
    resizeEditorPanel: "編集パネルの幅を調整",
    collapseEditorPanel: "編集パネルを折りたたむ",
    expandEditorPanel: "編集パネルを展開",
    fileEditorLoading: "ビジュアルエディターを読み込み中...",
    fileEditorLoaded: "編集可能な要素を選択してください。",
    fileEditorUnsaved: "未保存のビジュアル編集があります",
    fileEditorSaved: "ビジュアル編集を保存しました。",
    fileEditorSaveFailed: "ビジュアル編集の保存に失敗しました。",
    fileEditorUnsupported: "この要素はビジュアル編集に対応していません。",
    fileEditorConfirmClose: "未保存のビジュアル編集を破棄しますか？",
    metadataEditor: "ノートメタデータを編集",
    metadataTitle: "タイトル",
    metadataSummary: "概要",
    metadataCollection: "コレクション",
    metadataTags: "タグ",
    metadataAddCollection: "コレクションを追加...",
    metadataAddTag: "タグを追加...",
    metadataStorageNote: "Agent Server 接続時は YAML メタデータへ書き戻します。静的モードではブラウザー内のローカル上書きのみ保存します。",
    save: "保存",
    cancel: "キャンセル",
    metadataSaved: "メタデータを保存しました。",
    metadataSaveFailed: "メタデータの保存に失敗しました。",
    codeEditor: "HTML コードエディター",
    codeFullscreen: "全画面",
    codeExitFullscreen: "全画面を終了",
    codeWrap: "折り返し",
    saveAndClose: "保存して閉じる",
    codeLoading: "ソースを読み込み中...",
    codeLoaded: "ソースを読み込みました。",
    codeUnsaved: "未保存の変更があります",
    codeSaved: "HTML ソースを保存しました。",
    codeSaveFailed: "HTML ソースの保存に失敗しました。",
    codeNeedsAgent: "HTML ソースを保存するには Agent Server 接続が必要です。",
    codeShareSafetyConfirm: "この HTML はローカルノートとして保存できますが、公開共有の安全チェックを通過しない可能性があります。\n\n理由: {reasons}\n\nそれでも保存しますか？",
    codeShareSafetyFailed: "共有安全性の事前チェックに失敗しました。",
    codeConfirmClose: "未保存のソース変更を破棄しますか？",
    codePosition: "{line} 行目、{column} 列目",
    stateSaveFailed: "状態の保存に失敗しました。",
    navigationSaveFailed: "ナビゲーション設定の保存に失敗しました。",
    favoriteAction: "お気に入り",
    unfavoriteAction: "お気に入り解除",
    archiveAction: "アーカイブ",
    unarchiveAction: "アーカイブ解除",
    confirmArchive: "このノートをアーカイブしますか？復元するまで、アーカイブ済みライブラリ表示にのみ表示されます。",
    permanentDeleteAction: "完全に削除",
    confirmPermanentDelete: "このアーカイブ済みノートを完全に削除しますか？Agent Server 接続時は HTML ファイルとメタデータを削除します。この操作は元に戻せません。",
    deleteNeedsAgent: "アーカイブ済みノートの完全削除には Agent Server 接続が必要です。",
    deleteFailed: "完全削除に失敗しました。",
    addToAiContext: "Q&A コンテキストに追加",
    removeFromAiContext: "Q&A コンテキストから削除",
    item: "項目",
  },
};

const libraryFilterDefinitions = [
  { value: "all", labelKey: "allItems", test: () => true },
  { value: "inbox", labelKey: "inbox", test: (item) => getItemCollection(item) === "Inbox" },
  { value: "recent", labelKey: "recent", test: () => true },
  { value: "favorites", labelKey: "favorites", test: (item) => isFavorite(item) },
  { value: "generated", labelKey: "generated", test: (item) => item.agent?.generated || item.source_type === "topic" },
  { value: "imported", labelKey: "imported", test: (item) => item.source_type === "imported" || item.source_type === "html" },
  { value: "archived", labelKey: "archived", test: (item) => isArchived(item) },
];

const STORAGE_PREFIX = "html-lore-";

function getRuntimeConfig(name) {
  return window[`HTML_LORE_${name}`];
}

function hasRuntimeConfig(name) {
  return getRuntimeConfig(name) !== undefined;
}

function storageKey(name) {
  return `${STORAGE_PREFIX}${name}`;
}

function getStored(name) {
  return localStorage.getItem(storageKey(name));
}

function setStored(name, value) {
  localStorage.setItem(storageKey(name), value);
}

function getDefaultAgentUrl() {
  if (hasRuntimeConfig("STATIC_DEMO")) return "";
  const configuredUrl = getRuntimeConfig("AGENT_URL");
  if (configuredUrl) return configuredUrl;
  if (window.location.protocol === "file:") return "";
  const host = window.location.hostname;
  const port = window.location.port;
  const isLocalHost = host === "127.0.0.1" || host === "localhost";
  if (isLocalHost && port && port !== "80" && port !== "443") return "http://127.0.0.1:8787";
  if (host.endsWith("github.io")) return "";
  if (window.location.protocol === "http:" || window.location.protocol === "https:") return window.location.origin;
  return "";
}

function getPagesHomeUrl() {
  if (hasRuntimeConfig("STATIC_DEMO")) return "../";
  return getRuntimeConfig("PAGES_URL") || "https://jmocoder.github.io/html_lore/";
}

function getDefaultAgentToken() {
  return getRuntimeConfig("AGENT_TOKEN") || getStored("agent-token") || "";
}

const state = {
  manifest: null,
  items: [],
  filter: { type: "library", value: "all" },
  query: "",
  agentUrl: getDefaultAgentUrl(),
  agentToken: getDefaultAgentToken(),
  authEnabled: false,
  authenticated: false,
  authChecked: false,
  currentUser: { username: "", dataId: "" },
  profile: loadProfile(),
  loginSubmitting: false,
  currentVersion: "1.1.6",
  latestVersion: "",
  updateAvailable: false,
  versionCheckComplete: false,
  language: getInitialLanguage(),
  themeMode: getInitialThemeMode(),
  feedbackKey: "connectAgent",
  feedbackParams: {},
  feedbackTimer: 0,
  activeSettingsTab: "basic",
  aiConfig: loadAiConfig(),
  aiStatus: null,
  aiRuns: [],
  aiJobs: [],
  aiJobsOpen: false,
  expandedAiJobIds: new Set(),
  expandedAiGenerationJobIds: new Set(),
  aiGenerationJobNotices: {},
  aiHistoryOpen: false,
  aiHistory: [],
  aiHistoryLoaded: false,
  aiHistoryContextKey: "",
  aiConversations: [],
  aiConversationLoadingKey: "",
  aiSuppressedContextKeys: new Set(),
  aiJobsLoaded: false,
  aiJobsPollTimer: 0,
  aiGenerationDetailJob: null,
  aiGenerationDetailJobId: "",
  aiGenerationDetailStageIndex: 0,
  aiGenerationDetailEventSource: null,
  aiGenerationDetailPollTimer: 0,
  aiKnownCompletedJobIds: new Set(),
  aiSubmittedJobIds: new Set(),
  selectedAiRunId: "",
  aiRunDetails: {},
  aiConversationId: "",
  aiConversationContextKey: "",
  aiContentExpansion: false,
  aiConversationLoadedKey: "",
  dataConfig: loadDataConfig(),
  itemState: loadItemState(),
  navConfig: loadNavConfig(),
  navSectionCollapsed: getInitialNavSectionState(),
  sidebarCollapsed: getInitialSidebarState(),
  sidebarWidth: getInitialSidebarWidth(),
  viewMode: getInitialViewMode(),
  aiPanelOpen: false,
  aiPanelWidth: getInitialAiPanelWidth(),
  aiComposerHeight: getInitialAiComposerHeight(),
  multiFilterOpen: false,
  sortOpen: false,
  sortMode: getInitialSortMode(),
  tagMatchMode: "any",
  selectedTags: new Set(),
  manualAiContextIds: new Set(),
  onlyFavorites: getInitialFavoriteFilter(),
  currentReaderItemId: "",
  editingItemId: "",
  editingTags: new Set(),
  codeEditingItemId: "",
  codeEditorOriginal: "",
  codeEditorDirty: false,
  codeEditorWrap: true,
  codeEditorFullscreen: false,
  codeEditorSaving: false,
  fileEditingItemId: "",
  fileEditorOriginal: "",
  fileEditorDirty: false,
  fileEditorMode: "text",
  fileEditorSelectedPath: "",
  fileEditorHistory: [],
  fileEditorHistoryIndex: -1,
  fileEditorSyncing: false,
  fileEditorHistoryTimer: 0,
  fileEditorPanelWidth: getInitialFileEditorPanelWidth(),
  fileEditorPanelCollapsed: false,
  pendingMaterialFiles: [],
  pendingReferenceFile: null,
  newPromptManualHeight: 0,
  materialUpload: { status: "idle", progress: 0, message: "" },
  referenceUpload: { status: "idle", progress: 0, message: "" },
  shares: [],
  sharingItemId: "",
};

const elements = {
  body: document.body,
  loginScreen: document.querySelector("#login-screen"),
  loginForm: document.querySelector("#login-form"),
  loginUsername: document.querySelector("#login-username"),
  loginPassword: document.querySelector("#login-password"),
  loginFeedback: document.querySelector("#login-feedback"),
  logoutButton: document.querySelector("#logout-button"),
  settingsProfileAvatar: document.querySelector("#settings-profile-avatar"),
  settingsProfileName: document.querySelector("#settings-profile-name"),
  settingsProfileId: document.querySelector("#settings-profile-id"),
  avatarUploadTrigger: document.querySelector("#avatar-upload-trigger"),
  avatarUpload: document.querySelector("#avatar-upload"),
  brandHome: document.querySelector("#brand-home"),
  sidebar: document.querySelector(".sidebar"),
  sidebarCollapse: document.querySelector("#sidebar-collapse"),
  sidebarResize: document.querySelector("#sidebar-resize"),
  navSectionToggles: document.querySelectorAll("[data-nav-section-toggle]"),
  navSections: document.querySelectorAll("[data-nav-section]"),
  importEntries: document.querySelectorAll("[data-import-entry]"),
  htmlImportFile: ensureHtmlImportInput(),
  materialGenerateFile: document.querySelector("#material-generate-file"),
  materialReferenceFile: document.querySelector("#material-reference-file"),
  newGenerateTheme: document.querySelector("#new-generate-theme"),
  newGenerateTargetUse: document.querySelector("#new-generate-target-use"),
  newGenerateStylePreference: document.querySelector("#new-generate-style-preference"),
  newGenerateAudience: document.querySelector("#new-generate-audience"),
  siteTitle: document.querySelector("#site-title"),
  languageSelect: document.querySelector("#language-select"),
  themeModeButtons: document.querySelectorAll("[data-theme-mode]"),
  settingsOpen: document.querySelector("#settings-open"),
  settingsBack: document.querySelector("#settings-back"),
  settingsPage: document.querySelector("#settings-page"),
  settingsContent: document.querySelector(".settings-content"),
  settingsTabs: document.querySelectorAll("[data-settings-tab]"),
  settingsSections: document.querySelectorAll("[data-settings-section]"),
  collectionManagement: document.querySelector("#collection-management"),
  libraryManagement: document.querySelector("#library-management"),
  tagManagement: document.querySelector("#tag-management"),
  aiSettingsForm: document.querySelector("#ai-settings-form"),
  aiAssistantForm: document.querySelector("#ai-assistant-form"),
  assistantFeedback: document.querySelector("#assistant-feedback"),
  backupSettingsForm: document.querySelector("#backup-settings-form"),
  autoBackup: document.querySelector("#auto-backup"),
  createBackup: document.querySelector("#create-backup"),
  restoreBackup: document.querySelector("#restore-backup"),
  restoreBackupFile: document.querySelector("#restore-backup-file"),
  backupFeedback: document.querySelector("#backup-feedback"),
  webdavSettingsForm: document.querySelector("#webdav-settings-form"),
  webdavUrl: document.querySelector("#webdav-url"),
  webdavUsername: document.querySelector("#webdav-username"),
  webdavPath: document.querySelector("#webdav-path"),
  testWebdav: document.querySelector("#test-webdav"),
  webdavFeedback: document.querySelector("#webdav-feedback"),
  exportManifest: document.querySelector("#export-manifest"),
  exportPreferences: document.querySelector("#export-preferences"),
  exportFeedback: document.querySelector("#export-feedback"),
  aiProvider: document.querySelector("#ai-provider"),
  currentModel: document.querySelector("#current-model"),
  apiBaseUrl: document.querySelector("#api-base-url"),
  apiKey: document.querySelector("#api-key"),
  newModel: document.querySelector("#new-model"),
  modelTemperature: document.querySelector("#model-temperature"),
  modelMaxTokens: document.querySelector("#model-max-tokens"),
  testProvider: document.querySelector("#test-provider"),
  settingsFeedback: document.querySelector("#settings-feedback"),
  aiRunRefresh: document.querySelector("#ai-run-refresh"),
  aiRunList: document.querySelector("#ai-run-list"),
  aiRunFeedback: document.querySelector("#ai-run-feedback"),
  aiGenerationRefresh: document.querySelector("#ai-generation-refresh"),
  aiGenerationList: document.querySelector("#ai-generation-list"),
  aiGenerationFeedback: document.querySelector("#ai-generation-feedback"),
  aiGenerationDetail: document.querySelector("#ai-generation-detail"),
  aiGenerationDetailTitle: document.querySelector("#ai-generation-detail-title"),
  aiGenerationDetailMeta: document.querySelector("#ai-generation-detail-meta"),
  aiGenerationDetailStatus: document.querySelector("#ai-generation-detail-status"),
  aiGenerationStageList: document.querySelector("#ai-generation-stage-list"),
  aiGenerationStagePanel: document.querySelector("#ai-generation-stage-panel"),
  aiGenerationDetailChecklist: document.querySelector("#ai-generation-detail-checklist"),
  aiGenerationDetailSkills: document.querySelector("#ai-generation-detail-skills"),
  aiGenerationDetailFeedback: document.querySelector("#ai-generation-detail-feedback"),
  aiGenerationDetailOpen: document.querySelector("#ai-generation-detail-open"),
  aiGenerationDetailRetry: document.querySelector("#ai-generation-detail-retry"),
  aiGenerationDetailClose: document.querySelector("#ai-generation-detail-close"),
  aiConversationRefresh: document.querySelector("#ai-conversation-refresh"),
  aiConversationList: document.querySelector("#ai-conversation-list"),
  aiConversationFeedback: document.querySelector("#ai-conversation-feedback"),
  versionStatus: document.querySelector("#version-status"),
  libraryNav: document.querySelector("#library-nav"),
  collectionNav: document.querySelector("#collection-nav"),
  tagNav: document.querySelector("#tag-nav"),
  multiFilterToggle: document.querySelector("#multi-filter-toggle"),
  multiFilterPopover: document.querySelector("#multi-filter-popover"),
  multiFilterResultCount: document.querySelector("#multi-filter-result-count"),
  multiTagOptions: document.querySelector("#multi-tag-options"),
  tagMatchButtons: document.querySelectorAll("[data-tag-match-mode]"),
  sortToggle: document.querySelector("#sort-toggle"),
  sortPopover: document.querySelector("#sort-popover"),
  sortButtons: document.querySelectorAll("[data-sort-mode]"),
  favoriteFilter: document.querySelector("#favorite-filter"),
  aiPanelOpen: document.querySelector("#ai-panel-open"),
  aiPanel: document.querySelector("#ai-panel"),
  aiPanelClose: document.querySelector("#ai-panel-close"),
  aiPanelResize: document.querySelector("#ai-panel-resize"),
  aiComposer: document.querySelector("#ai-composer"),
  aiComposerResize: document.querySelector("#ai-composer-resize"),
  aiContextLabel: document.querySelector("#ai-context-label"),
  aiContextCompact: document.querySelector("#ai-context-compact"),
  aiContextCard: document.querySelector(".ai-context-card"),
  aiChatLog: document.querySelector("#ai-chat-log"),
  aiChatForm: document.querySelector("#ai-chat-form"),
  aiChatInput: document.querySelector("#ai-chat-input"),
  aiSendButton: document.querySelector(".ai-send-button"),
  aiContentExpansion: document.querySelector("#ai-content-expansion"),
  aiGenerateNote: document.querySelector("#ai-generate-note"),
  aiNewChat: document.querySelector("#ai-new-chat"),
  aiHistoryToggle: document.querySelector("#ai-history-toggle"),
  aiHistoryList: document.querySelector("#ai-history-list"),
  aiJobToggle: document.querySelector("#ai-job-toggle"),
  aiJobList: document.querySelector("#ai-job-list"),
  luckyButton: document.querySelector("#lucky-button"),
  searchInput: document.querySelector("#search-input"),
  contentGrid: document.querySelector("#content-grid"),
  newCard: document.querySelector("#new-card"),
  newItemForm: document.querySelector("#new-item-form"),
  newItemInput: document.querySelector("#new-item-input"),
  newPromptResize: document.querySelector("#new-prompt-resize"),
  newGenerationToggle: document.querySelector("#new-generation-toggle"),
  newGenerationOptions: document.querySelector("#new-generation-options"),
  newFileTrigger: document.querySelector("#new-file-trigger"),
  newFileRow: document.querySelector("#new-file-row"),
  newFileName: document.querySelector("#new-file-name"),
  newFileStatus: document.querySelector("#new-file-status"),
  newFileProgress: document.querySelector("#new-file-progress"),
  newFileRemove: document.querySelector("#new-file-remove"),
  newReferenceTrigger: document.querySelector("#new-reference-trigger"),
  newReferenceName: document.querySelector("#new-reference-name"),
  newReferenceRemove: document.querySelector("#new-reference-remove"),
  newFeedback: document.querySelector("#new-feedback"),
  agentStatus: document.querySelector("#agent-status"),
  reader: document.querySelector("#reader"),
  readerClose: document.querySelector("#reader-close"),
  readerTitle: document.querySelector("#reader-title"),
  readerSummary: document.querySelector("#reader-summary"),
  readerSource: document.querySelector("#reader-source"),
  readerTags: document.querySelector("#reader-tags"),
  readerEdit: document.querySelector("#reader-edit"),
  readerFavorite: document.querySelector("#reader-favorite"),
  readerArchive: document.querySelector("#reader-archive"),
  readerAiPanelOpen: document.querySelector("#reader-ai-panel-open"),
  readerOriginal: document.querySelector("#reader-original"),
  readerShare: document.querySelector("#reader-share"),
  readerFrame: document.querySelector("#reader-frame"),
  shareManagementList: document.querySelector("#share-management-list"),
  shareManagementFeedback: document.querySelector("#share-management-feedback"),
  shareDialog: document.querySelector("#share-dialog"),
  shareForm: document.querySelector("#share-form"),
  shareDuration: document.querySelector("#share-duration"),
  shareLink: document.querySelector("#share-link"),
  shareExpiry: document.querySelector("#share-expiry"),
  shareFeedback: document.querySelector("#share-feedback"),
  shareCreate: document.querySelector("#share-create"),
  shareCopy: document.querySelector("#share-copy"),
  shareRevoke: document.querySelector("#share-revoke"),
  shareCancel: document.querySelector("#share-cancel"),
  shareCancelIcon: document.querySelector("#share-cancel-icon"),
  generateNoteDialog: document.querySelector("#generate-note-dialog"),
  generateNoteForm: document.querySelector("#generate-note-form"),
  generateTheme: document.querySelector("#generate-theme"),
  generateTargetUse: document.querySelector("#generate-target-use"),
  generateAudience: document.querySelector("#generate-audience"),
  generateStylePreference: document.querySelector("#generate-style-preference"),
  generateNoteFeedback: document.querySelector("#generate-note-feedback"),
  generateNoteSubmit: document.querySelector("#generate-note-submit"),
  generateNoteCancel: document.querySelector("#generate-note-cancel"),
  generateNoteCancelIcon: document.querySelector("#generate-note-cancel-icon"),
  metadataEditor: document.querySelector("#metadata-editor"),
  metadataForm: document.querySelector("#metadata-form"),
  metadataTitle: document.querySelector("#metadata-title"),
  metadataSummary: document.querySelector("#metadata-summary"),
  metadataCollection: document.querySelector("#metadata-collection"),
  metadataTagPicker: document.querySelector("#metadata-tag-picker"),
  metadataEditCode: document.querySelector("#metadata-edit-code"),
  metadataEditFile: document.querySelector("#metadata-edit-file"),
  metadataCancel: document.querySelector("#metadata-cancel"),
  metadataCancelIcon: document.querySelector("#metadata-cancel-icon"),
  codeEditor: document.querySelector("#code-editor"),
  codeEditorItemTitle: document.querySelector("#code-editor-item-title"),
  codeEditorTextarea: document.querySelector("#code-editor-textarea"),
  codeEditorWrap: document.querySelector("#code-editor-wrap"),
  codeEditorFullscreen: document.querySelector("#code-editor-fullscreen"),
  codeEditorSave: document.querySelector("#code-editor-save"),
  codeEditorSaveClose: document.querySelector("#code-editor-save-close"),
  codeEditorClose: document.querySelector("#code-editor-close"),
  codeEditorFeedback: document.querySelector("#code-editor-feedback"),
  codeEditorPosition: document.querySelector("#code-editor-position"),
  fileEditor: document.querySelector("#file-editor"),
  fileEditorItemTitle: document.querySelector("#file-editor-item-title"),
  fileEditorFrame: document.querySelector("#file-editor-frame"),
  fileEditorStage: document.querySelector(".file-editor-stage"),
  fileEditorPanelResize: document.querySelector("#file-editor-panel-resize"),
  fileEditorPanelToggle: document.querySelector("#file-editor-panel-toggle"),
  fileEditorModeText: document.querySelector("#file-editor-mode-text"),
  fileEditorModeElement: document.querySelector("#file-editor-mode-element"),
  fileEditorUndo: document.querySelector("#file-editor-undo"),
  fileEditorRedo: document.querySelector("#file-editor-redo"),
  fileEditorReset: document.querySelector("#file-editor-reset"),
  fileEditorSave: document.querySelector("#file-editor-save"),
  fileEditorSaveClose: document.querySelector("#file-editor-save-close"),
  fileEditorClose: document.querySelector("#file-editor-close"),
  fileEditorPanel: document.querySelector("#file-editor-panel"),
  fileEditorSelectedName: document.querySelector("#file-editor-selected-name"),
  fileEditorText: document.querySelector("#file-editor-text"),
  fileEditorColor: document.querySelector("#file-editor-color"),
  fileEditorBackground: document.querySelector("#file-editor-background"),
  fileEditorBold: document.querySelector("#file-editor-bold"),
  fileEditorItalic: document.querySelector("#file-editor-italic"),
  fileEditorUnderline: document.querySelector("#file-editor-underline"),
  fileEditorStrike: document.querySelector("#file-editor-strike"),
  fileEditorFontSize: document.querySelector("#file-editor-font-size"),
  fileEditorLineHeight: document.querySelector("#file-editor-line-height"),
  fileEditorFontWeight: document.querySelector("#file-editor-font-weight"),
  fileEditorTextAlign: document.querySelector("#file-editor-text-align"),
  fileEditorFeedback: document.querySelector("#file-editor-feedback"),
};

function ensureHtmlImportInput() {
  const existing = document.querySelector("#html-import-file");
  if (existing) return existing;
  const input = document.createElement("input");
  input.id = "html-import-file";
  input.type = "file";
  input.accept = ".html,.htm,text/html";
  input.hidden = true;
  document.body.append(input);
  return input;
}

async function boot() {
  if (isStaticShareRoute()) {
    await renderStaticShareFallback();
    return;
  }
  applyTheme();
  applyTranslations();
  updateNewFileMode();
  try {
    await checkAuthStatus();
    if (state.authEnabled && !state.authenticated) {
      showLoginScreen();
      return;
    }
    hideLoginScreen();
    await loadRemoteNavConfig();
    await loadShares();
    state.manifest = await loadManifest();
    state.items = Array.isArray(state.manifest.items) ? state.manifest.items : [];
    renderApp();
    applyStaticDemoMode();
    refreshAiStatus();
    checkVersionStatus();
    openFromHash();
  } catch (error) {
    elements.contentGrid.innerHTML = `<div class="empty-state">${t("manifestMissing")}</div>`;
    console.error(error);
  }
}

function isStaticShareRoute() {
  return /^\/share\/[^/]+\/?$/.test(window.location.pathname);
}

async function renderStaticShareFallback() {
  const token = window.location.pathname.split("/").filter(Boolean)[1] || "";
  document.documentElement.lang = "en";
  elements.body.className = "share-fallback-body";
  elements.body.innerHTML = `
    <main class="share-fallback-shell">
      <section class="share-fallback-banner">
        <div class="share-fallback-brand">HTMlore shared note</div>
        <h1>Loading shared note...</h1>
        <p></p>
      </section>
      <iframe class="share-fallback-frame" title="HTMlore shared note" sandbox="allow-scripts"></iframe>
    </main>
  `;
  try {
    const response = await fetch(`/api/public/shares/${encodeURIComponent(token)}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`Share not found: ${response.status}`);
    const data = await response.json();
    const item = data.item || {};
    const title = item.title || "Shared note";
    const summary = item.summary || "";
    const frame = document.querySelector(".share-fallback-frame");
    document.title = `${title} - HTMlore Share`;
    document.querySelector(".share-fallback-banner h1").textContent = title;
    document.querySelector(".share-fallback-banner p").textContent = summary;
    frame.title = title;
    frame.srcdoc = renderShareSrcdoc(data);
    window.addEventListener("message", (event) => {
      if (!frame || event.source !== frame.contentWindow || !event.data) return;
      if (event.data.type === "html-lore-share-height") {
        const height = Number(event.data.height);
        if (Number.isFinite(height) && height > 0) {
          frame.style.height = `${Math.min(Math.max(height, 420), 16000)}px`;
        }
      }
      if (event.data.type === "html-lore-share-anchor") {
        const top = Number(event.data.top);
        if (Number.isFinite(top)) {
          const frameTop = frame.getBoundingClientRect().top + window.scrollY;
          window.scrollTo({ top: Math.max(frameTop + top - 12, 0), behavior: "smooth" });
        }
      }
    });
  } catch (error) {
    console.error(error);
    document.querySelector(".share-fallback-banner h1").textContent = "Share not found";
    document.querySelector(".share-fallback-banner p").textContent = "This shared note is unavailable, expired, or has been revoked.";
    document.querySelector(".share-fallback-frame").remove();
  }
}

function renderShareSrcdoc(data) {
  const body = data.html || "";
  const styles = data.styles || "";
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root { color-scheme: light dark; }
    html { min-height: 100%; }
    body { margin: 0; overflow-wrap: anywhere; }
    a:not([href]) { color: inherit; text-decoration: none; pointer-events: none; }
    a[href^="#"] { pointer-events: auto; }
    img, video, svg, canvas { max-width: 100%; height: auto; }
  </style>
  ${styles}
</head>
<body>
  ${body}
  <script>
    function reportHeight() {
      const doc = document.documentElement;
      const height = Math.max(doc.scrollHeight, document.body ? document.body.scrollHeight : 0);
      parent.postMessage({ type: "html-lore-share-height", height }, "*");
    }
    function scrollToFragment(hash) {
      if (!hash || hash === "#") return;
      const id = decodeURIComponent(hash.slice(1));
      const target = document.getElementById(id);
      if (!target) return;
      const top = target.getBoundingClientRect().top;
      parent.postMessage({ type: "html-lore-share-anchor", top }, "*");
      target.scrollIntoView({ block: "start", behavior: "smooth" });
      reportHeight();
    }
    document.addEventListener("click", (event) => {
      const anchor = event.target.closest('a[href^="#"]');
      if (anchor) {
        event.preventDefault();
        scrollToFragment(anchor.getAttribute("href"));
        return;
      }
      const trigger = event.target.closest("[data-share-toggle]");
      if (!trigger) return;
      const target = document.getElementById(trigger.getAttribute("data-share-toggle"));
      if (target) {
        target.classList.toggle("open");
        reportHeight();
      }
    });
    window.addEventListener("load", reportHeight);
    if ("ResizeObserver" in window) new ResizeObserver(reportHeight).observe(document.documentElement);
    reportHeight();
  <\/script>
</body>
</html>`;
}

async function checkAuthStatus() {
  if (!state.agentUrl) {
    state.authEnabled = false;
    state.authenticated = true;
    state.authChecked = true;
    return;
  }
  const response = await apiFetch("/api/auth/status", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Unable to check auth status: ${response.status}`);
  }
  const data = await response.json();
  state.authEnabled = Boolean(data.enabled);
  state.authenticated = Boolean(data.authenticated);
  state.currentUser = {
    username: data.user || "",
    dataId: data.data_id || "",
  };
  state.authChecked = true;
}

function showLoginScreen(messageKey = "") {
  elements.body.classList.add("auth-required");
  elements.body.classList.remove("auth-session-active");
  elements.loginScreen.hidden = false;
  elements.loginFeedback.textContent = messageKey ? t(messageKey) : "";
  elements.loginUsername.focus();
}

function hideLoginScreen() {
  elements.body.classList.remove("auth-required");
  elements.body.classList.toggle("auth-session-active", state.authEnabled && state.authenticated);
  elements.loginScreen.hidden = true;
  elements.loginFeedback.textContent = "";
  elements.loginPassword.value = "";
}

async function submitLogout() {
  if (!state.agentUrl || !state.authEnabled) return;
  try {
    await apiFetch("/api/auth/logout", { method: "POST" });
  } catch (error) {
    console.warn("Logout failed.", error);
  }
  state.authenticated = false;
  state.currentUser = { username: "", dataId: "" };
  state.manifest = null;
  state.items = [];
  closeSettings();
  closeAiPanel();
  closeReader();
  showLoginScreen();
}

async function submitLogin(event) {
  event.preventDefault();
  if (!state.agentUrl || state.loginSubmitting) return;
  state.loginSubmitting = true;
  elements.loginFeedback.textContent = "";
  elements.loginForm.querySelector("button[type='submit']").disabled = true;
  try {
    const response = await apiFetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: elements.loginUsername.value,
        password: elements.loginPassword.value,
      }),
    });
    if (!response.ok) {
      showLoginScreen(response.status === 401 ? "loginFailed" : "loginUnavailable");
      return;
    }
    const data = await response.json();
    state.authEnabled = Boolean(data.enabled);
    state.authenticated = Boolean(data.authenticated);
    state.currentUser = {
      username: data.user || elements.loginUsername.value,
      dataId: data.data_id || "",
    };
    if (!state.authenticated) {
      showLoginScreen("loginFailed");
      return;
    }
    hideLoginScreen();
    await boot();
  } catch (error) {
    console.error(error);
    showLoginScreen("loginUnavailable");
  } finally {
    state.loginSubmitting = false;
    elements.loginForm.querySelector("button[type='submit']").disabled = false;
  }
}

async function loadManifest() {
  if (state.agentUrl) {
    try {
      const response = await apiFetch("/api/manifest", { cache: "no-store" });
      if (response.ok) return response.json();
    } catch (error) {
      console.warn("Agent manifest unavailable, falling back to static manifest.", error);
    }
  }
  const response = await fetch("manifest.json", { cache: "no-store" });
  if (!response.ok) throw new Error(`Unable to load manifest: ${response.status}`);
  return response.json();
}

async function refreshManifestAndWorkspace() {
  state.manifest = await loadManifest();
  state.items = Array.isArray(state.manifest.items) ? state.manifest.items : [];
  normalizeVisibleTagFilters();
  renderLibraryNav();
  renderCollectionNav();
  renderTagNav();
  renderMultiFilterOptions();
  renderManagementLists();
  renderGrid();
  renderAiContext();
}

function buildApiUrl(path) {
  if (!state.agentUrl) return path;
  return `${state.agentUrl.replace(/\/$/, "")}${path}`;
}

function buildApiEventUrl(path) {
  return withApiAccessToken(buildApiUrl(path));
}

function getApiHeaders(headers = {}) {
  const result = { ...headers };
  if (state.agentToken) result.Authorization = `Bearer ${state.agentToken}`;
  return result;
}

function apiFetch(path, options = {}) {
  return fetch(buildApiUrl(path), {
    ...options,
    credentials: "same-origin",
    headers: getApiHeaders(options.headers || {}),
  });
}

function apiUpload(path, formData, { onProgress } = {}) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", buildApiUrl(path), true);
    xhr.withCredentials = true;
    if (state.agentToken) xhr.setRequestHeader("Authorization", `Bearer ${state.agentToken}`);
    xhr.upload.addEventListener("progress", (event) => {
      if (!event.lengthComputable || typeof onProgress !== "function") return;
      onProgress({
        loaded: event.loaded,
        total: event.total,
        percent: Math.max(0, Math.min(100, Math.round((event.loaded / event.total) * 100))),
      });
    });
    xhr.addEventListener("load", () => {
      resolve({
        ok: xhr.status >= 200 && xhr.status < 300,
        status: xhr.status,
        text: () => Promise.resolve(xhr.responseText || ""),
        json: () => Promise.resolve(parseJsonSafely(xhr.responseText)),
      });
    });
    xhr.addEventListener("error", () => reject(new Error("Network upload failed.")));
    xhr.addEventListener("abort", () => reject(new Error("Upload aborted.")));
    xhr.send(formData);
  });
}

function parseJsonSafely(value) {
  try {
    return JSON.parse(value || "{}");
  } catch {
    return {};
  }
}

function withApiAccessToken(url) {
  if (!state.agentToken) return url;
  const separator = url.includes("?") ? "&" : "?";
  return `${url}${separator}access_token=${encodeURIComponent(state.agentToken)}`;
}

function renderApp() {
  applySidebarState();
  applySidebarWidth();
  applyNavSectionState();
  applyAiPanelState();
  updateMobileReaderTop();
  applyTheme();
  renderProfile();
  applyViewMode();
  applyFavoriteFilter();
  applyTranslations();
  renderWorkspaceBrand();
  renderFeedback();
  renderLibraryNav();
  renderCollectionNav();
  renderTagNav();
  renderMultiFilterOptions();
  applySortState();
  updateNewFileMode();
  renderGrid();
  renderAiContext();
  updateAgentStatus();
  renderAiConfig();
  renderDataConfig();
  renderManagementLists();
  renderShareManagement();
  renderVersionStatus();
}

function updateMobileReaderTop() {
  const isMobile = window.matchMedia("(max-width: 900px)").matches;
  const rawHeight = isMobile && elements.sidebar ? Math.ceil(elements.sidebar.getBoundingClientRect().height) : 0;
  const height = isMobile ? Math.max(58, rawHeight) : 0;
  document.documentElement.style.setProperty("--mobile-reader-top", `${height}px`);
}

function renderWorkspaceBrand() {
  if (!elements.siteTitle) return;
  elements.siteTitle.replaceChildren("HTM");
  const accent = document.createElement("em");
  accent.textContent = "lore";
  elements.siteTitle.append(accent);
}

async function checkVersionStatus() {
  try {
    if (state.agentUrl) {
      const response = await apiFetch("/api/version", { cache: "no-store" });
      if (response.ok) {
        const data = await response.json();
        state.currentVersion = normalizeVersion(data.version) || state.currentVersion;
      }
    }
    const latest = await fetchLatestGithubVersion();
    state.latestVersion = latest;
    state.updateAvailable = isVersionNewer(latest, state.currentVersion);
    state.versionCheckComplete = true;
  } catch (error) {
    state.versionCheckComplete = true;
    console.warn("Version check unavailable.", error);
  }
  renderVersionStatus();
}

async function fetchLatestGithubVersion() {
  const signal = AbortSignal.timeout ? AbortSignal.timeout(4000) : undefined;
  const releaseResponse = await fetch("https://api.github.com/repos/JMoCoder/html_lore/releases/latest", {
    headers: { Accept: "application/vnd.github+json" },
    signal,
  });
  if (releaseResponse.ok) {
    const release = await releaseResponse.json();
    const version = normalizeVersion(release.tag_name || release.name || "");
    if (version) return version;
  }
  const tagsResponse = await fetch("https://api.github.com/repos/JMoCoder/html_lore/tags", {
    headers: { Accept: "application/vnd.github+json" },
    signal,
  });
  if (!tagsResponse.ok) throw new Error(`GitHub tags returned ${tagsResponse.status}`);
  const tags = await tagsResponse.json();
  const versions = Array.isArray(tags) ? tags.map((tag) => normalizeVersion(tag.name)).filter(Boolean) : [];
  versions.sort(compareVersions).reverse();
  return versions[0] || "";
}

function renderVersionStatus() {
  document.querySelectorAll("[data-i18n='aboutVersion']").forEach((node) => {
    node.textContent = t("aboutVersion", { version: state.currentVersion });
  });
  if (!elements.versionStatus) return;
  if (!state.versionCheckComplete) {
    elements.versionStatus.textContent = "";
  } else if (state.updateAvailable) {
    elements.versionStatus.textContent = t("updateAvailable", { version: state.latestVersion });
  } else if (state.latestVersion) {
    elements.versionStatus.textContent = t("versionCurrent");
  } else {
    elements.versionStatus.textContent = t("versionCheckUnavailable");
  }
}

function renderLibraryNav() {
  elements.libraryNav.replaceChildren(...libraryFilterDefinitions.filter((filter) => {
    return isManagedItemVisible("library", filter.value);
  }).map((filter) => {
    const count = countLibraryFilter(filter.value);
    const active = state.filter.type === "library" && state.filter.value === filter.value;
    return navButton(t(filter.labelKey), count, active, () => {
      selectLibraryFilter(filter.value);
    });
  }));
}

function renderCollectionNav() {
  const buttons = getCollectionOptions()
    .filter((collection) => isManagedItemVisible("collections", collection.name))
    .map((collection) => {
    const active = state.filter.type === "collection" && state.filter.value === collection.name;
    return navButton(collection.name, countCollectionItems(collection.name), active, () => {
      selectCollection(collection.name);
    });
  });
  elements.collectionNav.replaceChildren(...buttons);
}

function renderTagNav() {
  const tags = getTagOptions()
    .filter((tag) => isManagedItemVisible("tags", tag.name))
    .map((tag) => ({ ...tag, count: countTagItems(tag.name) }))
    .filter((tag) => tag.count > 0)
    .map((tag) => {
    const active = state.filter.type === "tag" && state.filter.value === tag.name;
    const multiActive = state.selectedTags.has(tag.name);
    return navButton(`#${tag.name}`, tag.count, active || multiActive, () => {
      selectTag(tag.name);
    }, "tag-filter");
  });
  elements.tagNav.replaceChildren(...tags);
}

function navButton(label, count, active, onClick, extraClass = "") {
  const button = document.createElement("button");
  button.className = `nav-item${extraClass ? ` ${extraClass}` : ""}${active ? " active" : ""}`;
  button.type = "button";
  button.innerHTML = `<span>${escapeHtml(label)}</span><span>${count}</span>`;
  button.addEventListener("click", onClick);
  return button;
}

function countLibraryFilter(value) {
  const filter = libraryFilterDefinitions.find((item) => item.value === value);
  if (!filter) return 0;
  return state.items.filter((item) => filter.test(item) && isVisibleInArchiveScope(item, value)).length;
}

function countCollectionItems(name) {
  return state.items.filter((item) => !isArchived(item) && getItemCollection(item) === name).length;
}

function countTagItems(name) {
  return state.items.filter((item) => !isArchived(item) && getItemTags(item).includes(name)).length;
}

function normalizeVisibleTagFilters() {
  if (state.filter.type === "tag" && countTagItems(state.filter.value) === 0) {
    state.filter = { type: "library", value: "all" };
  }
  state.selectedTags.forEach((tag) => {
    if (countTagItems(tag) === 0) state.selectedTags.delete(tag);
  });
}

function filteredItems() {
  return sortItems(applySelectedTagFilters(baseItemsForTagFilters()));
}

function baseItemsForTagFilters() {
  const query = state.query.trim().toLowerCase();
  let items = [...state.items];

  if (state.filter.type === "library") {
    const filter = libraryFilterDefinitions.find((item) => item.value === state.filter.value);
    items = filter ? items.filter(filter.test) : items;
  } else if (state.filter.type === "collection") {
    items = items.filter((item) => getItemCollection(item) === state.filter.value);
  } else if (state.filter.type === "tag") {
    items = items.filter((item) => getItemTags(item).includes(state.filter.value));
  }

  const filterValue = state.filter.type === "library" ? state.filter.value : "";
  items = items.filter((item) => isVisibleInArchiveScope(item, filterValue));

  if (state.onlyFavorites) {
    items = items.filter((item) => isFavorite(item));
  }

  if (query) {
    items = items.filter((item) => searchableText(item).includes(query));
  }

  return items;
}

function applySelectedTagFilters(items, selectedTags = state.selectedTags, mode = state.tagMatchMode) {
  if (selectedTags.size === 0) return [...items];
  return items.filter((item) => {
    const tags = getItemTags(item);
    if (mode === "all") {
      return [...selectedTags].every((tag) => tags.includes(tag));
    }
    return tags.some((tag) => selectedTags.has(tag));
  });
}

function isVisibleInArchiveScope(item, value) {
  if (value === "archived") return isArchived(item);
  return !isArchived(item);
}

function searchableText(item) {
  return [
    getItemTitle(item),
    getItemSummary(item),
    item.path,
    getItemCollection(item),
    item.source_type,
    ...getItemTags(item),
  ].filter(Boolean).join(" ").toLowerCase();
}

function sortItems(items) {
  const sorted = [...items];
  const byNewest = (a, b) => String(b.updated).localeCompare(String(a.updated));
  const byOldest = (a, b) => String(a.updated).localeCompare(String(b.updated));
  const byTitleAz = (a, b) => String(getItemTitle(a) || "").localeCompare(String(getItemTitle(b) || ""), undefined, { sensitivity: "base" });
  const byTitleZa = (a, b) => byTitleAz(b, a);

  const comparator = {
    newest: (a, b) => byNewest(a, b) || byTitleAz(a, b),
    oldest: (a, b) => byOldest(a, b) || byTitleAz(a, b),
    "title-az": (a, b) => byTitleAz(a, b) || byNewest(a, b),
    "title-za": (a, b) => byTitleZa(a, b) || byNewest(a, b),
  }[state.sortMode] || ((a, b) => byNewest(a, b) || byTitleAz(a, b));

  return sorted.sort(comparator);
}

function renderGrid() {
  renderMultiFilterOptions();
  const items = filteredItems();
  elements.contentGrid.classList.remove("list-view");

  if (items.length === 0) {
    elements.contentGrid.innerHTML = `<div class="empty-state">${t("noMatches")}</div>`;
    return;
  }

  elements.contentGrid.replaceChildren(...items.map(renderCard));
}

function getWorkspaceTitle() {
  if (state.query) return t("searchTitle", { query: state.query });
  if (state.filter.type === "library") {
    const filter = libraryFilterDefinitions.find((item) => item.value === state.filter.value);
    return filter ? t(filter.labelKey) : t("knowledgeWorkspace");
  }
  if (state.filter.type === "collection") return state.filter.value;
  if (state.filter.type === "tag") return `#${state.filter.value}`;
  return t("knowledgeWorkspace");
}

function renderCard(item) {
  const card = document.createElement("article");
  card.className = "item-card";
  const sourceLabel = getSourceLabel(item);
  const collectionLabel = getItemCollection(item);
  const title = getItemTitle(item);
  const summary = getItemSummary(item);
  const tags = getItemTags(item);
  card.innerHTML = `
    <div class="card-topline">
      <span class="source-type">${escapeHtml(collectionLabel)} / ${escapeHtml(sourceLabel)}</span>
      <div class="item-actions">
        ${isArchived(item) ? "" : itemActionButton("edit", item)}
        ${itemActionButton("favorite", item)}
        ${itemActionButton("archive", item)}
        ${isArchived(item) ? "" : itemActionButton("share", item)}
        ${itemActionButton(isArchived(item) ? "delete" : "ai-context", item)}
      </div>
    </div>
    <h3>${escapeHtml(title)}</h3>
    <p>${escapeHtml(summary || t("noSummary"))}</p>
    <div class="card-tags">${tags.slice(0, 4).map((tag) => `<span>#${escapeHtml(tag)}</span>`).join("")}</div>
    <div class="card-footer">
      <span class="card-date">${escapeHtml(formatDate(getItemDisplayDate(item)))}</span>
      <div class="card-links">
        <button type="button" data-read>${escapeHtml(t("read"))}</button>
        <a href="${escapeHtml(getReaderRawUrl(item))}" target="_blank" rel="noreferrer">${escapeHtml(t("original"))}</a>
      </div>
    </div>
  `;
  card.querySelector("[data-read]").addEventListener("click", () => openReader(item));
  card.querySelector("[data-item-action='edit']")?.addEventListener("click", (event) => {
    event.stopPropagation();
    openMetadataEditor(item.id);
  });
  card.querySelector("[data-item-action='favorite']").addEventListener("click", (event) => {
    event.stopPropagation();
    toggleFavorite(item.id);
  });
  card.querySelector("[data-item-action='archive']").addEventListener("click", (event) => {
    event.stopPropagation();
    toggleArchive(item.id);
  });
  card.querySelector("[data-item-action='share']")?.addEventListener("click", (event) => {
    event.stopPropagation();
    openShareDialog(item.id);
  });
  card.querySelector("[data-item-action='ai-context']")?.addEventListener("click", (event) => {
    event.stopPropagation();
    toggleManualAiContext(item.id);
  });
  card.querySelector("[data-item-action='delete']")?.addEventListener("click", (event) => {
    event.stopPropagation();
    permanentlyDeleteItem(item.id);
  });
  card.addEventListener("dblclick", () => openReader(item));
  return card;
}

function getSourceLabel(item) {
  if (item.agent?.generated || item.source_type === "topic") return t("generatedSource");
  return t("importedSource");
}

function itemActionButton(action, item) {
  const active = action === "favorite" ? isFavorite(item)
    : action === "archive" ? isArchived(item)
      : action === "share" ? Boolean(getActiveShareForItem(item.id))
        : action === "ai-context" ? state.manualAiContextIds.has(item.id)
          : false;
  const label = {
    edit: t("editMetadata"),
    favorite: t(active ? "unfavoriteAction" : "favoriteAction"),
    archive: t(active ? "unarchiveAction" : "archiveAction"),
    share: t("shareAction"),
    "ai-context": t(active ? "removeFromAiContext" : "addToAiContext"),
    delete: t("permanentDeleteAction"),
  }[action];
  return `
    <button class="item-icon-button${active ? " active" : ""}" type="button" data-item-action="${action}" aria-label="${escapeHtml(label)}" title="${escapeHtml(label)}">
      ${action === "edit" ? editIcon() : action === "favorite" ? starIcon(active) : action === "archive" ? archiveIcon() : action === "share" ? shareIcon() : action === "delete" ? trashIcon() : contextToggleIcon(active)}
    </button>
  `;
}

function openReader(item) {
  state.currentReaderItemId = item.id;
  elements.reader.hidden = false;
  elements.reader.classList.remove("compact-reader-header");
  elements.body.classList.add("reader-open");
  requestAnimationFrame(updateMobileReaderTop);
  setTimeout(updateMobileReaderTop, 80);
  renderReaderMetadata(item);
  elements.readerFrame.src = getReaderContentUrl(item);
  renderReaderActions(item);
  renderAiContext();
  invalidateAiHistoryIfContextChanged();
  window.location.hash = `/${item.id}`;
}

function renderReaderMetadata(item) {
  elements.readerTitle.textContent = getItemTitle(item);
  if (elements.readerSummary) elements.readerSummary.textContent = getItemSummary(item) || "";
  elements.readerSource.textContent = `${getItemCollection(item)} / ${getSourceLabel(item)}`;
  elements.readerOriginal.href = getReaderRawUrl(item);
  elements.readerTags.replaceChildren(...getItemTags(item).map((tag) => {
    const span = document.createElement("span");
    span.textContent = `#${tag}`;
    return span;
  }));
}

function getReaderContentUrl(item) {
  if (!state.agentUrl) return item.path;
  return withApiAccessToken(buildApiUrl(`/api/items/${encodeURIComponent(item.id)}/content`));
}

function getReaderRawUrl(item) {
  if (!state.agentUrl) return item.path;
  return withApiAccessToken(buildApiUrl(`/api/items/${encodeURIComponent(item.id)}/raw`));
}

function bindReaderFrameScroll() {
  elements.reader.classList.remove("compact-reader-header");
  try {
    const readerWindow = elements.readerFrame.contentWindow;
    const readerDocument = elements.readerFrame.contentDocument;
    if (!readerWindow || !readerDocument) return;
    const updateMobileFrameHeight = () => {
      if (!window.matchMedia("(max-width: 900px)").matches) {
        elements.readerFrame.style.height = "";
        return;
      }
      const doc = readerDocument.documentElement;
      const body = readerDocument.body;
      const height = Math.max(doc?.scrollHeight || 0, body?.scrollHeight || 0, window.innerHeight);
      elements.readerFrame.style.height = `${Math.ceil(height)}px`;
    };
    const update = () => {
      updateMobileFrameHeight();
      if (window.matchMedia("(max-width: 900px)").matches) {
        elements.reader.classList.remove("compact-reader-header");
        return;
      }
      const scrollTop = readerWindow.scrollY || readerDocument.documentElement.scrollTop || readerDocument.body.scrollTop || 0;
      const compact = elements.reader.classList.contains("compact-reader-header");
      if (!compact && scrollTop > 36) {
        elements.reader.classList.add("compact-reader-header");
      } else if (compact && scrollTop < 10) {
        elements.reader.classList.remove("compact-reader-header");
      }
    };
    readerWindow.addEventListener("scroll", update, { passive: true });
    readerWindow.addEventListener("resize", update);
    setTimeout(update, 250);
    setTimeout(update, 900);
    update();
  } catch {
    elements.reader.classList.remove("compact-reader-header");
  }
}

function closeReader() {
  state.currentReaderItemId = "";
  elements.reader.hidden = true;
  elements.reader.classList.remove("compact-reader-header");
  elements.body.classList.remove("reader-open");
  elements.readerFrame.style.height = "";
  elements.readerFrame.removeAttribute("src");
  if (window.location.hash) {
    history.pushState("", document.title, window.location.pathname + window.location.search);
  }
  renderAiContext();
  invalidateAiHistoryIfContextChanged();
}

function returnToWorkspace() {
  clearFeedback();
  state.currentReaderItemId = "";
  elements.reader.hidden = true;
  elements.reader.classList.remove("compact-reader-header");
  elements.body.classList.remove("reader-open");
  elements.readerFrame.style.height = "";
  elements.readerFrame.removeAttribute("src");
  elements.settingsPage.hidden = true;
  if (window.location.hash) {
    history.pushState("", document.title, window.location.pathname + window.location.search);
  }
  renderAiContext();
  invalidateAiHistoryIfContextChanged();
}

function goHome() {
  state.filter = { type: "library", value: "all" };
  state.query = "";
  elements.searchInput.value = "";
  clearMultiFilters(false);
  returnToWorkspace();
  renderApp();
}

function openPagesHome() {
  window.location.href = getPagesHomeUrl();
}

function openWorkspaceHome() {
  selectLibraryFilter("all");
}

function selectLibraryFilter(value) {
  state.filter = { type: "library", value };
  clearMultiFilters(false);
  returnToWorkspace();
  renderApp();
}

function selectCollection(name) {
  state.filter = { type: "collection", value: name };
  syncSingleSelectionToMultiFilter("collection", name);
  returnToWorkspace();
  renderApp();
}

function selectTag(name) {
  state.filter = { type: "tag", value: name };
  syncSingleSelectionToMultiFilter("tag", name);
  returnToWorkspace();
  renderApp();
}

function syncSingleSelectionToMultiFilter(type, value) {
  if (state.selectedTags.size === 0) return;
  if (type === "tag") {
    state.selectedTags.clear();
    state.selectedTags.add(value);
  }
}

function openSettings(tab = "basic", updateHash = true) {
  clearFeedback();
  if (state.aiPanelOpen) closeAiPanel();
  setSettingsTab(tab, false);
  elements.settingsPage.hidden = false;
  maybeRefreshAiRuns();
  maybeRefreshAiGenerationHistory();
  maybeRefreshAiConversations();
  if (updateHash) {
    updateSettingsHash(state.activeSettingsTab);
  }
}

function toggleSettings() {
  if (elements.settingsPage.hidden) {
    openSettings();
  } else {
    closeSettings();
  }
}

function closeSettings() {
  elements.settingsPage.hidden = true;
  if (window.location.hash.startsWith("#/settings")) {
    history.pushState("", document.title, window.location.pathname + window.location.search);
  }
}

function renderSettingsTabs() {
  elements.settingsTabs.forEach((tab) => {
    const active = tab.dataset.settingsTab === state.activeSettingsTab;
    tab.classList.toggle("active", active);
  });
  elements.settingsSections.forEach((section) => {
    const active = section.dataset.settingsSection === state.activeSettingsTab;
    section.classList.toggle("active", active);
  });
  elements.settingsContent.scrollTop = 0;
}

function setSettingsTab(tab, updateHash = true) {
  const validTabs = new Set([...elements.settingsTabs].map((item) => item.dataset.settingsTab));
  state.activeSettingsTab = validTabs.has(tab) ? tab : "basic";
  renderSettingsTabs();
  if (!elements.settingsPage.hidden) {
    maybeRefreshAiRuns();
    maybeRefreshAiGenerationHistory();
    maybeRefreshAiConversations();
  }
  if (updateHash) {
    updateSettingsHash(state.activeSettingsTab);
  }
}

function updateSettingsHash(tab) {
  const nextHash = `#/settings/${tab}`;
  if (window.location.hash !== nextHash) {
    window.location.hash = `/settings/${tab}`;
  }
}

function openFromHash() {
  const id = decodeURIComponent(window.location.hash.replace(/^#\/?/, ""));
  if (id.startsWith("settings")) {
    const tab = id.split("/")[1] || "library";
    openSettings(tab, false);
    return;
  }
  if (!id) return;
  const item = state.items.find((candidate) => candidate.id === id);
  if (item) openReader(item);
}

async function submitNewItem(event) {
  event.preventDefault();
  const input = elements.newItemInput.value.trim();
  if (!state.pendingMaterialFiles.length && !input) {
    setFeedback("emptyInput");
    return;
  }

  await generateNoteFromMaterialFiles(state.pendingMaterialFiles);
}

function openHtmlImportPicker() {
  elements.htmlImportFile.value = "";
  elements.htmlImportFile.click();
}

function openMaterialGeneratePicker() {
  if (!state.agentUrl) {
    setFeedback("agentNotConfigured");
    return;
  }
  elements.materialGenerateFile.value = "";
  elements.materialGenerateFile.click();
}

function openMaterialReferencePicker() {
  elements.materialReferenceFile.value = "";
  elements.materialReferenceFile.click();
}

function setPendingMaterialFiles(files, options = {}) {
  const incomingFiles = Array.from(files || []).filter(Boolean);
  const currentFiles = options.append === false ? [] : Array.from(state.pendingMaterialFiles || []).filter(Boolean);
  if (options.append === false && options.cleanup !== false) {
    Array.from(state.pendingMaterialFiles || []).forEach((entry) => {
      if (entry.uploadId) apiFetch(`/api/ai/material-uploads/${encodeURIComponent(entry.uploadId)}`, { method: "DELETE" }).catch(() => {});
    });
  }
  const seen = new Set(currentFiles.map((entry) => entry.key || materialFileKey(entry.file || entry)));
  const nextFiles = [...currentFiles];
  const newEntries = [];
  incomingFiles.forEach((file) => {
    const key = materialFileKey(file);
    if (seen.has(key)) return;
    seen.add(key);
    const entry = {
      key,
      file,
      uploadId: "",
      status: "pending",
      progress: 0,
      message: "",
      error: "",
    };
    nextFiles.push(entry);
    newEntries.push(entry);
  });
  state.pendingMaterialFiles = nextFiles;
  state.materialUpload = materialUploadStateForEntries(state.pendingMaterialFiles);
  updateNewFileMode();
  if (state.materialUpload.status !== "too-large") {
    newEntries.forEach((entry) => uploadMaterialFileEntry(entry));
  } else {
    newEntries.forEach((entry) => {
      entry.status = "failed";
      entry.message = state.materialUpload.message;
    });
    state.materialUpload = materialUploadStateForFiles(state.pendingMaterialFiles.map((entry) => entry.file || entry));
    updateNewFileMode();
  }
}

function removePendingMaterialFile(fileKey) {
  const entries = Array.from(state.pendingMaterialFiles || []).filter(Boolean);
  const removed = entries.find((entry) => (entry.key || materialFileKey(entry.file || entry)) === fileKey);
  if (removed?.uploadId) {
    apiFetch(`/api/ai/material-uploads/${encodeURIComponent(removed.uploadId)}`, { method: "DELETE" }).catch(() => {});
  }
  state.pendingMaterialFiles = entries.filter((entry) => (entry.key || materialFileKey(entry.file || entry)) !== fileKey);
  state.materialUpload = materialUploadStateForEntries(state.pendingMaterialFiles);
  updateNewFileMode();
}

function materialFileKey(file) {
  return [file?.name || "", file?.size || 0, file?.lastModified || 0].join("::");
}

function setPendingReferenceFile(file) {
  state.pendingReferenceFile = file || null;
  state.referenceUpload = materialUploadStateForFiles(state.pendingReferenceFile ? [state.pendingReferenceFile] : []);
  updateNewReferenceFile();
}

function materialUploadStateForFiles(files) {
  const selectedFiles = Array.from(files || []).filter(Boolean);
  if (!selectedFiles.length) return { status: "idle", progress: 0, message: "" };
  const limit = getAiMaxUploadBytes();
  const totalLimit = getAiMaxUploadTotalBytes();
  const oversizedFile = selectedFiles.find((file) => limit && file.size > limit);
  if (oversizedFile) {
    return {
      status: "too-large",
      progress: 0,
      message: t("fileTooLargeStatus", { size: formatBytes(oversizedFile.size), limit: formatBytes(limit) || t("uploadLimitUnknown") }),
    };
  }
  const totalSize = selectedFiles.reduce((sum, file) => sum + Number(file.size || 0), 0);
  if (totalLimit && totalSize > totalLimit) {
    return {
      status: "too-large",
      progress: 0,
      message: t("filesTooLargeStatus", { size: formatBytes(totalSize), limit: formatBytes(totalLimit) || t("uploadLimitUnknown") }),
    };
  }
  return {
    status: "ready",
    progress: 0,
    message:
      selectedFiles.length === 1
        ? t("fileReadyStatus", { size: formatBytes(totalSize) })
        : t("filesReadyStatus", { count: selectedFiles.length, size: formatBytes(totalSize) }),
  };
}

function materialUploadStateForEntries(entries) {
  const selectedEntries = Array.from(entries || []).filter(Boolean);
  if (!selectedEntries.length) return { status: "idle", progress: 0, message: "" };
  const files = selectedEntries.map((entry) => entry.file || entry).filter(Boolean);
  const sizeState = materialUploadStateForFiles(files);
  if (sizeState.status === "too-large") return sizeState;
  if (selectedEntries.some((entry) => entry.status === "failed")) {
    return { status: "failed", progress: 0, message: selectedEntries.find((entry) => entry.status === "failed")?.message || t("materialNoteFailed") };
  }
  if (selectedEntries.some((entry) => ["pending", "starting", "uploading"].includes(entry.status))) {
    const progress = Math.round(selectedEntries.reduce((sum, entry) => sum + Number(entry.progress || 0), 0) / selectedEntries.length);
    return { status: "uploading", progress, message: t("fileUploadingStatus", { percent: progress }) };
  }
  return {
    status: "uploaded",
    progress: 100,
    message:
      selectedEntries.length === 1
        ? t("fileUploadQueued")
        : t("filesReadyStatus", { count: selectedEntries.length, size: formatBytes(files.reduce((sum, file) => sum + Number(file.size || 0), 0)) }),
  };
}

function setMaterialUploadState(status, progress, message = "") {
  state.materialUpload = { status, progress: Math.max(0, Math.min(100, Number(progress || 0))), message };
  updateNewFileMode();
}

function markUploadFailed(files, message) {
  const selectedFiles = Array.from(files || []).filter(Boolean);
  if (!selectedFiles.length) {
    state.materialUpload = { status: "failed", progress: 0, message: String(message || t("materialNoteFailed")) };
  } else {
    state.materialUpload = { status: "failed", progress: 0, message: t("fileUploadFailedStatus", { message: String(message || t("materialNoteFailed")) }) };
  }
  updateNewFileMode();
}

function firstOversizedGenerationFile(materialFiles, referenceFile) {
  const limit = getAiMaxUploadBytes();
  const files = Array.from(materialFiles || []).filter(Boolean).map((entry) => entry.file || entry);
  if (limit) {
    const oversizedFile = files.find((file) => file.size > limit);
    if (oversizedFile) return oversizedFile;
  }
  if (referenceFile && limit && referenceFile.size > limit) return referenceFile;
  const totalLimit = getAiMaxUploadTotalBytes();
  const totalSize = files.reduce((sum, file) => sum + Number(file.size || 0), 0) + Number(referenceFile?.size || 0);
  if (totalLimit && totalSize > totalLimit) return { name: "materials", size: totalSize, totalLimitExceeded: true };
  return null;
}

function getAiMaxUploadBytes() {
  const value = Number(state.aiStatus?.limits?.max_upload_bytes || 0);
  return Number.isFinite(value) && value > 0 ? value : 100 * 1024 * 1024;
}

function getAiMaxUploadTotalBytes() {
  const value = Number(state.aiStatus?.limits?.max_upload_total_bytes || 0);
  return Number.isFinite(value) && value > 0 ? value : 500 * 1024 * 1024;
}

function materialFilesLabel(files) {
  const selectedFiles = Array.from(files || []).filter(Boolean).map((entry) => entry.file || entry);
  if (!selectedFiles.length) return "";
  if (selectedFiles.length === 1) return t("fileSelected", { name: selectedFiles[0].name });
  return t("filesSelected", { name: selectedFiles[0].name, count: selectedFiles.length });
}

function materialFilesTitle(files) {
  return Array.from(files || [])
    .filter(Boolean)
    .map((entry) => entry.file || entry)
    .map((file) => file.name)
    .join("\n");
}

function materialFileStatus(entry, files) {
  const file = entry.file || entry;
  const limit = getAiMaxUploadBytes();
  if (limit && file.size > limit) {
    return {
      className: "has-error",
      text: t("fileTooLargeStatus", { size: formatBytes(file.size), limit: formatBytes(limit) || t("uploadLimitUnknown") }),
    };
  }
  const status = entry.status || state.materialUpload.status;
  if (["pending", "starting"].includes(status)) return { className: "is-uploading", text: t("fileUploadStarting") };
  if (status === "uploading") return { className: "is-uploading", text: t("fileUploadingStatus", { percent: entry.progress || 0 }) };
  if (status === "uploaded") return { className: "is-ready", text: t("fileUploadQueued") };
  if (status === "failed") return { className: "has-error", text: entry.message || state.materialUpload.message || t("materialNoteFailed") };
  if (status === "too-large") return { className: "has-error", text: state.materialUpload.message || t("materialNoteFailed") };
  const totalLimit = getAiMaxUploadTotalBytes();
  const totalSize = Array.from(files || []).reduce((sum, item) => sum + Number((item.file || item).size || 0), 0);
  if (totalLimit && totalSize > totalLimit) {
    return {
      className: "has-error",
      text: t("filesTooLargeStatus", { size: formatBytes(totalSize), limit: formatBytes(totalLimit) || t("uploadLimitUnknown") }),
    };
  }
  return { className: "is-ready", text: t("fileReadyStatus", { size: formatBytes(file.size) }) };
}

function canSubmitMaterialGeneration() {
  const entries = Array.from(state.pendingMaterialFiles || []).filter(Boolean);
  if (!entries.length) return !["starting", "uploading"].includes(state.materialUpload.status);
  return entries.every((entry) => entry.status === "uploaded" && entry.uploadId) && !["failed", "too-large", "uploading", "starting"].includes(state.materialUpload.status);
}

function updateMaterialEntry(key, values) {
  state.pendingMaterialFiles = Array.from(state.pendingMaterialFiles || []).map((entry) => {
    if ((entry.key || materialFileKey(entry.file || entry)) !== key) return entry;
    return { ...entry, ...values };
  });
  state.materialUpload = materialUploadStateForEntries(state.pendingMaterialFiles);
  updateNewFileMode();
}

async function uploadMaterialFileEntry(entry) {
  if (!state.agentUrl || !entry?.file) return;
  const file = entry.file;
  const tooLargeFile = firstOversizedGenerationFile([entry], null);
  if (tooLargeFile) {
    const limit = tooLargeFile.totalLimitExceeded ? getAiMaxUploadTotalBytes() : getAiMaxUploadBytes();
    const messageKey = tooLargeFile.totalLimitExceeded ? "filesTooLargeStatus" : "fileTooLargeStatus";
    updateMaterialEntry(entry.key, {
      status: "failed",
      progress: 0,
      message: t(messageKey, { size: formatBytes(tooLargeFile.size), limit: formatBytes(limit) || t("uploadLimitUnknown") }),
    });
    return;
  }
  updateMaterialEntry(entry.key, { status: "starting", progress: 0, message: t("fileUploadStarting"), error: "" });
  const formData = new FormData();
  formData.append("file", file);
  try {
    const response = await apiUpload("/api/ai/material-uploads", formData, {
      onProgress: (progress) => updateMaterialEntry(entry.key, {
        status: "uploading",
        progress: progress.percent,
        message: t("fileUploadingStatus", { percent: progress.percent }),
      }),
    });
    if (!response.ok) {
      const errorPayload = await response.json();
      throw new Error(errorMessageFromPayload(errorPayload, response.status));
    }
    const result = await response.json();
    const upload = Array.isArray(result.uploads) ? result.uploads[0] : null;
    if (!upload?.upload_id) throw new Error(t("materialNoteFailed"));
    updateMaterialEntry(entry.key, {
      status: "uploaded",
      progress: 100,
      uploadId: upload.upload_id,
      message: t("fileUploadQueued"),
      error: "",
    });
  } catch (error) {
    updateMaterialEntry(entry.key, {
      status: "failed",
      progress: 0,
      message: t("fileUploadFailedStatus", { message: error?.message || t("materialNoteFailed") }),
      error: error?.message || "",
    });
    console.error(error);
  }
}

function formatBytes(value) {
  const bytes = Number(value || 0);
  if (!Number.isFinite(bytes) || bytes <= 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let current = bytes;
  let index = 0;
  while (current >= 1024 && index < units.length - 1) {
    current /= 1024;
    index += 1;
  }
  const digits = current >= 10 || index === 0 ? 0 : 1;
  return `${current.toFixed(digits)} ${units[index]}`;
}

function errorMessageFromPayload(payload, status) {
  const detail = payload && typeof payload === "object" ? payload.detail || payload.message || payload.error : "";
  if (typeof detail === "string" && detail.trim()) return detail.trim();
  if (Array.isArray(detail) && detail.length) return detail.map((item) => item?.msg || item?.message || "").filter(Boolean).join("; ");
  return `Agent returned ${status}`;
}

async function generateNoteFromMaterialFiles(files) {
  if (!state.agentUrl) {
    setFeedback("agentNotConfigured");
    return;
  }
  const selectedEntries = Array.from(files || []).filter(Boolean);
  const selectedFiles = selectedEntries.map((entry) => entry.file || entry).filter(Boolean);
  const tooLargeFile = firstOversizedGenerationFile(selectedFiles, state.pendingReferenceFile);
  if (tooLargeFile) {
    if (tooLargeFile === state.pendingReferenceFile) {
      state.referenceUpload = materialUploadStateForFiles([state.pendingReferenceFile]);
      updateNewReferenceFile();
    } else {
      const limit = tooLargeFile.totalLimitExceeded ? getAiMaxUploadTotalBytes() : getAiMaxUploadBytes();
      const messageKey = tooLargeFile.totalLimitExceeded ? "filesTooLargeStatus" : "fileTooLargeStatus";
      markUploadFailed(selectedFiles, t(messageKey, { size: formatBytes(tooLargeFile.size), limit: formatBytes(limit) || t("uploadLimitUnknown") }));
    }
    setFeedback("materialNoteFailed");
    return;
  }
  if (!canSubmitMaterialGeneration()) {
    setFeedback("chooseFileFirst");
    return;
  }
  setMaterialUploadState("starting", 0, t("fileUploadStarting"));
  setFeedback("submittingJob");
  const formData = new FormData();
  selectedEntries.forEach((entry) => {
    if (entry.uploadId) formData.append("upload_id", entry.uploadId);
  });
  formData.append("instruction", elements.newItemInput.value.trim());
  formData.append("theme", elements.newGenerateTheme?.value || "default");
  formData.append("target_use", elements.newGenerateTargetUse?.value || "default");
  formData.append("style_preference", elements.newGenerateStylePreference?.value || "default");
  formData.append("audience", elements.newGenerateAudience?.value || "default");
  if (state.pendingReferenceFile) {
    formData.append("reference_style", "file");
    formData.append("reference_file", state.pendingReferenceFile);
    formData.append("reference_file_name", state.pendingReferenceFile.name || "");
    formData.append("reference_file_type", state.pendingReferenceFile.type || "");
    formData.append("reference_file_size", String(state.pendingReferenceFile.size || 0));
  }

  try {
    const response = await apiUpload("/api/ai/material-jobs", formData, {
      onProgress: (progress) => setMaterialUploadState("uploading", progress.percent, t("submittingJob")),
    });
    if (!response.ok) {
      const errorPayload = await response.json();
      throw new Error(errorMessageFromPayload(errorPayload, response.status));
    }
    const result = await response.json();
    setMaterialUploadState("queued", 100, t("fileUploadQueued"));
    trackSubmittedAiJob(result.job_id || "");
    await loadAiJobs();
    startAiJobPolling();
    elements.newItemInput.value = "";
    resetNewItemInputHeight();
    setPendingMaterialFiles([], { append: false, cleanup: false });
    setPendingReferenceFile(null);
    setFeedback("queuedJob", { jobId: result.job_id || "" });
  } catch (error) {
    await loadAiRuns();
    markUploadFailed(selectedFiles, error?.message || t("materialNoteFailed"));
    setFeedback("materialNoteFailed");
    console.error(error);
  }
}

function updateNewFileMode() {
  const entries = Array.from(state.pendingMaterialFiles || []).filter(Boolean);
  const files = entries.map((entry) => entry.file || entry).filter(Boolean);
  const hasFile = files.length > 0;
  elements.newFileTrigger?.classList.toggle("has-file", hasFile);
  if (elements.newFileRow) elements.newFileRow.hidden = !hasFile;
  elements.newFileRow?.classList.toggle("is-uploading", ["starting", "uploading", "pending"].includes(state.materialUpload.status));
  elements.newFileRow?.classList.toggle("has-error", ["failed", "too-large"].includes(state.materialUpload.status));
  if (elements.newFileName) {
    elements.newFileName.replaceChildren();
    if (hasFile) {
      const list = document.createElement("span");
      list.className = "new-file-list";
      entries.forEach((entry) => {
        const file = entry.file || entry;
        const item = document.createElement("span");
        const status = materialFileStatus(entry, entries);
        const progress = Math.max(0, Math.min(100, Number(entry.progress || 0)));
        const showItemProgress = ["pending", "starting", "uploading"].includes(entry.status);
        item.className = `new-file-item ${status.className}`;
        item.dataset.fileKey = entry.key || materialFileKey(file);
        item.innerHTML = `
          <span class="new-file-item-name">${escapeHtml(file.name || t("item"))}</span>
          <span class="new-file-item-status">${escapeHtml(status.text)}</span>
          <span class="new-file-item-progress"${showItemProgress ? "" : " hidden"}><span style="width: ${progress}%"></span></span>
          <button type="button" class="new-file-item-remove" aria-label="${escapeHtml(t("removeFile"))}" title="${escapeHtml(t("removeFile"))}">×</button>
        `;
        item.querySelector(".new-file-item-remove")?.addEventListener("click", () => removePendingMaterialFile(item.dataset.fileKey || ""));
        list.append(item);
      });
      elements.newFileName.append(list);
    }
    elements.newFileName.title = materialFilesTitle(files);
  }
  if (elements.newFileStatus) {
    elements.newFileStatus.textContent = hasFile && files.length > 1 ? state.materialUpload.message || materialFilesLabel(files) : "";
  }
  if (elements.newFileProgress) {
    elements.newFileProgress.hidden = true;
    elements.newFileProgress.querySelector("span").style.width = "0%";
  }
  if (elements.newItemForm) {
    elements.newItemForm.querySelector("button[type='submit']").disabled = !canSubmitMaterialGeneration();
  }
}

function updateNewReferenceFile() {
  const hasFile = Boolean(state.pendingReferenceFile);
  elements.newReferenceTrigger?.classList.toggle("has-file", hasFile);
  elements.newReferenceName?.classList.toggle("has-error", state.referenceUpload.status === "too-large");
  if (elements.newReferenceName) {
    elements.newReferenceName.hidden = !hasFile;
    const status = state.referenceUpload.message ? ` · ${state.referenceUpload.message}` : "";
    elements.newReferenceName.textContent = hasFile ? `${t("fileSelected", { name: state.pendingReferenceFile.name })}${status}` : "";
    elements.newReferenceName.title = hasFile ? `${state.pendingReferenceFile.name}${status}` : "";
  }
  if (elements.newReferenceRemove) {
    elements.newReferenceRemove.hidden = !hasFile;
  }
}

function toggleNewGenerationOptions() {
  if (!elements.newGenerationOptions) return;
  const expanded = !elements.newGenerationOptions.classList.contains("is-open");
  if (expanded) {
    elements.newGenerationOptions.hidden = false;
    requestAnimationFrame(() => {
      elements.newGenerationOptions.classList.add("is-open");
    });
  } else {
    elements.newGenerationOptions.classList.remove("is-open");
    window.setTimeout(() => {
      if (!elements.newGenerationOptions.classList.contains("is-open")) {
        elements.newGenerationOptions.hidden = true;
      }
    }, 220);
  }
  elements.newGenerationToggle?.setAttribute("aria-expanded", String(expanded));
}

function resizeNewItemInput() {
  const input = elements.newItemInput;
  if (!input) return;
  const manualHeight = Number(state.newPromptManualHeight || 0);
  input.style.height = `${manualHeight || 42}px`;
  const nextHeight = Math.min(Math.max(input.scrollHeight, manualHeight || 42), 220);
  input.style.height = `${nextHeight}px`;
}

function resetNewItemInputHeight() {
  const input = elements.newItemInput;
  if (!input) return;
  state.newPromptManualHeight = 0;
  input.style.height = "";
}

function startNewPromptResize(event) {
  event.preventDefault();
  const input = elements.newItemInput;
  if (!input) return;
  if (event.pointerId !== undefined) event.currentTarget?.setPointerCapture?.(event.pointerId);
  const promptBox = input.closest(".new-prompt-box");
  promptBox?.classList.add("is-resizing");
  const startY = event.clientY;
  const startHeight = input.getBoundingClientRect().height || 42;
  const moveEventName = event.type === "mousedown" ? "mousemove" : "pointermove";
  const upEventName = event.type === "mousedown" ? "mouseup" : "pointerup";
  const onMove = (moveEvent) => {
    input.style.height = `${Math.min(Math.max(startHeight + moveEvent.clientY - startY, 42), 220)}px`;
  };
  const onUp = () => {
    state.newPromptManualHeight = Math.ceil(input.getBoundingClientRect().height || 0);
    promptBox?.classList.remove("is-resizing");
    window.removeEventListener(moveEventName, onMove);
    window.removeEventListener(upEventName, onUp);
    if (event.type !== "mousedown") window.removeEventListener("pointercancel", onUp);
    window.removeEventListener("blur", onUp);
    event.currentTarget?.removeEventListener?.("lostpointercapture", onUp);
  };
  window.addEventListener(moveEventName, onMove);
  window.addEventListener(upEventName, onUp);
  if (event.type !== "mousedown") window.addEventListener("pointercancel", onUp);
  window.addEventListener("blur", onUp);
  event.currentTarget?.addEventListener?.("lostpointercapture", onUp, { once: true });
}

async function importHtmlFile(file) {
  if (!file) return;
  if (!state.agentUrl) {
    setFeedback("agentNotConfigured");
    return;
  }
  setFeedback("importingHtml");
  const formData = new FormData();
  formData.append("file", file);
  try {
    const response = await apiFetch("/api/uploads/html", {
      method: "POST",
      body: formData,
    });
    if (!response.ok) throw new Error(`Agent returned ${response.status}`);
    const result = await response.json();
    if (result.item) {
      const index = state.items.findIndex((item) => item.id === result.item.id);
      if (index >= 0) state.items[index] = result.item;
      else state.items.unshift(result.item);
    }
    renderLibraryNav();
    renderCollectionNav();
    renderTagNav();
    renderMultiFilterOptions();
    renderManagementLists();
    renderGrid();
    renderAiContext();
    setFeedback("importHtmlDone", { title: result.item?.title || file.name });
  } catch (error) {
    setFeedback("importHtmlFailed");
    console.error(error);
  }
}

function updateAgentStatus() {
  if (!elements.agentStatus) return;
  const connected = Boolean(state.agentUrl);
  const aiReady = Boolean(state.aiStatus?.available);
  elements.agentStatus.textContent = aiReady ? t("aiReady") : t(connected ? "agentConnected" : "staticMode");
  elements.agentStatus.classList.toggle("connected", connected || aiReady);
}

async function refreshAiStatus() {
  if (hasRuntimeConfig("STATIC_DEMO")) {
    state.aiStatus = null;
    renderAiConfig();
    updateAgentStatus();
    return;
  }
  try {
    const response = await apiFetch("/api/ai/status", { cache: "no-store" });
    if (!response.ok) throw new Error(`Agent returned ${response.status}`);
    state.aiStatus = await response.json();
    syncAiConfigFromServer(state.aiStatus.provider);
  } catch (error) {
    state.aiStatus = null;
  }
  renderAiConfig();
  updateAgentStatus();
}

function openReaderAiPanel() {
  const item = getItemById(state.currentReaderItemId);
  if (item && isArchived(item)) {
    permanentlyDeleteItem(item.id);
    return;
  }
  if (state.aiPanelOpen) {
    closeAiPanel();
    return;
  }
  state.manualAiContextIds.clear();
  renderGrid();
  renderAiContext();
  openAiPanel();
}

async function loadShares() {
  if (!state.agentUrl) {
    state.shares = [];
    return;
  }
  try {
    const response = await apiFetch("/api/shares", { cache: "no-store" });
    if (!response.ok) throw new Error(`Agent returned ${response.status}`);
    const data = await response.json();
    state.shares = Array.isArray(data.shares) ? data.shares : [];
  } catch (error) {
    state.shares = [];
    console.warn("Share list unavailable.", error);
  }
}

function getActiveShareForItem(itemId) {
  return state.shares.find((share) => share.item_id === itemId && share.active && !share.revoked);
}

function getShareUrl(share) {
  return share?.url_path ? new URL(share.url_path, window.location.origin).href : "";
}

function openShareDialog(itemId) {
  const item = getItemById(itemId);
  if (!item) return;
  state.sharingItemId = itemId;
  const activeShare = getActiveShareForItem(itemId);
  elements.shareDuration.value = activeShare?.duration || "1d";
  elements.shareLink.value = activeShare ? getShareUrl(activeShare) : "";
  elements.shareCreate.textContent = t(activeShare ? "updateShare" : "createShare");
  elements.shareCopy.hidden = !elements.shareLink.value;
  elements.shareRevoke.hidden = !activeShare;
  renderShareExpiry(activeShare);
  elements.shareFeedback.textContent = state.agentUrl ? (activeShare && !elements.shareLink.value ? t("shareLinkOneTime") : "") : t("shareNeedsAgent");
  elements.shareDialog.hidden = false;
  elements.shareDuration.focus();
}

function closeShareDialog() {
  state.sharingItemId = "";
  elements.shareDialog.hidden = true;
  elements.shareFeedback.textContent = "";
  elements.shareLink.value = "";
  renderShareExpiry(null);
}

async function submitShareDialog(event) {
  event.preventDefault();
  if (!state.agentUrl) {
    elements.shareFeedback.textContent = t("shareNeedsAgent");
    return;
  }
  const itemId = state.sharingItemId;
  const activeShare = getActiveShareForItem(itemId);
  try {
    let share;
    if (activeShare) {
      const response = await apiFetch(`/api/shares/${encodeURIComponent(activeShare.id)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ duration: elements.shareDuration.value }),
      });
      if (!response.ok) throw await buildShareError(response);
      const updated = await response.json();
      share = { ...updated, url_path: updated.url_path || activeShare.url_path };
      replaceShare(share);
      elements.shareLink.value = getShareUrl(share);
      elements.shareFeedback.textContent = t("shareUpdated");
    } else {
      const response = await apiFetch("/api/shares", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_id: itemId, duration: elements.shareDuration.value }),
      });
      if (!response.ok) throw await buildShareError(response);
      const data = await response.json();
      share = { ...data.share, url_path: data.url_path };
      replaceShare(share);
      elements.shareLink.value = new URL(data.url_path, window.location.origin).href;
      elements.shareFeedback.textContent = t("shareCreated");
    }
    renderReaderShareState();
    renderGrid();
    renderShareManagement();
    renderShareExpiry(share);
    elements.shareCreate.textContent = t("updateShare");
    elements.shareCopy.hidden = !elements.shareLink.value;
    elements.shareRevoke.hidden = false;
  } catch (error) {
    elements.shareFeedback.textContent = error?.code === "safety" ? t("shareBlocked") : t("shareFailed");
    console.error(error);
  }
}

async function buildShareError(response) {
  try {
    const data = await response.json();
    if (data?.detail?.safety) return { code: "safety", detail: data.detail };
    return { code: "error", detail: data.detail || response.status };
  } catch {
    return { code: "error", detail: response.status };
  }
}

function replaceShare(share) {
  const index = state.shares.findIndex((item) => item.id === share.id);
  if (index >= 0) state.shares[index] = share;
  else state.shares.unshift(share);
}

async function copyCurrentShareLink() {
  const value = elements.shareLink.value.trim();
  if (!value) return;
  await navigator.clipboard?.writeText(value);
  elements.shareFeedback.textContent = t("shareCopied");
}

async function revokeCurrentShare() {
  const share = getActiveShareForItem(state.sharingItemId);
  if (!share || !state.agentUrl) return;
  try {
    const response = await apiFetch(`/api/shares/${encodeURIComponent(share.id)}`, { method: "DELETE" });
    if (!response.ok) throw new Error(`Agent returned ${response.status}`);
    replaceShare(await response.json());
    elements.shareFeedback.textContent = t("shareRevoked");
    renderReaderShareState();
    renderGrid();
    renderShareManagement();
    openShareDialog(state.sharingItemId);
  } catch (error) {
    elements.shareFeedback.textContent = t("shareFailed");
    console.error(error);
  }
}

function renderReaderShareState() {
  const item = getItemById(state.currentReaderItemId);
  const archived = item ? isArchived(item) : false;
  const active = !archived && Boolean(getActiveShareForItem(state.currentReaderItemId));
  elements.readerShare.hidden = archived;
  elements.readerShare.classList.toggle("active", active);
  elements.readerShare.innerHTML = shareIcon();
  setIconButtonLabel(elements.readerShare, "shareAction");
}

function renderShareManagement() {
  if (!elements.shareManagementList) return;
  const activeShares = sortShareManagementRows(state.shares.filter((share) => !share.revoked));
  if (activeShares.length === 0) {
    elements.shareManagementList.innerHTML = `<div class="empty-state">${escapeHtml(t("noShares"))}</div>`;
    return;
  }
  elements.shareManagementList.replaceChildren(...activeShares.map(renderShareManagementRow));
}

function sortShareManagementRows(shares) {
  return [...shares].sort((left, right) => {
    const leftActive = getShareStatus(left).active ? 0 : 1;
    const rightActive = getShareStatus(right).active ? 0 : 1;
    if (leftActive !== rightActive) return leftActive - rightActive;
    const leftItem = getItemById(left.item_id);
    const rightItem = getItemById(right.item_id);
    const leftTime = getItemDisplayDate(leftItem || {}) || left.created_at || left.updated_at || "";
    const rightTime = getItemDisplayDate(rightItem || {}) || right.created_at || right.updated_at || "";
    return String(rightTime).localeCompare(String(leftTime)) || String(right.updated_at || "").localeCompare(String(left.updated_at || "")) || String(right.id || "").localeCompare(String(left.id || ""));
  });
}

function renderShareManagementRow(share) {
  const item = getItemById(share.item_id);
  const status = getShareStatus(share);
  const title = item ? getItemTitle(item) : share.item_id;
  const titleMarkup = item
    ? `<button type="button" class="share-row-title" data-share-read>${escapeHtml(title)}</button>`
    : `<strong>${escapeHtml(title)}</strong>`;
  const row = document.createElement("div");
  row.className = "management-row share-row";
  row.innerHTML = `
    <div class="management-name">
      ${titleMarkup}
    </div>
    <div class="share-row-details">
      <span class="share-row-meta">
        ${shareStatusMarkup(status)}
        <span>${escapeHtml(formatShareExpiry(share))}</span>
        <span>${escapeHtml(t("shareAccessCount", { count: share.access_count || 0 }))}</span>
      </span>
    </div>
    <div class="management-actions">
      <button type="button" data-share-revoke>${escapeHtml(t("revokeShare"))}</button>
      <button type="button" data-share-open>${escapeHtml(t("shareAction"))}</button>
    </div>
  `;
  row.querySelector("[data-share-read]")?.addEventListener("click", () => {
    closeSettings();
    openReader(item);
  });
  row.querySelector("[data-share-open]").addEventListener("click", () => openShareDialog(share.item_id));
  row.querySelector("[data-share-revoke]").addEventListener("click", async () => {
    try {
      const response = await apiFetch(`/api/shares/${encodeURIComponent(share.id)}`, { method: "DELETE" });
      if (!response.ok) throw new Error(`Agent returned ${response.status}`);
      replaceShare(await response.json());
      elements.shareManagementFeedback.textContent = t("shareRevoked");
      renderShareManagement();
      renderReaderShareState();
      renderGrid();
    } catch (error) {
      elements.shareManagementFeedback.textContent = t("shareFailed");
      console.error(error);
    }
  });
  return row;
}

function formatShareExpiry(share) {
  return share?.expires_at ? formatDateTime(share.expires_at) : t("shareNoExpiry");
}

function getShareStatus(share) {
  return {
    active: Boolean(share?.active && !share?.revoked),
    label: t(share?.active && !share?.revoked ? "shareActive" : "shareExpired"),
  };
}

function shareStatusMarkup(status) {
  return `<span class="share-status ${status.active ? "is-active" : "is-expired"}"><span class="share-status-dot" aria-hidden="true"></span>${escapeHtml(status.label)}</span>`;
}

function renderShareExpiry(share) {
  if (!elements.shareExpiry) return;
  if (!share) {
    elements.shareExpiry.hidden = true;
    elements.shareExpiry.replaceChildren();
    return;
  }
  const status = getShareStatus(share);
  const label = share.expires_at ? t("shareValidUntil", { date: formatDateTime(share.expires_at) }) : t("shareNoExpiry");
  elements.shareExpiry.hidden = false;
  elements.shareExpiry.innerHTML = `
    <span>${escapeHtml(label)}</span>
    ${shareStatusMarkup(status)}
  `;
}

function toggleManualAiContext(id) {
  if (state.manualAiContextIds.has(id)) {
    state.manualAiContextIds.delete(id);
  } else {
    state.manualAiContextIds.add(id);
  }
  renderGrid();
  const item = getItemById(id);
  if (item && state.currentReaderItemId === id && !elements.reader.hidden) {
    renderReaderActions(item);
  }
  renderAiContext();
}

function renderReaderActions(item) {
  const favorite = isFavorite(item);
  const archived = isArchived(item);
  const favoriteLabel = t(favorite ? "unfavoriteAction" : "favoriteAction");
  const archiveLabel = t(archived ? "unarchiveAction" : "archiveAction");
  elements.readerEdit.hidden = archived;
  if (!archived) {
    elements.readerEdit.innerHTML = editIcon();
    setIconButtonLabel(elements.readerEdit, "editMetadata");
  }
  elements.readerFavorite.classList.toggle("active", favorite);
  elements.readerFavorite.innerHTML = starIcon(favorite);
  elements.readerFavorite.setAttribute("aria-label", favoriteLabel);
  elements.readerFavorite.setAttribute("title", favoriteLabel);
  elements.readerArchive.classList.toggle("active", archived);
  elements.readerArchive.innerHTML = archiveIcon();
  elements.readerArchive.setAttribute("aria-label", archiveLabel);
  elements.readerArchive.setAttribute("title", archiveLabel);
  if (elements.readerAiPanelOpen) {
    elements.readerAiPanelOpen.hidden = !archived;
    elements.readerAiPanelOpen.innerHTML = trashIcon();
    setIconButtonLabel(elements.readerAiPanelOpen, "permanentDeleteAction");
    elements.readerAiPanelOpen.classList.toggle("danger", archived);
  }
  renderReaderShareState();
}

function getItemById(id) {
  return state.items.find((item) => item.id === id);
}

function getItemMetadata(item) {
  return state.itemState[item.id]?.metadata || {};
}

function getItemTitle(item) {
  const title = getItemMetadata(item).title;
  return typeof title === "string" && title.trim() ? title.trim() : item.title || t("item");
}

function getItemSummary(item) {
  const summary = getItemMetadata(item).summary;
  return typeof summary === "string" ? summary : item.summary || "";
}

function getItemCollection(item) {
  const collection = getItemMetadata(item).collection;
  return typeof collection === "string" && collection.trim() ? collection.trim() : item.collection || "Inbox";
}

function getItemDisplayDate(item) {
  return item.created || item.updated || "";
}

function getItemTags(item) {
  const tags = getItemMetadata(item).tags;
  if (Array.isArray(tags)) return normalizeTags(tags);
  return normalizeTags(item.tags || []);
}

function normalizeTags(tags) {
  return [...new Set(tags.map((tag) => String(tag || "").trim().replace(/^#/, "")).filter(Boolean))];
}

function parseTagInput(value) {
  return normalizeTags(String(value || "").split(/[,，]/));
}

function getCollectionOptions() {
  return mergeManifestAndItemNames("collections", (item) => getItemCollection(item));
}

function getTagOptions() {
  return mergeManifestAndItemNames("tags", (item) => getItemTags(item));
}

function mergeManifestAndItemNames(type, extractor) {
  const manifestNames = (state.manifest?.[type] || []).map((item) => item.name).filter(Boolean);
  const names = new Set(manifestNames);
  const dynamicNames = [];
  state.items.forEach((item) => {
    const value = extractor(item);
    const values = Array.isArray(value) ? value : [value];
    values.filter(Boolean).forEach((name) => {
      if (names.has(name)) return;
      names.add(name);
      dynamicNames.push(name);
    });
  });
  dynamicNames.sort((a, b) => String(a).localeCompare(String(b), undefined, { sensitivity: "base" }));
  return [...manifestNames, ...dynamicNames].map((name) => ({ name }));
}

function itemOverride(id) {
  state.itemState[id] ||= {};
  return state.itemState[id];
}

function isFavorite(item) {
  const override = state.itemState[item.id];
  return typeof override?.favorite === "boolean" ? override.favorite : Boolean(item.favorite);
}

function isArchived(item) {
  const override = state.itemState[item.id];
  return typeof override?.archived === "boolean" ? override.archived : Boolean(item.archived);
}

async function toggleFavorite(id) {
  const item = getItemById(id);
  if (!item) return;
  await updateItemState(item, { favorite: !isFavorite(item) });
}

async function toggleArchive(id) {
  const item = getItemById(id);
  if (!item) return;
  if (!isArchived(item) && !window.confirm(t("confirmArchive"))) return;
  await updateItemState(item, { archived: !isArchived(item) });
}

async function updateItemState(item, values) {
  if (state.agentUrl) {
    try {
      const response = await apiFetch(`/api/items/${encodeURIComponent(item.id)}/state`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      if (!response.ok) throw new Error(`Agent returned ${response.status}`);
      const updated = await response.json();
      const index = state.items.findIndex((candidate) => candidate.id === item.id);
      if (index >= 0) state.items[index] = updated;
      const override = state.itemState[item.id];
      if (override) {
        if ("favorite" in values) delete override.favorite;
        if ("archived" in values) delete override.archived;
        if (!Object.keys(override).length) delete state.itemState[item.id];
        saveItemState();
      }
      clearFeedback();
      renderAfterItemStateChange(updated);
      return;
    } catch (error) {
      setFeedback("stateSaveFailed");
      console.error(error);
      return;
    }
  }

  const override = itemOverride(item.id);
  if ("favorite" in values) override.favorite = values.favorite;
  if ("archived" in values) override.archived = values.archived;
  saveItemState();
  clearFeedback();
  renderAfterItemStateChange(item);
}

async function permanentlyDeleteItem(id) {
  const item = getItemById(id);
  if (!item || !isArchived(item)) return;
  if (!state.agentUrl) {
    setFeedback("deleteNeedsAgent");
    return;
  }
  if (!window.confirm(t("confirmPermanentDelete"))) return;

  try {
    const response = await apiFetch(`/api/items/${encodeURIComponent(id)}`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error(`Agent returned ${response.status}`);
    removeItemLocally(id);
  } catch (error) {
    setFeedback("deleteFailed");
    console.error(error);
  }
}

function removeItemLocally(id) {
  state.items = state.items.filter((item) => item.id !== id);
  state.manualAiContextIds.delete(id);
  delete state.itemState[id];
  saveItemState();
  if (state.currentReaderItemId === id) {
    closeReader();
  }
  renderLibraryNav();
  renderCollectionNav();
  renderTagNav();
  renderMultiFilterOptions();
  renderManagementLists();
  renderGrid();
  renderAiContext();
  maybeAutoBackup();
}

function openMetadataEditor(id) {
  const item = getItemById(id);
  if (!item) return;
  if (isArchived(item)) return;
  state.editingItemId = id;
  state.editingTags = new Set(getItemTags(item));
  elements.metadataTitle.value = getItemTitle(item);
  elements.metadataSummary.value = getItemSummary(item);
  renderMetadataCollectionOptions(getItemCollection(item));
  renderMetadataTagPicker();
  elements.metadataEditor.hidden = false;
  elements.metadataTitle.focus();
  elements.metadataTitle.select();
}

function closeMetadataEditor() {
  state.editingItemId = "";
  state.editingTags = new Set();
  elements.metadataEditor.hidden = true;
}

async function openCodeEditor(id = state.editingItemId) {
  const item = getItemById(id);
  if (!item || isArchived(item)) return;
  state.codeEditingItemId = item.id;
  state.codeEditorOriginal = "";
  state.codeEditorDirty = false;
  elements.codeEditorItemTitle.textContent = getItemTitle(item);
  elements.codeEditorTextarea.value = "";
  elements.codeEditorFeedback.textContent = t("codeLoading");
  elements.codeEditor.hidden = false;
  applyCodeEditorWrapState();
  applyCodeEditorFullscreenState();
  updateCodeEditorPosition();
  elements.codeEditorTextarea.focus();
  try {
    const response = state.agentUrl
      ? await apiFetch(`/api/items/${encodeURIComponent(item.id)}/raw`, { cache: "no-store" })
      : await fetch(getReaderRawUrl(item), { cache: "no-store" });
    if (!response.ok) throw new Error(`Source returned ${response.status}`);
    const source = await response.text();
    if (state.codeEditingItemId !== item.id) return;
    state.codeEditorOriginal = source;
    state.codeEditorDirty = false;
    elements.codeEditorTextarea.value = source;
    elements.codeEditorFeedback.textContent = t("codeLoaded");
    updateCodeEditorPosition();
  } catch (error) {
    console.error(error);
    elements.codeEditorFeedback.textContent = t("codeSaveFailed");
  }
}

function closeCodeEditor(force = false) {
  if (!force && state.codeEditorDirty && !window.confirm(t("codeConfirmClose"))) return false;
  state.codeEditingItemId = "";
  state.codeEditorOriginal = "";
  state.codeEditorDirty = false;
  state.codeEditorFullscreen = false;
  applyCodeEditorFullscreenState();
  elements.codeEditor.hidden = true;
  elements.codeEditorTextarea.value = "";
  elements.codeEditorFeedback.textContent = "";
  return true;
}

function markCodeEditorDirty() {
  state.codeEditorDirty = elements.codeEditorTextarea.value !== state.codeEditorOriginal;
  elements.codeEditorFeedback.textContent = state.codeEditorDirty ? t("codeUnsaved") : t("codeLoaded");
  updateCodeEditorPosition();
}

function updateCodeEditorPosition() {
  const value = elements.codeEditorTextarea.value.slice(0, elements.codeEditorTextarea.selectionStart || 0);
  const lines = value.split("\n");
  elements.codeEditorPosition.textContent = t("codePosition", {
    line: lines.length,
    column: (lines[lines.length - 1] || "").length + 1,
  });
}

function applyCodeEditorWrapState() {
  elements.codeEditorTextarea.classList.toggle("no-wrap", !state.codeEditorWrap);
  elements.codeEditorWrap.setAttribute("aria-pressed", state.codeEditorWrap ? "true" : "false");
}

function toggleCodeEditorWrap() {
  state.codeEditorWrap = !state.codeEditorWrap;
  applyCodeEditorWrapState();
}

function applyCodeEditorFullscreenState() {
  elements.codeEditor.classList.toggle("is-fullscreen", state.codeEditorFullscreen);
  const label = t(state.codeEditorFullscreen ? "codeExitFullscreen" : "codeFullscreen");
  elements.codeEditorFullscreen.setAttribute("aria-label", label);
  elements.codeEditorFullscreen.setAttribute("title", label);
  elements.codeEditorFullscreen.innerHTML = state.codeEditorFullscreen ? `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M9 3v6H3"></path>
      <path d="M3 9l6-6"></path>
      <path d="M15 3v6h6"></path>
      <path d="M21 9l-6-6"></path>
      <path d="M9 21v-6H3"></path>
      <path d="M3 15l6 6"></path>
      <path d="M15 21v-6h6"></path>
      <path d="M21 15l-6 6"></path>
    </svg>
  ` : `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M8 3H3v5"></path>
      <path d="M3 3l6 6"></path>
      <path d="M16 3h5v5"></path>
      <path d="M21 3l-6 6"></path>
      <path d="M8 21H3v-5"></path>
      <path d="M3 21l6-6"></path>
      <path d="M16 21h5v-5"></path>
      <path d="M21 21l-6-6"></path>
    </svg>
  `;
}

function toggleCodeEditorFullscreen() {
  const viewport = captureCodeEditorViewport();
  state.codeEditorFullscreen = !state.codeEditorFullscreen;
  applyCodeEditorFullscreenState();
  restoreCodeEditorViewport(viewport);
}

async function saveCodeEditor({ closeAfterSave = false } = {}) {
  const item = getItemById(state.codeEditingItemId);
  if (!item) return;
  if (!state.agentUrl) {
    elements.codeEditorFeedback.textContent = t("codeNeedsAgent");
    return;
  }
  const content = elements.codeEditorTextarea.value;
  const canContinue = await confirmCodeEditorShareSafety(item.id, content);
  if (!canContinue) return;
  state.codeEditorSaving = true;
  elements.codeEditorSave.disabled = true;
  elements.codeEditorSaveClose.disabled = true;
  try {
    const response = await apiFetch(`/api/items/${encodeURIComponent(item.id)}/content`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    });
    if (!response.ok) throw new Error(`Agent returned ${response.status}`);
    const updated = await response.json();
    const index = state.items.findIndex((candidate) => candidate.id === item.id);
    if (index >= 0) state.items[index] = updated;
    state.codeEditorOriginal = content;
    state.codeEditorDirty = false;
    await refreshManifestAndWorkspace();
    refreshReaderAfterContentEdit(updated);
    elements.codeEditorFeedback.textContent = t("codeSaved");
    setFeedback("codeSaved");
    if (closeAfterSave) {
      closeCodeEditor(true);
      closeMetadataEditor();
    }
  } catch (error) {
    console.error(error);
    elements.codeEditorFeedback.textContent = t("codeSaveFailed");
  } finally {
    state.codeEditorSaving = false;
    elements.codeEditorSave.disabled = false;
    elements.codeEditorSaveClose.disabled = false;
  }
}

function captureCodeEditorViewport() {
  const textarea = elements.codeEditorTextarea;
  return {
    selectionStart: textarea.selectionStart || 0,
    selectionEnd: textarea.selectionEnd || 0,
    selectionDirection: textarea.selectionDirection || "none",
    scrollTop: textarea.scrollTop,
    scrollLeft: textarea.scrollLeft,
  };
}

function restoreCodeEditorViewport(viewport) {
  const textarea = elements.codeEditorTextarea;
  const restore = () => {
    textarea.focus({ preventScroll: true });
    textarea.setSelectionRange(viewport.selectionStart, viewport.selectionEnd, viewport.selectionDirection);
    textarea.scrollTop = viewport.scrollTop;
    textarea.scrollLeft = viewport.scrollLeft;
    updateCodeEditorPosition();
  };
  restore();
  requestAnimationFrame(restore);
}

async function confirmCodeEditorShareSafety(itemId, content) {
  try {
    const response = await apiFetch(`/api/items/${encodeURIComponent(itemId)}/content/share-safety`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    });
    if (!response.ok) throw new Error(`Safety precheck returned ${response.status}`);
    const scan = await response.json();
    if (scan.shareable) return true;
    const reasons = Array.isArray(scan.reasons) && scan.reasons.length ? scan.reasons.join(", ") : "unknown";
    return window.confirm(t("codeShareSafetyConfirm", { reasons }));
  } catch (error) {
    console.error(error);
    elements.codeEditorFeedback.textContent = t("codeShareSafetyFailed");
    return window.confirm(t("codeShareSafetyConfirm", { reasons: t("codeShareSafetyFailed") }));
  }
}

function refreshReaderAfterContentEdit(item) {
  if (elements.reader.hidden || state.currentReaderItemId !== item.id) return;
  renderReaderMetadata(item);
  renderReaderActions(item);
  const url = getReaderContentUrl(item);
  const separator = url.includes("?") ? "&" : "?";
  elements.readerFrame.src = `${url}${separator}edited=${Date.now()}`;
}

function insertCodeEditorTab(event) {
  event.preventDefault();
  const textarea = elements.codeEditorTextarea;
  const start = textarea.selectionStart || 0;
  const end = textarea.selectionEnd || 0;
  const value = textarea.value;
  textarea.value = `${value.slice(0, start)}  ${value.slice(end)}`;
  textarea.selectionStart = start + 2;
  textarea.selectionEnd = start + 2;
  markCodeEditorDirty();
}

async function openFileEditor(id = state.editingItemId) {
  const item = getItemById(id);
  if (!item || isArchived(item)) return;
  state.fileEditingItemId = item.id;
  state.fileEditorOriginal = "";
  state.fileEditorDirty = false;
  state.fileEditorMode = "text";
  state.fileEditorSelectedPath = "";
  state.fileEditorHistory = [];
  state.fileEditorHistoryIndex = -1;
  state.fileEditorPanelCollapsed = false;
  elements.fileEditorItemTitle.textContent = getItemTitle(item);
  elements.fileEditorFeedback.textContent = t("fileEditorLoading");
  elements.fileEditorSelectedName.textContent = t("fileNoSelection");
  elements.fileEditor.hidden = false;
  applyFileEditorPanelState();
  setFileEditorMode("text");
  updateFileEditorHistoryButtons();
  try {
    const response = state.agentUrl
      ? await apiFetch(`/api/items/${encodeURIComponent(item.id)}/raw`, { cache: "no-store" })
      : await fetch(getReaderRawUrl(item), { cache: "no-store" });
    if (!response.ok) throw new Error(`Source returned ${response.status}`);
    const source = await response.text();
    if (state.fileEditingItemId !== item.id) return;
    state.fileEditorOriginal = source;
    loadFileEditorDocument(source);
    pushFileEditorHistory(source, { dirty: false });
    elements.fileEditorFeedback.textContent = t("fileEditorLoaded");
  } catch (error) {
    console.error(error);
    elements.fileEditorFeedback.textContent = t("fileEditorSaveFailed");
  }
}

function closeFileEditor(force = false) {
  if (!force && state.fileEditorDirty && !window.confirm(t("fileEditorConfirmClose"))) return false;
  state.fileEditingItemId = "";
  state.fileEditorOriginal = "";
  state.fileEditorDirty = false;
  state.fileEditorSelectedPath = "";
  state.fileEditorHistory = [];
  state.fileEditorHistoryIndex = -1;
  window.clearTimeout(state.fileEditorHistoryTimer);
  state.fileEditorHistoryTimer = 0;
  elements.fileEditor.hidden = true;
  elements.fileEditorFrame.removeAttribute("srcdoc");
  elements.fileEditorFeedback.textContent = "";
  updateFileEditorHistoryButtons();
  return true;
}

function loadFileEditorDocument(source) {
  elements.fileEditorFrame.srcdoc = injectFileEditorRuntime(source);
}

function injectFileEditorRuntime(source) {
  const runtime = `
<style id="html-lore-visual-editor-style">
  [data-html-lore-selected="true"] { outline: 2px solid #0f766e !important; outline-offset: 2px !important; }
  [data-html-lore-hover="true"] { outline: 1px dashed rgba(15,118,110,.65) !important; outline-offset: 2px !important; }
  [data-html-lore-editing-text="true"] { cursor: text !important; }
</style>
<script id="html-lore-visual-editor-runtime">
(() => {
  const blocked = new Set(["HTML","BODY","HEAD","META","TITLE","STYLE","SCRIPT","LINK","IFRAME","OBJECT","EMBED","CANVAS","SVG","NOSCRIPT"]);
  const textTargets = new Set(["P","H1","H2","H3","H4","H5","H6","LI","A","BUTTON","SPAN","STRONG","EM","SMALL","LABEL","TD","TH","BLOCKQUOTE","PRE","CODE","FIGCAPTION"]);
  const inlineTargets = new Set(["A","BUTTON","SPAN","STRONG","EM","SMALL","LABEL","CODE","B","I","U","S","MARK"]);
  let selected = null;
  let hover = null;
  let mode = "text";
  function pathFor(element) {
    const parts = [];
    let node = element;
    while (node && node.nodeType === 1 && node !== document.documentElement) {
      const parent = node.parentElement;
      if (!parent) break;
      const index = Array.from(parent.children).indexOf(node);
      parts.unshift(index);
      node = parent;
    }
    return parts.join(".");
  }
  function elementFor(path) {
    if (!path) return null;
    let node = document.documentElement;
    for (const raw of path.split(".")) {
      const index = Number(raw);
      if (!Number.isInteger(index) || !node.children[index]) return null;
      node = node.children[index];
    }
    return node;
  }
  function editable(element) {
    if (!element || blocked.has(element.tagName)) return false;
    if (element.closest("script,style,iframe,object,embed,canvas,svg")) return false;
    return true;
  }
  function selectable(element) {
    if (!editable(element)) return false;
    if (textTargets.has(element.tagName)) return true;
    if (isCompositeTextBlock(element)) return true;
    if (element.children.length === 0 && (element.textContent || "").trim()) return true;
    return false;
  }
  function isCompositeTextBlock(element) {
    if (!editable(element) || !String(element.textContent || "").trim()) return false;
    if (element.children.length === 0 || element.children.length > 8) return false;
    const hasOwnText = Array.from(element.childNodes).some((node) => node.nodeType === Node.TEXT_NODE && String(node.textContent || "").trim());
    if (!hasOwnText) return false;
    return Array.from(element.children).every((child) => inlineTargets.has(child.tagName));
  }
  function selectionTarget(rawTarget) {
    let target = rawTarget;
    if (target && target.nodeType === Node.TEXT_NODE) target = target.parentElement;
    if (!target || target.nodeType !== Node.ELEMENT_NODE) return null;
    const parent = target.parentElement;
    if (inlineTargets.has(target.tagName) && isCompositeTextBlock(parent)) return parent;
    return target;
  }
  function snapshot(element) {
    const computed = getComputedStyle(element);
    return {
      path: pathFor(element),
      tag: element.tagName.toLowerCase(),
      text: element.textContent || "",
      style: {
        color: element.style.color || rgbToHex(computed.color, "#000000"),
        backgroundColor: element.style.backgroundColor || inheritedBackgroundColor(element),
        fontSize: parseFloat(computed.fontSize) || "",
        lineHeight: computed.lineHeight === "normal" ? "" : parseFloat(computed.lineHeight) / (parseFloat(computed.fontSize) || 16),
        fontWeight: element.style.fontWeight || computed.fontWeight || "",
        fontStyle: element.style.fontStyle || computed.fontStyle || "",
        textDecoration: element.style.textDecoration || computed.textDecorationLine || "",
        textAlign: element.style.textAlign || computed.textAlign || "",
      },
    };
  }
  function select(element) {
    if (!editable(element)) {
      parent.postMessage({ type: "html-lore-file-editor-unsupported" }, "*");
      return;
    }
    if (selected) {
      selected.removeAttribute("data-html-lore-selected");
      selected.removeAttribute("data-html-lore-editing-text");
      selected.removeAttribute("contenteditable");
    }
    selected = element;
    selected.setAttribute("data-html-lore-selected", "true");
    applyMode();
    parent.postMessage({ type: "html-lore-file-editor-select", selection: snapshot(element) }, "*");
  }
  function applyMode() {
    if (!selected) return;
    if (mode === "text") {
      selected.setAttribute("contenteditable", "plaintext-only");
      selected.setAttribute("data-html-lore-editing-text", "true");
      selected.focus({ preventScroll: true });
    } else {
      selected.removeAttribute("contenteditable");
      selected.removeAttribute("data-html-lore-editing-text");
    }
  }
  function rgbToHex(value, fallback) {
    const text = String(value || "");
    const match = text.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?/i);
    if (!match) return fallback;
    if (match[4] !== undefined && Number(match[4]) === 0) return fallback;
    return "#" + [match[1], match[2], match[3]].map((part) => Number(part).toString(16).padStart(2, "0")).join("");
  }
  function inheritedBackgroundColor(element) {
    let node = element;
    while (node && node.nodeType === Node.ELEMENT_NODE) {
      const value = getComputedStyle(node).backgroundColor;
      const hex = rgbToHex(value, "");
      if (hex) return hex;
      node = node.parentElement;
    }
    return "#ffffff";
  }
  function serialize() {
    const clone = document.documentElement.cloneNode(true);
    clone.querySelector("#html-lore-visual-editor-style")?.remove();
    clone.querySelector("#html-lore-visual-editor-runtime")?.remove();
    clone.querySelectorAll("[data-html-lore-selected],[data-html-lore-hover]").forEach((node) => {
      node.removeAttribute("data-html-lore-selected");
      node.removeAttribute("data-html-lore-hover");
      node.removeAttribute("data-html-lore-editing-text");
      node.removeAttribute("contenteditable");
    });
    return "<!doctype html>\\n" + clone.outerHTML;
  }
  document.addEventListener("mouseover", (event) => {
    const target = selectionTarget(event.target);
    if (!selectable(target) || target === selected) return;
    if (hover) hover.removeAttribute("data-html-lore-hover");
    hover = target;
    hover.setAttribute("data-html-lore-hover", "true");
  }, true);
  document.addEventListener("mouseout", () => {
    if (hover) hover.removeAttribute("data-html-lore-hover");
    hover = null;
  }, true);
  document.addEventListener("click", (event) => {
    const target = selectionTarget(event.target);
    if (mode === "text" && target === selected) return;
    if (!selectable(target)) return;
    event.preventDefault();
    event.stopPropagation();
    select(target);
  }, true);
  document.addEventListener("input", (event) => {
    if (!selected || event.target !== selected) return;
    parent.postMessage({ type: "html-lore-file-editor-direct-text", selection: snapshot(selected) }, "*");
  }, true);
  window.addEventListener("message", (event) => {
    const message = event.data || {};
    if (message.type === "html-lore-file-editor-mode") {
      mode = message.mode === "element" ? "element" : "text";
      applyMode();
    }
    if (message.type === "html-lore-file-editor-apply") {
      const element = elementFor(message.path);
      if (!editable(element)) return;
      if ("text" in message.values) element.textContent = String(message.values.text || "");
      const style = message.values.style || {};
      for (const [key, value] of Object.entries(style)) {
        element.style[key] = value == null ? "" : String(value);
      }
      if (message.silent) return;
      select(element);
    }
    if (message.type === "html-lore-file-editor-select") {
      const element = elementFor(message.path);
      if (editable(element)) select(element);
    }
    if (message.type === "html-lore-file-editor-serialize") {
      parent.postMessage({ type: "html-lore-file-editor-serialized", html: serialize(), requestId: message.requestId }, "*");
    }
  });
})();
</script>`;
  if (/<\/body\s*>/i.test(source)) return source.replace(/<\/body\s*>/i, `${runtime}</body>`);
  return `${source}${runtime}`;
}

function setFileEditorMode(mode) {
  state.fileEditorMode = mode === "element" ? "element" : "text";
  elements.fileEditorModeText.classList.toggle("active", state.fileEditorMode === "text");
  elements.fileEditorModeElement.classList.toggle("active", state.fileEditorMode === "element");
  elements.fileEditorText.disabled = state.fileEditorMode !== "text";
  postFileEditorMessage({ type: "html-lore-file-editor-mode", mode: state.fileEditorMode });
}

function applyFileEditorPanelState() {
  state.fileEditorPanelWidth = clampFileEditorPanelWidth(state.fileEditorPanelWidth);
  elements.fileEditor.classList.toggle("panel-collapsed", state.fileEditorPanelCollapsed);
  elements.fileEditor.style.setProperty("--file-editor-panel-width", `${state.fileEditorPanelWidth}px`);
  const label = t(state.fileEditorPanelCollapsed ? "expandEditorPanel" : "collapseEditorPanel");
  elements.fileEditorPanelToggle.setAttribute("aria-label", label);
  elements.fileEditorPanelToggle.setAttribute("title", label);
  elements.fileEditorPanelToggle.innerHTML = state.fileEditorPanelCollapsed ? `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="m15 18-6-6 6-6"></path>
    </svg>
  ` : `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="m9 18 6-6-6-6"></path>
    </svg>
  `;
}

function toggleFileEditorPanel() {
  state.fileEditorPanelCollapsed = !state.fileEditorPanelCollapsed;
  setStored("file-editor-panel-collapsed", String(state.fileEditorPanelCollapsed));
  applyFileEditorPanelState();
}

function handleFileEditorMessage(event) {
  if (event.source !== elements.fileEditorFrame.contentWindow) return;
  const message = event.data || {};
  if (message.type === "html-lore-file-editor-select") {
    updateFileEditorSelection(message.selection);
  } else if (message.type === "html-lore-file-editor-direct-text") {
    updateFileEditorSelection(message.selection);
    markFileEditorDirty();
    scheduleFileEditorHistorySnapshot();
  } else if (message.type === "html-lore-file-editor-unsupported") {
    elements.fileEditorFeedback.textContent = t("fileEditorUnsupported");
  }
}

function updateFileEditorSelection(selection) {
  state.fileEditorSelectedPath = selection.path || "";
  state.fileEditorSyncing = true;
  elements.fileEditorSelectedName.textContent = selection.tag ? `<${selection.tag}>` : t("fileNoSelection");
  elements.fileEditorText.value = selection.text || "";
  elements.fileEditorColor.value = normalizeColorInput(selection.style?.color || "#000000", "#000000");
  elements.fileEditorBackground.value = normalizeColorInput(selection.style?.backgroundColor || "#ffffff", "#ffffff");
  elements.fileEditorFontSize.value = selection.style?.fontSize ? Math.round(Number(selection.style.fontSize)) : "";
  elements.fileEditorLineHeight.value = selection.style?.lineHeight ? Number(selection.style.lineHeight).toFixed(1) : "";
  elements.fileEditorFontWeight.value = normalizeWeightValue(selection.style?.fontWeight || "");
  elements.fileEditorTextAlign.value = normalizeAlignValue(selection.style?.textAlign || "");
  elements.fileEditorBold.setAttribute("aria-pressed", normalizeWeightValue(selection.style?.fontWeight || "") === "700" ? "true" : "false");
  elements.fileEditorItalic.setAttribute("aria-pressed", String(selection.style?.fontStyle || "") === "italic" ? "true" : "false");
  const decoration = String(selection.style?.textDecoration || "");
  elements.fileEditorUnderline.setAttribute("aria-pressed", decoration.includes("underline") ? "true" : "false");
  elements.fileEditorStrike.setAttribute("aria-pressed", decoration.includes("line-through") ? "true" : "false");
  state.fileEditorSyncing = false;
  elements.fileEditorFeedback.textContent = state.fileEditorDirty ? t("fileEditorUnsaved") : t("fileEditorLoaded");
}

function normalizeColorInput(value, fallback = "#000000") {
  const text = String(value || "").trim();
  if (/^#[0-9a-f]{6}$/i.test(text)) return text.toLowerCase();
  if (/^#[0-9a-f]{3}$/i.test(text)) {
    return `#${text.slice(1).split("").map((part) => `${part}${part}`).join("")}`.toLowerCase();
  }
  const rgb = text.match(/^rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})/i);
  if (rgb) {
    const [red, green, blue] = rgb.slice(1, 4).map((part) => clampNumber(part, 0, 255));
    return `#${[red, green, blue].map((part) => Math.round(part).toString(16).padStart(2, "0")).join("")}`;
  }
  return fallback;
}

function normalizeWeightValue(value) {
  const text = String(value || "");
  if (Number(text) >= 650) return "700";
  if (Number(text) >= 550) return "600";
  if (Number(text) >= 350) return "400";
  return "";
}

function normalizeAlignValue(value) {
  return ["left", "center", "right"].includes(value) ? value : "";
}

function applyFileEditorPanelChange({ pushHistory = true, changed = "" } = {}) {
  if (state.fileEditorSyncing || !state.fileEditorSelectedPath) return;
  const style = {};
  if (changed === "color") style.color = elements.fileEditorColor.value || "";
  if (changed === "backgroundColor") style.backgroundColor = elements.fileEditorBackground.value || "";
  if (changed === "fontSize") style.fontSize = elements.fileEditorFontSize.value ? `${clampNumber(elements.fileEditorFontSize.value, 10, 48)}px` : "";
  if (changed === "lineHeight") style.lineHeight = elements.fileEditorLineHeight.value ? String(clampNumber(elements.fileEditorLineHeight.value, 1, 2.4)) : "";
  if (changed === "fontWeight") style.fontWeight = elements.fileEditorFontWeight.value || "";
  if (changed === "fontStyle") style.fontStyle = elements.fileEditorItalic.getAttribute("aria-pressed") === "true" ? "italic" : "";
  if (changed === "textDecoration") style.textDecoration = getFileEditorTextDecorationValue();
  if (changed === "textAlign") style.textAlign = elements.fileEditorTextAlign.value || "";
  postFileEditorMessage({
    type: "html-lore-file-editor-apply",
    path: state.fileEditorSelectedPath,
    silent: changed === "text",
    values: {
      ...(changed === "text" && state.fileEditorMode === "text" ? { text: elements.fileEditorText.value } : {}),
      style,
    },
  });
  markFileEditorDirty();
  if (pushHistory) snapshotFileEditorHistory();
}

function clampNumber(value, min, max) {
  const number = Number(value);
  if (!Number.isFinite(number)) return min;
  return Math.min(max, Math.max(min, number));
}

function postFileEditorMessage(message) {
  elements.fileEditorFrame.contentWindow?.postMessage(message, "*");
}

function markFileEditorDirty() {
  state.fileEditorDirty = true;
  elements.fileEditorFeedback.textContent = t("fileEditorUnsaved");
}

function resetFileEditorElement() {
  if (!state.fileEditorSelectedPath) return;
  postFileEditorMessage({
    type: "html-lore-file-editor-apply",
    path: state.fileEditorSelectedPath,
    values: {
      style: {
        color: "",
        backgroundColor: "",
        fontSize: "",
        lineHeight: "",
        fontWeight: "",
        fontStyle: "",
        textDecoration: "",
        textAlign: "",
      },
    },
  });
  markFileEditorDirty();
  snapshotFileEditorHistory();
}

function getFileEditorTextDecorationValue() {
  const values = [];
  if (elements.fileEditorUnderline.getAttribute("aria-pressed") === "true") values.push("underline");
  if (elements.fileEditorStrike.getAttribute("aria-pressed") === "true") values.push("line-through");
  return values.join(" ");
}

function toggleFileEditorTextStyle(style) {
  if (!state.fileEditorSelectedPath) return;
  if (style === "bold") {
    const active = elements.fileEditorBold.getAttribute("aria-pressed") === "true";
    elements.fileEditorBold.setAttribute("aria-pressed", active ? "false" : "true");
    elements.fileEditorFontWeight.value = active ? "" : "700";
    applyFileEditorPanelChange({ changed: "fontWeight" });
    return;
  }
  if (style === "italic") {
    const active = elements.fileEditorItalic.getAttribute("aria-pressed") === "true";
    elements.fileEditorItalic.setAttribute("aria-pressed", active ? "false" : "true");
    applyFileEditorPanelChange({ changed: "fontStyle" });
    return;
  }
  if (style === "underline") {
    const active = elements.fileEditorUnderline.getAttribute("aria-pressed") === "true";
    elements.fileEditorUnderline.setAttribute("aria-pressed", active ? "false" : "true");
    applyFileEditorPanelChange({ changed: "textDecoration" });
    return;
  }
  if (style === "strike") {
    const active = elements.fileEditorStrike.getAttribute("aria-pressed") === "true";
    elements.fileEditorStrike.setAttribute("aria-pressed", active ? "false" : "true");
    applyFileEditorPanelChange({ changed: "textDecoration" });
  }
}

function startFileEditorPanelResize(event) {
  if (state.fileEditorPanelCollapsed) return;
  event.preventDefault();
  if (event.pointerId !== undefined) event.currentTarget?.setPointerCapture?.(event.pointerId);
  elements.body.classList.add("ai-panel-resizing");
  const panelBox = elements.fileEditorPanel.getBoundingClientRect();
  const pointerOffset = event.clientX - panelBox.left;
  const startWidth = panelBox.width;
  const onMove = (moveEvent) => {
    state.fileEditorPanelWidth = clampFileEditorPanelWidth(startWidth + panelBox.left - moveEvent.clientX + pointerOffset);
    applyFileEditorPanelState();
  };
  const onUp = () => {
    elements.body.classList.remove("ai-panel-resizing");
    setStored("file-editor-panel-width", String(state.fileEditorPanelWidth));
    window.removeEventListener("pointermove", onMove);
    window.removeEventListener("pointerup", onUp);
    window.removeEventListener("pointercancel", onUp);
    window.removeEventListener("blur", onUp);
    event.currentTarget?.removeEventListener?.("lostpointercapture", onUp);
  };
  window.addEventListener("pointermove", onMove);
  window.addEventListener("pointerup", onUp);
  window.addEventListener("pointercancel", onUp);
  window.addEventListener("blur", onUp);
  event.currentTarget?.addEventListener?.("lostpointercapture", onUp, { once: true });
}

function requestFileEditorHtml() {
  return new Promise((resolve) => {
    const requestId = `file-edit-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    const fallbackTimer = window.setTimeout(() => {
      window.removeEventListener("message", listener);
      resolve(serializeFileEditorFrameDirectly());
    }, 500);
    const listener = (event) => {
      if (event.source !== elements.fileEditorFrame.contentWindow) return;
      const message = event.data || {};
      if (message.type !== "html-lore-file-editor-serialized" || message.requestId !== requestId) return;
      window.clearTimeout(fallbackTimer);
      window.removeEventListener("message", listener);
      resolve(String(message.html || "") || serializeFileEditorFrameDirectly());
    };
    window.addEventListener("message", listener);
    postFileEditorMessage({ type: "html-lore-file-editor-serialize", requestId });
  });
}

function serializeFileEditorFrameDirectly() {
  const doc = elements.fileEditorFrame.contentDocument;
  if (!doc?.documentElement) return "";
  const clone = doc.documentElement.cloneNode(true);
  clone.querySelector("#html-lore-visual-editor-style")?.remove();
  clone.querySelector("#html-lore-visual-editor-runtime")?.remove();
  clone.querySelectorAll("[data-html-lore-selected],[data-html-lore-hover],[data-html-lore-editing-text],[contenteditable]").forEach((node) => {
    node.removeAttribute("data-html-lore-selected");
    node.removeAttribute("data-html-lore-hover");
    node.removeAttribute("data-html-lore-editing-text");
    node.removeAttribute("contenteditable");
  });
  return `<!doctype html>\n${clone.outerHTML}`;
}

async function snapshotFileEditorHistory() {
  const html = await requestFileEditorHtml();
  pushFileEditorHistory(html);
}

function scheduleFileEditorHistorySnapshot() {
  window.clearTimeout(state.fileEditorHistoryTimer);
  state.fileEditorHistoryTimer = window.setTimeout(() => {
    state.fileEditorHistoryTimer = 0;
    snapshotFileEditorHistory();
  }, 650);
}

function pushFileEditorHistory(html, options = {}) {
  const current = state.fileEditorHistory[state.fileEditorHistoryIndex];
  if (current === html) return;
  state.fileEditorHistory = state.fileEditorHistory.slice(0, state.fileEditorHistoryIndex + 1);
  state.fileEditorHistory.push(html);
  state.fileEditorHistoryIndex = state.fileEditorHistory.length - 1;
  if (options.dirty === false) state.fileEditorDirty = false;
  updateFileEditorHistoryButtons();
}

function updateFileEditorHistoryButtons() {
  elements.fileEditorUndo.disabled = state.fileEditorHistoryIndex <= 0;
  elements.fileEditorRedo.disabled = state.fileEditorHistoryIndex >= state.fileEditorHistory.length - 1;
}

function stepFileEditorHistory(direction) {
  const next = state.fileEditorHistoryIndex + direction;
  if (next < 0 || next >= state.fileEditorHistory.length) return;
  state.fileEditorHistoryIndex = next;
  const html = state.fileEditorHistory[next];
  state.fileEditorDirty = html !== state.fileEditorOriginal;
  loadFileEditorDocument(html);
  state.fileEditorSelectedPath = "";
  elements.fileEditorSelectedName.textContent = t("fileNoSelection");
  elements.fileEditorFeedback.textContent = state.fileEditorDirty ? t("fileEditorUnsaved") : t("fileEditorLoaded");
  updateFileEditorHistoryButtons();
}

async function saveFileEditor({ closeAfterSave = false } = {}) {
  const item = getItemById(state.fileEditingItemId);
  if (!item) return;
  if (!state.agentUrl) {
    elements.fileEditorFeedback.textContent = t("codeNeedsAgent");
    return;
  }
  if (state.fileEditorMode === "text" && state.fileEditorSelectedPath) {
    applyFileEditorPanelChange({ pushHistory: false, changed: "text" });
  }
  const content = await requestFileEditorHtml();
  if (!content.trim()) {
    elements.fileEditorFeedback.textContent = t("fileEditorSaveFailed");
    return;
  }
  const canContinue = await confirmCodeEditorShareSafety(item.id, content);
  if (!canContinue) return;
  elements.fileEditorSave.disabled = true;
  elements.fileEditorSaveClose.disabled = true;
  try {
    const response = await apiFetch(`/api/items/${encodeURIComponent(item.id)}/content`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    });
    if (!response.ok) throw new Error(`Agent returned ${response.status}`);
    const updated = await response.json();
    state.fileEditorOriginal = content;
    state.fileEditorDirty = false;
    await refreshManifestAndWorkspace();
    refreshReaderAfterContentEdit(updated);
    elements.fileEditorFeedback.textContent = t("fileEditorSaved");
    setFeedback("fileEditorSaved");
    if (closeAfterSave) {
      closeFileEditor(true);
      closeMetadataEditor();
    } else {
      pushFileEditorHistory(content, { dirty: false });
    }
  } catch (error) {
    console.error(error);
    elements.fileEditorFeedback.textContent = t("fileEditorSaveFailed");
  } finally {
    elements.fileEditorSave.disabled = false;
    elements.fileEditorSaveClose.disabled = false;
  }
}

function renderMetadataCollectionOptions(selectedCollection) {
  const names = new Set(getCollectionOptions().map((collection) => collection.name));
  names.add(selectedCollection || "Inbox");
  elements.metadataCollection.replaceChildren();
  const addOption = document.createElement("option");
  addOption.value = "__add__";
  addOption.textContent = t("metadataAddCollection");
  elements.metadataCollection.append(addOption);
  [...names].filter(Boolean).sort((a, b) => a.localeCompare(b)).forEach((name) => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    elements.metadataCollection.append(option);
  });
  elements.metadataCollection.value = selectedCollection || "Inbox";
}

function renderMetadataTagPicker() {
  elements.metadataTagPicker.replaceChildren();
  const addButton = document.createElement("button");
  addButton.type = "button";
  addButton.className = "metadata-chip add-chip";
  addButton.textContent = `+ ${t("metadataAddTag")}`;
  addButton.addEventListener("click", addMetadataTag);
  elements.metadataTagPicker.append(addButton);
  const names = new Set(getTagOptions().map((tag) => tag.name));
  state.editingTags.forEach((tag) => names.add(tag));
  [...names].filter(Boolean).sort((a, b) => a.localeCompare(b)).forEach((name) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "metadata-chip";
    button.classList.toggle("active", state.editingTags.has(name));
    button.textContent = `#${name}`;
    button.addEventListener("click", () => {
      if (state.editingTags.has(name)) state.editingTags.delete(name);
      else state.editingTags.add(name);
      renderMetadataTagPicker();
    });
    elements.metadataTagPicker.append(button);
  });
}

function addMetadataCollection() {
  const name = window.prompt(t("addCollection"));
  const cleaned = String(name || "").trim();
  if (!cleaned) {
    elements.metadataCollection.value = getCurrentMetadataCollectionFallback();
    return;
  }
  renderMetadataCollectionOptions(cleaned);
  elements.metadataCollection.value = cleaned;
}

function addMetadataTag() {
  const name = window.prompt(t("addTag"));
  const cleaned = String(name || "").trim().replace(/^#/, "");
  if (!cleaned) return;
  state.editingTags.add(cleaned);
  renderMetadataTagPicker();
}

function getCurrentMetadataCollectionFallback() {
  const item = getItemById(state.editingItemId);
  return item ? getItemCollection(item) : "Inbox";
}

async function saveMetadataEditor(event) {
  event.preventDefault();
  const item = getItemById(state.editingItemId);
  if (!item) {
    closeMetadataEditor();
    return;
  }
  const metadata = {
    title: elements.metadataTitle.value.trim() || item.title || t("item"),
    summary: elements.metadataSummary.value.trim(),
    collection: elements.metadataCollection.value.trim() || "Inbox",
    tags: [...state.editingTags],
  };

  if (state.agentUrl) {
    try {
      const response = await apiFetch(`/api/items/${encodeURIComponent(item.id)}/metadata`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(metadata),
      });
      if (!response.ok) throw new Error(`Agent returned ${response.status}`);
      const updated = await response.json();
      const index = state.items.findIndex((candidate) => candidate.id === item.id);
      if (index >= 0) state.items[index] = updated;
      delete state.itemState[item.id]?.metadata;
      saveItemState();
    } catch (error) {
      setFeedback("metadataSaveFailed");
      console.error(error);
      return;
    }
  } else {
    itemOverride(item.id).metadata = metadata;
    saveItemState();
  }
  closeMetadataEditor();
  renderAfterItemStateChange(getItemById(item.id) || item);
  setFeedback("metadataSaved");
}

function renderAfterItemStateChange(item) {
  normalizeVisibleTagFilters();
  renderLibraryNav();
  renderCollectionNav();
  renderTagNav();
  renderMultiFilterOptions();
  renderManagementLists();
  renderGrid();
  if (!elements.reader.hidden && state.currentReaderItemId === item.id) {
    renderReaderMetadata(item);
    renderReaderActions(item);
  }
  renderAiContext();
  maybeAutoBackup();
}

function getInitialLanguage() {
  const saved = getStored("language");
  if (saved && i18n[saved]) return saved;
  return "en";
}

function setLanguage(language) {
  if (!i18n[language]) return;
  state.language = language;
  setStored("language", language);
  renderApp();
}

function getInitialThemeMode() {
  const saved = getStored("theme");
  if (saved === "system" || saved === "dark" || saved === "light") return saved;
  return "system";
}

function getInitialViewMode() {
  return "cards";
}

function getInitialSortMode() {
  const saved = getStored("sort-mode");
  return ["newest", "oldest", "title-az", "title-za"].includes(saved) ? saved : "newest";
}

function getInitialAiPanelWidth() {
  const saved = Number(getStored("ai-panel-width"));
  if (Number.isFinite(saved) && saved >= 320 && saved <= 720) return saved;
  return 420;
}

function getInitialFileEditorPanelWidth() {
  const saved = Number(getStored("file-editor-panel-width"));
  if (Number.isFinite(saved) && saved >= 260 && saved <= 560) return saved;
  return 320;
}

function getInitialAiComposerHeight() {
  const saved = Number(getStored("ai-composer-height"));
  if (Number.isFinite(saved) && saved >= 142 && saved <= 320) return saved;
  return 172;
}

function getInitialSidebarWidth() {
  const saved = Number(getStored("sidebar-width"));
  if (Number.isFinite(saved) && saved >= 240 && saved <= 420) return saved;
  return 280;
}

function clampAiPanelWidth(width) {
  const viewportLimit = Math.max(320, window.innerWidth - 120);
  return Math.min(720, Math.max(320, Math.min(width, viewportLimit)));
}

function clampFileEditorPanelWidth(width) {
  const viewportLimit = Math.max(260, window.innerWidth - 360);
  return Math.min(560, Math.max(260, Math.min(width, viewportLimit)));
}

function clampAiComposerHeight(height) {
  const viewportLimit = Math.max(142, Math.min(320, Math.round(window.innerHeight * 0.42)));
  return Math.min(viewportLimit, Math.max(142, height));
}

function clampSidebarWidth(width) {
  const viewportLimit = Math.max(240, window.innerWidth - state.aiPanelWidth - 360);
  return Math.min(420, Math.max(240, Math.min(width, viewportLimit)));
}

function getInitialSidebarState() {
  return getStored("sidebar-collapsed") === "true";
}

function getInitialNavSectionState() {
  try {
    return JSON.parse(getStored("nav-section-collapsed") || "{}");
  } catch {
    return {};
  }
}

function toggleNavSection(section) {
  state.navSectionCollapsed[section] = !state.navSectionCollapsed[section];
  setStored("nav-section-collapsed", JSON.stringify(state.navSectionCollapsed));
  applyNavSectionState();
}

function applyNavSectionState() {
  elements.navSections.forEach((section) => {
    const key = section.dataset.navSection;
    section.classList.toggle("collapsed", Boolean(state.navSectionCollapsed[key]));
  });
  elements.navSectionToggles.forEach((button) => {
    const key = button.dataset.navSectionToggle;
    const sectionName = t(key);
    const label = t(state.navSectionCollapsed[key] ? "expandNavSection" : "collapseNavSection", { name: sectionName });
    button.setAttribute("aria-label", label);
    button.setAttribute("title", label);
  });
}

function toggleSidebar() {
  state.sidebarCollapsed = !state.sidebarCollapsed;
  setStored("sidebar-collapsed", String(state.sidebarCollapsed));
  applySidebarState();
}

function applySidebarState() {
  elements.body.classList.toggle("sidebar-collapsed", state.sidebarCollapsed);
  const label = t(state.sidebarCollapsed ? "expandSidebar" : "collapseSidebar");
  elements.sidebarCollapse.setAttribute("aria-label", label);
  elements.sidebarCollapse.setAttribute("title", label);
  requestAnimationFrame(updateMobileReaderTop);
}

function applySidebarWidth() {
  if (!state.sidebarCollapsed) {
    state.sidebarWidth = clampSidebarWidth(state.sidebarWidth);
  }
  elements.body.style.setProperty("--sidebar-width", `${state.sidebarWidth}px`);
}

function startSidebarResize(event) {
  if (state.sidebarCollapsed) return;
  event.preventDefault();
  if (event.pointerId !== undefined) event.currentTarget?.setPointerCapture?.(event.pointerId);
  elements.body.classList.add("sidebar-resizing");
  const startX = event.clientX;
  const startWidth = state.sidebarWidth;
  const moveEventName = event.type === "mousedown" ? "mousemove" : "pointermove";
  const upEventName = event.type === "mousedown" ? "mouseup" : "pointerup";
  const onMove = (moveEvent) => {
    state.sidebarWidth = clampSidebarWidth(startWidth + moveEvent.clientX - startX);
    applySidebarWidth();
  };
  const onUp = () => {
    elements.body.classList.remove("sidebar-resizing");
    setStored("sidebar-width", String(state.sidebarWidth));
    window.removeEventListener(moveEventName, onMove);
    window.removeEventListener(upEventName, onUp);
    window.removeEventListener("pointercancel", onUp);
    window.removeEventListener("blur", onUp);
    event.currentTarget?.removeEventListener?.("lostpointercapture", onUp);
  };
  window.addEventListener(moveEventName, onMove);
  window.addEventListener(upEventName, onUp);
  window.addEventListener("pointercancel", onUp);
  window.addEventListener("blur", onUp);
  event.currentTarget?.addEventListener?.("lostpointercapture", onUp, { once: true });
}

function getInitialFavoriteFilter() {
  return getStored("only-favorites") === "true";
}

function setViewMode(mode) {
  if (mode !== "cards" && mode !== "list") return;
  state.viewMode = mode;
  setStored("view-mode", mode);
  applyViewMode();
  renderGrid();
}

function openAiPanel() {
  state.aiPanelOpen = true;
  applyAiPanelState();
  renderAiContext();
  renderInitialAiMessage();
  restoreLatestAiConversationForCurrentContext();
  loadAiJobs();
  elements.aiChatInput.focus();
}

function closeAiPanel() {
  state.aiPanelOpen = false;
  state.aiHistoryOpen = false;
  resetAiConversationSession();
  applyAiPanelState();
}

function toggleAiPanel() {
  if (state.aiPanelOpen) {
    closeAiPanel();
  } else {
    openAiPanel();
  }
}

function applyAiPanelState() {
  state.aiPanelWidth = clampAiPanelWidth(state.aiPanelWidth);
  elements.aiPanel.hidden = false;
  elements.aiPanel.setAttribute("aria-hidden", String(!state.aiPanelOpen));
  elements.aiPanel.style.width = `${state.aiPanelWidth}px`;
  elements.body.style.setProperty("--ai-panel-width", `${state.aiPanelWidth}px`);
  elements.body.classList.toggle("ai-panel-open", state.aiPanelOpen);
  elements.aiPanelOpen.classList.toggle("active", state.aiPanelOpen);
  if (elements.aiSendButton && !elements.aiSendButton.innerHTML.trim()) elements.aiSendButton.innerHTML = enterArrowIcon();
  applyAiComposerHeight();
  renderAiToolbarActions();
  applySidebarWidth();
}

function applyAiComposerHeight() {
  if (!elements.aiComposer) return;
  state.aiComposerHeight = clampAiComposerHeight(state.aiComposerHeight);
  elements.aiComposer.style.setProperty("--ai-composer-height", `${state.aiComposerHeight}px`);
}

function renderAiContext() {
  const detailed = getAiContextLabel({ compact: false });
  if (elements.aiContextLabel) elements.aiContextLabel.textContent = detailed;
  renderAiCompactContext();
  updateAiPanelConversationState();
  restoreLatestAiConversationForCurrentContext();
}

function renderAiCompactContext() {
  if (!elements.aiContextCompact) return;
  const parts = getAiCompactContextParts();
  elements.aiContextCompact.replaceChildren();
  if (parts.prefix) {
    const prefix = document.createElement("span");
    prefix.className = "ai-context-prefix";
    prefix.textContent = parts.prefix;
    elements.aiContextCompact.append(prefix);
  }
  const value = document.createElement("span");
  value.className = "ai-context-value";
  value.textContent = parts.value;
  value.title = parts.title || parts.value;
  elements.aiContextCompact.append(value);
}

function getAiCompactContextParts() {
  const manualItems = [...state.manualAiContextIds].map(getItemById).filter(Boolean);
  if (manualItems.length > 0) {
    return { value: t("aiContextManualCount", { count: manualItems.length }) };
  }
  if (state.currentReaderItemId) {
    const item = getItemById(state.currentReaderItemId);
    return {
      prefix: aiContextPrefix("aiContextReader"),
      value: item ? getItemTitle(item) : t("item"),
    };
  }
  return { value: getAiContextLabel({ compact: true }) };
}

function aiContextPrefix(key) {
  const marker = "__HTML_LORE_CONTEXT_VALUE__";
  const translated = t(key, { title: marker, name: marker, query: marker });
  return translated.includes(marker) ? translated.split(marker)[0] : "";
}

function getAiContextLabel(options = {}) {
  const compact = Boolean(options.compact);
  const manualItems = [...state.manualAiContextIds].map(getItemById).filter(Boolean);
  if (manualItems.length > 0) {
    if (compact) return t("aiContextManualCount", { count: manualItems.length });
    return t("aiContextManualItems", { titles: manualItems.map((item) => getItemTitle(item)).join(", ") });
  }

  const parts = [];
  let primaryCollection = "";
  let primaryTag = "";
  if (state.currentReaderItemId) {
    const item = getItemById(state.currentReaderItemId);
    parts.push(t("aiContextReader", { title: item ? getItemTitle(item) : t("item") }));
  } else if (state.query.trim()) {
    parts.push(t("aiContextSearch", { query: state.query.trim() }));
  } else if (state.filter.type === "library") {
    const filter = libraryFilterDefinitions.find((item) => item.value === state.filter.value);
    parts.push(state.filter.value === "all" ? t("aiContextGlobal") : t("aiContextLibrary", { name: filter ? t(filter.labelKey) : state.filter.value }));
  } else if (state.filter.type === "collection") {
    primaryCollection = state.filter.value;
    parts.push(t("aiContextCollection", { name: state.filter.value }));
  } else if (state.filter.type === "tag") {
    primaryTag = state.filter.value;
    parts.push(t("aiContextTag", { name: state.filter.value }));
  } else {
    parts.push(t("aiContextGlobal"));
  }

  const extraTags = [...state.selectedTags].filter((name) => name !== primaryTag);
  if (extraTags.length > 0) {
    if (compact && extraTags.length > 1) {
      parts.push(t("aiContextTagSummary", { first: `#${extraTags[0]}`, count: extraTags.length }));
    } else {
      const mode = t(state.tagMatchMode === "all" ? "tagMatchModeAllLabel" : "tagMatchModeAnyLabel");
      parts.push(t("aiContextTags", { mode, names: extraTags.map((tag) => `#${tag}`).join(", ") }));
    }
  }

  if (state.onlyFavorites) {
    parts.push(t("aiContextFavoritesOnly"));
  }
  return parts.join(" · ");
}

function renderInitialAiMessage() {
  updateAiPanelConversationState();
}

function appendAiMessage(role, text, sources = [], options = {}) {
  const message = document.createElement("article");
  message.className = `ai-message ${role}${options.pending ? " pending" : ""}`;
  message.innerHTML = options.pending ? aiPendingMessageMarkup() : aiMessageMarkup(role, text, sources);
  elements.aiChatLog.append(message);
  updateAiPanelConversationState();
  scrollAiChatToBottom();
  return message;
}

function updateAiMessage(message, role, text, sources = []) {
  message.className = `ai-message ${role}`;
  message.innerHTML = aiMessageMarkup(role, text, sources);
  updateAiPanelConversationState();
  scrollAiChatToBottom();
}

function aiMessageMarkup(role, text, sources = []) {
  const displaySources = dedupeAiSources(sources);
  const sourceMarkup = role === "assistant" && displaySources.length > 0
    ? `<div class="ai-message-sources"><span>${escapeHtml(t("aiSources"))}</span>${displaySources.slice(0, 4).map(renderAiSourcePill).join("")}</div>`
    : "";
  const bodyMarkup = role === "assistant"
    ? renderMarkdown(stripAssistantSourceFooter(text, displaySources))
    : `<p>${escapeHtml(text)}</p>`;
  return `
    <strong>${escapeHtml(role === "user" ? t("aiUserPlaceholder") : t("aiConversation"))}</strong>
    <div class="ai-message-body">${bodyMarkup}</div>
    ${sourceMarkup}
  `;
}

function dedupeAiSources(sources = []) {
  const result = [];
  const seen = new Set();
  sources.forEach((source) => {
    const key = source?.kind === "external"
      ? `external:${String(source?.url || source?.title || "").trim().toLowerCase()}`
      : `local:${String(source?.item_id || source?.title || "").trim().toLowerCase()}`;
    if (!key || seen.has(key)) return;
    seen.add(key);
    result.push(source);
  });
  return result;
}

function aiPendingMessageMarkup() {
  return `
    <strong>${escapeHtml(t("aiConversation"))}</strong>
    <div class="ai-message-body">
      <p class="ai-typing">${escapeHtml(t("aiReplying").replace(/[.。…]+$/u, ""))}<span class="ai-typing-dots" aria-hidden="true"><span></span><span></span><span></span></span></p>
    </div>
  `;
}

function stripAssistantSourceFooter(text, sources = []) {
  const value = String(text ?? "").trimEnd();
  if (!sources.length || !value) return value;
  return value
    .replace(/(?:\n|\s)*(?:来源|Sources?|出典)\s*[:：]\s*(?:\[[0-9,\s，]+\][^\n]*(?:[;；]\s*)?)+\s*$/iu, "")
    .trimEnd();
}

function updateAiPanelConversationState() {
  const hasMessages = Boolean(elements.aiChatLog?.children.length);
  const hasHistory = state.aiHistoryLoaded && Array.isArray(state.aiHistory) && state.aiHistory.length > 0 && state.aiHistoryContextKey === getAiHistoryContextKey();
  elements.aiPanel?.classList.toggle("has-ai-messages", hasMessages);
  elements.aiPanel?.classList.toggle("has-ai-history", hasHistory || state.aiHistoryOpen);
  if (elements.aiContextCard) elements.aiContextCard.hidden = hasMessages;
}

function renderAiSourcePill(source) {
  const external = source?.kind === "external";
  const label = t(external ? "aiSourceExternal" : "aiSourceLocal");
  const title = sourceDisplayTitle(source);
  const content = `<span>${escapeHtml(label)}</span><b>${escapeHtml(title)}</b>`;
  if (external && source?.url) {
    return `<a class="external" href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer" title="${escapeHtml(title)}">${content}</a>`;
  }
  return `<em class="${external ? "external" : "local"}" title="${escapeHtml(title)}">${content}</em>`;
}

function sourceDisplayTitle(source) {
  if (!source) return "";
  if (source.kind === "external" && source.url) {
    try {
      const host = new URL(source.url).hostname;
      return `${source.title || host} · ${host}`;
    } catch {
      return source.title || source.url || "";
    }
  }
  return source.title || source.item_id || "";
}

function renderMarkdown(value) {
  const text = String(value ?? "").replace(/\r\n?/g, "\n");
  if (!text.trim()) return "<p></p>";
  const blocks = [];
  const lines = text.split("\n");
  let paragraph = [];
  let list = null;
  let quote = [];
  let code = [];
  let inCode = false;

  const flushParagraph = () => {
    if (paragraph.length === 0) return;
    blocks.push(`<p>${renderInlineMarkdown(paragraph.join(" "))}</p>`);
    paragraph = [];
  };
  const flushList = () => {
    if (!list) return;
    blocks.push(`<${list.type}>${list.items.map((item) => `<li>${renderInlineMarkdown(item)}</li>`).join("")}</${list.type}>`);
    list = null;
  };
  const appendListContinuation = (line) => {
    if (!list?.items.length) return false;
    const attachAfterBlank = /^(目标|证据|例如|重点|说明|原因|建议|步骤|方法|风险|收益|价值|结论|可以|可|是|要|让|对|寻找|引入|探索|匹配|设计|重点沟通|核心)/.test(line);
    const previousLooksLikeLabel = /^(\*\*)?[^。！？.!?]{2,80}(\*\*)?$/.test(list.items[list.items.length - 1] || "");
    if (!list.hadBlank || attachAfterBlank || previousLooksLikeLabel) {
      list.items[list.items.length - 1] = `${list.items[list.items.length - 1]} ${line}`;
      list.hadBlank = false;
      return true;
    }
    return false;
  };
  const flushQuote = () => {
    if (quote.length === 0) return;
    blocks.push(`<blockquote>${renderInlineMarkdown(quote.join(" "))}</blockquote>`);
    quote = [];
  };
  const flushCode = () => {
    if (code.length === 0) return;
    blocks.push(`<pre><code>${escapeHtml(code.join("\n"))}</code></pre>`);
    code = [];
  };
  const flushTextBlocks = () => {
    flushParagraph();
    flushList();
    flushQuote();
  };

  lines.forEach((line) => {
    if (/^```/.test(line.trim())) {
      if (inCode) {
        flushCode();
        inCode = false;
      } else {
        flushTextBlocks();
        inCode = true;
      }
      return;
    }
    if (inCode) {
      code.push(line);
      return;
    }

    const trimmed = line.trim();
    if (!trimmed) {
      if (list) list.hadBlank = true;
      else flushTextBlocks();
      return;
    }

    const heading = trimmed.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      flushTextBlocks();
      const level = heading[1].length + 2;
      blocks.push(`<h${level}>${renderInlineMarkdown(heading[2])}</h${level}>`);
      return;
    }

    const unordered = trimmed.match(/^[-*]\s+(.+)$/);
    const ordered = trimmed.match(/^\d+[.)]\s+(.+)$/);
    if (unordered || ordered) {
      flushParagraph();
      flushQuote();
      const type = unordered ? "ul" : "ol";
      if (!list || list.type !== type) flushList();
      if (!list) list = { type, items: [] };
      list.items.push((unordered || ordered)[1]);
      list.hadBlank = false;
      return;
    }

    const quoted = trimmed.match(/^>\s?(.+)$/);
    if (quoted) {
      flushParagraph();
      flushList();
      quote.push(quoted[1]);
      return;
    }

    if (appendListContinuation(trimmed)) return;
    flushList();
    flushQuote();
    paragraph.push(trimmed);
  });

  if (inCode) flushCode();
  flushTextBlocks();
  return blocks.join("");
}

function renderInlineMarkdown(value) {
  let html = escapeHtml(value);
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+|mailto:[^)\s]+)\)/g, (_match, label, href) => {
    const safeHref = escapeHtml(href);
    return `<a href="${safeHref}" target="_blank" rel="noreferrer">${label}</a>`;
  });
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/__([^_]+)__/g, "<strong>$1</strong>");
  html = html.replace(/(^|[\s(])\*([^*\n]+)\*/g, "$1<em>$2</em>");
  html = html.replace(/(^|[\s(])_([^_\n]+)_/g, "$1<em>$2</em>");
  return html;
}

function scrollAiChatToBottom() {
  elements.aiChatLog.scrollTop = elements.aiChatLog.scrollHeight;
}

async function submitAiMessage(event) {
  event.preventDefault();
  const text = elements.aiChatInput.value.trim();
  if (!text) return;
  appendAiMessage("user", text);
  elements.aiChatInput.value = "";
  autoGrowAiChatInput();
  const pendingMessage = appendAiMessage("assistant", t("aiReplying"), [], { pending: true });
  try {
    if (hasRuntimeConfig("STATIC_DEMO")) {
      await new Promise((resolve) => setTimeout(resolve, 250));
      updateAiMessage(pendingMessage, "assistant", t("aiAssistantPlaceholder"));
      return;
    }
    const conversationId = await ensureAiConversation();
    const response = await apiFetch(`/api/ai/conversations/${encodeURIComponent(conversationId)}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        content: text,
        source_mode: state.aiContentExpansion ? "local_plus_external" : "local_only",
      }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Agent returned ${response.status}`);
    updateAiMessage(pendingMessage, "assistant", data.message?.content || t("aiAssistantPlaceholder"), data.sources || []);
    await loadAiRuns();
  } catch (error) {
    updateAiMessage(pendingMessage, "assistant", error?.message || t("aiMessageFailed"));
    await loadAiRuns();
    console.error(error);
  }
}

function autoGrowAiChatInput() {
  const input = elements.aiChatInput;
  if (!input) return;
  input.scrollTop = input.scrollHeight;
}

function handleAiChatInputKeydown(event) {
  if (event.key !== "Enter" || event.shiftKey || !state.aiPanelOpen) return;
  event.preventDefault();
  elements.aiChatForm.requestSubmit();
}

async function ensureAiConversation() {
  const payload = buildAiContextPayload();
  const contextKey = getAiContextKey(payload);
  if (state.aiConversationId && state.aiConversationContextKey === contextKey) {
    return state.aiConversationId;
  }
  const response = await apiFetch("/api/ai/conversations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Agent returned ${response.status}`);
  state.aiConversationId = data.conversation?.id || "";
  state.aiConversationContextKey = data.conversation?.context_key || contextKey;
  state.aiConversationLoadedKey = state.aiConversationContextKey;
  state.aiSuppressedContextKeys.delete(contextKey);
  state.aiHistoryLoaded = false;
  if (!state.aiConversationId) throw new Error(t("aiMessageFailed"));
  return state.aiConversationId;
}

function buildAiContextPayload() {
  const manualItemIds = [...state.manualAiContextIds];
  const context = {
    include_archived: false,
    favorite: state.onlyFavorites ? true : null,
    tags: [...state.selectedTags],
    tag_match: state.tagMatchMode,
    q: state.query.trim(),
    sort: state.sortMode,
  };
  if (manualItemIds.length > 0) {
    context.manual_item_ids = manualItemIds;
  } else if (state.currentReaderItemId) {
    context.item_id = state.currentReaderItemId;
  } else if (state.filter.type === "library") {
    context.scope = state.filter.value === "all" ? "global" : "library";
    context.library = state.filter.value;
  } else if (state.filter.type === "collection") {
    context.scope = "collection";
    context.collection = state.filter.value;
  } else if (state.filter.type === "tag") {
    context.scope = "tag";
    context.tags = [...new Set([state.filter.value, ...context.tags])];
  } else {
    context.scope = "global";
    context.library = "all";
  }
  return {
    source_mode: state.aiContentExpansion ? "local_plus_external" : "local_only",
    context,
  };
}

function getAiContextKey(payload = buildAiContextPayload()) {
  const context = payload.context || {};
  const tags = [...new Set(context.tags || [])].map(String).sort();
  if (context.manual_item_ids?.length) {
    return `manual:${compactJson({ item_ids: [...context.manual_item_ids].map(String).sort() })}`;
  }
  if (context.item_id) {
    return `reader:${compactJson({ item_id: String(context.item_id) })}`;
  }
  const scope = context.scope || "global";
  return `${scope}:${compactJson({
    scope,
    q: context.q || "",
    library: context.library || "",
    collection: context.collection || "",
    tags,
    tag_match: context.tag_match || "any",
    favorite: context.favorite ?? null,
    include_archived: Boolean(context.include_archived),
    sort: context.sort || "newest",
  })}`;
}

function getAiHistoryContextKey() {
  return getAiContextKey(buildAiContextPayload());
}

function invalidateAiHistoryIfContextChanged() {
  const contextKey = getAiHistoryContextKey();
  if (state.aiHistoryContextKey === contextKey) return;
  state.aiHistory = [];
  state.aiHistoryLoaded = false;
  state.aiHistoryContextKey = contextKey;
  state.aiHistoryOpen = false;
  renderAiHistory();
  updateAiPanelConversationState();
  renderAiToolbarActions();
}

function compactJson(value) {
  if (Array.isArray(value)) return `[${value.map((item) => compactJson(item)).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${compactJson(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

function resetAiConversationSession(options = {}) {
  const clearMessages = options.clearMessages !== false;
  state.aiConversationId = "";
  state.aiConversationContextKey = "";
  state.aiConversationLoadedKey = "";
  state.aiConversationLoadingKey = "";
  if (clearMessages) {
    elements.aiChatLog.replaceChildren();
    updateAiPanelConversationState();
  }
}

async function restoreLatestAiConversationForCurrentContext() {
  if (!state.aiPanelOpen || !state.agentUrl) return;
  const payload = buildAiContextPayload();
  const contextKey = getAiContextKey(payload);
  if (state.aiSuppressedContextKeys.has(contextKey)) {
    resetAiConversationSession();
    state.aiConversationLoadedKey = contextKey;
    return;
  }
  if (state.aiConversationLoadedKey === contextKey || state.aiConversationLoadingKey === contextKey) return;
  resetAiConversationSession();
  state.aiConversationLoadingKey = contextKey;
  try {
    const response = await apiFetch(`/api/ai/conversations/latest?context_key=${encodeURIComponent(contextKey)}`, { cache: "no-store" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Agent returned ${response.status}`);
    if (state.aiConversationLoadingKey !== contextKey) return;
    if (data.conversation?.id) {
      await loadAiConversation(data.conversation);
    } else {
      resetAiConversationSession();
      state.aiConversationLoadedKey = contextKey;
    }
  } catch (error) {
    console.error(error);
    if (state.aiConversationLoadingKey === contextKey) {
      resetAiConversationSession();
      state.aiConversationLoadedKey = contextKey;
    }
  } finally {
    if (state.aiConversationLoadingKey === contextKey) state.aiConversationLoadingKey = "";
  }
}

async function loadAiConversation(conversation) {
  if (!conversation?.id || !state.agentUrl) return;
  const response = await apiFetch(`/api/ai/conversations/${encodeURIComponent(conversation.id)}/messages`, { cache: "no-store" });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Agent returned ${response.status}`);
  state.aiConversationId = conversation.id;
  state.aiConversationContextKey = conversation.context_key || "";
  state.aiConversationLoadedKey = state.aiConversationContextKey || getAiContextKey();
  if (state.aiConversationContextKey) state.aiSuppressedContextKeys.delete(state.aiConversationContextKey);
  renderAiConversationMessages(Array.isArray(data.messages) ? data.messages : []);
}

function renderAiConversationMessages(messages) {
  elements.aiChatLog.replaceChildren();
  messages.forEach((message) => {
    appendAiMessage(message.role === "user" ? "user" : "assistant", message.content || "", message.sources || []);
  });
  updateAiPanelConversationState();
  scrollAiChatToBottom();
}

function startNewAiConversation() {
  const contextKey = getAiContextKey();
  state.aiSuppressedContextKeys.add(contextKey);
  resetAiConversationSession();
  state.aiConversationLoadedKey = contextKey;
  state.aiHistoryOpen = false;
  renderAiHistory();
  renderAiToolbarActions();
  loadAiHistory({ keepClosed: true }).catch((error) => console.error(error));
}

function setAiContentExpansion(enabled) {
  if (hasRuntimeConfig("STATIC_DEMO")) {
    state.aiContentExpansion = false;
    if (elements.aiContentExpansion) elements.aiContentExpansion.checked = false;
    return;
  }
  state.aiContentExpansion = Boolean(enabled);
}

function applyStaticDemoMode() {
  if (!hasRuntimeConfig("STATIC_DEMO")) return;
  const disabledTitle = t("staticDemoUnavailable");
  state.aiContentExpansion = false;
  if (elements.aiContentExpansion) {
    elements.aiContentExpansion.checked = false;
    elements.aiContentExpansion.disabled = true;
    elements.aiContentExpansion.closest(".ai-source-toggle")?.classList.add("ai-source-toggle-disabled");
    elements.aiContentExpansion.closest(".ai-source-toggle")?.setAttribute("title", disabledTitle);
  }
  const deepResearch = document.querySelector("#ai-deep-research");
  if (deepResearch) {
    deepResearch.disabled = true;
    deepResearch.closest(".ai-source-toggle")?.classList.add("ai-source-toggle-disabled");
  }
  if (elements.aiGenerateNote) {
    elements.aiGenerateNote.disabled = true;
    elements.aiGenerateNote.title = disabledTitle;
  }
}

function openGenerateNoteDialog() {
  elements.generateTheme.value = "default";
  elements.generateTargetUse.value = "default";
  elements.generateAudience.value = "default";
  elements.generateStylePreference.value = "default";
  elements.generateNoteFeedback.textContent = state.agentUrl ? "" : t("generateNoteNeedsAgent");
  elements.generateNoteDialog.hidden = false;
  elements.generateTheme.focus();
}

function closeGenerateNoteDialog() {
  elements.generateNoteDialog.hidden = true;
  elements.generateNoteFeedback.textContent = "";
  elements.generateNoteSubmit.disabled = false;
}

async function submitGenerateNoteDialog(event) {
  event.preventDefault();
  if (!state.agentUrl) {
    elements.generateNoteFeedback.textContent = t("generateNoteNeedsAgent");
    return;
  }
  elements.generateNoteSubmit.disabled = true;
  elements.generateNoteFeedback.textContent = t("generateNoteRunning");
  try {
    const conversationId = await ensureAiConversation();
    const response = await apiFetch(`/api/ai/conversations/${encodeURIComponent(conversationId)}/generate-note/jobs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        theme: elements.generateTheme.value,
        target_use: elements.generateTargetUse.value,
        audience: elements.generateAudience.value,
        style_preference: elements.generateStylePreference.value,
      }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Agent returned ${response.status}`);
    trackSubmittedAiJob(data.job_id || "");
    await loadAiJobs();
    startAiJobPolling();
    elements.generateNoteFeedback.textContent = t("aiJobQueued", { jobId: data.job_id || "" });
  } catch (error) {
    await loadAiRuns();
    elements.generateNoteFeedback.textContent = error?.message || t("generateNoteFailed");
    console.error(error);
  } finally {
    elements.generateNoteSubmit.disabled = false;
  }
}

function toggleMultiFilterPopover() {
  state.multiFilterOpen = !state.multiFilterOpen;
  applyMultiFilterState();
}

function closeMultiFilterPopover() {
  state.multiFilterOpen = false;
  applyMultiFilterState();
}

function toggleSortPopover() {
  state.sortOpen = !state.sortOpen;
  applySortState();
}

function closeSortPopover() {
  state.sortOpen = false;
  applySortState();
}

function uploadAvatar(file) {
  if (!file) return;
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    state.profile.avatarType = "image";
    state.profile.avatarImage = String(reader.result || "");
    saveProfile();
    renderProfile();
  });
  reader.readAsDataURL(file);
}

function applyMultiFilterState() {
  elements.multiFilterPopover.hidden = !state.multiFilterOpen;
  elements.multiFilterToggle.classList.toggle("open", state.multiFilterOpen);
  elements.multiFilterToggle.classList.toggle("active", hasMultiFilters());
  elements.tagMatchButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.tagMatchMode === state.tagMatchMode);
  });
}

function applySortState() {
  elements.sortPopover.hidden = !state.sortOpen;
  elements.sortToggle.classList.toggle("active", state.sortOpen || state.sortMode !== "newest");
  elements.sortButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.sortMode === state.sortMode);
  });
}

function setSortMode(mode) {
  if (!["newest", "oldest", "title-az", "title-za"].includes(mode)) return;
  state.sortMode = mode;
  state.sortOpen = false;
  setStored("sort-mode", mode);
  applySortState();
  renderGrid();
}

function hasMultiFilters() {
  return state.selectedTags.size > 0;
}

function setTagMatchMode(mode) {
  if (mode !== "any" && mode !== "all") return;
  state.tagMatchMode = mode;
  applyMultiFilterState();
  renderMultiFilterOptions();
  renderGrid();
  renderAiContext();
}

function renderMultiFilterOptions() {
  const baseItems = baseItemsForTagFilters();
  const resultItems = applySelectedTagFilters(baseItems);
  if (elements.multiFilterResultCount) {
    elements.multiFilterResultCount.textContent = t("tagFilterSelectedCount", { count: resultItems.length });
  }
  elements.multiTagOptions.replaceChildren(...getTagOptions()
    .filter((tag) => isManagedItemVisible("tags", tag.name))
    .map((tag) => ({
      ...tag,
      baseCount: countTagItemsInScope(tag.name, baseItems),
      count: countMultiFilterTagItems(tag.name, baseItems, resultItems),
    }))
    .filter((tag) => tag.baseCount > 0)
    .map((tag) => multiFilterOption(tag.name, tag.count)));
  applyMultiFilterState();
}

function countMultiFilterTagItems(name, baseItems, resultItems) {
  const scope = state.tagMatchMode === "all" && state.selectedTags.size > 0 ? resultItems : baseItems;
  return countTagItemsInScope(name, scope);
}

function countTagItemsInScope(name, items) {
  return items.filter((item) => getItemTags(item).includes(name)).length;
}

function multiFilterOption(name, count) {
  const selected = state.selectedTags.has(name);
  const label = document.createElement("label");
  label.className = "multi-filter-option";
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = selected;
  checkbox.addEventListener("change", () => {
    toggleMultiFilterValue(name);
  });
  const text = document.createElement("span");
  text.textContent = `#${name}`;
  const badge = document.createElement("span");
  badge.className = "multi-filter-count";
  badge.textContent = count;
  label.append(checkbox, text, badge);
  return label;
}

function toggleMultiFilterValue(name) {
  if (state.selectedTags.has(name)) {
    state.selectedTags.delete(name);
  } else {
    state.selectedTags.add(name);
  }
  renderCollectionNav();
  renderTagNav();
  renderMultiFilterOptions();
  renderGrid();
  renderAiContext();
}

function clearMultiFilters(shouldRender = true) {
  state.selectedTags.clear();
  if (!shouldRender) return;
  renderCollectionNav();
  renderTagNav();
  renderMultiFilterOptions();
  renderGrid();
  renderAiContext();
}

function startAiPanelResize(event) {
  event.preventDefault();
  if (event.pointerId !== undefined) event.currentTarget?.setPointerCapture?.(event.pointerId);
  elements.body.classList.add("ai-panel-resizing");
  const panelBox = elements.aiPanel.getBoundingClientRect();
  const startX = event.clientX;
  const startWidth = panelBox.width;
  const moveEventName = event.type === "mousedown" ? "mousemove" : "pointermove";
  const upEventName = event.type === "mousedown" ? "mouseup" : "pointerup";
  const onMove = (moveEvent) => {
    state.aiPanelWidth = clampAiPanelWidth(startWidth + startX - moveEvent.clientX);
    applyAiPanelState();
  };
  const onUp = () => {
    elements.body.classList.remove("ai-panel-resizing");
    setStored("ai-panel-width", String(state.aiPanelWidth));
    window.removeEventListener(moveEventName, onMove);
    window.removeEventListener(upEventName, onUp);
    window.removeEventListener("pointercancel", onUp);
    window.removeEventListener("blur", onUp);
    event.currentTarget?.removeEventListener?.("lostpointercapture", onUp);
  };
  window.addEventListener(moveEventName, onMove);
  window.addEventListener(upEventName, onUp);
  window.addEventListener("pointercancel", onUp);
  window.addEventListener("blur", onUp);
  event.currentTarget?.addEventListener?.("lostpointercapture", onUp, { once: true });
}

function startAiComposerResize(event) {
  event.preventDefault();
  if (event.pointerId !== undefined) event.currentTarget?.setPointerCapture?.(event.pointerId);
  elements.body.classList.add("ai-composer-resizing");
  const startY = event.clientY;
  const startHeight = state.aiComposerHeight;
  const moveEventName = event.type === "mousedown" ? "mousemove" : "pointermove";
  const upEventName = event.type === "mousedown" ? "mouseup" : "pointerup";
  const onMove = (moveEvent) => {
    state.aiComposerHeight = clampAiComposerHeight(startHeight + startY - moveEvent.clientY);
    applyAiComposerHeight();
  };
  const onUp = () => {
    elements.body.classList.remove("ai-composer-resizing");
    setStored("ai-composer-height", String(state.aiComposerHeight));
    window.removeEventListener(moveEventName, onMove);
    window.removeEventListener(upEventName, onUp);
    if (event.type !== "mousedown") window.removeEventListener("pointercancel", onUp);
    window.removeEventListener("blur", onUp);
    event.currentTarget?.removeEventListener?.("lostpointercapture", onUp);
  };
  window.addEventListener(moveEventName, onMove);
  window.addEventListener(upEventName, onUp);
  if (event.type !== "mousedown") window.addEventListener("pointercancel", onUp);
  window.addEventListener("blur", onUp);
  event.currentTarget?.addEventListener?.("lostpointercapture", onUp, { once: true });
}

function toggleFavoriteFilter() {
  state.onlyFavorites = !state.onlyFavorites;
  setStored("only-favorites", String(state.onlyFavorites));
  applyFavoriteFilter();
  renderGrid();
  renderAiContext();
}

function applyFavoriteFilter() {
  elements.favoriteFilter.classList.toggle("active", state.onlyFavorites);
  const label = t(state.onlyFavorites ? "showAllFavorites" : "onlyFavorites");
  elements.favoriteFilter.setAttribute("aria-label", label);
  elements.favoriteFilter.setAttribute("title", label);
}

function applyViewMode() {
  state.viewMode = "cards";
  elements.contentGrid.classList.remove("list-view");
}

function setThemeMode(mode) {
  if (!["system", "light", "dark"].includes(mode)) return;
  state.themeMode = mode;
  setStored("theme", mode);
  applyTheme();
}

function applyTheme() {
  const resolvedTheme = getResolvedTheme();
  document.documentElement.dataset.theme = resolvedTheme;
  document.documentElement.dataset.themeMode = state.themeMode;
  elements.themeModeButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.themeMode === state.themeMode);
  });
  updateThemeMetaColor(resolvedTheme);
}

function getResolvedTheme() {
  return state.themeMode === "system" ? getSystemTheme() : state.themeMode;
}

function getSystemTheme() {
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function updateThemeMetaColor(resolvedTheme) {
  document.querySelector('meta[name="theme-color"]')?.setAttribute("content", resolvedTheme === "dark" ? "#111827" : "#0f766e");
}

function loadAiConfig() {
  try {
    return JSON.parse(getStored("ai-config") || "{}");
  } catch {
    return {};
  }
}

function loadDataConfig() {
  try {
    return JSON.parse(getStored("data-config") || "{}");
  } catch {
    return {};
  }
}

function loadProfile() {
  try {
    return {
      avatarType: "brand",
      avatarImage: "",
      ...JSON.parse(getStored("profile") || "{}"),
    };
  } catch {
    return { avatarType: "brand", avatarImage: "" };
  }
}

function saveProfile() {
  setStored("profile", JSON.stringify(state.profile));
}

function renderProfile() {
  const username = state.currentUser.username || "Guest";
  const dataId = state.currentUser.dataId || "static";
  renderAvatar(elements.settingsProfileAvatar, true);
  if (elements.settingsProfileName) elements.settingsProfileName.textContent = username;
  if (elements.settingsProfileId) elements.settingsProfileId.textContent = `ID: ${dataId}`;
}

function renderAvatar(target, large) {
  if (!target) return;
  if (state.profile.avatarType === "image" && state.profile.avatarImage) {
    target.innerHTML = `<img src="${escapeHtml(state.profile.avatarImage)}" alt="">`;
    return;
  }
  target.innerHTML = `<img src="assets/html-lore-logo.svg" alt="">`;
}

function loadItemState() {
  try {
    return JSON.parse(getStored("item-state") || "{}");
  } catch {
    return {};
  }
}

function saveItemState() {
  setStored("item-state", JSON.stringify(state.itemState));
}

function loadNavConfig() {
  try {
    return JSON.parse(getStored("nav-config") || '{"library":{},"collections":{},"tags":{}}');
  } catch {
    return { library: {}, collections: {}, tags: {} };
  }
}

async function loadRemoteNavConfig() {
  if (!state.agentUrl) return;
  try {
    const response = await apiFetch("/api/navigation", { cache: "no-store" });
    if (!response.ok) throw new Error(`Agent returned ${response.status}`);
    state.navConfig = normalizeNavConfig(await response.json());
    saveNavConfig();
  } catch (error) {
    console.error(error);
  }
}

function saveNavConfig() {
  setStored("nav-config", JSON.stringify(state.navConfig));
}

async function persistNavConfig() {
  saveNavConfig();
  if (!state.agentUrl) return;
  try {
    const response = await apiFetch("/api/navigation", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(normalizeNavConfig(state.navConfig)),
    });
    if (!response.ok) throw new Error(`Agent returned ${response.status}`);
    state.navConfig = normalizeNavConfig(await response.json());
    saveNavConfig();
  } catch (error) {
    setFeedback("navigationSaveFailed");
    console.error(error);
  }
}

function normalizeNavConfig(config) {
  return {
    library: config?.library || {},
    collections: config?.collections || {},
    tags: config?.tags || {},
  };
}

function getManagedItemConfig(type, name) {
  state.navConfig[type] ||= {};
  state.navConfig[type][name] ||= { visible: true };
  return state.navConfig[type][name];
}

function isManagedItemVisible(type, name) {
  const config = getManagedItemConfig(type, name);
  return config.visible !== false;
}

function renderManagementLists() {
  renderLibraryManagement();
  renderManagementList("collections", getCollectionOptions(), elements.collectionManagement);
  renderManagementList("tags", getTagOptions(), elements.tagManagement);
}

function renderLibraryManagement() {
  const rows = libraryFilterDefinitions.map((filter) => {
    return {
      name: filter.value,
      label: t(filter.labelKey),
      count: countLibraryFilter(filter.value),
    };
  });
  elements.libraryManagement.replaceChildren(...rows.map((item) => renderManagementRow("library", item.name, item.count, item.label)));
}

function renderManagementList(type, items, container) {
  const actions = renderManagementActions(type);
  const rows = items.map((item) => {
    const count = type === "collections" ? countCollectionItems(item.name) : type === "tags" ? countTagItems(item.name) : item.count;
    return renderManagementRow(type, item.name, count);
  });
  container.replaceChildren(actions, ...rows);
}

function renderManagementActions(type) {
  const panel = document.createElement("div");
  panel.className = "management-actions-panel";
  panel.innerHTML = `
    <p>${escapeHtml(t("managementStaticNote"))}</p>
    <div>
      <input type="text" disabled value="" placeholder="${escapeHtml(type === "collections" ? t("addCollection") : t("addTag"))}">
      <button type="button" disabled>${escapeHtml(type === "collections" ? t("addCollection") : t("addTag"))}</button>
    </div>
  `;
  return panel;
}

function renderManagementRow(type, name, count, label = name) {
  const config = getManagedItemConfig(type, name);
  const row = document.createElement("div");
  row.className = "management-row";
  const actions = type === "library" ? "" : `
    <div class="management-actions">
      <button type="button" disabled title="${escapeHtml(t("requiresWriter"))}">${escapeHtml(t("rename"))}</button>
      <button type="button" disabled title="${escapeHtml(t("requiresWriter"))}">${escapeHtml(t("merge"))}</button>
      <button type="button" disabled title="${escapeHtml(t("requiresWriter"))}">${escapeHtml(t("delete"))}</button>
    </div>
  `;
  row.classList.toggle("management-row-compact", type === "library");
  row.innerHTML = `
    <div class="management-name">
      <strong>${escapeHtml(label)}</strong>
      <span>${count}</span>
    </div>
    <label class="switch-row">
      <input type="checkbox" ${config.visible === false ? "" : "checked"} data-management-visible>
      <span>${escapeHtml(t("visible"))}</span>
    </label>
    ${actions}
  `;
  row.querySelector("[data-management-visible]").addEventListener("change", async (event) => {
    getManagedItemConfig(type, name).visible = event.target.checked;
    await persistNavConfig();
    renderLibraryNav();
    renderCollectionNav();
    renderTagNav();
  });
  return row;
}

function renderAiConfig() {
  const config = state.aiConfig || {};
  elements.aiProvider.value = config.provider || "openai-compatible";
  elements.currentModel.value = config.currentModel || config.model || "";
  elements.apiBaseUrl.value = config.apiBaseUrl || config.base_url || "";
  elements.newModel.value = config.newModel || "";
  elements.modelTemperature.value = config.temperature || "0.7";
  elements.modelMaxTokens.value = config.maxTokens || "4096";
  elements.apiKey.value = "";
}

function maybeRefreshAiRuns() {
  if (state.activeSettingsTab !== "ai-runs") return;
  loadAiRuns();
}

function maybeRefreshAiGenerationHistory() {
  if (state.activeSettingsTab !== "ai-generation-history") return;
  loadAiGenerationHistory();
}

function maybeRefreshAiConversations() {
  if (state.activeSettingsTab !== "ai-conversations") return;
  loadAiConversationManagement();
}

async function loadAiJobs() {
  if (!elements.aiJobList || !state.agentUrl) {
    state.aiJobs = [];
    renderAiJobs();
    return;
  }
  try {
    const response = await apiFetch("/api/ai/jobs?limit=20", { cache: "no-store" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Agent returned ${response.status}`);
    const previous = new Set(state.aiJobs.map((job) => `${job.job_id}:${job.status}`));
    const wasLoaded = state.aiJobsLoaded;
    state.aiJobs = Array.isArray(data.jobs) ? data.jobs : [];
    renderAiJobs();
    if (state.activeSettingsTab === "ai-generation-history") renderAiGenerationHistory();
    if (!wasLoaded) {
      state.aiJobs.filter((job) => job.status === "completed").forEach((job) => state.aiKnownCompletedJobIds.add(job.job_id));
    }
    const completedNow = state.aiJobs.filter((job) => {
      if (job.status !== "completed" || state.aiKnownCompletedJobIds.has(job.job_id)) return false;
      return wasLoaded || state.aiSubmittedJobIds.has(job.job_id);
    });
    const failedNow = wasLoaded ? state.aiJobs.filter((job) => job.status === "failed" && !previous.has(`${job.job_id}:failed`)) : [];
    state.aiJobsLoaded = true;
    completedNow.forEach((job) => state.aiKnownCompletedJobIds.add(job.job_id));
    completedNow.forEach((job) => state.aiSubmittedJobIds.delete(job.job_id));
    if (completedNow.length > 0) {
      await refreshManifestAndWorkspace();
      await loadAiRuns();
    }
    if (failedNow.length > 0 && elements.generateNoteFeedback) {
      elements.generateNoteFeedback.textContent = t("aiJobFailed", { message: failedNow[0].error?.message || failedNow[0].message || failedNow[0].job_id });
    }
    if (hasActiveAiJobs()) startAiJobPolling();
    else stopAiJobPolling();
  } catch (error) {
    console.error(error);
  }
}

function toggleAiJobs() {
  state.aiJobsOpen = !state.aiJobsOpen;
  state.aiHistoryOpen = false;
  renderAiHistory();
  renderAiJobs();
  renderAiToolbarActions();
  if (state.aiJobsOpen) loadAiJobs();
}

function toggleAiHistory() {
  state.aiHistoryOpen = !state.aiHistoryOpen;
  state.aiJobsOpen = false;
  renderAiJobs();
  renderAiHistory();
  renderAiToolbarActions();
  if (state.aiHistoryOpen) loadAiHistory();
}

function closeAiHistoryPanel() {
  if (!state.aiHistoryOpen) return;
  state.aiHistoryOpen = false;
  renderAiHistory();
  renderAiToolbarActions();
}

function handleAiHistoryOutsideClick(event) {
  if (!state.aiHistoryOpen) return;
  const path = event.composedPath?.() || [];
  if (path.includes(elements.aiHistoryList) || path.includes(elements.aiHistoryToggle)) return;
  const target = event.target;
  if (elements.aiHistoryList?.contains(target) || elements.aiHistoryToggle?.contains(target)) return;
  closeAiHistoryPanel();
}

function closeAiJobsPanel() {
  if (!state.aiJobsOpen) return;
  state.aiJobsOpen = false;
  renderAiJobs();
  renderAiToolbarActions();
}

function renderAiToolbarActions() {
  const activeCount = activeAiJobCount();
  if (elements.aiHistoryToggle) {
    elements.aiHistoryToggle.innerHTML = historyIcon();
    elements.aiHistoryToggle.classList.toggle("active", state.aiHistoryOpen);
    elements.aiHistoryToggle.setAttribute("aria-expanded", String(state.aiHistoryOpen));
  }
  if (elements.aiNewChat) {
    elements.aiNewChat.innerHTML = plusIcon();
    elements.aiNewChat.classList.remove("active");
  }
  if (elements.aiJobToggle) {
    elements.aiJobToggle.innerHTML = `${queueIcon()}${activeCount > 0 ? `<span>${activeCount}</span>` : ""}`;
    elements.aiJobToggle.classList.toggle("active", state.aiJobsOpen);
    elements.aiJobToggle.setAttribute("aria-expanded", String(state.aiJobsOpen));
  }
}

async function loadAiHistory(options = {}) {
  const contextKey = getAiHistoryContextKey();
  state.aiHistoryContextKey = contextKey;
  if (!elements.aiHistoryList || !state.agentUrl) {
    state.aiHistory = [];
    state.aiHistoryLoaded = true;
    renderAiHistory();
    updateAiPanelConversationState();
    return;
  }
  try {
    const params = new URLSearchParams({ limit: "20" });
    if (contextKey) params.set("context_key", contextKey);
    const response = await apiFetch(`/api/ai/conversations?${params.toString()}`, { cache: "no-store" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Agent returned ${response.status}`);
    state.aiHistory = Array.isArray(data.conversations) ? data.conversations : [];
    state.aiHistoryLoaded = true;
    if (options.keepClosed) state.aiHistoryOpen = false;
    renderAiHistory();
    updateAiPanelConversationState();
  } catch (error) {
    console.error(error);
    state.aiHistoryLoaded = true;
    state.aiHistory = null;
    renderAiHistory();
    updateAiPanelConversationState();
  }
}

async function loadAiConversationManagement() {
  if (!elements.aiConversationList) return;
  if (elements.aiConversationRefresh) elements.aiConversationRefresh.disabled = true;
  if (!state.agentUrl) {
    state.aiConversations = [];
    renderAiConversationManagement();
    elements.aiConversationFeedback.textContent = t("aiConversationHistoryUnavailable");
    if (elements.aiConversationRefresh) elements.aiConversationRefresh.disabled = false;
    return;
  }
  try {
    const response = await apiFetch("/api/ai/conversations?limit=100", { cache: "no-store" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Agent returned ${response.status}`);
    state.aiConversations = Array.isArray(data.conversations) ? data.conversations : [];
    renderAiConversationManagement();
    elements.aiConversationFeedback.textContent = "";
  } catch (error) {
    state.aiConversations = [];
    renderAiConversationManagement();
    elements.aiConversationFeedback.textContent = t("aiConversationHistoryFailed");
    console.error(error);
  } finally {
    if (elements.aiConversationRefresh) elements.aiConversationRefresh.disabled = false;
  }
}

function renderAiConversationManagement() {
  if (!elements.aiConversationList) return;
  if (state.aiConversations.length === 0) {
    elements.aiConversationList.innerHTML = `<div class="empty-state">${escapeHtml(t("aiConversationHistoryEmpty"))}</div>`;
    return;
  }
  elements.aiConversationList.replaceChildren(...state.aiConversations.map(renderAiConversationManagementRow));
}

function renderAiConversationManagementRow(conversation) {
  const row = document.createElement("div");
  row.className = "management-row ai-conversation-row";
  const title = conversation.title || t("aiConversation");
  const count = Number(conversation.message_count || 0);
  const contextLabel = getConversationContextLabel(conversation);
  row.innerHTML = `
    <div class="management-name">
      <strong>${escapeHtml(title)}</strong>
      <span class="ai-run-meta">
        <em>${escapeHtml(contextLabel)}</em>
        <span>${escapeHtml(formatDateTime(conversation.updated_at || conversation.created_at))}</span>
        <span>${escapeHtml(String(count))}</span>
      </span>
    </div>
    <div class="ai-run-actions-inline">
      <button type="button" class="ai-run-icon-button" data-ai-conversation-delete="${escapeHtml(conversation.id || "")}" aria-label="${escapeHtml(t("deleteConversation"))}" title="${escapeHtml(t("deleteConversation"))}">${trashIcon()}</button>
      <button type="button" class="ai-run-icon-button primary-inline-button" data-ai-conversation-open="${escapeHtml(conversation.id || "")}" aria-label="${escapeHtml(t("openConversationContext"))}" title="${escapeHtml(t("openConversationContext"))}">${openContextIcon()}</button>
    </div>
  `;
  row.querySelector("[data-ai-conversation-open]")?.addEventListener("click", () => openAiConversationContext(conversation));
  row.querySelector("[data-ai-conversation-delete]")?.addEventListener("click", () => deleteAiConversation(conversation.id || "", { refreshManagement: true }));
  return row;
}

function getConversationContextLabel(conversation) {
  const snapshot = conversation.context_snapshot || {};
  const scope = String(snapshot.scope || "");
  const items = Array.isArray(snapshot.items) ? snapshot.items : [];
  const requested = snapshot.requested || {};
  if (scope === "reader" && items[0]?.title) return t("aiContextReader", { title: items[0].title });
  if (scope === "manual") return t("aiContextManualCount", { count: items.length || (snapshot.item_ids || []).length || 0 });
  if (requested.collection) return t("aiContextCollection", { name: requested.collection });
  if (Array.isArray(requested.tags) && requested.tags.length > 0) return t("aiContextTags", { mode: t(requested.tag_match === "all" ? "tagMatchModeAllLabel" : "tagMatchModeAnyLabel"), names: requested.tags.map((tag) => `#${tag}`).join(", ") });
  if (requested.q) return t("aiContextSearch", { query: requested.q });
  if (requested.library && requested.library !== "all") return t("aiContextLibrary", { name: requested.library });
  return t("aiContextGlobal");
}

function openAiConversationContext(conversation) {
  const snapshot = conversation.context_snapshot || {};
  const requested = snapshot.requested || {};
  const itemIds = Array.isArray(snapshot.item_ids) ? snapshot.item_ids.map(String).filter(Boolean) : [];
  closeSettings();
  state.manualAiContextIds.clear();
  if (snapshot.scope === "reader" && itemIds[0]) {
    const item = getItemById(itemIds[0]);
    if (item) openReader(item);
  } else if (snapshot.scope === "manual" && itemIds.length > 0) {
    itemIds.forEach((id) => {
      if (getItemById(id)) state.manualAiContextIds.add(id);
    });
    returnToWorkspace();
    renderGrid();
  } else if (requested.collection) {
    selectCollection(String(requested.collection));
  } else if (Array.isArray(requested.tags) && requested.tags.length > 0) {
    selectTag(String(requested.tags[0]));
    state.selectedTags = new Set(requested.tags.map(String));
    state.tagMatchMode = requested.tag_match === "all" ? "all" : "any";
    renderApp();
  } else {
    selectLibraryFilter(String(requested.library || "all"));
  }
  if (!state.aiPanelOpen) openAiPanel();
  loadAiConversation(conversation).catch((error) => console.error(error));
}

async function deleteAiConversation(conversationId, options = {}) {
  if (!conversationId || !state.agentUrl) return;
  if (!window.confirm(t("deleteConversationConfirm"))) return;
  try {
    const response = await apiFetch(`/api/ai/conversations/${encodeURIComponent(conversationId)}`, { method: "DELETE" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Agent returned ${response.status}`);
    if (elements.aiConversationFeedback) elements.aiConversationFeedback.textContent = t("aiConversationDeleted");
    if (state.aiConversationId === conversationId) resetAiConversationSession();
    await loadAiHistory({ keepClosed: !state.aiHistoryOpen });
    if (options.refreshManagement !== false) await loadAiConversationManagement();
  } catch (error) {
    if (elements.aiConversationFeedback) elements.aiConversationFeedback.textContent = error?.message || t("aiConversationHistoryFailed");
    console.error(error);
  }
}

function renderAiHistory() {
  if (!elements.aiHistoryList) return;
  updateAiPanelConversationState();
  elements.aiHistoryList.hidden = !state.aiHistoryOpen;
  if (!state.aiHistoryOpen) return;
  const header = renderAiPopoverHeader(t("aiConversationHistory"), closeAiHistoryPanel);
  if (state.aiHistory === null) {
    elements.aiHistoryList.replaceChildren(header, emptyState(t("aiConversationHistoryFailed")));
    return;
  }
  if (!state.aiHistoryLoaded) {
    elements.aiHistoryList.replaceChildren(header, emptyState(t("loading")));
    return;
  }
  if (state.aiHistory.length === 0) {
    elements.aiHistoryList.replaceChildren(header, emptyState(t("aiConversationHistoryEmpty")));
    return;
  }
  elements.aiHistoryList.replaceChildren(header, ...state.aiHistory.map(renderAiHistoryRow));
}

function renderAiHistoryRow(conversation) {
  const row = document.createElement("div");
  row.className = "ai-history-row";
  row.classList.toggle("active", conversation.id === state.aiConversationId);
  const contextLabel = getConversationContextLabel(conversation);
  row.innerHTML = `
    <button type="button" class="ai-history-row-main">
      <strong>${escapeHtml(conversation.title || t("aiConversation"))}</strong>
      <span>${escapeHtml(contextLabel)} · ${escapeHtml(formatDateTime(conversation.updated_at || conversation.created_at))} · ${escapeHtml(String(conversation.message_count || 0))}</span>
    </button>
    <button type="button" class="ai-history-delete" aria-label="${escapeHtml(t("deleteConversation"))}" title="${escapeHtml(t("deleteConversation"))}">${trashIcon()}</button>
  `;
  row.querySelector(".ai-history-row-main")?.addEventListener("click", async () => {
    try {
      state.aiHistoryOpen = false;
      renderAiHistory();
      openAiConversationContext(conversation);
    } catch (error) {
      console.error(error);
    }
  });
  row.querySelector(".ai-history-delete")?.addEventListener("click", (event) => {
    event.stopPropagation();
    deleteAiConversation(conversation.id || "", { refreshManagement: false }).catch((error) => console.error(error));
  });
  return row;
}

function renderAiJobs() {
  if (!elements.aiJobList || !elements.aiJobToggle) return;
  renderAiToolbarActions();
  elements.aiJobList.hidden = !state.aiJobsOpen;
  if (!state.aiJobsOpen) return;
  const header = renderAiPopoverHeader(t("aiJobQueue"), closeAiJobsPanel);
  if (state.aiJobs.length === 0) {
    elements.aiJobList.replaceChildren(header, emptyState(t("aiJobQueueEmpty")), renderAiJobMoreButton());
    return;
  }
  const orderedJobs = getOrderedAiJobs(state.aiJobs).slice(0, 5);
  elements.aiJobList.replaceChildren(header, ...orderedJobs.map(renderAiJobRow), renderAiJobMoreButton());
}

function getOrderedAiJobs(jobs) {
  return [...(Array.isArray(jobs) ? jobs : [])].sort((a, b) => String(b.created_at || "").localeCompare(String(a.created_at || "")));
}

function renderAiJobMoreButton() {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "ai-job-more-button";
  button.textContent = t("aiGenerationHistoryMore");
  button.addEventListener("click", openAiGenerationHistorySettings);
  return button;
}

function renderAiPopoverHeader(label, onClose) {
  const header = document.createElement("div");
  header.className = "ai-popover-head";
  const title = document.createElement("span");
  title.textContent = label;
  const close = document.createElement("button");
  close.type = "button";
  close.className = "ai-popover-close";
  close.textContent = "×";
  close.setAttribute("aria-label", t("close"));
  close.setAttribute("title", t("close"));
  close.addEventListener("click", onClose);
  header.append(title, close);
  return header;
}

function emptyState(message) {
  const node = document.createElement("div");
  node.className = "empty-state";
  node.textContent = message;
  return node;
}

function renderAiJobRow(job) {
  const row = document.createElement("div");
  row.className = "ai-job-row";
  const jobId = String(job.job_id || "");
  const statusClass = `status-${String(job.status || "pending").toLowerCase().replace(/[^a-z0-9-]/g, "") || "pending"}`;
  row.classList.add(statusClass);
  const label = job.label || getAiRunKindLabel(job);
  const isActive = ["pending", "running"].includes(job.status);
  const isFailed = job.status === "failed";
  const timeValue = job.completed_at || job.updated_at || job.created_at || "";
  const timeMeta = timeValue ? `<span>${escapeHtml(formatDateTime(timeValue))}</span>` : "";
  const retryAction = isFailed && job.retryable
    ? `<button type="button" class="ai-job-icon-button" data-ai-job-retry="${escapeHtml(job.job_id)}" aria-label="${escapeHtml(t("aiJobRetry"))}" title="${escapeHtml(t("aiJobRetry"))}">${retryIcon()}</button>`
    : "";
  row.innerHTML = `
    <div class="ai-job-main">
      <strong>${escapeHtml(label)}</strong>
      <span class="ai-run-meta">
        ${isActive ? '<i class="ai-job-progress-dot" aria-hidden="true"></i>' : ""}
        <em class="ai-run-status ${statusClass}">${escapeHtml(getAiRunStatusLabel(job.status))}</em>
        ${timeMeta}
      </span>
    </div>
    <div class="ai-job-actions">
      ${retryAction}
      <button type="button" class="ai-job-detail-link" data-ai-job-details="${escapeHtml(jobId)}">${escapeHtml(t("aiGenerationHistoryDetails"))}</button>
    </div>
  `;
  row.querySelector("[data-ai-job-retry]")?.addEventListener("click", (event) => {
    event.stopPropagation();
    retryAiJob(job.job_id);
  });
  row.querySelector("[data-ai-job-details]")?.addEventListener("click", (event) => {
    event.stopPropagation();
    openAiGenerationHistorySettings();
  });
  return row;
}

function openAiGenerationHistorySettings() {
  closeAiJobsPanel();
  openSettings("ai-generation-history");
}

async function loadAiGenerationHistory() {
  if (!elements.aiGenerationList) return;
  if (elements.aiGenerationRefresh) elements.aiGenerationRefresh.disabled = true;
  if (!state.agentUrl) {
    state.aiJobs = [];
    renderAiGenerationHistory();
    elements.aiGenerationFeedback.textContent = t("aiRunHistoryUnavailable");
    if (elements.aiGenerationRefresh) elements.aiGenerationRefresh.disabled = false;
    return;
  }
  try {
    const response = await apiFetch("/api/ai/jobs?limit=100", { cache: "no-store" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Agent returned ${response.status}`);
    state.aiJobs = Array.isArray(data.jobs) ? data.jobs : [];
    renderAiJobs();
    renderAiGenerationHistory();
    elements.aiGenerationFeedback.textContent = "";
  } catch (error) {
    state.aiJobs = [];
    renderAiJobs();
    renderAiGenerationHistory();
    elements.aiGenerationFeedback.textContent = t("aiRunHistoryFailed");
    console.error(error);
  } finally {
    if (elements.aiGenerationRefresh) elements.aiGenerationRefresh.disabled = false;
  }
}

function renderAiGenerationHistory() {
  if (!elements.aiGenerationList) return;
  const jobs = getOrderedAiJobs(state.aiJobs);
  if (jobs.length === 0) {
    elements.aiGenerationList.innerHTML = `<div class="empty-state">${escapeHtml(t("aiJobQueueEmpty"))}</div>`;
    return;
  }
  const activeOrder = new Map(
    [...jobs]
      .filter((job) => ["pending", "running"].includes(String(job.status || "").toLowerCase()))
      .sort((a, b) => String(a.created_at || "").localeCompare(String(b.created_at || "")))
      .map((job, index) => [String(job.job_id || ""), index + 1])
  );
  elements.aiGenerationList.replaceChildren(...jobs.map((job) => renderAiGenerationHistoryRow(job, activeOrder)));
}

function renderAiGenerationHistoryRow(job, activeOrder = new Map()) {
  const row = document.createElement("div");
  row.className = "management-row ai-generation-row";
  const jobId = String(job.job_id || "");
  const expanded = state.expandedAiGenerationJobIds.has(jobId);
  const statusClass = `status-${String(job.status || "pending").toLowerCase().replace(/[^a-z0-9-]/g, "") || "pending"}`;
  const title = job.label || getAiRunKindLabel(job);
  const generatedAt = job.completed_at || job.updated_at || job.created_at || "";
  const item = job.item_id ? getItemById(job.item_id) : null;
  const notice = state.aiGenerationJobNotices[jobId] || "";
  const isActive = ["pending", "running"].includes(String(job.status || "").toLowerCase());
  const openButton = job.status === "completed" && item
    ? `<button type="button" class="ai-run-icon-button" data-ai-generation-open="${escapeHtml(jobId)}" aria-label="${escapeHtml(t("aiGenerationHistoryOpenItem"))}" title="${escapeHtml(t("aiGenerationHistoryOpenItem"))}">${openNoteIcon()}</button>`
    : "";
  const retryButton = job.status === "failed"
    ? `<button type="button" class="ai-run-icon-button" data-ai-generation-retry="${escapeHtml(jobId)}" aria-label="${escapeHtml(t("aiJobRetry"))}" title="${escapeHtml(job.retryable ? t("aiJobRetry") : t("aiJobNotRetryable"))}"${job.retryable ? "" : " disabled"}>${retryIcon()}</button>`
    : "";
  const queueIndex = activeOrder.get(jobId);
  const activeButton = isActive
    ? `<button type="button" class="ai-run-status-button" disabled>${queueIndex ? `<span class="ai-run-queue-index">#${escapeHtml(String(queueIndex))}</span>` : ""}<i class="ai-job-progress-dot" aria-hidden="true"></i>${escapeHtml(getAiRunStatusLabel(job.status))}</button>`
    : "";
  row.innerHTML = `
    <div class="management-name">
      <strong>${escapeHtml(title)}</strong>
      <span class="ai-run-meta">
        <em class="ai-run-status ${statusClass}">${escapeHtml(getAiRunStatusLabel(job.status))}</em>
        ${generatedAt ? `<span>${escapeHtml(t("aiGenerationHistoryGeneratedAt", { date: formatDateTime(generatedAt) }))}</span>` : ""}
      </span>
    </div>
    <div class="ai-run-actions-inline">
      ${openButton}
      ${retryButton}
      ${activeButton}
      <button type="button" class="ai-run-icon-button" data-ai-generation-delete="${escapeHtml(jobId)}" aria-label="${escapeHtml(t("delete"))}" title="${escapeHtml(t("delete"))}">${trashIcon()}</button>
      <button type="button" class="ai-run-icon-button primary-inline-button" data-ai-generation-more="${escapeHtml(jobId)}" aria-label="${escapeHtml(t("aiGenerationHistoryDetails"))}" title="${escapeHtml(t("aiGenerationHistoryDetails"))}">${detailIcon()}</button>
    </div>
    ${notice ? `<div class="ai-generation-row-notice">${escapeHtml(notice)}</div>` : ""}
    ${expanded ? `<div class="ai-generation-more-panel">${escapeHtml(t("aiGenerationHistoryMorePlaceholder"))}</div>` : ""}
  `;
  row.querySelector("[data-ai-generation-open]")?.addEventListener("click", () => {
    if (!item) return;
    closeSettings();
    openReader(item);
  });
  row.querySelector("[data-ai-generation-retry]")?.addEventListener("click", () => retryAiGenerationJob(jobId));
  row.querySelector("[data-ai-generation-delete]")?.addEventListener("click", () => deleteAiGenerationJob(jobId));
  row.querySelector("[data-ai-generation-more]")?.addEventListener("click", () => openAiGenerationDetail(job));
  return row;
}

async function deleteAiGenerationJob(jobId) {
  if (!jobId) return;
  if (!window.confirm(t("aiGenerationHistoryDeleteConfirm"))) return;
  await cancelAiJob(jobId);
}

function openAiGenerationDetail(job) {
  const jobId = String(job?.job_id || "");
  if (!jobId || !elements.aiGenerationDetail) return;
  state.aiGenerationDetailJobId = jobId;
  state.aiGenerationDetailJob = job || null;
  state.aiGenerationDetailStageIndex = 0;
  elements.aiGenerationDetail.hidden = false;
  renderAiGenerationDetail();
  loadAiGenerationDetail(jobId);
}

function closeAiGenerationDetail() {
  if (!elements.aiGenerationDetail) return;
  elements.aiGenerationDetail.hidden = true;
  state.aiGenerationDetailJobId = "";
  state.aiGenerationDetailJob = null;
  state.aiGenerationDetailStageIndex = 0;
  stopAiGenerationDetailPolling();
}

async function loadAiGenerationDetail(jobId = state.aiGenerationDetailJobId) {
  if (!jobId || !state.agentUrl) return;
  if (!state.aiGenerationDetailJob && elements.aiGenerationDetailFeedback) {
    elements.aiGenerationDetailFeedback.textContent = t("aiGenerationDetailLoading");
  }
  try {
    const response = await apiFetch(`/api/ai/jobs/${encodeURIComponent(jobId)}`, { cache: "no-store" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Agent returned ${response.status}`);
    state.aiGenerationDetailJob = data.job || null;
    syncAiJobInList(state.aiGenerationDetailJob);
    if (elements.aiGenerationDetailFeedback) elements.aiGenerationDetailFeedback.textContent = "";
    renderAiGenerationDetail();
    if (["pending", "running"].includes(String(state.aiGenerationDetailJob?.status || "").toLowerCase())) {
      startAiGenerationDetailPolling();
    } else {
      stopAiGenerationDetailPolling();
    }
  } catch (error) {
    if (elements.aiGenerationDetailFeedback) elements.aiGenerationDetailFeedback.textContent = error?.message || t("aiGenerationDetailLoadFailed");
    console.error(error);
  }
}

function syncAiJobInList(job) {
  if (!job?.job_id) return;
  const index = state.aiJobs.findIndex((item) => item.job_id === job.job_id);
  if (index >= 0) state.aiJobs[index] = job;
  else state.aiJobs.unshift(job);
  renderAiJobs();
  if (state.activeSettingsTab === "ai-generation-history") renderAiGenerationHistory();
}

function startAiGenerationDetailPolling() {
  if (!state.aiGenerationDetailJobId) return;
  if (state.aiGenerationDetailEventSource || state.aiGenerationDetailPollTimer) return;
  if (window.EventSource) {
    const source = new EventSource(buildApiEventUrl(`/api/ai/jobs/${encodeURIComponent(state.aiGenerationDetailJobId)}/events`), { withCredentials: true });
    state.aiGenerationDetailEventSource = source;
    source.addEventListener("job", (event) => {
      const data = parseJsonSafe(event.data);
      if (!data?.job) return;
      state.aiGenerationDetailJob = data.job;
      syncAiJobInList(data.job);
      if (elements.aiGenerationDetailFeedback) elements.aiGenerationDetailFeedback.textContent = "";
      renderAiGenerationDetail();
      if (!["pending", "running"].includes(String(data.job.status || "").toLowerCase())) {
        stopAiGenerationDetailPolling();
      }
    });
    source.onerror = () => {
      stopAiGenerationDetailEventSource();
      if (state.aiGenerationDetailJobId && !state.aiGenerationDetailPollTimer) {
        state.aiGenerationDetailPollTimer = window.setInterval(() => loadAiGenerationDetail(), 1800);
      }
    };
    return;
  }
  state.aiGenerationDetailPollTimer = window.setInterval(() => loadAiGenerationDetail(), 1800);
}

function stopAiGenerationDetailPolling() {
  stopAiGenerationDetailEventSource();
  if (state.aiGenerationDetailPollTimer) {
    window.clearInterval(state.aiGenerationDetailPollTimer);
    state.aiGenerationDetailPollTimer = 0;
  }
}

function stopAiGenerationDetailEventSource() {
  if (!state.aiGenerationDetailEventSource) return;
  state.aiGenerationDetailEventSource.close();
  state.aiGenerationDetailEventSource = null;
}

function parseJsonSafe(value) {
  try {
    return JSON.parse(value);
  } catch (_) {
    return null;
  }
}

function renderAiGenerationDetail() {
  const job = state.aiGenerationDetailJob;
  if (!elements.aiGenerationDetail || !job) return;
  const title = job.label || getAiRunKindLabel(job);
  const statusClass = `status-${String(job.status || "pending").toLowerCase().replace(/[^a-z0-9-]/g, "") || "pending"}`;
  elements.aiGenerationDetailTitle.textContent = title;
  elements.aiGenerationDetailMeta.innerHTML = [
    job.created_at ? `${escapeHtml(t("aiGenerationDetailCreated"))}: ${escapeHtml(formatDateTime(job.created_at))}` : "",
    job.updated_at ? `${escapeHtml(t("aiGenerationDetailUpdated"))}: ${escapeHtml(formatDateTime(job.updated_at))}` : "",
    job.completed_at ? `${escapeHtml(t("aiGenerationDetailCompleted"))}: ${escapeHtml(formatDateTime(job.completed_at))}` : "",
  ].filter(Boolean).map((item) => `<span>${item}</span>`).join("");
  const stageLabel = job.current_stage ? formatAiGenerationStage(job.current_stage) : "";
  const currentAction = getAiGenerationCurrentAction(job);
  elements.aiGenerationDetailStatus.innerHTML = `
    <span class="ai-run-status ${statusClass}">${escapeHtml(getAiRunStatusLabel(job.status))}</span>
    ${stageLabel ? `<span>${escapeHtml(t("aiGenerationDetailCurrentStage"))}: ${escapeHtml(stageLabel)}</span>` : ""}
    ${currentAction ? `<span>${escapeHtml(t("aiGenerationDetailCurrentAction"))}: ${escapeHtml(currentAction)}</span>` : ""}
    ${job.message ? `<span>${escapeHtml(t("aiGenerationDetailMessage"))}: ${escapeHtml(job.message)}</span>` : ""}
    ${job.error?.message ? `<span class="ai-run-error">${escapeHtml(t("aiGenerationDetailError"))}: ${escapeHtml(job.error.message)}</span>` : ""}
  `;
  renderAiGenerationDetailActions(job);
  renderAiGenerationStageList(job);
  renderAiGenerationStagePanel(job);
  renderAiGenerationDetailChecklist(job);
  renderAiGenerationDetailSkills(job);
}

function renderAiGenerationDetailActions(job) {
  const item = job.item_id ? getItemById(job.item_id) : null;
  const canOpenItem = job.status === "completed" && item;
  elements.aiGenerationDetailOpen.hidden = false;
  elements.aiGenerationDetailOpen.disabled = !canOpenItem;
  elements.aiGenerationDetailRetry.hidden = job.status !== "failed";
  elements.aiGenerationDetailRetry.disabled = job.status === "failed" && !job.retryable;
  elements.aiGenerationDetailRetry.title = job.status === "failed" && !job.retryable ? t("aiJobNotRetryable") : t("aiJobRetry");
  elements.aiGenerationDetailOpen.onclick = () => {
    if (!canOpenItem) return;
    closeAiGenerationDetail();
    closeSettings();
    openReader(item);
  };
  elements.aiGenerationDetailRetry.onclick = () => retryAiGenerationJob(job.job_id || "");
}

function getAiGenerationStages(job) {
  const traces = Array.isArray(job?.stage_trace) ? job.stage_trace.map((entry) => ({ ...entry })) : [];
  const currentStage = String(job?.current_stage || "").trim();
  if (currentStage && !isTerminalAiJobStatus(job?.status)) {
    const hasActiveCurrent = traces.some((entry) => String(entry.stage || entry.node || "") === currentStage && !isTerminalAiStageStatus(entry.status));
    const last = traces[traces.length - 1] || null;
    const lastStage = String(last?.stage || last?.node || "");
    const lastIsCompletedCurrent = lastStage === currentStage && isTerminalAiStageStatus(last?.status);
    if (!hasActiveCurrent && !lastIsCompletedCurrent) {
      traces.push({
        stage: currentStage,
        agent: aiGenerationAgentForStage(currentStage),
        status: job.status === "pending" ? "pending" : "running",
        message: job.message || getAiGenerationCurrentAction(job),
      });
    }
  }
  if (traces.length > 0) return traces;
  if (currentStage) return [{ stage: currentStage, status: job.status || "pending", message: job.message || "" }];
  return [];
}

function renderAiGenerationStageList(job) {
  const stages = getAiGenerationStages(job);
  if (!elements.aiGenerationStageList) return;
  if (stages.length === 0) {
    elements.aiGenerationStageList.innerHTML = `<div class="empty-state">${escapeHtml(t("aiGenerationDetailNoStage"))}</div>`;
    return;
  }
  const maxIndex = stages.length - 1;
  if (state.aiGenerationDetailStageIndex > maxIndex) state.aiGenerationDetailStageIndex = maxIndex;
  elements.aiGenerationStageList.replaceChildren(...stages.map((stage, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "ai-generation-stage-node";
    button.classList.toggle("active", index === state.aiGenerationDetailStageIndex);
    button.classList.toggle("running", stage.status === "running");
    button.classList.toggle("failed", stage.status === "failed");
    button.innerHTML = `
      <span class="ai-generation-stage-dot"></span>
      <strong>${escapeHtml(formatAiGenerationStage(stage.stage || stage.node || stage.name || ""))}</strong>
      <small>${escapeHtml([stage.agent || "", getAiRunStatusLabel(stage.status)].filter(Boolean).join(" · "))}</small>
    `;
    button.addEventListener("click", () => {
      state.aiGenerationDetailStageIndex = index;
      renderAiGenerationDetail();
    });
    return button;
  }));
}

function renderAiGenerationStagePanel(job) {
  const stages = getAiGenerationStages(job);
  const stage = stages[state.aiGenerationDetailStageIndex] || null;
  const artifact = findAiGenerationArtifact(job, stage);
  if (!elements.aiGenerationStagePanel) return;
  if (!stage) {
    elements.aiGenerationStagePanel.innerHTML = `<div class="empty-state">${escapeHtml(t("aiGenerationDetailNoData"))}</div>`;
    return;
  }
  const metadataRows = renderKeyValueList(stage.metadata || {});
  const artifactRows = artifact ? renderAiGenerationArtifactDetail(artifact) : "";
  const loadingRows = !artifact && !isTerminalAiStageStatus(stage.status)
    ? `<section class="ai-generation-stage-loading">${escapeHtml(t("aiGenerationDetailLoading"))}</section>`
    : "";
  const currentAction = stage.message || getAiGenerationCurrentAction({ ...job, current_stage: stage.stage });
  elements.aiGenerationStagePanel.innerHTML = `
    <div class="ai-generation-stage-detail-head">
      <div>
        <p>${escapeHtml(stage.agent || stage.node || "")}</p>
        <h3>${escapeHtml(formatAiGenerationStage(stage.stage || stage.node || stage.name || ""))}</h3>
      </div>
      <span class="ai-run-status status-${escapeHtml(normalizeAiRunStatus(stage.status))}">${escapeHtml(getAiRunStatusLabel(stage.status))}</span>
    </div>
    <div class="ai-generation-stage-facts">
      ${stage.started_at ? `<span>${escapeHtml(t("aiGenerationDetailStarted"))}: ${escapeHtml(formatDateTime(stage.started_at))}</span>` : ""}
      ${stage.completed_at ? `<span>${escapeHtml(t("aiGenerationDetailCompleted"))}: ${escapeHtml(formatDateTime(stage.completed_at))}</span>` : ""}
      ${formatDuration(stage.duration_ms) ? `<span>${escapeHtml(formatDuration(stage.duration_ms))}</span>` : ""}
    </div>
    ${currentAction ? `<section><h4>${escapeHtml(t("aiGenerationDetailCurrentAction"))}</h4><p>${escapeHtml(currentAction)}</p></section>` : ""}
    ${stage.error_summary || stage.error ? `<section><h4>${escapeHtml(t("aiGenerationDetailError"))}</h4><p class="ai-run-error">${escapeHtml(stage.error_summary || stage.error)}</p></section>` : ""}
    ${loadingRows}
    ${artifactRows}
    ${metadataRows ? `<section><h4>${escapeHtml(t("aiGenerationDetailMetadata"))}</h4>${metadataRows}</section>` : ""}
  `;
}

function findAiGenerationArtifact(job, stage) {
  const artifacts = Array.isArray(job?.agent_artifacts) ? job.agent_artifacts : [];
  if (!stage || artifacts.length === 0) return null;
  const stageKey = String(stage.stage || stage.node || "").toLowerCase();
  const agentKey = String(stage.agent || "").toLowerCase();
  return artifacts.find((artifact) => {
    const artifactStage = String(artifact.stage || "").toLowerCase();
    const artifactAgent = String(artifact.agent || "").toLowerCase();
    return (stageKey && artifactStage && (artifactStage.includes(stageKey) || stageKey.includes(artifactStage))) ||
      (agentKey && artifactAgent && artifactAgent === agentKey);
  }) || null;
}

function renderAiGenerationArtifactDetail(artifact) {
  const summary = artifact.summary ? `<section><h4>${escapeHtml(t("aiGenerationDetailSummary"))}</h4><p>${escapeHtml(artifact.summary)}</p></section>` : "";
  const inputSummary = artifact.input_summary ? `<section><h4>${escapeHtml(t("aiGenerationDetailInputSummary"))}</h4><p>${escapeHtml(artifact.input_summary)}</p></section>` : "";
  const outputSummary = artifact.output_summary ? `<section><h4>${escapeHtml(t("aiGenerationDetailOutputSummary"))}</h4><p>${escapeHtml(artifact.output_summary)}</p></section>` : "";
  const qualityScore = Number(artifact.quality_score || 0);
  const quality = qualityScore > 0 ? `<section><h4>${escapeHtml(t("aiGenerationDetailQualityScore"))}</h4><p>${escapeHtml(formatQualityScore(qualityScore))}</p></section>` : "";
  const usageRows = artifact.usage && typeof artifact.usage === "object" ? renderKeyValueList(artifact.usage) : "";
  const usage = usageRows ? `<section><h4>${escapeHtml(t("aiGenerationDetailUsage"))}</h4>${usageRows}</section>` : "";
  const warnings = Array.isArray(artifact.warnings) && artifact.warnings.length > 0
    ? `<section><h4>${escapeHtml(t("aiGenerationDetailWarnings"))}</h4><ul class="ai-generation-detail-list">${artifact.warnings.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></section>`
    : "";
  const data = artifact.data && typeof artifact.data === "object" ? renderKeyValueList(artifact.data) : "";
  return `${summary}${inputSummary}${outputSummary}${quality}${usage}${warnings}${data ? `<section><h4>${escapeHtml(artifact.title || artifact.agent || t("aiJobArtifacts"))}</h4>${data}</section>` : ""}`;
}

function renderAiGenerationDetailChecklist(job) {
  const items = Array.isArray(job.execution_checklist) ? job.execution_checklist : [];
  if (!elements.aiGenerationDetailChecklist) return;
  if (items.length === 0) {
    elements.aiGenerationDetailChecklist.innerHTML = `<p>${escapeHtml(t("aiGenerationDetailNoData"))}</p>`;
    return;
  }
  elements.aiGenerationDetailChecklist.innerHTML = `<ul class="ai-generation-chip-list">${items.map((item) => `<li><span>${escapeHtml(item.label || item.title || item.id || "")}</span><em>${escapeHtml(getAiRunStatusLabel(item.status))}</em></li>`).join("")}</ul>`;
}

function renderAiGenerationDetailSkills(job) {
  const items = Array.isArray(job.skill_trace) ? job.skill_trace : [];
  if (!elements.aiGenerationDetailSkills) return;
  if (items.length === 0) {
    elements.aiGenerationDetailSkills.innerHTML = `<p>${escapeHtml(t("aiGenerationDetailNoData"))}</p>`;
    return;
  }
  elements.aiGenerationDetailSkills.innerHTML = renderAiGenerationSkillGroups(items);
}

function renderAiGenerationSkillGroups(items) {
  const defaultSkills = [];
  const enhancedSkills = [];
  items.forEach((item) => {
    if (isDefaultAiGenerationSkill(item)) {
      defaultSkills.push(item);
    } else {
      enhancedSkills.push(item);
    }
  });
  return [
    defaultSkills.length ? renderAiGenerationSkillGroup(t("aiGenerationDefaultSkills"), defaultSkills) : "",
    enhancedSkills.length ? renderAiGenerationSkillGroup(t("aiGenerationEnhancedSkills"), enhancedSkills) : "",
  ].filter(Boolean).join("");
}

function renderAiGenerationSkillGroup(title, items) {
  return `
    <section class="ai-generation-skill-group">
      <h4>${escapeHtml(title)}</h4>
      <ul class="ai-generation-skill-list">
        ${items.map(renderAiGenerationSkillItem).join("")}
      </ul>
    </section>
  `;
}

function renderAiGenerationSkillItem(item) {
  const title = item.title || item.id || "";
  const meta = [item.agent || "", item.version ? `v${item.version}` : "", item.source || ""].filter(Boolean).join(" · ");
  const reason = item.trigger_reason || "";
  return `
    <li>
      <div>
        <span>${escapeHtml(title)}</span>
        ${meta ? `<em>${escapeHtml(meta)}</em>` : ""}
      </div>
      ${reason ? `<small>${escapeHtml(t("aiGenerationSkillTriggeredBy"))}: ${escapeHtml(reason)}</small>` : ""}
    </li>
  `;
}

function isDefaultAiGenerationSkill(item) {
  const kind = String(item?.kind || "").toLowerCase();
  if (kind === "default") return true;
  if (kind === "enhanced") return false;
  return ["html_page_design", "safe_static_html", "content_quality_review"].includes(String(item?.id || ""));
}

function toggleAiJobDetails(jobId) {
  if (!jobId) return;
  if (state.expandedAiJobIds.has(jobId)) {
    state.expandedAiJobIds.delete(jobId);
  } else {
    state.expandedAiJobIds.add(jobId);
  }
  renderAiJobs();
}

function hasAiJobDetails(job) {
  return Boolean(
    job?.current_stage ||
    (Array.isArray(job?.stage_trace) && job.stage_trace.length > 0) ||
    (Array.isArray(job?.execution_checklist) && job.execution_checklist.length > 0) ||
    (Array.isArray(job?.skill_trace) && job.skill_trace.length > 0)
  );
}

function renderAiJobDetails(job) {
  const currentStage = job.current_stage
    ? `<p><span>${escapeHtml(t("aiJobCurrentStage"))}</span><b>${escapeHtml(formatAiGenerationStage(job.current_stage))}</b></p>`
    : "";
  const trace = Array.isArray(job.stage_trace) ? job.stage_trace.slice(-8) : [];
  const traceRows = trace.map((entry) => {
    const stage = formatAiGenerationStage(entry.stage || entry.node || "");
    const actor = entry.agent || entry.name || "";
    const status = entry.status || "";
    const message = entry.message || entry.error || "";
    const duration = formatDuration(entry.duration_ms);
    const metadata = entry.metadata && typeof entry.metadata === "object" ? entry.metadata : {};
    const outputSummary = formatAiStageMetadata(metadata);
    const metaText = [duration, outputSummary].filter(Boolean).join(" · ");
    return `<li><b>${escapeHtml(stage)}</b>${actor ? `<span>${escapeHtml(actor)}</span>` : ""}${status ? `<em>${escapeHtml(status)}</em>` : ""}${metaText ? `<em>${escapeHtml(metaText)}</em>` : ""}${message ? `<small>${escapeHtml(message)}</small>` : ""}</li>`;
  }).join("");
  const checklist = Array.isArray(job.execution_checklist) ? job.execution_checklist.slice(0, 8) : [];
  const checklistRows = checklist.map((item) => {
    const label = item.label || item.title || item.name || item.id || "";
    const status = item.status || (item.completed ? "completed" : "");
    return `<li><span>${escapeHtml(label)}</span>${status ? `<em>${escapeHtml(status)}</em>` : ""}</li>`;
  }).join("");
  const skills = Array.isArray(job.skill_trace) ? job.skill_trace : [];
  const skillRows = skills.length ? renderAiGenerationSkillGroups(skills) : "";
  const artifacts = Array.isArray(job.agent_artifacts) ? job.agent_artifacts.slice(-8) : [];
  const artifactRows = artifacts.map(renderAiAgentArtifact).join("");
  return `
    <div class="ai-job-detail">
      ${currentStage}
      ${traceRows ? `<section><h4>${escapeHtml(t("aiJobTrace"))}</h4><ol class="ai-job-trace">${traceRows}</ol></section>` : ""}
      ${artifactRows ? `<section><h4>${escapeHtml(t("aiJobArtifacts"))}</h4><ol class="ai-job-artifacts">${artifactRows}</ol></section>` : ""}
      ${checklistRows ? `<section><h4>${escapeHtml(t("aiJobChecklist"))}</h4><ul class="ai-job-checklist">${checklistRows}</ul></section>` : ""}
      ${skillRows ? `<section><h4>${escapeHtml(t("aiJobSkills"))}</h4>${skillRows}</section>` : ""}
    </div>
  `;
}

function isTerminalAiJobStatus(status) {
  return ["completed", "failed", "cancelled", "canceled"].includes(String(status || "").toLowerCase());
}

function isTerminalAiStageStatus(status) {
  return ["completed", "failed", "warning", "skipped"].includes(String(status || "").toLowerCase());
}

function aiGenerationAgentForStage(stage) {
  const map = {
    parsing: "Ingest",
    analyzing_requirements: "RequirementAnalyst",
    planning: "Planner",
    writing_content: "ContentWriter",
    designing_style: "StyleDesigner",
    coding_html: "HTMLCoder",
    verifying: "Verifier",
    safety_checking: "SafetyReviewer",
    finalizing: "Finalizer",
    writing: "WriteGateway",
  };
  return map[String(stage || "")] || "";
}

function renderAiAgentArtifact(artifact) {
  const title = artifact.title || artifact.agent || "";
  const agent = artifact.agent || "";
  const summary = artifact.summary || "";
  const data = artifact.data && typeof artifact.data === "object" ? artifact.data : {};
  const chips = flattenArtifactData(data).slice(0, 8).map((item) => `<span>${escapeHtml(item)}</span>`).join("");
  return `
    <li>
      <b>${escapeHtml(title)}</b>
      ${agent ? `<em>${escapeHtml(agent)}</em>` : ""}
      ${summary ? `<small>${escapeHtml(summary)}</small>` : ""}
      ${chips ? `<div class="ai-artifact-chips">${chips}</div>` : ""}
    </li>
  `;
}

function flattenArtifactData(data) {
  const items = [];
  Object.entries(data || {}).forEach(([key, value]) => {
    if (value === "" || value === null || value === undefined) return;
    if (Array.isArray(value)) {
      const text = value.map((item) => {
        if (item && typeof item === "object") return item.title || item.name || item.id || item.code || "";
        return String(item || "");
      }).filter(Boolean).slice(0, 3).join(", ");
      if (text) items.push(`${key}: ${text}`);
      return;
    }
    if (value && typeof value === "object") {
      const text = Object.entries(value).slice(0, 3).map(([childKey, childValue]) => `${childKey}=${childValue}`).join(", ");
      if (text) items.push(`${key}: ${text}`);
      return;
    }
    items.push(`${key}: ${value}`);
  });
  return items;
}

function formatAiStageMetadata(metadata) {
  if (!metadata || typeof metadata !== "object") return "";
  if (metadata.output_chars) return `${metadata.output_chars} chars`;
  if (metadata.section_count) return `${metadata.section_count} sections`;
  if (metadata.score) return `score ${metadata.score}`;
  if (metadata.risk_level) return String(metadata.risk_level);
  if (metadata.retry_count) return `retry ${metadata.retry_count}`;
  if (metadata.error_type) return String(metadata.error_type);
  return "";
}

async function cancelAiJob(jobId) {
  if (!jobId || !state.agentUrl) return;
  try {
    const response = await apiFetch(`/api/ai/jobs/${encodeURIComponent(jobId)}`, { method: "DELETE" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Agent returned ${response.status}`);
    await loadAiJobs();
    if (state.activeSettingsTab === "ai-generation-history") renderAiGenerationHistory();
  } catch (error) {
    console.error(error);
  }
}

async function retryAiJob(jobId) {
  if (!jobId || !state.agentUrl) return;
  try {
    const response = await apiFetch(`/api/ai/jobs/${encodeURIComponent(jobId)}/retry`, { method: "POST" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Agent returned ${response.status}`);
    state.aiSubmittedJobIds.add(data.job_id || jobId);
    appendAiMessage("assistant", t("aiJobRetrying", { jobId: data.job_id || jobId }));
    await loadAiJobs();
    if (state.activeSettingsTab === "ai-generation-history") renderAiGenerationHistory();
    startAiJobPolling();
    return { ok: true, jobId: data.job_id || jobId };
  } catch (error) {
    appendAiMessage("assistant", error?.message || t("aiJobFailed", { message: jobId }));
    console.error(error);
    return { ok: false, message: error?.message || t("aiJobFailed", { message: jobId }) };
  }
}

async function retryAiGenerationJob(jobId) {
  const job = state.aiJobs.find((item) => String(item.job_id || "") === String(jobId || "")) ||
    (String(state.aiGenerationDetailJob?.job_id || "") === String(jobId || "") ? state.aiGenerationDetailJob : null);
  if (job && !job.retryable) {
    const message = t("aiJobNotRetryable");
    if (elements.aiGenerationFeedback) elements.aiGenerationFeedback.textContent = message;
    state.aiGenerationJobNotices[jobId] = message;
    renderAiGenerationHistory();
    if (state.aiGenerationDetailJobId === jobId && elements.aiGenerationDetailFeedback) {
      elements.aiGenerationDetailFeedback.textContent = message;
    }
    return;
  }
  if (elements.aiGenerationFeedback) elements.aiGenerationFeedback.textContent = "";
  state.aiGenerationJobNotices[jobId] = "";
  renderAiGenerationHistory();
  const result = await retryAiJob(jobId);
  if (result?.ok) {
    state.aiGenerationJobNotices[jobId] = t("aiJobRetrying", { jobId: result.jobId || jobId });
  } else {
    state.aiGenerationJobNotices[jobId] = result?.message || t("aiJobFailed", { message: jobId });
  }
  renderAiGenerationHistory();
}

function hasActiveAiJobs() {
  return activeAiJobCount() > 0;
}

function activeAiJobCount() {
  return state.aiJobs.filter((job) => ["pending", "running"].includes(job.status)).length;
}

function startAiJobPolling() {
  if (state.aiJobsPollTimer) return;
  state.aiJobsPollTimer = window.setInterval(loadAiJobs, 1600);
}

function trackSubmittedAiJob(jobId) {
  if (!jobId) return;
  state.aiSubmittedJobIds.add(jobId);
}

function stopAiJobPolling() {
  if (!state.aiJobsPollTimer) return;
  window.clearInterval(state.aiJobsPollTimer);
  state.aiJobsPollTimer = 0;
}

async function loadAiRuns() {
  if (!elements.aiRunList) return;
  if (elements.aiRunRefresh) elements.aiRunRefresh.disabled = true;
  if (!state.agentUrl) {
    state.aiRuns = [];
    renderAiRuns();
    elements.aiRunFeedback.textContent = t("aiRunHistoryUnavailable");
    if (elements.aiRunRefresh) elements.aiRunRefresh.disabled = false;
    return;
  }
  try {
    const response = await apiFetch("/api/ai/runs?limit=20", { cache: "no-store" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Agent returned ${response.status}`);
    state.aiRuns = Array.isArray(data.runs) ? data.runs : [];
    renderAiRuns();
    elements.aiRunFeedback.textContent = "";
  } catch (error) {
    state.aiRuns = [];
    renderAiRuns();
    elements.aiRunFeedback.textContent = t("aiRunHistoryFailed");
    console.error(error);
  } finally {
    if (elements.aiRunRefresh) elements.aiRunRefresh.disabled = false;
  }
}

function renderAiRuns() {
  if (!elements.aiRunList) return;
  if (state.aiRuns.length === 0) {
    elements.aiRunList.innerHTML = `<div class="empty-state">${escapeHtml(t("aiRunHistoryEmpty"))}</div>`;
    return;
  }
  elements.aiRunList.replaceChildren(...state.aiRuns.map(renderAiRunRow));
}

function renderAiRunRow(run) {
  const row = document.createElement("div");
  row.className = "management-row ai-run-row";
  const runId = String(run.id || "");
  const selected = runId && state.selectedAiRunId === runId;
  const details = selected ? state.aiRunDetails[runId] : null;
  const kindLabel = getAiRunKindLabel(run);
  const statusLabel = getAiRunStatusLabel(run.status);
  const statusClass = `status-${String(run.status || "pending").toLowerCase().replace(/[^a-z0-9-]/g, "") || "pending"}`;
  const nodeCount = Array.isArray(run.node_trace) ? run.node_trace.length : 0;
  const duration = formatDuration(run.duration_ms);
  const durationMeta = duration ? `<span>${escapeHtml(t("aiRunDuration", { duration }))}</span>` : "";
  const completedMeta = run.completed_at ? `<span>${escapeHtml(t(run.kind === "material_html_generation" ? "aiRunGeneratedAt" : "aiRunCompletedAt", { date: formatDateTime(run.completed_at) }))}</span>` : "";
  const capabilityMeta = [
    run.cancellable ? "" : `<span class="ai-run-capability muted">${escapeHtml(t("aiRunNotCancellable"))}</span>`,
    run.retryable ? `<span class="ai-run-capability">${escapeHtml(t("aiRunRetryable"))}</span>` : "",
  ].join("");
  const facts = [
    completedMeta,
    durationMeta,
    `<span>${escapeHtml(t("aiRunNodeCount", { count: nodeCount }))}</span>`,
    capabilityMeta,
  ].filter(Boolean).join("");
  row.innerHTML = `
    <div class="management-name">
      <strong>${escapeHtml(kindLabel)}</strong>
      <span class="ai-run-meta">
        <span class="ai-run-meta-primary">
          <em class="ai-run-status ${statusClass}">${escapeHtml(statusLabel)}</em>
          <span class="ai-run-facts">${facts}</span>
        </span>
      </span>
    </div>
    <div class="ai-run-actions-inline">
      <button type="button" class="secondary-button" data-ai-run-details="${escapeHtml(runId)}">${escapeHtml(t(selected ? "aiRunHideDetails" : "aiRunDetails"))}</button>
    </div>
    ${selected ? renderAiRunDetails(details) : ""}
  `;
  row.querySelector("[data-ai-run-details]")?.addEventListener("click", () => toggleAiRunDetails(runId));
  return row;
}

function renderAiRunDetails(run) {
  if (!run) {
    return `<div class="ai-run-detail-panel">${escapeHtml(t("aiRunDetailsLoading"))}</div>`;
  }
  if (run.error_loading) {
    return `<div class="ai-run-detail-panel ai-run-error">${escapeHtml(t("aiRunDetailsFailed"))}</div>`;
  }
  const specItems = renderKeyValueList(run.spec || {});
  const usageItems = renderAiRunUsage(run.usage || {});
  const budgetItems = renderKeyValueList(run.budget || {});
  const errorMessage = run.error?.message ? `<p class="ai-run-error">${escapeHtml(t("aiRunError", { message: run.error.message }))}</p>` : "";
  return `
    <div class="ai-run-detail-panel">
      <section>
        <h4>${escapeHtml(t("aiRunSpec"))}</h4>
        ${specItems || `<p>${escapeHtml(t("aiRunNoDetailData"))}</p>`}
      </section>
      <section>
        <h4>${escapeHtml(t("aiRunUsage"))}</h4>
        ${usageItems || `<p>${escapeHtml(t("aiRunNoDetailData"))}</p>`}
      </section>
      <section>
        <h4>${escapeHtml(t("aiRunBudget"))}</h4>
        ${budgetItems || `<p>${escapeHtml(t("aiRunNoDetailData"))}</p>`}
      </section>
      ${errorMessage}
    </div>
  `;
}

function renderKeyValueList(values) {
  const entries = Object.entries(values || {}).filter(([, value]) => value !== "" && value !== null && value !== undefined);
  if (entries.length === 0) return "";
  return `<dl>${entries.map(([key, value]) => `<div><dt>${escapeHtml(key)}</dt><dd>${escapeHtml(formatAiRunValue(value))}</dd></div>`).join("")}</dl>`;
}

function renderAiRunUsage(usage) {
  const rows = [];
  if (usage.input_tokens) rows.push(t("aiRunInputTokens", { count: usage.input_tokens }));
  if (usage.output_tokens) rows.push(t("aiRunOutputTokens", { count: usage.output_tokens }));
  if (usage.total_tokens) rows.push(t("aiRunTotalTokens", { count: usage.total_tokens }));
  return rows.length > 0 ? `<ul>${rows.map((row) => `<li>${escapeHtml(row)}</li>`).join("")}</ul>` : "";
}

function formatAiRunValue(value) {
  if (Array.isArray(value)) return value.join(", ");
  if (typeof value === "object" && value !== null) return JSON.stringify(value);
  return String(value);
}

async function toggleAiRunDetails(runId) {
  if (!runId) return;
  if (state.selectedAiRunId === runId) {
    state.selectedAiRunId = "";
    renderAiRuns();
    return;
  }
  state.selectedAiRunId = runId;
  renderAiRuns();
  if (!state.aiRunDetails[runId]) {
    await loadAiRunDetails(runId);
  }
}

async function loadAiRunDetails(runId) {
  if (!state.agentUrl) return;
  try {
    const response = await apiFetch(`/api/ai/runs/${encodeURIComponent(runId)}`, { cache: "no-store" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Agent returned ${response.status}`);
    state.aiRunDetails[runId] = data.run || {};
  } catch (error) {
    state.aiRunDetails[runId] = { error_loading: true };
    console.error(error);
  }
  renderAiRuns();
}

function getAiRunKindLabel(run) {
  const kind = String(run?.kind || "");
  if (kind === "html_generation") return t("aiRunHtmlGeneration");
  if (kind === "material_html_generation") return t("aiRunMaterialGeneration");
  if (kind === "knowledge_qa") return t("aiRunKnowledgeQa");
  return t("aiRunUnknownKind");
}

function getAiRunStatusLabel(status) {
  const key = {
    completed: "aiRunStatusCompleted",
    failed: "aiRunStatusFailed",
    running: "aiRunStatusRunning",
    started: "aiRunStatusRunning",
    pending: "aiRunStatusPending",
    retrying: "aiRunStatusRetrying",
    warning: "aiRunStatusWarning",
  }[normalizeAiRunStatus(status)];
  return key ? t(key) : String(status || t("aiRunStatusPending"));
}

function normalizeAiRunStatus(status) {
  const value = String(status || "").toLowerCase().replace(/[^a-z0-9-]/g, "");
  if (value === "started") return "running";
  if (value === "done") return "completed";
  return value || "pending";
}

function getAiGenerationCurrentAction(job) {
  const stages = getAiGenerationStages(job);
  const running = [...stages].reverse().find((stage) => ["started", "running", "retrying"].includes(normalizeAiRunStatus(stage.status)));
  const currentStage = running?.stage || job.current_stage || "";
  const agent = running?.agent || "";
  const message = running?.message || "";
  if (message && !String(message).toLowerCase().includes("started")) return message;
  const label = formatAiGenerationStage(currentStage);
  if (!label && !agent) return "";
  return [agent, label].filter(Boolean).join(" · ");
}

function formatQualityScore(value) {
  const score = Number(value || 0);
  if (!Number.isFinite(score) || score <= 0) return "";
  return score <= 1 ? `${Math.round(score * 100)} / 100` : `${Math.round(score)} / 100`;
}

function formatAiGenerationStage(stage) {
  const normalized = String(stage || "").trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
  const key = {
    parse: "aiGenerationStageParsing",
    parsing: "aiGenerationStageParsing",
    ingest: "aiGenerationStageParsing",
    ingesting: "aiGenerationStageParsing",
    analyze: "aiGenerationStageAnalyzing",
    analyzing: "aiGenerationStageAnalyzing",
    requirement_analysis: "aiGenerationStageAnalyzing",
    analyzing_requirements: "aiGenerationStageAnalyzing",
    requirement_analyst: "aiGenerationStageAnalyzing",
    planning: "aiGenerationStagePlanning",
    plan: "aiGenerationStagePlanning",
    planner: "aiGenerationStagePlanning",
    writing: "aiGenerationStageWriting",
    content_writing: "aiGenerationStageWriting",
    writing_content: "aiGenerationStageWriting",
    content_writer: "aiGenerationStageWriting",
    designing: "aiGenerationStageDesigning",
    designing_style: "aiGenerationStageDesigning",
    style_design: "aiGenerationStageDesigning",
    style_designer: "aiGenerationStageDesigning",
    coding: "aiGenerationStageCoding",
    coding_html: "aiGenerationStageCoding",
    html_coding: "aiGenerationStageCoding",
    html_coder: "aiGenerationStageCoding",
    verifying: "aiGenerationStageVerifying",
    verification: "aiGenerationStageVerifying",
    verifier: "aiGenerationStageVerifying",
    safety: "aiGenerationStageSafety",
    safety_review: "aiGenerationStageSafety",
    safety_checking: "aiGenerationStageSafety",
    safety_reviewer: "aiGenerationStageSafety",
    finalizing: "aiGenerationStageFinalizing",
    finalize: "aiGenerationStageFinalizing",
    finalizer: "aiGenerationStageFinalizing",
    write: "aiGenerationStageWritingFile",
    writing_file: "aiGenerationStageWritingFile",
  }[normalized];
  if (key) return t(key);
  return normalized ? normalized.replace(/_/g, " ") : "";
}

function syncAiConfigFromServer(provider) {
  if (!provider) return;
  state.aiConfig = {
    ...state.aiConfig,
    provider: provider.provider || state.aiConfig?.provider || "openai-compatible",
    currentModel: provider.model || state.aiConfig?.currentModel || "gpt-5.5",
    apiBaseUrl: provider.base_url || state.aiConfig?.apiBaseUrl || "",
  };
  setStored("ai-config", JSON.stringify(state.aiConfig));
}

async function saveAiConfig(event) {
  event.preventDefault();
  const apiKey = elements.apiKey.value.trim();
  const config = {
    provider: elements.aiProvider.value,
    currentModel: elements.currentModel.value.trim(),
    apiBaseUrl: elements.apiBaseUrl.value.trim(),
    newModel: elements.newModel.value.trim(),
    temperature: elements.modelTemperature.value,
    maxTokens: elements.modelMaxTokens.value,
  };

  state.aiConfig = config;
  setStored("ai-config", JSON.stringify(config));

  if (apiKey) {
    elements.settingsFeedback.textContent = t("settingsNeedsAgent");
    elements.apiKey.value = "";
    return;
  }

  try {
    const response = await apiFetch("/api/ai/providers", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider: config.provider,
        base_url: config.apiBaseUrl,
        model: config.currentModel || "gpt-5.5",
        enabled: true,
      }),
    });
    if (!response.ok) throw new Error(`Agent returned ${response.status}`);
    const data = await response.json();
    syncAiConfigFromServer(data.provider);
    await refreshAiStatus();
    elements.settingsFeedback.textContent = t("settingsSavedAgent");
  } catch (error) {
    elements.settingsFeedback.textContent = t("settingsAgentFailed");
    console.error(error);
  } finally {
    elements.apiKey.value = "";
  }
}

function renderDataConfig() {
  const config = state.dataConfig || {};
  elements.autoBackup.checked = Boolean(config.autoBackup);
  elements.webdavUrl.value = config.webdav?.url || "";
  elements.webdavUsername.value = config.webdav?.username || "";
  elements.webdavPath.value = config.webdav?.path || "";
}

function saveDataConfig() {
  setStored("data-config", JSON.stringify(state.dataConfig));
}

function setAutoBackup(enabled) {
  state.dataConfig.autoBackup = enabled;
  saveDataConfig();
  if (enabled) {
    maybeAutoBackup(true);
  }
}

function saveWebdavSettings(event) {
  event.preventDefault();
  state.dataConfig.webdav = {
    url: elements.webdavUrl.value.trim(),
    username: elements.webdavUsername.value.trim(),
    path: elements.webdavPath.value.trim(),
  };
  saveDataConfig();
  elements.webdavFeedback.textContent = t("webdavSaved");
  maybeAutoBackup();
}

function testWebdavSettings() {
  elements.webdavFeedback.textContent = state.agentUrl ? t("settingsAgentFailed") : t("settingsNeedsAgent");
}

function createBackup() {
  downloadJson(`html-lore-backup-${dateStamp()}.json`, buildBackupPayload());
  state.dataConfig.lastBackupAt = new Date().toISOString();
  saveDataConfig();
  elements.backupFeedback.textContent = t("backupCreated");
}

function buildBackupPayload() {
  return {
    type: "html-lore-backup",
    version: 1,
    createdAt: new Date().toISOString(),
    manifestVersion: state.manifest?.version,
    preferences: getPreferencePayload(),
    manifest: state.manifest,
  };
}

function getPreferencePayload() {
  return {
    language: state.language,
    theme: state.themeMode,
    viewMode: state.viewMode,
    onlyFavorites: state.onlyFavorites,
    aiConfig: state.aiConfig,
    dataConfig: getExportableDataConfig(),
    navConfig: state.navConfig,
    itemState: state.itemState,
  };
}

function getExportableDataConfig() {
  const { lastBackupSnapshot, ...config } = state.dataConfig || {};
  return config;
}

function restoreBackupFile(file) {
  if (!file) return;
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    try {
      const backup = JSON.parse(String(reader.result || "{}"));
      const validTypes = new Set(["html-lore-backup"]);
      if (!validTypes.has(backup.type) || !backup.preferences) {
        throw new Error("Invalid backup file");
      }
      restorePreferences(backup.preferences);
      elements.backupFeedback.textContent = t("backupRestored");
      renderApp();
    } catch (error) {
      elements.backupFeedback.textContent = t("backupFailed");
      console.error(error);
    } finally {
      elements.restoreBackupFile.value = "";
    }
  });
  reader.readAsText(file);
}

function restorePreferences(preferences) {
  if (preferences.language && i18n[preferences.language]) {
    state.language = preferences.language;
    setStored("language", state.language);
  }
  if (preferences.theme === "system" || preferences.theme === "dark" || preferences.theme === "light") {
    state.themeMode = preferences.theme;
    setStored("theme", state.themeMode);
  }
  state.viewMode = "cards";
  setStored("view-mode", state.viewMode);
  state.onlyFavorites = Boolean(preferences.onlyFavorites);
  setStored("only-favorites", String(state.onlyFavorites));
  state.aiConfig = preferences.aiConfig || {};
  state.dataConfig = preferences.dataConfig || {};
  state.navConfig = preferences.navConfig || { library: {}, collections: {}, tags: {} };
  state.itemState = preferences.itemState || {};
  setStored("ai-config", JSON.stringify(state.aiConfig));
  setStored("data-config", JSON.stringify(state.dataConfig));
  setStored("nav-config", JSON.stringify(state.navConfig));
  saveItemState();
}

function maybeAutoBackup(force = false) {
  if (!state.dataConfig.autoBackup) return;
  state.dataConfig.lastBackupAt = new Date().toISOString();
  state.dataConfig.lastBackupSnapshot = buildBackupPayload();
  saveDataConfig();
  if (force) {
    elements.backupFeedback.textContent = t("backupCreated");
  }
}

function exportManifestData() {
  downloadJson(`html-lore-manifest-${dateStamp()}.json`, state.manifest || {});
  elements.exportFeedback.textContent = t("exportCreated");
}

function exportPreferencesData() {
  downloadJson(`html-lore-preferences-${dateStamp()}.json`, getPreferencePayload());
  elements.exportFeedback.textContent = t("exportCreated");
}

function downloadJson(filename, payload) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 0);
}

function dateStamp() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

async function testProviderConfig() {
  try {
    const response = await apiFetch("/api/ai/test-provider", { method: "POST" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok || !data.ok) throw new Error(data.message || data.detail || `Agent returned ${response.status}`);
    elements.settingsFeedback.textContent = t("settingsSavedAgent");
    await refreshAiStatus();
  } catch (error) {
    elements.settingsFeedback.textContent = t("settingsAgentFailed");
    console.error(error);
  }
}

function openLuckyItem() {
  const items = filteredItems();
  if (items.length === 0) return;
  const index = Math.floor(Math.random() * items.length);
  openReader(items[index]);
}

function submitAssistantJob(event) {
  event.preventDefault();
  if (window.confirm(t("assistantConfirm"))) {
    elements.assistantFeedback.textContent = t("assistantComingSoon");
  }
}

function starIcon(filled = false) {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path ${filled ? 'fill="currentColor"' : ""} d="m12 3 2.82 5.72 6.31.92-4.57 4.45 1.08 6.28L12 17.4l-5.64 2.97 1.08-6.28-4.57-4.45 6.31-.92L12 3Z"></path>
    </svg>
  `;
}

function archiveIcon() {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M3 7h18"></path>
      <path d="M5 7v12h14V7"></path>
      <path d="M8 7V4h8v3"></path>
      <path d="M9 12h6"></path>
    </svg>
  `;
}

function contextToggleIcon(active) {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      ${active ? "" : '<path d="M12 5v14"></path>'}
      <path d="M5 12h14"></path>
    </svg>
  `;
}

function queueIcon() {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M4 6h16"></path>
      <path d="M4 12h16"></path>
      <path d="M4 18h10"></path>
    </svg>
  `;
}

function plusIcon() {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 5v14"></path>
      <path d="M5 12h14"></path>
    </svg>
  `;
}

function historyIcon() {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M3 12a9 9 0 1 0 3-6.7"></path>
      <path d="M3 4v5h5"></path>
      <path d="M12 7v5l3 2"></path>
    </svg>
  `;
}

function retryIcon() {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M3 12a9 9 0 0 1 15.3-6.4"></path>
      <path d="M18 2v5h-5"></path>
      <path d="M21 12a9 9 0 0 1-15.3 6.4"></path>
      <path d="M6 22v-5h5"></path>
    </svg>
  `;
}

function enterArrowIcon() {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M7 7v4a3 3 0 0 0 3 3h9"></path>
      <path d="m15 10 4 4-4 4"></path>
    </svg>
  `;
}

function aiSparkIcon() {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 3l1.7 4.3L18 9l-4.3 1.7L12 15l-1.7-4.3L6 9l4.3-1.7L12 3Z"></path>
      <path d="M19 14l.9 2.1L22 17l-2.1.9L19 20l-.9-2.1L16 17l2.1-.9L19 14Z"></path>
      <path d="M5 13l.8 1.8L8 16l-2.2.8L5 19l-.8-2.2L2 16l2.2-1.2L5 13Z"></path>
    </svg>
  `;
}

function trashIcon() {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M3 6h18"></path>
      <path d="M8 6V4h8v2"></path>
      <path d="M6 6l1 15h10l1-15"></path>
      <path d="M10 11v6"></path>
      <path d="M14 11v6"></path>
    </svg>
  `;
}

function editIcon() {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 20h9"></path>
      <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5Z"></path>
    </svg>
  `;
}

function shareIcon() {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7"></path>
      <path d="m16 6-4-4-4 4"></path>
      <path d="M12 2v14"></path>
    </svg>
  `;
}

function openContextIcon() {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M7 17 17 7"></path>
      <path d="M9 7h8v8"></path>
      <path d="M5 5v14h14"></path>
    </svg>
  `;
}

function openNoteIcon() {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M6 4h12a2 2 0 0 1 2 2v9l-5 5H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Z"></path>
      <path d="M13 20v-5h5"></path>
    </svg>
  `;
}

function detailIcon() {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="8"></circle>
      <path d="M12 8v4"></path>
      <path d="M12 16h.1"></path>
    </svg>
  `;
}

function moreDotsIcon() {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M5 12h.1"></path>
      <path d="M12 12h.1"></path>
      <path d="M19 12h.1"></path>
    </svg>
  `;
}

function moonIcon() {
  return `
    <svg class="button-icon moon-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M14.3 3.1A8.9 8.9 0 1 0 21 14.8a7.4 7.4 0 0 1-4.2 1.3 7.6 7.6 0 0 1-7.6-7.6 7.4 7.4 0 0 1 5.1-5.4Z"></path>
      <path d="m18.3 3.2.5 1.4 1.4.5-1.4.5-.5 1.4-.5-1.4-1.4-.5 1.4-.5.5-1.4Z"></path>
      <circle cx="20" cy="8.5" r="1"></circle>
    </svg>
  `;
}

function sunIcon() {
  return `
    <svg class="button-icon" viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="4"></circle>
      <path d="M12 2v2"></path>
      <path d="M12 20v2"></path>
      <path d="m4.93 4.93 1.41 1.41"></path>
      <path d="m17.66 17.66 1.41 1.41"></path>
      <path d="M2 12h2"></path>
      <path d="M20 12h2"></path>
      <path d="m6.34 17.66-1.41 1.41"></path>
      <path d="m19.07 4.93-1.41 1.41"></path>
    </svg>
  `;
}

function normalizeVersion(value) {
  const match = String(value || "").trim().match(/^v?(\d+(?:\.\d+){0,2})/i);
  return match ? match[1] : "";
}

function compareVersions(left, right) {
  const a = normalizeVersion(left).split(".").map((part) => Number(part || 0));
  const b = normalizeVersion(right).split(".").map((part) => Number(part || 0));
  const length = Math.max(a.length, b.length, 3);
  for (let index = 0; index < length; index += 1) {
    const diff = (a[index] || 0) - (b[index] || 0);
    if (diff !== 0) return diff;
  }
  return 0;
}

function isVersionNewer(candidate, current) {
  if (!candidate || !current) return false;
  return compareVersions(candidate, current) > 0;
}

function setIconButtonLabel(button, key) {
  const label = t(key);
  button.setAttribute("aria-label", label);
  button.setAttribute("title", label);
}

function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) return;
  window.addEventListener("load", () => {
    const swPath = hasRuntimeConfig("STATIC_DEMO") ? "sw.js?v=1.1.6-demo" : "sw.js";
    navigator.serviceWorker.register(swPath).catch((error) => {
      console.warn("Service worker registration failed", error);
    });
  });
}

function t(key, params = {}) {
  const dictionary = i18n[state.language] || i18n.en;
  const fallback = i18n.en[key] || key;
  const template = dictionary[key] || fallback;
  return Object.entries(params).reduce((text, [name, value]) => {
    return text.replaceAll(`{${name}}`, String(value));
  }, template);
}

function applyTranslations() {
  document.documentElement.lang = t("appLanguage");
  elements.languageSelect.value = state.language;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-attr]").forEach((node) => {
    node.dataset.i18nAttr.split(",").forEach((entry) => {
      const [attribute, key] = entry.split(":").map((part) => part.trim());
      node.setAttribute(attribute, t(key));
    });
  });
  renderFeedback();
  applyNavSectionState();
  applyFavoriteFilter();
  applyMultiFilterState();
  applySortState();
  applyCodeEditorFullscreenState();
  updateThemeMetaColor(getResolvedTheme());
  renderVersionStatus();
}

function setFeedback(key, params = {}) {
  window.clearTimeout(state.feedbackTimer);
  state.feedbackKey = key;
  state.feedbackParams = params;
  renderFeedback();
  if (isTransientFeedback(key)) {
    state.feedbackTimer = window.setTimeout(clearFeedback, 4200);
  }
}

function clearFeedback() {
  window.clearTimeout(state.feedbackTimer);
  state.feedbackTimer = 0;
  state.feedbackKey = "connectAgent";
  state.feedbackParams = {};
  renderFeedback();
}

function isTransientFeedback(key) {
  return new Set([
    "emptyInput",
    "agentNotConfigured",
    "agentUnavailable",
    "importHtmlDone",
    "importHtmlFailed",
    "stateSaveFailed",
    "deleteNeedsAgent",
    "deleteFailed",
    "metadataSaved",
    "metadataSaveFailed",
    "codeSaved",
    "codeSaveFailed",
    "codeNeedsAgent",
    "editFileComingSoon",
    "fileEditorSaved",
    "fileEditorSaveFailed",
    "navigationSaveFailed",
  ]).has(key);
}

function renderFeedback() {
  elements.newFeedback.textContent = state.feedbackKey === "connectAgent" ? "" : t(state.feedbackKey, state.feedbackParams).trim();
}

function formatDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value).slice(0, 10);
  return date.toISOString().slice(0, 10);
}

function formatDateTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  const formatter = new Intl.DateTimeFormat(state.language || "en", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
  return formatter.format(date);
}

function formatDuration(value) {
  const milliseconds = Number(value || 0);
  if (!Number.isFinite(milliseconds) || milliseconds <= 0) return "";
  if (milliseconds < 1000) return `${Math.round(milliseconds)}ms`;
  return `${(milliseconds / 1000).toFixed(milliseconds < 10_000 ? 1 : 0)}s`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

elements.searchInput.addEventListener("input", (event) => {
  state.query = event.target.value;
  renderGrid();
  renderAiContext();
});
elements.brandHome.addEventListener("click", openWorkspaceHome);
elements.sidebarCollapse.addEventListener("click", toggleSidebar);
elements.sidebarResize.addEventListener("pointerdown", startSidebarResize);
elements.sidebarResize.addEventListener("mousedown", startSidebarResize);
elements.navSectionToggles.forEach((button) => {
  button.addEventListener("click", () => toggleNavSection(button.dataset.navSectionToggle));
});
elements.aiPanelOpen.addEventListener("click", toggleAiPanel);
elements.aiPanelClose.addEventListener("click", closeAiPanel);
elements.aiPanelResize.addEventListener("pointerdown", startAiPanelResize);
elements.aiPanelResize.addEventListener("mousedown", startAiPanelResize);
elements.aiComposerResize?.addEventListener("pointerdown", startAiComposerResize);
elements.aiComposerResize?.addEventListener("mousedown", startAiComposerResize);
elements.aiChatForm.addEventListener("submit", submitAiMessage);
elements.aiChatInput.addEventListener("keydown", handleAiChatInputKeydown);
elements.aiChatInput.addEventListener("input", autoGrowAiChatInput);
elements.aiContentExpansion.addEventListener("change", (event) => setAiContentExpansion(event.target.checked));
elements.aiGenerateNote.addEventListener("click", openGenerateNoteDialog);
elements.aiNewChat?.addEventListener("click", startNewAiConversation);
elements.aiHistoryToggle?.addEventListener("click", toggleAiHistory);
elements.aiJobToggle?.addEventListener("click", toggleAiJobs);
document.addEventListener("click", handleAiHistoryOutsideClick);
elements.luckyButton.addEventListener("click", openLuckyItem);
elements.multiFilterToggle.addEventListener("click", toggleMultiFilterPopover);
elements.tagMatchButtons.forEach((button) => {
  button.addEventListener("click", () => setTagMatchMode(button.dataset.tagMatchMode));
});
elements.sortToggle.addEventListener("click", toggleSortPopover);
elements.sortButtons.forEach((button) => {
  button.addEventListener("click", () => setSortMode(button.dataset.sortMode));
});
elements.favoriteFilter.addEventListener("click", toggleFavoriteFilter);
document.addEventListener("click", (event) => {
  if (!state.multiFilterOpen) return;
  if (elements.multiFilterPopover.contains(event.target) || elements.multiFilterToggle.contains(event.target)) return;
  closeMultiFilterPopover();
});
document.addEventListener("click", (event) => {
  if (!state.sortOpen) return;
  if (elements.sortPopover.contains(event.target) || elements.sortToggle.contains(event.target)) return;
  closeSortPopover();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && elements.aiGenerationDetail && !elements.aiGenerationDetail.hidden) {
    closeAiGenerationDetail();
    return;
  }
  if (event.key === "Escape" && !elements.codeEditor.hidden) {
    closeCodeEditor();
    return;
  }
  if (event.key === "Escape" && !elements.fileEditor.hidden) {
    closeFileEditor();
    return;
  }
  if (event.key === "Escape" && !elements.metadataEditor.hidden) {
    closeMetadataEditor();
  }
  if (event.key === "Escape" && !elements.shareDialog.hidden) {
    closeShareDialog();
  }
});
elements.languageSelect.addEventListener("change", (event) => setLanguage(event.target.value));
elements.themeModeButtons.forEach((button) => {
  button.addEventListener("click", () => setThemeMode(button.dataset.themeMode));
});
elements.avatarUploadTrigger.addEventListener("click", () => elements.avatarUpload.click());
elements.avatarUpload.addEventListener("change", (event) => uploadAvatar(event.target.files?.[0]));
elements.settingsOpen.addEventListener("click", toggleSettings);
elements.settingsBack.addEventListener("click", closeSettings);
elements.settingsTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    setSettingsTab(tab.dataset.settingsTab);
  });
});
elements.aiSettingsForm.addEventListener("submit", saveAiConfig);
elements.aiAssistantForm.addEventListener("submit", submitAssistantJob);
elements.autoBackup.addEventListener("change", (event) => setAutoBackup(event.target.checked));
elements.createBackup.addEventListener("click", createBackup);
elements.restoreBackup.addEventListener("click", () => elements.restoreBackupFile.click());
elements.restoreBackupFile.addEventListener("change", (event) => restoreBackupFile(event.target.files?.[0]));
elements.webdavSettingsForm.addEventListener("submit", saveWebdavSettings);
elements.testWebdav.addEventListener("click", testWebdavSettings);
elements.exportManifest.addEventListener("click", exportManifestData);
elements.exportPreferences.addEventListener("click", exportPreferencesData);
elements.testProvider.addEventListener("click", testProviderConfig);
elements.aiRunRefresh?.addEventListener("click", loadAiRuns);
elements.aiGenerationRefresh?.addEventListener("click", loadAiGenerationHistory);
elements.aiGenerationDetailClose?.addEventListener("click", closeAiGenerationDetail);
elements.aiGenerationDetail?.addEventListener("click", (event) => {
  if (event.target === elements.aiGenerationDetail) closeAiGenerationDetail();
});
elements.aiConversationRefresh?.addEventListener("click", loadAiConversationManagement);
elements.newItemForm.addEventListener("submit", submitNewItem);
elements.newGenerationToggle?.addEventListener("click", toggleNewGenerationOptions);
elements.newItemInput.addEventListener("input", resizeNewItemInput);
elements.newPromptResize?.addEventListener("pointerdown", startNewPromptResize);
elements.newPromptResize?.addEventListener("mousedown", startNewPromptResize);
elements.newFileTrigger?.addEventListener("click", openMaterialGeneratePicker);
elements.newFileRemove?.addEventListener("click", () => setPendingMaterialFiles([], { append: false }));
elements.newReferenceTrigger?.addEventListener("click", openMaterialReferencePicker);
elements.newReferenceRemove?.addEventListener("click", () => setPendingReferenceFile(null));
elements.readerClose.addEventListener("click", closeReader);
elements.readerEdit.addEventListener("click", () => {
  if (state.currentReaderItemId) openMetadataEditor(state.currentReaderItemId);
});
elements.readerFavorite.addEventListener("click", () => {
  if (state.currentReaderItemId) toggleFavorite(state.currentReaderItemId);
});
elements.readerArchive.addEventListener("click", () => {
  if (state.currentReaderItemId) toggleArchive(state.currentReaderItemId);
});
elements.readerShare.addEventListener("click", () => {
  if (state.currentReaderItemId) openShareDialog(state.currentReaderItemId);
});
elements.readerAiPanelOpen?.addEventListener("click", () => {
  if (state.currentReaderItemId) permanentlyDeleteItem(state.currentReaderItemId);
});
elements.readerFrame.addEventListener("load", bindReaderFrameScroll);
elements.shareForm.addEventListener("submit", submitShareDialog);
elements.shareCopy.addEventListener("click", copyCurrentShareLink);
elements.shareRevoke.addEventListener("click", revokeCurrentShare);
elements.shareCancel.addEventListener("click", closeShareDialog);
elements.shareCancelIcon.addEventListener("click", closeShareDialog);
elements.shareDialog.addEventListener("click", (event) => {
  if (event.target === elements.shareDialog) closeShareDialog();
});
elements.generateNoteForm.addEventListener("submit", submitGenerateNoteDialog);
elements.generateNoteCancel.addEventListener("click", closeGenerateNoteDialog);
elements.generateNoteCancelIcon.addEventListener("click", closeGenerateNoteDialog);
elements.generateNoteDialog.addEventListener("click", (event) => {
  if (event.target === elements.generateNoteDialog) closeGenerateNoteDialog();
});
elements.metadataForm.addEventListener("submit", saveMetadataEditor);
elements.metadataEditCode.addEventListener("click", () => openCodeEditor());
elements.metadataEditFile.addEventListener("click", () => openFileEditor());
elements.metadataCancel.addEventListener("click", closeMetadataEditor);
elements.metadataCancelIcon.addEventListener("click", closeMetadataEditor);
elements.metadataEditor.addEventListener("click", (event) => {
  if (event.target === elements.metadataEditor) closeMetadataEditor();
});
elements.metadataCollection.addEventListener("change", () => {
  if (elements.metadataCollection.value === "__add__") addMetadataCollection();
});
elements.codeEditorSave.addEventListener("click", () => saveCodeEditor());
elements.codeEditorSaveClose.addEventListener("click", () => saveCodeEditor({ closeAfterSave: true }));
elements.codeEditorClose.addEventListener("click", () => closeCodeEditor());
elements.codeEditorWrap.addEventListener("click", toggleCodeEditorWrap);
elements.codeEditorFullscreen.addEventListener("click", toggleCodeEditorFullscreen);
elements.codeEditorTextarea.addEventListener("input", markCodeEditorDirty);
elements.codeEditorTextarea.addEventListener("keyup", updateCodeEditorPosition);
elements.codeEditorTextarea.addEventListener("click", updateCodeEditorPosition);
elements.codeEditorTextarea.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
    event.preventDefault();
    saveCodeEditor({ closeAfterSave: event.shiftKey });
  } else if (event.key === "Tab") {
    insertCodeEditorTab(event);
  }
});
elements.codeEditor.addEventListener("click", (event) => {
  if (event.target === elements.codeEditor) closeCodeEditor();
});
elements.fileEditorModeText.addEventListener("click", () => setFileEditorMode("text"));
elements.fileEditorModeElement.addEventListener("click", () => setFileEditorMode("element"));
elements.fileEditorPanelResize.addEventListener("pointerdown", startFileEditorPanelResize);
elements.fileEditorPanelToggle.addEventListener("click", toggleFileEditorPanel);
elements.fileEditorUndo.addEventListener("click", () => stepFileEditorHistory(-1));
elements.fileEditorRedo.addEventListener("click", () => stepFileEditorHistory(1));
elements.fileEditorReset.addEventListener("click", resetFileEditorElement);
elements.fileEditorSave.addEventListener("click", () => saveFileEditor());
elements.fileEditorSaveClose.addEventListener("click", () => saveFileEditor({ closeAfterSave: true }));
elements.fileEditorClose.addEventListener("click", () => closeFileEditor());
elements.fileEditorText.addEventListener("input", () => applyFileEditorPanelChange({ pushHistory: false, changed: "text" }));
elements.fileEditorText.addEventListener("change", () => snapshotFileEditorHistory());
elements.fileEditorBold.addEventListener("click", () => toggleFileEditorTextStyle("bold"));
elements.fileEditorItalic.addEventListener("click", () => toggleFileEditorTextStyle("italic"));
elements.fileEditorUnderline.addEventListener("click", () => toggleFileEditorTextStyle("underline"));
elements.fileEditorStrike.addEventListener("click", () => toggleFileEditorTextStyle("strike"));
[
  [elements.fileEditorColor, "color"],
  [elements.fileEditorBackground, "backgroundColor"],
  [elements.fileEditorFontSize, "fontSize"],
  [elements.fileEditorLineHeight, "lineHeight"],
  [elements.fileEditorFontWeight, "fontWeight"],
  [elements.fileEditorTextAlign, "textAlign"],
].forEach(([control, changed]) => {
  control.addEventListener("input", () => applyFileEditorPanelChange({ pushHistory: false, changed }));
  control.addEventListener("change", () => snapshotFileEditorHistory());
});
window.addEventListener("message", handleFileEditorMessage);
elements.importEntries.forEach((button) => {
  button.addEventListener("click", openHtmlImportPicker);
});
elements.htmlImportFile.addEventListener("change", (event) => importHtmlFile(event.target.files?.[0]));
elements.materialGenerateFile.addEventListener("change", (event) => setPendingMaterialFiles(event.target.files, { append: true }));
elements.materialReferenceFile?.addEventListener("change", (event) => setPendingReferenceFile(event.target.files?.[0]));
window.addEventListener("hashchange", openFromHash);
window.matchMedia?.("(prefers-color-scheme: dark)").addEventListener("change", () => {
  if (state.themeMode === "system") applyTheme();
});
elements.loginForm.addEventListener("submit", submitLogin);
elements.logoutButton?.addEventListener("click", submitLogout);

boot();
registerServiceWorker();
