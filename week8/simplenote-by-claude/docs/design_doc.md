# Simplenote 开发设计文档

**文档版本**: 1.0
**文档日期**: 2026-03-11
**作者**: Development Team
**关联文档**: [PRD](./simplenote-prd.md) | [技术栈](./tech_stack.md)

---

## 1. 系统架构设计

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  React Components (Client & Server Components)        │ │
│  │  • NoteList (Client)                                   │ │
│  │  • NoteEditor (Client)                                 │ │
│  │  • SearchBar (Client)                                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/Server Actions
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Next.js App Router                                    │ │
│  │  • Server Actions (CRUD operations)                    │ │
│  │  • API Routes (optional REST endpoints)                │ │
│  │  • Server Components (initial data fetching)           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↕ Mongoose ODM
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MongoDB Database                                      │ │
│  │  • notes collection                                    │ │
│  │  • Indexes: updatedAt, title, content (text search)   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈说明

| 层级 | 技术选型 | 选型理由 |
|------|---------|---------|
| 前端框架 | Next.js 14/15 (App Router) | 全栈框架，SSR/SSG 支持，优化首屏加载 |
| UI 库 | React 18/19 | 组件化开发，生态成熟 |
| 类型系统 | TypeScript | 类型安全，减少运行时错误 |
| 样式方案 | Tailwind CSS | 快速开发，保持 UI 一致性 |
| 数据库 | MongoDB | 文档型数据库，Schema 灵活，全文搜索支持 |
| ODM | Mongoose | Schema 定义，数据验证，查询构建 |
| 状态管理 | React Hooks + Server Actions | 简化状态管理，减少客户端复杂度 |

---

## 2. 数据库设计

### 2.1 数据模型

**Note Collection**

```typescript
interface Note {
  _id: ObjectId;           // MongoDB 自动生成
  title: string;           // 笔记标题，可为空
  content: string;         // 笔记内容，可为空
  createdAt: Date;         // 创建时间，自动生成
  updatedAt: Date;         // 更新时间，自动更新
}
```

**Mongoose Schema 定义**

```typescript
import mongoose from 'mongoose';

const noteSchema = new mongoose.Schema(
  {
    title: {
      type: String,
      default: '',
      trim: true,
      maxlength: 500
    },
    content: {
      type: String,
      default: '',
      maxlength: 100000
    }
  },
  {
    timestamps: true  // 自动管理 createdAt 和 updatedAt
  }
);

// 全文搜索索引
noteSchema.index({ title: 'text', content: 'text' });

// 按更新时间排序索引
noteSchema.index({ updatedAt: -1 });

export const Note = mongoose.models.Note || mongoose.model('Note', noteSchema);
```

### 2.2 索引策略

| 索引类型 | 字段 | 用途 | 优先级 |
|---------|------|------|--------|
| Text Index | title, content | 全文搜索 | P0 |
| Single Index | updatedAt (desc) | 列表排序 | P0 |
| Unique Index | _id | 主键查询 | P0 (默认) |

---

## 3. API 设计

### 3.1 Server Actions (推荐方案)

使用 Next.js Server Actions 实现数据操作，减少 API 样板代码。

**文件结构**
```
app/
  actions/
    note-actions.ts    # 所有笔记相关的 Server Actions
```

**API 定义**

```typescript
// app/actions/note-actions.ts
'use server';

import { revalidatePath } from 'next/cache';
import { Note } from '@/db/models/note';
import { connectDB } from '@/db/db';

// 获取所有笔记
export async function getNotes() {
  await connectDB();
  const notes = await Note.find({})
    .sort({ updatedAt: -1 })
    .lean();
  return JSON.parse(JSON.stringify(notes));
}

// 获取单个笔记
export async function getNote(id: string) {
  await connectDB();
  const note = await Note.findById(id).lean();
  return JSON.parse(JSON.stringify(note));
}

// 创建笔记
export async function createNote() {
  await connectDB();
  const note = await Note.create({
    title: '',
    content: ''
  });
  revalidatePath('/');
  return JSON.parse(JSON.stringify(note));
}

// 更新笔记
export async function updateNote(id: string, data: { title?: string; content?: string }) {
  await connectDB();
  const note = await Note.findByIdAndUpdate(
    id,
    { $set: data },
    { new: true, runValidators: true }
  ).lean();
  revalidatePath('/');
  return JSON.parse(JSON.stringify(note));
}

// 删除笔记
export async function deleteNote(id: string) {
  await connectDB();
  await Note.findByIdAndDelete(id);
  revalidatePath('/');
  return { success: true };
}

// 搜索笔记
export async function searchNotes(query: string) {
  await connectDB();
  const notes = await Note.find(
    { $text: { $search: query } },
    { score: { $meta: 'textScore' } }
  )
    .sort({ score: { $meta: 'textScore' } })
    .lean();
  return JSON.parse(JSON.stringify(notes));
}
```

