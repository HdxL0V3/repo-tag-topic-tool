# GitHub 仓库主题标签标注工具

基于 pydantic-ai + DeepSeek LLM 的轻量级 Agent 工具，自动为 GitHub 仓库生成 3-5 个精准的主题标签（类似 GitHub Topics）。

## 快速开始

### 1. 环境准备

- Python 3.10+
- DeepSeek API Key（[申请地址](https://platform.deepseek.com)）

### 2. 安装

```bash
# 克隆项目
git clone <repo-url> && cd tool

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env，填入你的 API Key
# DEEPSEEK_API_KEY=sk-your-api-key
```

### 4. 运行

```bash
# 使用示例数据
python main.py

# 指定输入文件
python main.py data/my_repos.json

# 指定输入和输出
python main.py data/input.json data/output.json
```

## 输入格式

JSON 数组，每个元素需包含以下字段：

```json
[
    {
        "repo_id": 4542716,
        "repo_name": "NixOS/nixpkgs",
        "description": "Nix Packages collection & NixOS",
        "readme_text": "Nixpkgs is a collection of over 100,000 software packages...",
        "topics": "nixpkgs, nix, nixos, linux"
    }
]
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `repo_id` | int | 是 | 仓库唯一标识 |
| `repo_name` | str | 是 | 仓库全名 |
| `description` | str | 是 | 仓库描述 |
| `readme_text` | str | 否 | README 文本（超 2000 字符自动截断） |
| `topics` | str | 否 | 现有标签，用于去重参考 |

## 输出格式

在原始字段基础上追加：

```json
{
    "suggested_topics": ["package-manager", "linux-distribution", "functional", "cross-platform"],
    "reasoning": "Nix 包管理器，实现了纯函数式 Linux 发行版，支持跨平台构建"
}
```

## 项目结构

```
tool/
├── main.py               # 入口脚本
├── src/
│   ├── agent.py          # Agent 核心逻辑
│   ├── models.py         # Pydantic 数据模型
│   └── utils.py          # 工具函数
├── data/
│   ├── input.json         # 示例输入
│   └── output.json        # 输出结果
├── SKILL.md              # 可复用技能文档
└── docs/                 # 设计文档
```

## 作为模块使用

```python
from src.agent import generate_topics, _create_agent
from src.models import RepoInfo

agent = _create_agent()

repo = RepoInfo(
    repo_id=12345,
    repo_name="owner/repo",
    description="A sample repository",
    readme_text="...",
    topics="python, web",
)

suggestion = generate_topics(repo, agent=agent)
print(suggestion.suggested_topics)  # ['flask', 'web-framework', ...]
```

## 切换 LLM 提供商

修改 `.env` 即可，支持任何 OpenAI 兼容 API：

```env
# OpenAI
DEEPSEEK_BASE_URL=https://api.openai.com/v1
DEEPSEEK_MODEL=gpt-4o-mini

# 本地 Ollama
DEEPSEEK_BASE_URL=http://localhost:11434/v1
DEEPSEEK_MODEL=llama3
```

## 标签质量标准

- **英文小写**，多词用连字符连接（`machine-learning`）
- **具体而非宽泛**（`package-manager` 优于 `tool`）
- **覆盖三个维度**：技术栈、领域用途、项目类型
- **与现有标签去重**

## 更多信息

- 详细使用说明见 [SKILL.md](SKILL.md)
- 设计文档见 [docs/superpowers/specs/](docs/superpowers/specs/)