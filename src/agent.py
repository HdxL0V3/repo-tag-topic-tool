"""Agent 核心逻辑。

使用 pydantic-ai 框架 + DeepSeek LLM 为 GitHub 仓库生成主题标签。
"""

import os
import time
from typing import Optional

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

from .models import RepoInfo, TopicSuggestion

# 加载环境变量
load_dotenv()

# DeepSeek 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# 系统提示词
SYSTEM_PROMPT = """你是一个专业的 GitHub 仓库主题标签标注专家。你的任务是根据仓库信息，生成3到5个精准的主题标签（类似 GitHub Topics）。

## 标签生成规则

1. **标签语言**：使用英文小写，多个单词用连字符连接（如 `machine-learning`、`react-native`）
2. **标签粒度**：要具体，不要太宽泛。例如用 `package-manager` 而不是 `tool`，用 `linux-distribution` 而不是 `linux`
3. **覆盖维度**：标签应覆盖以下维度：
   - **技术栈**：主要编程语言、框架、平台（如 `python`、`react`、`docker`）
   - **领域/用途**：仓库解决什么问题（如 `package-management`、`image-processing`）
   - **项目类型**：仓库的性质（如 `library`、`cli-tool`、`framework`）
4. **去重**：不要生成与现有标签含义相同的标签，避免重复
5. **准确性**：标签必须准确反映仓库的实际内容，不要猜测或编造

## 输出要求

- 严格返回3到5个标签
- 每个标签必须简洁、有意义
- 在 reasoning 中简短说明为什么选择这些标签"""


def _create_model() -> OpenAIChatModel:
    """创建 DeepSeek 模型实例。

    Returns:
        配置好的 OpenAIChatModel 实例。

    Raises:
        ValueError: API Key 未配置时抛出。
    """
    if not DEEPSEEK_API_KEY:
        raise ValueError(
            "DEEPSEEK_API_KEY 未配置。请在 .env 文件中设置 DEEPSEEK_API_KEY。"
        )

    return OpenAIChatModel(
        model_name=DEEPSEEK_MODEL,
        base_url=DEEPSEEK_BASE_URL,
        api_key=DEEPSEEK_API_KEY,
    )


def _create_agent() -> Agent:
    """创建主题标注 Agent。

    Returns:
        配置好的 pydantic-ai Agent 实例。
    """
    model = _create_model()
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        output_type=TopicSuggestion,
    )


def generate_topics(
    repo: RepoInfo,
    agent: Optional[Agent] = None,
    max_retries: int = 2,
) -> Optional[TopicSuggestion]:
    """为单个仓库生成主题标签。

    Args:
        repo: 仓库信息。
        agent: 可复用的 Agent 实例。如果为 None，则创建新实例。
        max_retries: 失败重试次数。

    Returns:
        TopicSuggestion 实例，失败时返回 None。
    """
    if agent is None:
        agent = _create_agent()

    summary = repo.get_summary()

    for attempt in range(max_retries + 1):
        try:
            result = agent.run_sync(summary)
            return result.data
        except Exception as e:
            if attempt < max_retries:
                wait = (attempt + 1) * 2  # 递增等待：2s, 4s
                print(f"  ⚠ 第 {attempt + 1} 次尝试失败: {e}，{wait}秒后重试...")
                time.sleep(wait)
            else:
                print(f"  ✗ 处理失败（已重试 {max_retries} 次）: {e}")
                return None
    return None