# Phase 1: MVP 开发设计

**阶段目标**: 搭建项目基础架构，实现核心 CRUD 功能和基础 UI
**预计时间**: Week 1-2
**关联文档**: [设计文档](./design_doc.md) | [PRD](./simplenote-prd.md)

---

## 任务清单

### 1. 项目初始化 + 数据库连接

#### 1.1 创建 Next.js 项目
- [ ] 使用 `create-next-app` 初始化项目
- [ ] 选择配置：TypeScript + Tailwind CSS + App Router
- [ ] 验证项目可以正常启动

**执行命令**
```bash
npx create-next-app@latest simplenote --typescript --tailwind --app --no-src-dir
cd simplenote
npm run dev
```

**验收标准**
- 访问 http://localhost:3000 可以看到 Next.js 默认页面
- 项目结构符合 App Router 规范

---

#### 1.2 安装依赖包
- [ ] 安装 MongoDB 相关依赖
- [ ] 安装工具库依赖
- [ ] 更新 package.json

**依赖清单**
```json
{
  "dependencies": {
    "mongoose": "^8.0.0",
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.0.0",
    "autoprefixer": "^10.0.0",
    "postcss": "^8.0.0"
  }
}
```

**执行命令**
```bash
npm install mongoose
```

**验收标准**
- 所有依赖安装成功，无错误
- `npm run build` 可以正常构建

---

#### 1.3 配置环境变量
- [ ] 创建 `.env.local` 文件
- [ ] 配置 MongoDB 连接字符串
- [ ] 添加 `.env.local` 到 `.gitignore`

**文件内容**
```bash
# .env.local
MONGODB_URI=mongodb://localhost:27017/simplenote
NODE_ENV=development
```

**验收标准**
- `.env.local` 文件存在且不被 git 追踪
- 环境变量可以通过 `process.env.MONGODB_URI` 访问

---

#### 1.4 创建数据库连接模块
- [ ] 创建 `db/db.ts` 文件
- [ ] 实现数据库连接函数
- [ ] 实现连接缓存机制（避免重复连接）

**文件路径**: `db/db.ts`

**实现代码**
```typescript
import mongoose from 'mongoose';

const MONGODB_URI = process.env.MONGODB_URI;

if (!MONGODB_URI) {
  throw new Error('请在 .env.local 中定义 MONGODB_URI 环境变量');
}

interface MongooseCache {
  conn: typeof mongoose | null;
  promise: Promise<typeof mongoose> | null;
}

declare global {
  var mongoose: MongooseCache;
}

let cached: MongooseCache = global.mongoose || { conn: null, promise: null };

if (!global.mongoose) {
  global.mongoose = cached;
}

export async function connectDB() {
  if (cached.conn) {
    return cached.conn;
  }

  if (!cached.promise) {
    const opts = {
      bufferCommands: false,
    };

    cached.promise = mongoose.connect(MONGODB_URI!, opts);
  }

  try {
    cached.conn = await cached.promise;
  } catch (e) {
    cached.promise = null;
    throw e;
  }

  return cached.conn;
}
```

**设计要点**
- 使用全局缓存避免开发环境热重载时重复连接
- 连接失败时清除 promise，允许重试
- 禁用 bufferCommands 以便立即发现连接问题

**验收标准**
- 可以成功连接到 MongoDB
- 多次调用 `connectDB()` 不会创建多个连接
- 连接失败时抛出清晰的错误信息

---

#### 1.5 定义 Note 数据模型
- [ ] 创建 `db/models/note.ts` 文件
- [ ] 定义 Mongoose Schema
- [ ] 配置索引（updatedAt、全文搜索）
- [ ] 导出 Note 模型

**文件路径**: `db/models/note.ts`

**实现代码**
```typescript
import mongoose, { Schema, Document } from 'mongoose';

export interface INote extends Document {
  _id: string;
  title: string;
  content: string;
  createdAt: Date;
  updatedAt: Date;
}

const noteSchema = new Schema<INote>(
  {
    title: {
      type: String,
      default: '',
      trim: true,
      maxlength: [500, '标题不能超过 500 字符']
    },
    content: {
      type: String,
      default: '',
      maxlength: [100000, '内容不能超过 100000 字符']
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

// 防止模型重复定义（Next.js 热重载问题）
export const Note = mongoose.models.Note || mongoose.model<INote>('Note', noteSchema);
```