### 3.2 REST API (备选方案)

如果需要独立的 API 端点（如移动端调用），可使用 Route Handlers。

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | /api/notes | 获取所有笔记 | - | `{ notes: Note[] }` |
| GET | /api/notes/:id | 获取单个笔记 | - | `{ note: Note }` |
| POST | /api/notes | 创建笔记 | `{ title?, content? }` | `{ note: Note }` |
| PATCH | /api/notes/:id | 更新笔记 | `{ title?, content? }` | `{ note: Note }` |
| DELETE | /api/notes/:id | 删除笔记 | - | `{ success: true }` |
| GET | /api/notes/search?q=keyword | 搜索笔记 | - | `{ notes: Note[] }` |

---

## 4. 前端设计

### 4.1 组件架构

```
app/
  page.tsx                    # 主页面 (Server Component)
  components/
    Sidebar.tsx               # 侧边栏容器 (Client Component)
    SearchBar.tsx             # 搜索框 (Client Component)
    NewNoteButton.tsx         # 新建按钮 (Client Component)
    NoteList.tsx              # 笔记列表 (Client Component)
    NoteListItem.tsx          # 列表项 (Client Component)
    NoteEditor.tsx            # 编辑器 (Client Component)
    DeleteButton.tsx          # 删除按钮 (Client Component)
    EmptyState.tsx            # 空状态 (Client Component)
```

### 4.2 核心组件设计

#### 4.2.1 主页面 (page.tsx)

```typescript
// app/page.tsx
import { getNotes } from './actions/note-actions';
import Sidebar from './components/Sidebar';
import NoteEditor from './components/NoteEditor';

export default async function Home() {
  const initialNotes = await getNotes();

  return (
    <div className="flex h-screen">
      <Sidebar initialNotes={initialNotes} />
      <NoteEditor />
    </div>
  );
}
```

#### 4.2.2 侧边栏组件

```typescript
// app/components/Sidebar.tsx
'use client';

import { useState } from 'react';
import SearchBar from './SearchBar';
import NewNoteButton from './NewNoteButton';
import NoteList from './NoteList';

interface SidebarProps {
  initialNotes: Note[];
}

export default function Sidebar({ initialNotes }: SidebarProps) {
  const [notes, setNotes] = useState(initialNotes);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null);

  const filteredNotes = searchQuery
    ? notes.filter(note =>
        note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        note.content.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : notes;

  return (
    <aside className="w-80 border-r flex flex-col">
      <SearchBar value={searchQuery} onChange={setSearchQuery} />
      <NewNoteButton onNoteCreated={(note) => setNotes([note, ...notes])} />
      <NoteList
        notes={filteredNotes}
        selectedId={selectedNoteId}
        onSelect={setSelectedNoteId}
      />
    </aside>
  );
}
```

#### 4.2.3 笔记编辑器

```typescript
// app/components/NoteEditor.tsx
'use client';

import { useState, useEffect } from 'react';
import { updateNote } from '../actions/note-actions';
import { useDebounce } from '@/hooks/useDebounce';

interface NoteEditorProps {
  note: Note | null;
}

export default function NoteEditor({ note }: NoteEditorProps) {
  const [title, setTitle] = useState(note?.title || '');
  const [content, setContent] = useState(note?.content || '');
  const [saveStatus, setSaveStatus] = useState<'saved' | 'saving' | 'unsaved'>('saved');

  const debouncedTitle = useDebounce(title, 1000);
  const debouncedContent = useDebounce(content, 1000);

  useEffect(() => {
    if (!note) return;

    const save = async () => {
      setSaveStatus('saving');
      await updateNote(note._id, { title: debouncedTitle, content: debouncedContent });
      setSaveStatus('saved');
    };

    if (debouncedTitle !== note.title || debouncedContent !== note.content) {
      save();
    }
  }, [debouncedTitle, debouncedContent, note]);

  if (!note) {
    return <div className="flex-1 flex items-center justify-center text-gray-400">
      选择或创建一个笔记
    </div>;
  }

  return (
    <div className="flex-1 flex flex-col p-8">
      <input
        type="text"
        value={title}
        onChange={(e) => {
          setTitle(e.target.value);
          setSaveStatus('unsaved');
        }}
        placeholder="Untitled"
        className="text-3xl font-bold mb-4 outline-none"
      />
      <textarea
        value={content}
        onChange={(e) => {
          setContent(e.target.value);
          setSaveStatus('unsaved');
        }}
        placeholder="开始写作..."
        className="flex-1 outline-none resize-none"
      />
      <div className="text-sm text-gray-400 mt-2">
        {saveStatus === 'saved' && '已保存'}
        {saveStatus === 'saving' && '保存中...'}
        {saveStatus === 'unsaved' && '未保存'}
      </div>
    </div>
  );
}
```

