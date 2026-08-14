# GitHub 仓库主题标签标注

## 概述

为 GitHub 仓库自动生成 3-5 个精准的主题标签（类似 GitHub Topics），帮助仓库分类、搜索优化和推荐系统建设。

## 适用场景

- 大规模开源仓库自动分类与标注
- GitHub 仓库搜索引擎优化
- 开源项目推荐系统的标签体系构建
- 仓库目录/黄页的标签补全
- 代码仓库知识图谱的标签节点生成

## 前置条件

### 环境要求

- Python 3.10+
- DeepSeek API Key（或其他 OpenAI 兼容的 LLM API）

### 依赖安装

```bash
pip install -r requirements.txt
```

### 配置

复制 `.env.example` 为 `.env`，填写 API Key：

```env
DEEPSEEK_API_KEY=sk-your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

## 输入规范

### 数据格式

JSON 数组，每个元素包含以下字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `repo_id` | int | 是 | 仓库唯一标识 |
| `repo_name` | str | 是 | 仓库全名，如 `owner/repo` |
| `description` | str | 是 | 仓库描述文本 |
| `readme_text` | str | 否 | README 全文（超过 2000 字符会自动截断） |
| `topics` | str | 否 | 现有主题标签，用于去重参考 |

### 示例输入

```json
[
    {
        "repo_id": 4542716,
        "repo_name": "NixOS/nixpkgs",
        "description": "Nix Packages collection & NixOS",
        "readme_text": "Nixpkgs is a collection of over 100,000 software packages...",
        "topics": "nixpkgs, nix, nixos, linux, hacktoberfest"
    }
]
```

## 输出规范

在原始字段基础上追加以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `suggested_topics` | list[str] | 3-5 个建议主题标签 |
| `reasoning` | str | 标注理由简述 |

### 示例输出

```json
[
    {
        "repo_id": 4542716,
        "repo_name": "NixOS/nixpkgs",
        "description": "Nix Packages collection & NixOS",
        "readme_text": "Nixpkgs is a collection of over 100,000 software packages...",
        "topics": "nixpkgs, nix, nixos, linux, hacktoberfest",
        "suggested_topics": ["package-manager", "linux-distribution", "functional", "build-system", "cross-platform"],
        "reasoning": "仓库是 Nix 包管理器，实现了纯函数式 Linux 发行版，支持跨平台构建"
    }
]
```

## 标签质量标准

生成的标签应满足以下标准：

1. **语言**: 英文小写，多词用连字符连接（`machine-learning`）
2. **粒度**: 具体而非宽泛（`package-manager` 优于 `tool`）
3. **覆盖维度**:
   - 技术栈（编程语言、框架）
   - 领域/用途（解决什么问题）
   - 项目类型（library、cli-tool、framework 等）
4. **去重**: 不与现有标签重复
5. **准确**: 基于仓库实际内容，不猜测不编造

## 使用方法

### 命令行

```bash
# 使用默认路径（data/input.json → data/output.json）
python main.py

# 指定输入文件
python main.py data/my_repos.json

# 指定输入和输出文件
python main.py data/my_repos.json data/my_results.json
```

### 作为 Python 模块

```python
from src.agent import generate_topics, _create_agent
from src.models import RepoInfo

# 创建 Agent（复用实例提高效率）
agent = _create_agent()

# 处理单个仓库
repo = RepoInfo(
    repo_id=12345,
    repo_name="owner/repo",
    description="A sample repository",
    readme_text="...",
    topics="python, web",
)
suggestion = generate_topics(repo, agent=agent)
print(suggestion.suggested_topics)  # ['flask', 'web-framework', ...]
print(suggestion.reasoning)
```

## Agent 配置要点

### 模型选择

- **推荐模型**: `deepseek-chat`（DeepSeek V3），性价比高，标签质量好
- **备选模型**: `deepseek-reasoner`（DeepSeek R1），推理能力更强但速度较慢
- 支持任何 OpenAI 兼容的 API，修改 `.env` 中的 `DEEPSEEK_BASE_URL` 和 `DEEPSEEK_MODEL` 即可切换

### 性能参考

- 单条处理时间：约 2-5 秒（DeepSeek V3）
- 建议速率控制：每条间隔 0.5 秒，避免触发 API 限流
- 错误重试：自动重试 2 次，间隔递增（2s / 4s）

### 系统提示词调优

标签生成的质量很大程度上取决于系统提示词。核心调优方向：

1. **标签粒度控制**: 在提示词中明确"不要使用过于宽泛的标签"，并提供反例
2. **覆盖维度引导**: 要求 Agent 从技术栈、领域用途、项目类型三个维度分别思考
3. **去重指令**: 明确要求参考现有标签进行去重

### 批量处理建议

- 大批量数据（>1000 条）建议分批处理，每批 500 条
- 使用 `--input` 和 `--output` 参数指定中间文件，防止中断后丢失进度
- 失败条目会自动标记，可后续再处理

## 扩展性

### 切换到其他 LLM 提供商

修改 `.env` 即可：

```env
# OpenAI
DEEPSEEK_BASE_URL=https://api.openai.com/v1
DEEPSEEK_MODEL=gpt-4o-mini

# 本地模型（如 Ollama）
DEEPSEEK_BASE_URL=http://localhost:11434/v1
DEEPSEEK_MODEL=llama3
```

### 自定义标签风格

修改 `src/agent.py` 中的 `SYSTEM_PROMPT`，例如：
- 要求标签为中文
- 要求标签带有层级前缀（如 `lang:python`）
- 要求输出更多标签

## 项目结构

```
tool/
├── .env                  # API Key 配置（不提交）
├── .env.example          # 配置模板
├── .gitignore
├── requirements.txt
├── main.py               # 入口脚本
├── src/
│   ├── __init__.py
│   ├── agent.py          # Agent 核心逻辑
│   ├── models.py         # 数据模型
│   └── utils.py          # 工具函数
├── data/
│   ├── input.json         # 示例输入
│   └── output.json        # 输出结果
└── SKILL.md              # 本文件
```

## 维护说明

- 定期更新 `requirements.txt` 中的 pydantic-ai 版本
- 关注 DeepSeek API 的模型更新，及时调整 `DEEPSEEK_MODEL`
- 如果标签质量下降，优先检查系统提示词是否需要调整