### Coding Agent

“Coding Agent”指的是一个能够自动完成编程任务的AI系统，比如根据自然语言描述生成代码、修改代码、运行测试等。

#### 回顾 Prompt 的概念

| 英文术语             | 中文解释 | 作用                               |
| ---------------- | ---- | -------------------------------- |
| System prompt    | 系统提示 | 定义LLM的整体行为规则，比如“你是一个助手，不要输出有害内容” |
| User prompt      | 用户提示 | 用户输入的具体请求，比如“帮我写一个快速排序”          |
| Assistant prompt | 助手提示 | LLM的回应内容，比如“以下是快速排序的Python实现……”  |

System prompt，决定了Agent的行为边界和风格

#### 构建Coding Agent的核心流程

1. **Read in terminal and keep appending to conversation**
    - 从终端读取用户输入，并持续追加到对话历史中（保持上下文）。
2. **Tell LLM what tools are available**
    - 向LLM说明它可以调用哪些工具（如读文件、写文件、运行命令等）。
3. **It asks for tool use at appropriate time**
    - LLM在需要时会主动请求调用工具，比如“请帮我读取main.py文件”。
4. **You execute tool offline and return response**
    - 系统在本地执行工具，并将结果返回给LLM。
5. **“Read_file”, “List_dir”, “Edit_file”**
    - 举例说明常用工具：读取文件、列出目录、编辑文件。
6. **Create a new file, edit a new file**
     - Agent不仅能读，还能写和修改代码文件

总结：
- **REPL（Read-Eval-Print Loop）** 的扩展版本，加入了LLM和工具调用
- LLM **不直接执行代码**，而是请求 **调用工具** ，由系统安全地执行

#### Claude Code 的内部机制

The “Secret” Sauce.

| 技术点                                           | 中文解释         | 详细说明                                                      |
| --------------------------------------------- | ------------ | --------------------------------------------------------- |
| Front-load context with tiny targeted prompts | 用小型定向提示前置上下文 | 在对话开始前，先给LLM注入关键背景信息，避免它“跑偏”                              |
| System reminders everywhere                   | 系统提醒无处不在     | 在系统提示、用户提示、工具调用、工具结果中反复插入提醒，防止LLM“遗忘”目标                   |
| Command prefix extraction                     | 命令前缀提取       | 让LLM输出结构化文本（如`<command>read_file:main.py</command>`），方便解析 |
| Spawns sub agents                             | 生成子智能体       | 将复杂任务拆分给多个子Agent，避免上下文过长或混乱                               |

总结：
- 这些技巧是构建**可靠、可控、可扩展**Coding Agent的关键。
- 特别是“System reminders everywhere”，是防止LLM“ drift（漂移）”的核心手段。
- “子智能体”机制类似于**多线程或微服务**，每个子Agent专注一个小任务。

#### 从零构建一个 Coding Agent

课程代码 `coding_agent_from_scratch_lecture.py`

##### 1 核心组件

**工具定义（Tools）**

这里的工具就是 Python 的函数，Agent 可以通过调用这些函数来完成任务。

- `read_file_tool`: 读取文件内容
- `list_files_tool`: 列出目录中的文件和文件夹
- `edit_file_tool`: 编辑文件（支持创建新文件或替换内容）

**工具注册表（Tool Registry）**

通过注册表，Agent 可以知道它有哪些工具可以调用。

```python
TOOL_REGISTRY = {
    "read_file": read_file_tool,
    "list_files": list_files_tool,
    "edit_file": edit_file_tool 
}
```

##### 2 系统提示（System Prompt）

```python
SYSTEM_PROMPT = """
You are a coding assistant whose goal it is to help us solve coding tasks. 
You have access to a series of tools you can execute. Hear are the tools you can execute:

{tool_list_repr}

When you want to use a tool, reply with exactly one line in the format: 'tool: TOOL_NAME({{JSON_ARGS}})' and nothing else.
Use compact single-line JSON with double quotes. After receiving a tool_result(...) message, continue the task.
If no tool is needed, respond normally.
"""
```

这份系统提示包含：
- Agent 的角色定义（coding assistant）
- 可用工具列表 `{tool_list_repr}`（通过 `get_tool_str_representation()` 自动生成工具描述）
- 工具调用格式说明：`tool: TOOL_NAME({JSON_ARGS})`

关键点：
- **Front-load context** ，在对话开始前就告诉 LLM 所有可用工具及其用法。

##### 3 工具调用解析（Command Prefix Extraction）

`extract_tool_invocations()` 函数负责：
- 从 LLM 响应中提取 `tool: TOOL_NAME({...})` 格式的命令
- 解析 JSON 参数
- 返回工具名称和参数的元组列表

**Command prefix extraction** ，让 LLM 输出结构化文本，便于系统解析和执行。