### 4.3 自定义 Hooks

#### useDebounce Hook

```typescript
// hooks/useDebounce.ts
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
```

---

## 5. 关键技术实现

### 5.1 自动保存机制

**实现方案**: Debounce + useEffect

```typescript
// 1. 用户输入触发 state 更新
// 2. useDebounce hook 延迟 1 秒
// 3. useEffect 监听 debounced value 变化
// 4. 调用 Server Action 保存数据
// 5. 更新保存状态指示器
```

**优点**:
- 减少不必要的数据库写入
- 提升用户体验（无需手动保存）
- 避免频繁网络请求

### 5.2 全文搜索实现

**方案 1: MongoDB Text Index (推荐)**

```typescript
// 创建文本索引
noteSchema.index({ title: 'text', content: 'text' });

// 搜索查询
const notes = await Note.find(
  { $text: { $search: query } },
  { score: { $meta: 'textScore' } }
).sort({ score: { $meta: 'textScore' } });
```

**方案 2: 客户端过滤 (备选)**

```typescript
// 适用于笔记数量较少的情况
const filteredNotes = notes.filter(note =>
  note.title.toLowerCase().includes(query.toLowerCase()) ||
  note.content.toLowerCase().includes(query.toLowerCase())
);
```

### 5.3 实时搜索优化

```typescript
// 使用 debounce 减少搜索频率
const debouncedSearch = useDebounce(searchQuery, 300);

useEffect(() => {
  if (debouncedSearch) {
    searchNotes(debouncedSearch).then(setFilteredNotes);
  } else {
    setFilteredNotes(allNotes);
  }
}, [debouncedSearch]);
```

### 5.4 删除确认机制

```typescript
// 使用浏览器原生 confirm
const handleDelete = async () => {
  if (confirm('确定要删除这条笔记吗？')) {
    await deleteNote(noteId);
    // 更新 UI
  }
};

// 或使用自定义 Modal 组件
const [showDeleteModal, setShowDeleteModal] = useState(false);
```

---

## 6. 状态管理策略

### 6.1 状态分类

| 状态类型 | 存储位置 | 示例 | 管理方式 |
|---------|---------|------|---------|
| 服务端状态 | MongoDB | 笔记数据 | Server Actions + revalidatePath |
| 客户端 UI 状态 | React State | 选中的笔记 ID、搜索关键词 | useState |
| 表单状态 | React State | 编辑器输入内容 | useState + useDebounce |
| 缓存状态 | Next.js Cache | 笔记列表 | Server Components |

### 6.2 数据流

```
User Input → React State → Debounce → Server Action → MongoDB
                                                         ↓
User Interface ← revalidatePath ← Next.js Cache ← Response
```

---

## 7. 性能优化

### 7.1 首屏加载优化

| 优化项 | 实现方式 | 预期效果 |
|-------|---------|---------|
| SSR | Server Components 预渲染笔记列表 | 首屏可见时间 < 1s |
| 代码分割 | Next.js 自动分割 | 减少初始 JS 体积 |
| 图片优化 | next/image (如有图片) | 懒加载 + 自动格式转换 |
| 字体优化 | next/font | 字体预加载，避免闪烁 |

### 7.2 运行时性能优化

```typescript
// 1. 列表虚拟化 (笔记数量 > 100 时)
import { FixedSizeList } from 'react-window';

// 2. 组件 memo 化
const NoteListItem = memo(({ note, isSelected, onSelect }) => {
  // ...
});

// 3. 避免不必要的重渲染
const handleSelect = useCallback((id) => {
  setSelectedId(id);
}, []);
```

### 7.3 数据库查询优化

```typescript
// 1. 使用 lean() 返回普通对象
const notes = await Note.find({}).lean();

// 2. 只查询需要的字段
const notes = await Note.find({}).select('title content updatedAt').lean();

// 3. 分页查询 (未来扩展)
const notes = await Note.find({})
  .sort({ updatedAt: -1 })
  .limit(50)
  .skip(page * 50);
```

