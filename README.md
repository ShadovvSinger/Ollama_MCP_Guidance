# ask-ollama

> 🎯 **快速开始**：
> 如果您正在通过 LLM（如 Claude）使用本项目，请首先让 LLM 调用 `get_started_guide` 工具。
> 这个入门指南将帮助 LLM 全面了解项目，从而为您提供更好的服务。

基于 MCP (Model Context Protocol) 的 Ollama API 交互服务。该项目提供了一个标准化的接口，用于与 Ollama 服务进行交互，支持模型查询、文本生成、对话等功能。

> ⚠️ **项目状态说明**：
> - 这是一个 Cursor MCP Server 项目，目前仅支持在 Cursor 中使用
> - 项目处于开发阶段，尚未实现 Ollama 的所有 API 端点
> - 项目文档和注释采用中英双语，未来将统一为英文（并提供中文文档备份）

## 功能特点

- ✨ 标准化的 JSON 响应格式
- 🔍 完整的错误处理和状态反馈
- 📊 详细的性能指标统计
- 🛠 简单的配置管理
- 📚 内置的 API 文档导航

## 使用环境

- 本项目设计为 Cursor IDE 的 MCP 服务
- 需要在 Cursor 中通过 MCP 协议调用
- 不提供独立的客户端实现

## 安装