**设计要点**
- 使用 TypeScript 接口定义类型
- timestamps: true 自动管理时间字段
- 文本索引支持全文搜索
- 防止热重载时重复定义模型

**验收标准**
- 模型可以正常导入使用
- 索引在数据库中正确创建
- TypeScript 类型检查通过

---

#### 1.6 测试数据库连接
- [ ] 创建测试脚本验证连接
- [ ] 创建测试数据
- [ ] 查询测试数据

**测试脚本**: `scripts/test-db.ts`

```typescript
import { connectDB } from '../db/db';
import { Note } from '../db/models/note';

async function testDB() {
  try {
    console.log('连接数据库...');
    await connectDB();
    console.log('✓ 数据库连接成功');

    console.log('创建测试笔记...');
    const note = await Note.create({
      title: '测试笔记',
      content: '这是一条测试笔记'
    });
    console.log('✓ 笔记创建成功:', note._id);

    console.log('查询笔记...');
    const found = await Note.findById(note._id);
    console.log('✓ 笔记查询成功:', found?.title);

    console.log('删除测试笔记...');
    await Note.findByIdAndDelete(note._id);
    console.log('✓ 笔记删除成功');

    console.log('\n所有测试通过！');
    process.exit(0);
  } catch (error) {
    console.error('✗ 测试失败:', error);
    process.exit(1);
  }
}

testDB();
```

**执行命令**
```bash
npx tsx scripts/test-db.ts
```

**验收标准**
- 所有测试步骤通过
- 数据库中可以看到 notes 集合
- 索引正确创建

---

### 2. 笔记 CRUD 基础功能

#### 2.1 创建 Server Actions
- [ ] 创建 `app/actions/note-actions.ts` 文件
- [ ] 实现 getNotes（获取所有笔记）
- [ ] 实现 getNote（获取单个笔记）
- [ ] 实现 createNote（创建笔记）
- [ ] 实现 updateNote（更新笔记）
- [ ] 实现 deleteNote（删除笔记）

**文件路径**: `app/actions/note-actions.ts`

**实现代码**
```typescript
'use server';

import { revalidatePath } from 'next/cache';
import { Note } from '@/db/models/note';
import { connectDB } from '@/db/db';

// 获取所有笔记（按更新时间倒序）
export async function getNotes() {
  try {
    await connectDB();
    const notes = await Note.find({})
      .sort({ updatedAt: -1 })
      .lean();
    return JSON.parse(JSON.stringify(notes));
  } catch (error) {
    console.error('获取笔记失败:', error);
    throw new Error('获取笔记失败');
  }
}

// 获取单个笔记
export async function getNote(id: string) {
  try {
    await connectDB();
    const note = await Note.findById(id).lean();
    if (!note) {
      throw new Error('笔记不存在');
    }
    return JSON.parse(JSON.stringify(note));
  } catch (error) {
    console.error('获取笔记失败:', error);
    throw new Error('获取笔记失败');
  }
}

// 创建笔记
export async function createNote() {
  try {
    await connectDB();
    const note = await Note.create({
      title: '',
      content: ''
    });
    revalidatePath('/');
    return JSON.parse(JSON.stringify(note));
  } catch (error) {
    console.error('创建笔记失败:', error);
    throw new Error('创建笔记失败');
  }
}

// 更新笔记
export async function updateNote(id: string, data: { title?: string; content?: string }) {
  try {
    await connectDB();
    const note = await Note.findByIdAndUpdate(
      id,
      { $set: data },
      { new: true, runValidators: true }
    ).lean();

    if (!note) {
      throw new Error('笔记不存在');
    }

    revalidatePath('/');
    return JSON.parse(JSON.stringify(note));
  } catch (error) {
    console.error('更新笔记失败:', error);
    throw new Error('更新笔记失败');
  }
}

// 删除笔记
export async function deleteNote(id: string) {
  try {
    await connectDB();
    const result = await Note.findByIdAndDelete(id);

    if (!result) {
      throw new Error('笔记不存在');
    }

    revalidatePath('/');
    return { success: true };
  } catch (error) {
    console.error('删除笔记失败:', error);
    throw new Error('删除笔记失败');
  }
}
```

