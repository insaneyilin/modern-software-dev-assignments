## 熟悉项目结构

- app/ FastAPI 的 app 目录
  - main.py FastAPI 应用入口
    - 初始化 FastAPI 应用
    - 初始化数据库
    - 注册路由（action_items, notes）
    - 提供前端 HTML 和静态文件服务
  - db.py 数据库访问
    - SQLite 数据库连接管理
    - 表初始化（notes, action_items）
    - CRUD 封装
  - routers/ API 路由
    - action_items.py 动作项路由
    - notes.py 笔记路由
  - services/ 业务逻辑
    - extract.py 动作项提取，从文本中提取 action items (基于启发式规则)
- frontend/ 前端目录
  - index.html 单页面应用，包含笔记和动作项的输入和展示
    - 单文件 HTML，内联 CSS/JS
    - 通过 Fetch API 与后端交互
- tests/ 测试目录
  - test_extract.py 动作项提取测试

```
┌─────────────────────────────────────┐
│      Frontend (index.html)          │  ← 表示层
│      - 单页应用，原生 JS              │
└──────────────┬──────────────────────┘
               │ HTTP/REST API
┌──────────────▼──────────────────────┐
│      Routers (API 路由层)           │  ← 控制层
│      - notes.py                     │
│      - action_items.py              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Services (业务逻辑层)           │  ← 业务层
│      - extract.py                   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      DB (数据访问层)                 │  ← 数据层
│      - db.py                        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      SQLite Database                │  ← 持久化层
│      - app.db                       │
└─────────────────────────────────────┘
```

设计特点
- 分层设计：路由、业务逻辑、数据访问分离
- 模块化：使用 FastAPI 的 APIRouter 组织路由
- 简单直接：SQLite + 原生 HTML/JS，无复杂依赖
- 可测试：业务逻辑独立，便于单元测试

数据流
1. 用户输入文本 → 前端发送 POST /action-items/extract
2. Router 接收请求 → 调用 extract_action_items() 服务
3. Service 处理文本 → 返回提取的行动项列表
4. Router 调用 DB 层 → 保存到数据库
5. 返回 JSON 响应 → 前端渲染结果

### 什么是 FastAPI ?

FastAPI 是一个用于构建 Web API 的 Python 框架。

类比：餐厅服务员
- 服务员（FastAPI）接收点单（HTTP 请求）
- 把需求传给厨房（业务逻辑）
- 把菜品（响应）送回给顾客（前端）

```python
# week2/app/main.py
app = FastAPI(title="Action Item Extractor")
```

这行代码创建了一个 FastAPI 应用实例，相当于启动了一个“服务器”。

FastAPI 的作用：
1. 接收 HTTP 请求（GET、POST 等）
2. 解析请求数据（JSON、表单等）
3. 调用你的 Python 函数处理业务逻辑
4. 返回 JSON 或 HTML 响应

为什么选择 FastAPI？
- 自动生成 API 文档（访问 `/docs` 可查看）
- 类型提示支持，减少错误
- 性能较好
- 代码简洁

### 什么是路由

**路由 = URL 路径到函数的映射**

类比：快递地址
- 不同地址（URL）对应不同收件人（函数）
- 路由告诉服务器：当用户访问某个 URL 时，应该执行哪个函数

```python
# week2/app/main.py
@app.get("/")  # 路由：当访问根路径 "/" 时
def index() -> str:  # 执行这个函数
    html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
    return html_path.read_text(encoding="utf-8")
```

```python
# week2/app/routers/action_items.py
@router.post("/extract")  # 路由：POST 请求到 "/action-items/extract"
def extract(payload: Dict[str, Any]) -> Dict[str, Any]:
    # 执行提取行动项的逻辑
    items = extract_action_items(text)
    return {"note_id": note_id, "items": [...]}
```

路由的组成：
1. HTTP 方法：`GET`、`POST`、`PUT`、`DELETE`
   - `GET`：获取数据（如查看笔记）
   - `POST`：提交数据（如创建笔记、提取行动项）
2. URL 路径：如 `/notes`、`/action-items/extract`
3. 处理函数：收到请求后执行的代码

为什么需要路由？
- 没有路由：
    - 所有请求都进入同一个函数，需要手动判断 URL 和参数，代码混乱
- 有路由：
    - 不同功能对应不同 URL，结构清晰
    - 自动解析参数
    - 便于维护和扩展

**项目中的路由示例** ：

| URL | 方法 | 功能 |
|-----|------|------|
| `/` | GET | 返回首页 HTML |
| `/notes` | POST | 创建新笔记 |
| `/notes/{note_id}` | GET | 获取指定笔记 |
| `/action-items/extract` | POST | 从文本提取行动项 |
| `/action-items` | GET | 获取所有行动项 |
| `/action-items/{id}/done` | POST | 标记行动项完成 |

### 前后端交互流程

```
用户点击按钮 
    ↓
前端 JavaScript 代码执行
    ↓
使用 Fetch API 发送 HTTP 请求
    ↓
请求通过网络发送到后端服务器
    ↓
FastAPI 接收请求，执行对应路由的函数
    ↓
后端处理数据，返回 JSON 响应
    ↓
前端接收响应，更新页面显示
```

**什么是 Fetch API？**

Fetch API 是浏览器提供的 JavaScript 接口，用于发送 HTTP 请求。