---

## 8. 错误处理

### 8.1 错误分类

| 错误类型 | 处理策略 | 用户提示 |
|---------|---------|---------|
| 网络错误 | 自动重试 3 次 | "网络连接失败，请检查网络" |
| 数据库错误 | 记录日志，返回通用错误 | "操作失败，请稍后重试" |
| 验证错误 | 返回具体错误信息 | "标题不能超过 500 字符" |
| 404 错误 | 重定向到首页 | "笔记不存在" |

### 8.2 错误边界

```typescript
// app/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h2 className="text-2xl mb-4">出错了</h2>
      <p className="text-gray-600 mb-4">{error.message}</p>
      <button
        onClick={reset}
        className="px-4 py-2 bg-blue-500 text-white rounded"
      >
        重试
      </button>
    </div>
  );
}
```

---

## 9. 测试策略

### 9.1 测试金字塔

```
        /\
       /  \      E2E Tests (Playwright)
      /____\     - 核心用户流程
     /      \
    /        \   Integration Tests (Jest + Testing Library)
   /__________\  - 组件交互、Server Actions
  /            \
 /______________\ Unit Tests (Jest)
                  - 工具函数、Hooks
```

### 9.2 测试用例

**单元测试**
```typescript
// __tests__/hooks/useDebounce.test.ts
describe('useDebounce', () => {
  it('should debounce value changes', async () => {
    // ...
  });
});
```

**集成测试**
```typescript
// __tests__/components/NoteEditor.test.tsx
describe('NoteEditor', () => {
  it('should auto-save after 1 second of inactivity', async () => {
    // ...
  });
});
```

**E2E 测试**
```typescript
// e2e/note-crud.spec.ts
test('user can create, edit, and delete a note', async ({ page }) => {
  // ...
});
```

---

## 10. 部署方案

### 10.1 环境配置

**环境变量**
```bash
# .env.local
MONGODB_URI=mongodb://localhost:27017/simplenote
NODE_ENV=development

# .env.production
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/simplenote
NODE_ENV=production
```

### 10.2 部署流程

**Vercel 部署 (推荐)**

```bash
# 1. 安装 Vercel CLI
npm i -g vercel

# 2. 登录
vercel login

# 3. 部署
vercel --prod
```

**配置项**
- Framework Preset: Next.js
- Build Command: `next build`
- Output Directory: `.next`
- Environment Variables: 在 Vercel Dashboard 配置

### 10.3 数据库部署

**MongoDB Atlas (推荐)**

1. 创建免费集群
2. 配置网络访问（允许 Vercel IP）
3. 创建数据库用户
4. 获取连接字符串
5. 在 Vercel 中配置 `MONGODB_URI`

---

## 11. 开发规范

### 11.1 代码规范

```json
// .eslintrc.json
{
  "extends": ["next/core-web-vitals", "prettier"],
  "rules": {
    "no-console": "warn",
    "prefer-const": "error"
  }
}
```

### 11.2 Git 工作流

```
main (生产环境)
  ↑
develop (开发环境)
  ↑
feature/xxx (功能分支)
```

### 11.3 提交规范

```
feat: 新增笔记搜索功能
fix: 修复自动保存延迟问题
docs: 更新 API 文档
style: 调整编辑器样式
refactor: 重构笔记列表组件
test: 添加 NoteEditor 测试用例
chore: 更新依赖版本
```

---

## 12. 项目里程碑

### Phase 1: MVP
- [ ] 项目初始化 + 数据库连接
- [ ] 笔记 CRUD 基础功能
- [ ] 基础 UI 布局

### Phase 2: 核心功能
- [ ] 自动保存机制
- [ ] 全文搜索
- [ ] 删除确认

### Phase 3: 优化
- [ ] 性能优化
- [ ] 错误处理
- [ ] 测试覆盖

### Phase 4: 部署
- [ ] 生产环境部署
- [ ] 监控配置
- [ ] 文档完善

---

## 13. 风险与挑战

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| MongoDB 连接不稳定 | 数据操作失败 | 实现连接池 + 自动重连 |
| 自动保存冲突 | 数据丢失 | 使用乐观锁 + 版本号 |
| 搜索性能差 | 用户体验下降 | 文本索引 + 分页加载 |
| 首屏加载慢 | 用户流失 | SSR + 代码分割 |

---

## 14. 参考资料

- [Next.js Documentation](https://nextjs.org/docs)
- [MongoDB Manual](https://docs.mongodb.com/manual/)
- [Mongoose Guide](https://mongoosejs.com/docs/guide.html)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs)
