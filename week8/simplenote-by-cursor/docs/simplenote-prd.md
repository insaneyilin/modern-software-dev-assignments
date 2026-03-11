# Simplenote 产品需求文档 (PRD)

**文档版本**: 1.0  
**产品名称**: Simplenote  
**文档日期**: 2026-03-11  
**产品定位**: 极简主义笔记应用

---

## 1. 产品概述

### 1.1 产品背景

Simplenote 是一款面向个人用户的轻量级笔记工具，设计哲学是"简单至上"。产品摒弃复杂的功能堆砌，专注于提供流畅、无干扰的记录体验，让用户能够专注于内容创作本身。

### 1.2 产品愿景

成为用户随手记录想法的首选工具——像纸笔一样简单，却比纸笔更强大。

### 1.3 目标用户

| 用户类型 | 特征描述 | 核心痛点 |
|---------|---------|---------|
| 普通记录者 | 需要快速记录日常想法、待办事项 | 现有工具太重，打开慢，干扰多 |
| 文字工作者 | 作家、博主、学生，需要专注写作 | 排版功能干扰创作思路 |
| 知识管理者 | 需要整理和检索大量笔记 | 笔记一多就找不到，需要强大的搜索 |

---

## 2. 核心功能需求

### 2.1 功能清单

| 优先级 | 功能模块 | 功能描述 | 验收标准 |
|-------|---------|---------|---------|
| P0 | 笔记创建 | 用户可以创建新的空白笔记 | 一键创建，新笔记自动获得焦点 |
| P0 | 笔记编辑 | 用户可编辑笔记标题和内容 | 实时保存，无手动保存按钮 |
| P0 | 笔记删除 | 用户可以删除不需要的笔记 | 删除前需确认，防止误操作 |
| P0 | 笔记列表 | 侧边栏展示所有笔记 | 按最近更新时间倒序排列 |
| P0 | 全文搜索 | 按标题或内容搜索笔记 | 实时过滤，搜索结果即时展示 |
| P1 | 时间戳 | 显示笔记创建和更新时间 | 友好格式（如"2分钟前"） |
| P1 | 内容预览 | 列表中显示笔记内容预览 | 显示首行或前50字符 |
| P2 | 空状态引导 | 无笔记时的友好提示 | 引导用户创建第一条笔记 |

### 2.2 功能详细说明

#### 2.2.1 创建笔记

- **触发方式**: 侧边栏顶部的"新建笔记"按钮
- **默认状态**: 新笔记标题为空（显示"Untitled"占位），内容为空
- **交互细节**: 创建后自动聚焦标题输入框
- **即时反馈**: 新笔记立即出现在列表顶部并被选中

#### 2.2.2 编辑笔记

- **编辑区域**: 右侧编辑面板分为标题区（单行输入）和内容区（多行文本域）
- **保存机制**: 自动保存，用户停止输入后延迟保存
- **状态指示**: 显示保存状态（保存中/已保存/未保存）
- **输入验证**: 笔记至少需要有标题或内容才能保存

#### 2.2.3 删除笔记

- **触发方式**: 编辑面板右上角的删除图标
- **确认机制**: 弹出确认对话框，需用户确认后才删除
- **删除后**: 自动选择列表中下一条笔记（或上一条）

#### 2.2.4 笔记列表

- **排序规则**: 按最后更新时间倒序（最新修改在前）
- **列表项信息**: 标题 + 内容预览 + 更新时间
- **选中状态**: 当前编辑的笔记高亮显示
- **滚动行为**: 列表独立滚动，与编辑区互不干扰

#### 2.2.5 全文搜索

- **搜索位置**: 侧边栏顶部，搜索框常驻
- **搜索范围**: 同时搜索笔记标题和内容
- **实时性**: 输入即搜索，无需点击搜索按钮
- **结果展示**: 列表即时过滤，仅显示匹配笔记
- **空结果**: 显示"没有找到匹配的笔记"提示

---

## 3. 用户流程

### 3.1 核心用户旅程

```
+------------------------------------------------------------------+
|                     用户首次使用流程                             |
+------------------------------------------------------------------+
|                                                                   |
|  打开应用 ---> 看到空状态引导 ---> 点击"新建笔记"                 |
|      |                              |                             |
|      |                              v                             |
|      |                      新笔记出现在列表顶部                  |
|      |                              |                             |
|      |                              v                             |
|      |                      自动聚焦标题输入框                    |
|      |                              |                             |
|      |                              v                             |
|      |                      输入标题和内容                        |
|      |                              |                             |
|      |                              v                             |
|      |                      自动保存，状态显示"已保存"           |
|      |                              |                             |
|      +------------------------------+                             |
|                                   |                               |
|                                   v                               |
|                           继续编辑或搜索                          |
|                                                                   |
+-------------------------------------------------------------------+
```

### 3.2 日常操作流程