类比：打电话
- 你（前端）拨号（URL）
- 说明需求（请求方法和数据）
- 等待对方（后端）回复
- 根据回复做后续处理

```javascript
// week2/frontend/index.html 第 40-44 行
const res = await fetch('/action-items/extract', {
  method: 'POST',  // 请求方法：POST（提交数据）
  headers: { 'Content-Type': 'application/json' },  // 告诉后端：我发送的是 JSON 格式
  body: JSON.stringify({ text, save_note: save }),  // 实际发送的数据
});
```

详细拆解：
1. `fetch('/action-items/extract', {...})`
   - 向 `/action-items/extract` 发送请求
2. `method: 'POST'`
   - 使用 POST 方法（用于提交数据）
3. `headers: { 'Content-Type': 'application/json' }`
   - 告诉后端：数据是 JSON 格式
4. `body: JSON.stringify({ text, save_note: save })`
   - 将 JavaScript 对象转为 JSON 字符串发送
5. `await res.json()`
   - 等待响应，并将 JSON 字符串解析为 JavaScript 对象

#### 完整的前后端交互示例

**前端代码（用户点击"Extract"按钮时）：**

```javascript
// 1. 用户点击按钮，触发这个函数
btn.addEventListener('click', async () => {
  // 2. 获取用户输入的文本
  const text = $('#text').value;
  const save = $('#save_note').checked;
  
  // 3. 显示"正在提取..."
  itemsEl.textContent = 'Extracting...';
  
  // 4. 发送请求到后端
  const res = await fetch('/action-items/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, save_note: save }),
  });
  
  // 5. 接收后端返回的数据
  const data = await res.json();
  
  // 6. 更新页面，显示提取的行动项
  itemsEl.innerHTML = data.items.map(it => (
    `<div class="item">${it.text}</div>`
  )).join('');
});
```

**后端代码（接收请求并处理）：**

```python
# week2/app/routers/action_items.py
@router.post("/extract")
def extract(payload: Dict[str, Any]) -> Dict[str, Any]:
    # 1. 接收前端发送的数据
    text = str(payload.get("text", "")).strip()
    
    # 2. 调用业务逻辑函数提取行动项
    items = extract_action_items(text)
    
    # 3. 保存到数据库
    ids = db.insert_action_items(items, note_id=note_id)
    
    # 4. 返回 JSON 响应给前端
    return {"note_id": note_id, "items": [{"id": i, "text": t} for i, t in zip(ids, items)]}
```

**数据格式转换** ：

```
前端 JavaScript 对象
    ↓ JSON.stringify()
JSON 字符串（通过网络传输）
    ↓ FastAPI 自动解析
后端 Python 字典
    ↓ 处理业务逻辑
后端 Python 字典
    ↓ FastAPI 自动转换
JSON 字符串（通过网络传输）
    ↓ res.json()
前端 JavaScript 对象
```

### 总结

1. FastAPI：用于构建 Web API 的 Python 框架，处理 HTTP 请求和响应
2. 路由：将 URL 映射到处理函数，让不同请求执行不同代码
3. Fetch API：浏览器提供的接口，用于前端向后端发送 HTTP 请求并接收响应

在你的项目中：
- 用户在前端输入文本并点击"Extract"
- 前端用 Fetch API 发送 POST 请求到 `/action-items/extract`
- FastAPI 路由接收请求，调用提取函数
- 后端返回 JSON，前端更新页面显示结果

这就是前后端分离的 Web 应用基本工作方式。

## 练习 1： Scaffold a New Feature

Ollama 的结构化输出功能，constrained decoding 技术。

普通的 “JSON mode” 是大多数 LLM 接口（OpenAI、Anthropic、Ollama 等）都提供的一种宽松格式开关。打开后，系统只会在提示词里追加一句类似
“You must output valid JSON.”
然后让模型自由生成。
没有任何硬性约束。

Ollama 的“结构化输出”并不是简单地“让模型尽量输出合法 JSON”，而是把 JSON Schema 作为硬约束直接注入到采样（sampling）阶段，让模型在每一步只能挑选符合 Schema 的 token，从而把格式错误率压到接近 0

“有限状态自动机”
- 节点 = Schema 里当前还能出现的 token 集合
- 边 = 下一个合法字符

引擎每生成一个新 token，都先问这张自动机“哪些 token 不会破坏 JSON 结构”，然后把其余 token 的概率强行置 0（logits 掩码），再做 softmax 和采样。
由于掩码是即时计算的，模型永远走不出 Schema 的“合法路径”，所以一次性就能吐出满足格式的完整 JSON，不需要后校验、重试或修复

## 练习 2： 单元测试

## 练习 3： 重构后端代码

Perform a refactor of the code in the backend, focusing in particular on well-defined API contracts/schemas, database layer cleanup, app lifecycle/configuration, error handling. 

## 练习 4： 使用 Agentic Mode 自动化小任务

1. Integrate the LLM-powered extraction as a new endpoint. Update the frontend to include an "Extract LLM" button that, when clicked, triggers the extraction process via the new endpoint.

2. Expose one final endpoint to retrieve all notes. Update the frontend to include a "List Notes" button that, when clicked, fetches and displays them.

## 练习 5： 生成 README 文件

Analyze the current codebase and generate a well-structured `README.md` file. The README should include, at a minimum:
- A brief overview of the project
- How to set up and run the project
- API endpoints and functionality
- Instructions for running the test suite

