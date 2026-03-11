```
┌──────────────────────────────────────────────────────────────┐
│  前端 + 后端 (全栈框架)                                         │
│  • Next.js 14/15 (App Router 模式)                            │
│    - Server Components (默认，减少客户端 JS)                  │
│    - Client Components (用于交互式 UI)                        │
│  • React 18/19 (服务端渲染 + 客户端hydration)                  │
│  • TypeScript (类型安全)                                      │
│  • Tailwind CSS (保持与 V1 一致的 UI 风格)                     │
├──────────────────────────────────────────────────────────────┤
│  后端 API 层                                                   │
│  • Next.js API Routes / Route Handlers                        │
│    - 或 Node.js + Express (分离后端)                          │
│  • 数据获取: Server Actions (Next.js 14+) 或 REST API         │
├──────────────────────────────────────────────────────────────┤
│  数据库                                                       │
│  MongoDB (与 V1 PostgreSQL 形成对比)                           │
│      • Mongoose (ODM) 或原生驱动                               │
│      • 文档型，Schema 灵活                                     │
├──────────────────────────────────────────────────────────────┤
│  部署 & 工具                                                   │
│  • 开发: next dev                                             │
│  • 构建: next build (SSR/SSG 输出)                            │
│  • 可选部署: Vercel (Next.js 原生支持)                         │
└──────────────────────────────────────────────────────────────┘
```
