"""项目入口。

加载仓库数据，调用 Agent 生成主题标签，输出结果。

使用方法：
    python main.py                          # 使用默认 data/input.json
    python main.py data/my_input.json       # 指定输入文件
    python main.py data/my_input.json data/my_output.json  # 指定输入输出
"""

import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from src.agent import generate_topics, _create_agent
from src.models import RepoInfo
from src.utils import load_json, save_json

# 加载环境变量
load_dotenv()

# 默认路径
DEFAULT_INPUT = "data/input.json"
DEFAULT_OUTPUT = "data/output.json"


def main(input_path: str, output_path: str) -> None:
    """主流程：加载数据 → 标注 → 保存结果。

    Args:
        input_path: 输入 JSON 文件路径。
        output_path: 输出 JSON 文件路径。
    """
    print("=" * 60)
    print("GitHub 仓库主题标签标注工具")
    print("=" * 60)

    # 1. 加载数据
    print(f"\n📂 加载数据: {input_path}")
    raw_data = load_json(input_path)
    print(f"   共加载 {len(raw_data)} 条仓库数据")

    # 2. 创建 Agent（复用实例）
    print("\n🤖 初始化 Agent...")
    agent = _create_agent()
    print("   Agent 就绪")

    # 3. 逐条处理
    print(f"\n🔍 开始标注（共 {len(raw_data)} 条）...\n")
    results = []
    success_count = 0
    fail_count = 0
    start_time = time.time()

    for i, item in enumerate(raw_data, 1):
        repo_name = item.get("repo_name", item.get("b.repo_name", f"#{item.get('repo_id', item.get('r.repo_id', 'unknown'))}"))
        print(f"[{i}/{len(raw_data)}] {repo_name}")

        try:
            # 规范化字段名（兼容原始格式和清洗后格式）
            repo = RepoInfo(
                repo_id=item.get("repo_id", item.get("r.repo_id", 0)),
                repo_name=repo_name,
                description=item.get("description", item.get("a.description", "")),
                readme_text=item.get("readme_text", item.get("a.readme_text", "")),
                topics=item.get("topics", item.get("a.topics", "")),
            )

            suggestion = generate_topics(repo, agent=agent)

            # 保留原始数据，追加新字段
            result = dict(item)
            if suggestion:
                result["suggested_topics"] = suggestion.suggested_topics
                result["reasoning"] = suggestion.reasoning
                print(f"  ✓ 标签: {', '.join(suggestion.suggested_topics)}")
                success_count += 1
            else:
                result["suggested_topics"] = []
                result["reasoning"] = "生成失败"
                print(f"  ✗ 生成失败")
                fail_count += 1

            results.append(result)

        except Exception as e:
            print(f"  ✗ 异常: {e}")
            result = dict(item)
            result["suggested_topics"] = []
            result["reasoning"] = f"处理异常: {str(e)}"
            results.append(result)
            fail_count += 1

        # 速率控制：每条之间短暂间隔
        if i < len(raw_data):
            time.sleep(0.5)

    # 4. 保存结果
    elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    print(f"📊 处理完成")
    print(f"   总数: {len(raw_data)} | 成功: {success_count} | 失败: {fail_count}")
    print(f"   耗时: {elapsed:.1f} 秒")
    print(f"\n💾 保存结果: {output_path}")
    save_json(results, output_path)
    print("   完成！")


if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT
    main(input_path, output_path)