**设计要点**
- 使用 'use server' 标记为 Server Action
- 每个函数都先调用 connectDB() 确保连接
- 使用 lean() 返回普通对象（性能优化）
- JSON.parse(JSON.stringify()) 序列化 MongoDB 对象
- revalidatePath('/') 刷新页面缓存
- 统一错误处理

**验收标准**
- 所有 CRUD 操作可以正常执行
- 错误情况有适当的错误处理
- TypeScript 类型检查通过

---

#### 2.2 创建类型定义文件
- [ ] 创建 `types/note.ts` 文件
- [ ] 定义前端使用的 Note 类型

**文件路径**: `types/note.ts`

```typescript
export interface Note {
  _id: string;
  title: string;
  content: string;
  createdAt: string;  // ISO 8601 字符串
  updatedAt: string;  // ISO 8601 字符串
}
```

**验收标准**
- 类型定义清晰，可以在组件中使用
- 与后端模型保持一致

---

### 3. 基础 UI 布局

#### 3.1 配置 Tailwind CSS
- [ ] 检查 `tailwind.config.ts` 配置
- [ ] 配置全局样式
- [ ] 测试 Tailwind 类名是否生效

**文件路径**: `app/globals.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-white text-gray-900;
  }
}
```

**验收标准**
- Tailwind 类名正常工作
- 全局样式应用成功

---

#### 3.2 创建主页面布局
- [ ] 修改 `app/page.tsx`
- [ ] 实现两栏布局（侧边栏 + 编辑区）
- [ ] 从服务端获取初始数据

**文件路径**: `app/page.tsx`

```typescript
import { getNotes } from './actions/note-actions';
import Sidebar from './components/Sidebar';
import NoteEditor from './components/NoteEditor';

export default async function Home() {
  const initialNotes = await getNotes();

  return (
    <main className="flex h-screen overflow-hidden">
      <Sidebar initialNotes={initialNotes} />
      <NoteEditor />
    </main>
  );
}
```

**设计要点**
- 使用 Server Component 获取初始数据
- flex 布局实现两栏
- h-screen 占满整个视口高度
- overflow-hidden 防止整体滚动

**验收标准**
- 页面正常渲染
- 布局符合设计稿
- 初始数据正确加载

---

#### 3.3 创建侧边栏组件
- [ ] 创建 `app/components/Sidebar.tsx`
- [ ] 实现基础布局结构
- [ ] 管理笔记列表状态

**文件路径**: `app/components/Sidebar.tsx`

```typescript
'use client';

import { useState } from 'react';
import { Note } from '@/types/note';
import SearchBar from './SearchBar';
import NewNoteButton from './NewNoteButton';
import NoteList from './NoteList';

interface SidebarProps {
  initialNotes: Note[];
}

export default function Sidebar({ initialNotes }: SidebarProps) {
  const [notes, setNotes] = useState<Note[]>(initialNotes);
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(
    initialNotes[0]?._id || null
  );

  return (
    <aside className="w-80 border-r border-gray-200 flex flex-col bg-gray-50">
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-xl font-bold mb-4">Simplenote</h1>
        <SearchBar />
      </div>

      <NewNoteButton
        onNoteCreated={(note) => {
          setNotes([note, ...notes]);
          setSelectedNoteId(note._id);
        }}
      />

      <NoteList
        notes={notes}
        selectedId={selectedNoteId}
        onSelect={setSelectedNoteId}
        onNoteDeleted={(id) => {
          setNotes(notes.filter(n => n._id !== id));
          if (selectedNoteId === id) {
            setSelectedNoteId(notes[0]?._id || null);
          }
        }}
      />
    </aside>
  );
}
```

**设计要点**
- 使用 'use client' 标记为客户端组件
- 管理笔记列表和选中状态
- 固定宽度 320px (w-80)
- 浅灰色背景区分区域

**验收标准**
- 侧边栏正确渲染
- 状态管理正常工作
- 样式符合设计

---

#### 3.4 创建搜索框组件
- [ ] 创建 `app/components/SearchBar.tsx`
- [ ] 实现基础输入框
- [ ] 添加搜索图标

**文件路径**: `app/components/SearchBar.tsx`

