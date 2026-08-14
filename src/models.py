"""数据模型定义。

定义仓库输入信息和主题标签输出的 Pydantic 模型。
"""

from pydantic import BaseModel, Field


class RepoInfo(BaseModel):
    """GitHub 仓库信息输入模型。"""

    repo_id: int
    repo_name: str
    description: str
    readme_text: str = ""
    topics: str = ""

    def get_summary(self, max_readme_len: int = 2000) -> str:
        """构造用于 Agent 推理的仓库摘要文本。

        Args:
            max_readme_len: README 文本最大截取长度。

        Returns:
            格式化的仓库摘要字符串。
        """
        readme = self.readme_text[:max_readme_len] if self.readme_text else "无"
        return (
            f"仓库名称: {self.repo_name}\n"
            f"描述: {self.description or '无'}\n"
            f"现有标签: {self.topics or '无'}\n"
            f"README 摘要: {readme}"
        )


class TopicSuggestion(BaseModel):
    """主题标签建议输出模型。"""

    suggested_topics: list[str] = Field(
        description="3到5个建议的 GitHub 主题标签",
        min_length=3,
        max_length=5,
    )
    reasoning: str = Field(
        description="生成这些标签的简短理由，50字以内"
    )