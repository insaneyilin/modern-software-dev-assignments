### MCP

为什么需要 MCP ?

LLM 本质上还是静态知识的压缩，模型训练完，部署；如果要更新知识，需要更新数据重新训练。

如何处理 Dynamic data？比如
- 今天天气怎么样
- 谁是现在的总统
- 比特币今天价格是多少

一种解法是利用 RAG 和 tool-calling，比如接入各种 API 查询天气等实时信息。

但是，每接一个新 API 就要写一次接口适配工作，工作量 `M * N` 。（模型 x 工具）

本质是缺少模型和工具交互的标准接口协议。

如果有一个通用协议来对接模型、工具两端，那么适配接口的工作量可以减少为 `M + N`，模型不用关心工具细节，只需要对接这个通用协议即可。

这就是 MCP 的思想 (Model Context Protocol) 。

再类比一下，你有各种充电设备，usb 2.0/3.0, lightning 等，如果每个设备都去买一个充电转接头，麻烦，买一个通用插座即可。MCP 就是想扮演大模型和各种工具交互的通用插座。

2024 年 11 月 Anthropic 对外公布了 MCP 的概念，改变了之前各家自己做插件适配的孤岛情况。

MCP 定义：
> [!info]
> Open protocol that allows systems to provide context to AI models in a generalizable way.

#### MCP 基础

- 把 M×N 的完全二分图拆成 M+N：
    - M 个 Host（Cursor、Claude Code、GitHub Copilot…）
    - N 个 MCP Server（包装好的工具）
    - 只要双方都遵守 MCP，就能即插即用，无需重复写 connector。
- 统一 JSON-RPC 2.0 格式，错误码、重试机制、流式传输等可复用
- 继承 LSP（Language Server Protocol）经验，但 LSP 是“被动响应”，MCP 支持“主动推送 / 代理执行”，更适合 Agent 场景

MCP 术语：
- Host: 最终用户运行的桌面或 Web 应用
- MCP Client: 嵌在 Host 里的库，stateful session per server
- MCP Server: 工具的轻量级 wrapper，把任意工具（DB、API、脚本）包装成标准 JSON-RPC 服务
- Tool: Callable function，比如读数据库、发邮件等 API

MCP 数据流
1. 用户向 MCP server 发起工具调用请求（Host → Client → Server）
2. Server 返回工具元数据的 JSON
3. Host 把元数据 JSON 注入 LLM 的 system prompt
4. User prompt 触发模型生成结构化的 tool calling
5. tool calling 执行后，Server 把结果塞回对话，LLM 继续生成自然语言回答。

#### MCP 局限性

- Agent 还无法很好处理很多工具（规划/反思机制还不够）
- APIs 会快速消耗 context window
- 很多 APIs 不是 AI-native 的，需要更好的设计

#### 从零构建一个 MCP server

下面我们通过一个简单的文件操作 MCP server 来演示如何从零构建。

##### **1. 安装 fastmcp**

首先需要安装 `fastmcp` 库：

```bash
pip install fastmcp
```

##### **2. 创建 MCP 实例**

导入必要的库并创建 FastMCP 实例：

```python
from pathlib import Path
from typing import Any, Dict
from fastmcp import FastMCP

mcp = FastMCP(name="SimpleMCPTestServer")
```

##### **3. 定义工具函数并使用装饰器注册为 MCP 工具**

使用 `@mcp.tool` 装饰器将普通 Python 函数注册为 MCP 工具：
- 有清晰的文档字符串（docstring），描述工具的功能和参数
- 返回可序列化的数据结构（通常是字典）

这里就是 coding agent `coding_agent_from_scratch_lecture.py` 中的工具定义。

**文件读取工具**

```python
@mcp.tool
def read_file_tool(filename: str) -> Dict[str, Any]:
    """
    Gets the full content of a file provided by the user.
    :param filename: The name of the file to read.
    :return: The full content of the file.
    """
    full_path = resolve_abs_path(filename)
    with open(str(full_path), "r") as f:
        content = f.read()
    return {
        "file_path": str(full_path),
        "content": content
    }
```

**目录列表工具**

```python
@mcp.tool
def list_files_tool(path: str) -> Dict[str, Any]:
    """
    Lists the files in a directory provided by the user.
    :param path: The path to the directory to list files from.
    :return: A list of files in the directory.
    """
    full_path = resolve_abs_path(path)
    all_files = []
    for item in full_path.iterdir():
        all_files.append({
            "filename": item.name,
            "type": "file" if item.is_file() else "dir"
        })
    return {
        "path": str(full_path),
        "files": all_files
    }
```

##### **4. 运行 MCP server**

在 `__main__` 块中启动 MCP 服务器：

```python
if __name__ == "__main__":
    mcp.run()
```

**关键要点：**

- **装饰器模式**：`@mcp.tool` 装饰器自动将函数注册为 MCP 工具，无需手动配置
- **文档字符串**：工具函数的 docstring 会被自动解析为工具的元数据，供 LLM 理解工具功能
- **类型注解**：返回类型注解帮助 MCP 框架理解工具的输出格式
- **标准化接口**：所有工具都遵循相同的调用模式，返回字典格式的结果

这样，一个简单的 MCP server 就构建完成了。Host（如 Cursor）可以通过标准 MCP 协议调用这些工具，而无需关心具体的实现细节。

##### **5. 测试 MCP server**

直接用 `npx @modelcontextprotocol/inspector` 来测试。

```bash
npx @modelcontextprotocol/inspector python simple_mcp_server.py
```

注意这里 python 的路径需要指定为你的 MCP server 的 python 路径。