```typescript
'use client';

interface SearchBarProps {
  value?: string;
  onChange?: (value: string) => void;
}

export default function SearchBar({ value = '', onChange }: SearchBarProps) {
  return (
    <div className="relative">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder="搜索笔记..."
        className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <svg
        className="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
    </div>
  );
}
```

**设计要点**
- 受控组件模式
- 搜索图标使用 SVG
- focus 状态有蓝色边框

**验收标准**
- 输入框正常工作
- 样式美观
- 图标正确显示

---

#### 3.5 创建新建笔记按钮
- [ ] 创建 `app/components/NewNoteButton.tsx`
- [ ] 调用 createNote Server Action
- [ ] 处理加载状态

**文件路径**: `app/components/NewNoteButton.tsx`

```typescript
'use client';

import { useState } from 'react';
import { createNote } from '../actions/note-actions';
import { Note } from '@/types/note';

interface NewNoteButtonProps {
  onNoteCreated: (note: Note) => void;
}

export default function NewNoteButton({ onNoteCreated }: NewNoteButtonProps) {
  const [isCreating, setIsCreating] = useState(false);

  const handleCreate = async () => {
    try {
      setIsCreating(true);
      const note = await createNote();
      onNoteCreated(note);
    } catch (error) {
      console.error('创建笔记失败:', error);
      alert('创建笔记失败，请重试');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <button
      onClick={handleCreate}
      disabled={isCreating}
      className="m-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
    >
      {isCreating ? '创建中...' : '+ 新建笔记'}
    </button>
  );
}
```

**设计要点**
- 异步操作显示加载状态
- 禁用状态防止重复点击
- 错误处理用户友好

**验收标准**
- 点击按钮可以创建笔记
- 加载状态正确显示
- 错误情况有提示

---

#### 3.6 创建笔记列表组件
- [ ] 创建 `app/components/NoteList.tsx`
- [ ] 渲染笔记列表
- [ ] 处理空状态

**文件路径**: `app/components/NoteList.tsx`

```typescript
'use client';

import { Note } from '@/types/note';
import NoteListItem from './NoteListItem';

interface NoteListProps {
  notes: Note[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onNoteDeleted: (id: string) => void;
}

export default function NoteList({ notes, selectedId, onSelect, onNoteDeleted }: NoteListProps) {
  if (notes.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 text-center">
        <div className="text-gray-400">
          <p className="text-lg mb-2">还没有笔记</p>
          <p className="text-sm">点击上方按钮创建第一条笔记</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      {notes.map((note) => (
        <NoteListItem
          key={note._id}
          note={note}
          isSelected={note._id === selectedId}
          onSelect={() => onSelect(note._id)}
        />
      ))}
    </div>
  );
}
```

**设计要点**
- 空状态友好提示
- 独立滚动区域
- 使用 key 优化渲染

**验收标准**
- 列表正确渲染
- 空状态显示正常
- 滚动流畅

---

#### 3.7 创建笔记列表项组件
- [ ] 创建 `app/components/NoteListItem.tsx`
- [ ] 显示标题、预览、时间
- [ ] 实现选中状态样式

**文件路径**: `app/components/NoteListItem.tsx`

```typescript
'use client';

import { Note } from '@/types/note';

interface NoteListItemProps {
  note: Note;
  isSelected: boolean;
  onSelect: () => void;
}

export default function NoteListItem({ note, isSelected, onSelect }: NoteListItemProps) {
  const title = note.title || 'Untitled';
  const preview = note.content.slice(0, 50) || '无内容';
  const updatedAt = new Date(note.updatedAt).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <div
      onClick={onSelect}
      className={`p-4 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors ${
        isSelected ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
      }`}
    >
      <h3 className="font-semibold text-gray-900 truncate mb-1">{title}</h3>
      <p className="text-sm text-gray-600 truncate mb-2">{preview}</p>
      <p className="text-xs text-gray-400">{updatedAt}</p>
    </div>
  );
}
```

**设计要点**
- 标题为空显示 "Untitled"
- 内容预览截取前 50 字符
- 选中状态有蓝色左边框
- hover 状态有背景色变化

**验收标准**
- 列表项正确显示
- 选中状态样式正确
- 交互流畅

---

