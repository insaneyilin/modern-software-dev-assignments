## Rails 里的路由与控制器

### 1. 什么是控制器（Controller）？

**控制器是 MVC 架构中的"协调者"**，负责接收用户请求、调用模型处理数据、选择视图渲染响应。

#### 类比理解

想象餐厅的点餐流程：

```
顾客（浏览器）→ 服务员（控制器）→ 厨师（模型）→ 摆盘（视图）

顾客："我要一份牛排"
服务员：接收订单 → 交给厨师 → 厨师做好 → 服务员端给顾客
```

#### 代码示例

```ruby
class NotesController < ApplicationController
  # 用户访问 /notes 时执行
  def index
    @notes = Note.recent      # 调用模型查询数据
    @note = @notes.first      # 处理数据
    # 自动渲染 views/notes/index.html.erb
  end
end
```

#### 控制器的职责

| 职责 | 说明 |
|------|------|
| 接收请求 | 处理浏览器发来的 HTTP 请求 |
| 调用模型 | 使用 ActiveRecord 操作数据库 |
| 准备数据 | 设置实例变量（如 `@notes`）供视图使用 |
| 选择视图 | 决定渲染哪个模板文件 |
| 返回响应 | 发送 HTML/JSON/重定向给浏览器 |

---

### 2. 路由（Routes）是什么？

**路由是"指路牌"**，决定哪个 URL 对应哪个控制器动作。

#### 类比理解

就像餐厅菜单上的编号：

```
菜单上的编号 → 对应哪道菜
  /notes      → NotesController#index (列表)
  /notes/1    → NotesController#show (详情)
  /notes/new  → NotesController#new (新建表单)
```

#### 路由配置

```ruby
# config/routes.rb
Rails.application.routes.draw do
  root "notes#index"                    # GET / → NotesController#index
  
  resources :notes do                   # 自动生成以下路由
    collection do
      get :search                       # GET /notes/search
    end
  end
end
```

#### 生成的路由表

执行 `bin/rails routes` 可以看到：

| HTTP Verb | Path | Controller#Action | 用途 |
|-----------|------|-------------------|------|
| GET | / | notes#index | 首页 |
| GET | /notes | notes#index | 笔记列表 |
| POST | /notes | notes#create | 创建笔记 |
| GET | /notes/:id | notes#show | 显示单个笔记 |
| PATCH | /notes/:id | notes#update | 更新笔记 |
| DELETE | /notes/:id | notes#destroy | 删除笔记 |
| GET | /notes/search | notes#search | 搜索笔记 |

---

### 3. 为什么是 ERB 而不是 HTML？

#### ERB 是什么？

**ERB = Embedded Ruby（嵌入式 Ruby）**

它是 HTML + Ruby 代码的混合体，让你可以在 HTML 中嵌入动态内容。

#### 对比

**纯 HTML（静态）**
```html
<h1>我的笔记</h1>
<p>这里有 10 条笔记</p>  <!-- 数字是写死的 -->
```

**ERB（动态）**
```erb
<h1><%= @note.display_title %></h1>  <!-- 显示笔记标题 -->
<p>这里有 <%= @notes.count %> 条笔记</p>  <!-- 动态统计数量 -->
```

#### ERB 语法

| 语法 | 作用 | 示例 |
|------|------|------|
| `<%= %>` | 输出 Ruby 表达式结果 | `<%= @note.title %>` |
| `<% %>` | 执行 Ruby 代码（不输出） | `<% if @notes.empty? %>` |
| `<%= render %>` | 渲染部分模板 | `<%= render "sidebar" %>` |

#### 为什么 Rails 使用 ERB？

| 优势 | 说明 |
|------|------|
| 服务端渲染 | 在服务器生成完整 HTML，首屏加载快 |
| 动态内容 | 可以从数据库读取数据插入页面 |
| 代码复用 | `render "sidebar"` 可以复用组件 |
| 安全性 | 自动转义 HTML，防止 XSS 攻击 |
| 简洁 | 不用写 JavaScript 就能展示动态数据 |

#### 工作流程

```
用户访问 /notes
       ↓
Rails 找到对应控制器
       ↓
控制器查询 @notes = Note.all
       ↓
渲染 views/notes/index.html.erb
       ↓
ERB 模板中 <%= @notes %> 被替换为真实数据
       ↓
生成完整 HTML 发送给浏览器
```

---

### 总结

| 概念 | 一句话解释 |
|------|-----------|
| **控制器** | 接收请求 → 处理数据 → 选择视图的"指挥官" |
| **路由** | URL 到控制器动作的"地图" |
| **ERB** | 能在 HTML 中嵌入 Ruby 代码的模板语言，实现动态页面 |

这三者配合构成了 Rails 的**服务端渲染**架构，浏览器收到的永远是生成好的 HTML，而不是像 React/Vue 那样在浏览器端组装。
