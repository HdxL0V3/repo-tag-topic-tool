# GitHub 仓库主题标签标注生成器 — 设计文档

**日期**: 2026-08-14
**状态**: 已确认

---

## 1. 项目概述

构建一个轻量级 Python Agent 工具，使用 pydantic-ai 框架 + DeepSeek LLM，对 GitHub 仓库自动生成 3-5 个主题标签（类似 GitHub Topics）。输入为 JSON 格式的仓库信息数据，输出为追加了建议标签的 JSON 文件。

## 2. 项目结构

```
tool/
├── .env                  # DeepSeek API Key 配置（不提交到 git）
├── .env.example          # 配置模板
├── .gitignore            # 忽略 .env, __pycache__, .venv, CLAUDE.md 等
├── requirements.txt      # 依赖：pydantic-ai, python-dotenv, openai
├── main.py               # 入口：加载数据 → 调用 agent → 输出结果
├── src/
│   ├── __init__.py
│   ├── agent.py          # pydantic-ai agent 定义 + 主题标注逻辑
│   ├── models.py         # Pydantic 数据模型（输入/输出结构）
│   └── utils.py          # JSON 读写、批量处理工具
├── data/
│   ├── input.json         # 示例输入数据
│   └── output.json        # 输出结果（自动生成）
└── SKILL.md              # 可复用的任务技能文档
```

## 3. 核心流程

```
JSON 输入 → 逐条读取仓库信息 → 构造 prompt → Agent 推理 → 结构化输出(3-5个标签) → JSON 输出
```

## 4. 数据模型

### 输入字段（规范化后）

| 字段 | 类型 | 说明 |
|------|------|------|
| `repo_id` | int | 仓库唯一标识 |
| `repo_name` | str | 仓库全名，如 "NixOS/nixpkgs" |
| `description` | str | 仓库描述 |
| `readme_text` | str | README 全文（实际使用时会截断到 2000 字符） |
| `topics` | str | 现有主题标签，格式如 "{'tag1','tag2'}" |

### 输出字段

在原始字段基础上追加：

| 字段 | 类型 | 说明 |
|------|------|------|
| `suggested_topics` | list[str] | 3-5 个建议主题标签 |
| `reasoning` | str | 简短标注理由 |

## 5. Agent 设计

- **框架**: pydantic-ai
- **LLM 提供商**: DeepSeek（通过 OpenAI 兼容接口，`openai` provider）
- **API 配置**: 通过 `.env` 文件中的 `DEEPSEEK_API_KEY` 和 `DEEPSEEK_BASE_URL` 配置
- **系统提示词**: 引导 Agent 分析仓库的领域、技术栈、用途，参考现有 topics 去重，生成精准的英文标签
- **结构化输出**: 使用 Pydantic 模型约束输出格式，确保返回合法的 JSON 结构

## 6. 关键设计决策

- **README 截断**: readme_text 截取前 2000 字符，避免超出 token 限制
- **批量处理**: 逐条顺序处理，终端显示进度，单条失败不影响整体继续
- **错误重试**: 单条 API 调用失败自动重试 2 次，间隔递增
- **输出保留原始数据**: 输出 JSON 在原始字段基础上追加新字段，不丢失原始信息
- **并发控制**: 顺序处理，每条之间有短暂间隔，避免触发 API 速率限制

## 7. SKILL.md

生成一份可复用的 SKILL 文件，描述：
- 任务目标：为 GitHub 仓库生成主题标签
- 适用场景：仓库分类、搜索优化、推荐系统
- 输入输出规范
- Agent 配置要点
- 使用示例

## 8. .gitignore

忽略以下内容：
- `.env`（包含 API Key）
- `__pycache__/`、`*.pyc`
- `.venv/`、`venv/`
- `CLAUDE.md`（个人配置）
- `data/output.json`（生成结果）
- IDE 配置文件（`.vscode/`、`.idea/`）
- `.claude/`