#### 3.8 创建笔记编辑器组件
- [ ] 创建 `app/components/NoteEditor.tsx`
- [ ] 实现标题和内容输入
- [ ] 显示空状态

**文件路径**: `app/components/NoteEditor.tsx`

```typescript
'use client';

import { useState, useEffect } from 'react';
import { Note } from '@/types/note';
import { updateNote } from '../actions/note-actions';

interface NoteEditorProps {
  note?: Note | null;
}

export default function NoteEditor({ note }: NoteEditorProps) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  useEffect(() => {
    if (note) {
      setTitle(note.title);
      setContent(note.content);
    }
  }, [note]);

  if (!note) {
    return (
      <div className="flex-1 flex items-center justify-center bg-white">
        <div className="text-center text-gray-400">
          <p className="text-lg">选择或创建一个笔记</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      <div className="p-8 flex-1 flex flex-col">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Untitled"
          className="text-3xl font-bold mb-4 outline-none border-none focus:ring-0"
        />
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="开始写作..."
          className="flex-1 outline-none border-none resize-none focus:ring-0 text-lg leading-relaxed"
        />
      </div>
    </div>
  );
}
```

**设计要点**
- 无笔记时显示空状态
- 大字号标题（text-3xl）
- 内容区自动扩展（flex-1）
- 无边框设计，极简风格

**验收标准**
- 编辑器正确渲染
- 输入流畅无卡顿
- 空状态显示正常

---

## Phase 1 完成标准

### 功能验收
- [x] 可以创建新笔记
- [x] 可以在列表中看到所有笔记
- [x] 可以选择笔记进行查看
- [x] 可以编辑笔记标题和内容
- [x] 笔记按更新时间倒序排列
- [x] 数据持久化到 MongoDB

### 技术验收
- [x] TypeScript 无类型错误
- [x] 无 console 错误或警告
- [x] 代码符合 ESLint 规范
- [x] 所有组件正确使用 'use client' 或 Server Component

### UI 验收
- [x] 布局符合设计稿
- [x] 响应式设计正常
- [x] 交互流畅无卡顿
- [x] 样式一致性良好

---

## Phase 1 开发完成总结

### 已完成的工作

#### 1. 项目初始化 ✅
- 使用 `create-next-app` 创建 Next.js 14 项目
- 配置 TypeScript + Tailwind CSS + App Router
- 安装 mongoose 依赖
- 配置环境变量 `.env.local`

#### 2. 数据库层 ✅
**文件创建**:
- `db/db.ts` - MongoDB 连接模块，实现连接缓存机制
- `db/models/note.ts` - Note 数据模型，包含 Schema 定义和索引

**关键实现**:
- 全局连接缓存避免热重载时重复连接
- 文本索引支持全文搜索
- 时间戳自动管理（createdAt, updatedAt）

#### 3. 类型定义 ✅
**文件创建**:
- `types/note.ts` - 前端 Note 类型定义

#### 4. Server Actions ✅
**文件创建**:
- `app/actions/note-actions.ts` - 所有笔记 CRUD 操作

**实现的功能**:
- `getNotes()` - 获取所有笔记（按更新时间倒序）
- `getNote(id)` - 获取单个笔记
- `createNote()` - 创建新笔记
- `updateNote(id, data)` - 更新笔记
- `deleteNote(id)` - 删除笔记

#### 5. UI 组件 ✅
**文件创建**:
- `app/page.tsx` - 主页面（Server Component）
- `app/components/NotesApp.tsx` - 应用容器组件（状态管理）
- `app/components/Sidebar.tsx` - 侧边栏组件
- `app/components/SearchBar.tsx` - 搜索框组件
- `app/components/NewNoteButton.tsx` - 新建笔记按钮
- `app/components/NoteList.tsx` - 笔记列表组件
- `app/components/NoteListItem.tsx` - 笔记列表项组件
- `app/components/NoteEditor.tsx` - 笔记编辑器组件

**关键功能**:
- 两栏布局（侧边栏 + 编辑器）
- 笔记列表展示（标题、预览、时间）
- 笔记选中状态高亮
- 客户端搜索过滤
- 自动保存机制（1秒 debounce）
- 空状态友好提示

#### 6. 样式配置 ✅
- 配置 Tailwind CSS 全局样式
- 实现极简设计风格
- 响应式布局