1. 确保已安装 Python 3.10 或更高版本
2. 安装 [Ollama](https://ollama.ai)
3. 安装项目：

```bash
# 安装 uv（推荐）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建并激活虚拟环境
uv venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
uv pip install .
```

## 配置

项目使用 `config.json` 进行配置，主要配置项包括：

```json
{
    "ollama": {
        "host": "http://localhost:11434",  // Ollama 服务地址
        "timeout": 30,                     // 请求超时时间（秒）
        "user_agent": "ask-ollama/1.0"     // 请求标识
    },
    "api_doc": {
        "max_length": 8000,                // 文档内容最大长度
        "file_path": "ollama-api.md"       // API 文档路径
    }
}
```

## 使用

> 📌 **重要提示**：
> 如果您正在与 AI 助手交互，请确保它已经调用了 `get_started_guide` 工具。
> 这个入门指南包含了完整的使用说明和最佳实践，可以帮助 AI 更好地理解您的需求并提供准确的帮助。

### 1. 创建运行脚本

由于 Cursor MCP 需要从默认命令行环境中执行单条命令，建议创建一个自定义运行脚本。创建 `ask-ollama-cli` 文件（以下以 macOS/Linux 为例）：
（如果有不理解的地方，请提供信息，让AI来帮助你）

```bash
#!/bin/bash

# 虚拟环境配置
# 如果使用 conda，取消下面的注释并修改路径
# CONDA_PATH="你的conda路径/etc/profile.d/conda.sh"
# if [ -f "$CONDA_PATH" ]; then
#     source "$CONDA_PATH"
#     conda activate 你的环境名称
# fi

# 项目路径配置
PROJECT_PATH="你的项目路径/ask-ollama"
if [ ! -d "$PROJECT_PATH" ]; then
    echo "Error: Project directory not found at $PROJECT_PATH"
    exit 1
fi

# 运行程序
cd "$PROJECT_PATH"
source .venv/bin/activate  # 激活 uv 虚拟环境
python ask-ollama-server.py "$@"
```

然后设置脚本权限：
```bash
chmod +x ask-ollama-cli
```

> 注意：Windows 用户需要创建 `ask-ollama-cli.bat` 文件，内容相应调整。

### 2. 在 Cursor 中配置

1. 启动 Ollama 服务
2. 在 Cursor 的 MCP 配置中，使用以下命令：
```bash
/完整路径/ask-ollama-cli
```

> 提示：如果将脚本放在系统的可执行文件路径中（如 `/usr/local/bin/`），则可以直接使用脚本名称：
> ```bash
> ask-ollama-cli
> ```

### 3. 基本功能示例

> ⚠️ **本节待修改**

1. 查看可用模型：
```python
result = await get_ollama_list()
```

2. 简单对话：
```python
response = await simple_chat(
    model="llama2",
    prompt="你好，请介绍一下自己"
)
```

3. 生成文本嵌入：
```python
embeddings = await post_generate_embeddings(
    model="nomic-embed-text",
    text=["这是一段示例文本"]
)
```

## 支持的功能与限制

### API 端点支持状态

| 端点 | 方法 | 功能介绍 | 特性支持 | 工具名称 |
|------|------|----------|----------|----------|
| - | - | 项目入门指南<br>💫 **_不想读枯燥的表格？让 AI 来帮你！_**<br>*尝试让你的 AI 助手运行 `get_started_guide` 工具吧！* | - 智能项目导航 ✨<br>- 个性化功能推荐 🎯<br>- 最佳实践指导 💡 | `get_started_guide` |
| `/api/version` | GET | 获取Ollama服务器版本 | - 单次响应 ✅<br>- 包含构建信息 ✅ | `get_ollama_version` |
| `/api/tags` | GET | 获取已安装模型列表 | - 完整响应 ✅<br>- 包含模型元数据 ✅ | `get_ollama_list` |
| `/api/ps` | GET | 查看运行中的模型 | - 实时状态 ✅<br>- 资源使用数据 ✅ | `get_running_models` |
| `/api/show` | POST | 获取模型详细信息 | - 详细模式 ✅<br>- 完整配置信息 ✅ | `post_show_model` |
| `/api/chat` | POST | 对话式交互功能 | - 流式输出 ❌<br>- 多轮对话 ❌<br>- 系统提示词 ❌<br>- 图像输入 ❌ | `simple_chat` |
| `/api/generate` | POST | 基础文本生成 | - 流式输出 ❌<br>- 上下文管理 ❌<br>- raw模式 ❌<br>- 模型JSON格式输出 ❌<br>- 工具JSON包装 ✅ | `simple_generate` |
| `/api/embed` | POST | 生成文本向量表示 | - 批量处理 ✅<br>- 固定维度输出 ✅ | `post_generate_embeddings` |
| `/api/embeddings` | POST | 生成文本向量表示（已弃用） | - 批量处理 ✅<br>- 固定维度输出 ✅<br>- 已被 `/api/embed` 替代 ⚠️ | `post_generate_embeddings` |
| `/api/copy` | POST | 创建模型副本 | - 原子操作 ❌<br>- 跨版本复制 ❌ | 未实现（管理员权限） |
| `/api/pull` | POST | 下载并安装模型 | - 进度反馈 ❌<br>- 断点续传 ❌<br>- 版本管理 ❌ | 未实现（管理员权限） |
| `/api/delete` | DELETE | 移除指定模型 | - 不可逆操作 ❌<br>- 释放资源 ❌ | 未实现（管理员权限） |
| `/api/create` | POST | 创建新模型 | - 模型创建 ❌<br>- 参数配置 ❌ | 未实现（管理员权限） |
| `/api/blobs/:digest` | HEAD | 检查blob是否存在 | - 二进制对象检查 ❌<br>- SHA256校验 ❌ | 未实现（管理员权限） |
| `/api/blobs/:digest` | POST | 上传blob | - 二进制对象上传 ❌<br>- 大文件支持 ❌ | 未实现（管理员权限） |

### 功能限制说明

1. **基础功能限制**
   - 仅支持非流式响应（一次性返回结果）
   - 不支持多轮对话历史
   - 不支持系统提示词（system prompt）
   - 不支持上下文管理
   - 不支持 raw 模式和特定格式输出

2. **管理功能限制**
   - 出于安全考虑，不支持以下管理员级别操作：
     * 模型复制（`/api/copy`）
     * 模型下载（`/api/pull`）
     * 模型删除（`/api/delete`）
   - 配置文件中的 API 端点路径请勿随意修改

3. **实验性功能**
   - 图片处理功能尚未完全实现和测试，不建议在生产环境使用
   - 部分高级特性（如参数调优、模板定制）尚未实现

## 依赖要求

- Python >= 3.10
- httpx >= 0.28.1
- mcp[cli] >= 1.3.0

## 许可证

MIT License

> 💡 **友好提示**：如果您正在使用这个项目，欢迎通过邮件 (shadowsinger.tp@gmail.com) 告诉我。这不是必须的，但我很乐意知道这个项目对您有帮助！

<目前项目是面向cursor mcp的server项目，没有client，因此仅建议用于cursor mcp>
<目前项目是中文项目，注释中包含中文和英文内容，将在未来的某一个版本将注释全部改为英文，并提供中文注释文件备份方便中文用户>
<目前项目没有完全实现ollama支持的所有api端点>

<添加对于项目功能和未实现功能的说明：
1.目前项目不支持流式传输
2.目前项目不支持图片处理（尽管有相关代码，但未完全实现并测试）
3.目前项目没有完全实现ollama支持的所有api端点
4.关于实现的功能，请把notes.md最后的表格复制到此readme中进行说明。>