```python
def extract_tool_invocations(assistant_response_text: str) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Return list of (tool_name, args) requested in 'tool: name({...})' lines.
    The parser expects single-line, compact JSON in parentheses.
    """
    invocations = []
    for raw_line in assistant_response_text.splitlines():
        line = raw_line.strip()
        if not line.startswith("tool:"):
            continue
        try:
            # 提取工具名称和参数
            after = line[len("tool:"):].strip()
            name, rest = after.split("(", 1)
            name = name.strip()
            if not rest.endswith(")"):
                continue
            json_str = rest[:-1].strip()
            args = json.loads(json_str)
            invocations.append((name, args))
        except Exception:
            continue
    return invocations
```

##### 4 主循环（REPL, run_coding_agent_loop）

1. **初始化对话**：添加系统提示到对话历史
2. **读取用户输入**：从终端获取用户请求
3. **调用 LLM**：将完整对话历史发送给 LLM
4. **解析工具调用**：检查 LLM 响应中是否包含工具调用
5. **执行工具**：如果检测到工具调用 `tool: TOOL_NAME({{JSON_ARGS}})`，在本地安全执行
6. **返回结果**：将工具执行结果以 `tool_result({...})` 格式追加到对话
7. **继续对话**：重复步骤 3-6，直到 LLM 不再请求工具调用

```python
def run_coding_agent_loop():
    """
    Main REPL loop for the coding agent.
    Implements the core interaction cycle: read user input -> call LLM -> parse tool calls -> execute tools -> return results.
    """
    # Print the full system prompt for debugging/reference
    print(get_full_system_prompt())
    
    # Initialize conversation history with system prompt
    # The system prompt defines the agent's role and available tools
    conversation = [{
        "role": "system",
        "content": get_full_system_prompt()
    }]
    
    # Outer loop: continuously read user input until interrupted
    while True:
        try:
            # Read user input from terminal with colored prompt
            user_input = input(f"{YOU_COLOR}You:{RESET_COLOR}:")
        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C or EOF gracefully
            break
        
        # Append user input to conversation history
        conversation.append({
            "role": "user",
            "content": user_input.strip()
        })
        
        # Inner loop: handle LLM responses and tool invocations
        # This loop continues until LLM gives a final response (no tool calls)
        while True:
            # Call LLM with full conversation history
            assistant_response = execute_llm_call(conversation)
            
            # Extract tool invocations from LLM response
            # Format: "tool: TOOL_NAME({JSON_ARGS})"
            tool_invocations = extract_tool_invocations(assistant_response)
            
            # If no tool calls detected, this is a final response
            if not tool_invocations:
                # Print and save the assistant's final response
                print(f"{ASSISTANT_COLOR}Assistant:{RESET_COLOR}: {assistant_response}")
                conversation.append({
                    "role": "assistant",
                    "content": assistant_response
                })
                # Break inner loop, ready for next user input
                break
            
            # Execute all tool invocations found in the response
            for name, args in tool_invocations:
                # Get the tool function from registry
                tool = TOOL_REGISTRY[name]
                resp = ""
                
                # Debug: print tool name and arguments
                print(name, args)
                
                # Execute tool based on its name
                # Each tool has different parameter requirements
                if name == "read_file":
                    # read_file requires "filename" parameter
                    resp = tool(args.get("filename", "."))
                elif name == "list_files":
                    # list_files requires "path" parameter
                    resp = tool(args.get("path", "."))
                elif name == "edit_file":
                    # edit_file requires "path", "old_str", and "new_str" parameters
                    resp = tool(args.get("path", "."), 
                                args.get("old_str", ""), 
                                args.get("new_str", ""))
                
                # Append tool execution result to conversation as a "user" message
                # This allows LLM to see the tool result and continue processing
                # Format: "tool_result({JSON_RESULT})"
                conversation.append({
                    "role": "user",
                    "content": f"tool_result({json.dumps(resp)})"
                })
                # After appending tool result, the inner loop will call LLM again
                # LLM can then use the tool result to continue the task
```

##### 5 总结

| 技术点 | 实现方式 | 作用 |
|--------|---------|------|
| **System reminders everywhere** | 在系统提示中明确工具调用格式 | 防止 LLM 忘记如何调用工具 |
| **Command prefix extraction** | `extract_tool_invocations()` 解析结构化命令 | 安全地从 LLM 输出中提取工具调用 |
| **工具自动注册** | `get_full_system_prompt()` 动态生成工具列表 | 添加新工具时无需手动更新提示 |
| **路径解析** | `resolve_abs_path()` 处理相对/绝对路径 | 确保文件操作的安全性 |

**安全机制**：
- LLM **不直接执行代码**，只能通过预定义的工具操作文件系统
- 所有文件路径都通过 `resolve_abs_path()` 解析，防止路径遍历攻击
- 工具调用必须遵循严格的格式，否则会被忽略

**工作流程总结**：

```
用户: "读取 main.py 文件"
  ↓
LLM 响应: "tool: read_file({\"filename\": \"main.py\"})"
  ↓
系统解析并执行: read_file_tool("main.py")
  ↓
返回结果: tool_result({"file_path": "...", "content": "..."})
  ↓
LLM 继续处理: "这是 main.py 的内容：..."
```

**工具调用（Tool Calling）** 模式，LLM 作为"决策者"，系统作为"执行者"，两者通过 **结构化命令** 进行交互。