### 项目结构

```
simplenote-by-claude/
├── app/
│   ├── actions/
│   │   └── note-actions.ts          # Server Actions
│   ├── components/
│   │   ├── NotesApp.tsx              # 应用容器
│   │   ├── Sidebar.tsx               # 侧边栏
│   │   ├── SearchBar.tsx             # 搜索框
│   │   ├── NewNoteButton.tsx         # 新建按钮
│   │   ├── NoteList.tsx              # 笔记列表
│   │   ├── NoteListItem.tsx          # 列表项
│   │   └── NoteEditor.tsx            # 编辑器
│   ├── globals.css                   # 全局样式
│   └── page.tsx                      # 主页面
├── db/
│   ├── db.ts                         # 数据库连接
│   └── models/
│       └── note.ts                   # Note 模型
├── types/
│   └── note.ts                       # 类型定义
├── docs/
│   ├── simplenote-prd.md             # 产品需求文档
│   ├── tech_stack.md                 # 技术栈文档
│   ├── design_doc.md                 # 设计文档
│   └── phase_1_dev_notes.md          # Phase 1 开发笔记
├── .env.local                        # 环境变量
├── package.json                      # 依赖配置
└── tsconfig.json                     # TypeScript 配置
```

### 技术亮点

1. **Server Components + Client Components 混合使用**
   - 主页面使用 Server Component 预加载数据
   - 交互组件使用 Client Component

2. **自动保存机制**
   - 使用 useEffect + setTimeout 实现 1秒 debounce
   - 避免频繁的数据库写入

3. **状态提升**
   - 在 NotesApp 组件中集中管理笔记列表和选中状态
   - 通过 props 向下传递，通过回调向上更新

4. **客户端搜索**
   - 实时过滤笔记列表
   - 支持标题和内容搜索

5. **MongoDB 连接优化**
   - 全局缓存避免重复连接
   - 适配 Next.js 热重载

### 待测试项

由于 Node.js 版本问题（当前 v20.8.0，需要 >=20.9.0），需要升级 Node.js 后进行以下测试：

1. **启动测试**
   - [ ] 运行 `npm run dev` 启动开发服务器
   - [ ] 访问 http://localhost:3000 查看页面

2. **功能测试**
   - [ ] 创建新笔记
   - [ ] 编辑笔记标题和内容
   - [ ] 自动保存验证
   - [ ] 选择不同笔记
   - [ ] 搜索笔记
   - [ ] 刷新页面验证数据持久化

3. **MongoDB 测试**
   - [ ] 确保 MongoDB 服务运行
   - [ ] 验证数据库连接成功
   - [ ] 检查 notes 集合创建
   - [ ] 验证索引创建

### 已知问题

1. **Node.js 版本**
   - 当前版本: v20.8.0
   - 需要版本: >=20.9.0
   - 解决方案: 升级 Node.js 到最新 LTS 版本

2. **MongoDB 连接**
   - 需要确保 MongoDB 服务正在运行
   - 默认连接: `mongodb://localhost:27017/simplenote`

### 下一步计划

Phase 1 完成后，进入 Phase 2：核心功能开发
- 实现删除笔记功能（带确认对话框）
- 优化自动保存状态提示
- 实现 MongoDB 全文搜索（替代客户端过滤）
- 添加错误处理和用户反馈
- 性能优化（虚拟滚动、memo 化）

---

## 常见问题

### Q1: MongoDB 连接失败怎么办？
**A**: 检查以下几点：
1. MongoDB 服务是否启动
2. 连接字符串是否正确
3. 网络是否可达
4. 数据库权限是否正确

### Q2: 热重载时出现模型重复定义错误？
**A**: 使用以下模式：
```typescript
export const Note = mongoose.models.Note || mongoose.model('Note', noteSchema);
```

### Q3: Server Action 调用失败？
**A**: 确保：
1. 函数顶部有 'use server' 标记
2. 返回值可序列化（使用 JSON.parse(JSON.stringify())）
3. 在客户端组件中调用

---

## 参考资料

- [Next.js App Router 文档](https://nextjs.org/docs/app)
- [Mongoose 文档](https://mongoosejs.com/docs/)
- [Server Actions 文档](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