| 场景 | 用户目标 | 操作路径 | 预期结果 |
|------|---------|---------|---------|
| 记录灵感 | 快速记下想法 | 打开应用 -> 新建笔记 -> 输入 -> 自动保存 | 笔记已保存，下次可见 |
| 查找旧笔记 | 找到之前的记录 | 打开应用 -> 在搜索框输入关键词 -> 点击结果 | 进入对应笔记编辑页 |
| 清理笔记 | 删除不需要的内容 | 选中笔记 -> 点击删除 -> 确认 | 笔记被移除，列表更新 |
| 修改笔记 | 更新已有内容 | 从列表选择笔记 -> 编辑 -> 自动保存 | 内容更新，排序置顶 |

---

## 4. 界面设计需求

### 4.1 布局结构

```
+-------------------------------------------------------------+
|  Simplenote                                                 |
+-----------------+-------------------------------------------+
|                 |                                           |
|  +-----------+  |                                           |
|  | Search    |  |         Note Title                        |
|  +-----------+  |         +-------------------------+       |
|                 |         |                         |       |
|  +-----------+  |         |                         |       |
|  | + New Note|  |         |   Note Content Editor   |       |
|  +-----------+  |         |                         |       |
|                 |         |                         |       |
|  +-----------+  |         |                         |       |
|  | Note List |  |         |                         |       |
|  |           |  |         |                         |       |
|  | * Note 1  |  |         |                         |       |
|  |   preview |  |         |                         |       |
|  |   2m ago  |  |         |                         |       |
|  |           |  |         |                         |       |
|  | * Note 2  |  |         |                         |       |
|  |   preview |  |         |                         |       |
|  |   1h ago  |  |         |                         |       |
|  |           |  |         +-------------------------+       |
|  | ...       |  |                                           |
|  |           |  |                                     [X]   |
|  +-----------+  |                                    Delete |
|    Sidebar      |              Editor Panel                 |
|   (Fixed)       |            (Flexible)                     |
|                 |                                           |
+-----------------+-------------------------------------------+
```

### 4.2 设计原则

| 原则 | 说明 | 具体体现 |
|------|------|---------|
| 极简主义 | 每个元素都应有明确目的 | 无多余按钮、无复杂菜单 |
| 内容优先 | 让用户专注于写作 | 大面积编辑区，弱化装饰元素 |
| 即时反馈 | 操作结果立即可见 | 自动保存提示、实时搜索 |
| 一致性 | 相同操作有相同结果 | 统一的交互模式 |

### 4.3 视觉规范

- **配色**: 以白色/浅灰为底色，黑色文字，点缀色用于选中状态
- **字体**: 无衬线字体，标题略大，正文舒适阅读字号
- **间距**: 宽松的行间距和边距，减少视觉压迫感
- **图标**: 简洁线性图标，功能明确（搜索、新建、删除）

---

## 5. 数据需求

### 5.1 数据实体

**Note (笔记)**

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| ID | UUID | System generated | Immutable |
| Title | Text | User input | Can be empty, shows "Untitled" |
| Content | Long Text | User input | Can be empty |
| Created At | Timestamp | Auto recorded | Immutable |
| Updated At | Timestamp | Auto updated | Updates on every save |

### 5.2 数据操作

| Operation | Description | Trigger |
|-----------|-------------|---------|
| Create | Add a new note record | User clicks "New Note" |
| Read | Fetch note list or single note | App init, search, select note |
| Update | Modify note title or content | User edits, auto-saves |
| Delete | Permanently remove note | User confirms deletion |

### 5.3 数据持久化

- All data must persist across sessions
- Data sorted by update time (descending)
- Full-text search supported

---

## 6. 非功能性需求

### 6.1 性能需求

| Metric | Target | Description |
|--------|--------|-------------|
| First Load | < 3s | From open to interactive |
| Create Response | < 500ms | From click to editable |
| Save Delay | 1s debounce | Auto-save after typing stops |
| Search Response | < 100ms | From input to results display |

### 6.2 可用性需求

- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge latest 2 versions)
- **Responsive**: Desktop primary, tablet functional
- **Error Handling**: Friendly network error messages, auto-retry on recovery

### 6.3 安全需求

- Data transmission encrypted
- Delete confirmation to prevent accidents

---

## 7. 未来版本规划

### 7.1 近期可扩展功能 (P2)

| Feature | Description | User Value |
|---------|-------------|------------|
| Dark Mode | Dark theme toggle | Comfortable night usage |
| Tags | Add tags to notes | Better organization |
| Favorites | Pin/star important notes | Quick access to frequent notes |
| Export | Export as Markdown/TXT | Data portability |
| Keyboard Shortcuts | Ctrl+N for new, etc. | Efficiency boost |

### 7.2 远期愿景 (P3)

- User account system
- Cross-device sync
- Collaborative editing
- Version history

---

## 8. 附录

### 8.1 术语表

| Term | Definition |
|------|------------|
| CRUD | Create, Read, Update, Delete |
| Debounce | Delay mechanism, triggers after user stops input |
| Empty State | UI state when no data exists, usually includes guidance |

### 8.2 参考产品

- Simplenote (official version)
- Bear (iOS note app)
- Notion (more complex, as contrast reference)
