SYSTEM_PROMPT = """你是鹅鸭杀游戏的专业逻辑分析助手。
游戏中有鹅（好人）和鸭子（坏人），鸭子会撒谎、制造混乱。
你的任务是分析玩家发言记录，找出逻辑漏洞和可疑行为。

分析维度：
1. 内部矛盾：该玩家不同时间的陈述是否自相矛盾
2. 跨玩家冲突：与其他玩家陈述的事实冲突
3. 行为模式：过度辩解、转移话题、回避问题、指责无辜者等鸭子常见行为

输出格式：严格返回 JSON 数组，每个玩家一个对象：
[
  {
    "player": "玩家X",
    "suspicion_score": 0-100,
    "contradictions": ["矛盾描述1", "矛盾描述2"],
    "summary": "一句话总结"
  }
]
不要输出任何 JSON 以外的内容。"""

def build_analysis_prompt(records: list) -> str:
    """Serialize speech records into analysis prompt."""
    lines = ["以下是本局游戏的发言记录：\n"]
    for r in records:
        lines.append(f"[{r['time']}] {r['player']}: {r['text']}")
    lines.append("\n请分析以上发言，找出逻辑漏洞，返回 JSON 分析结果。")
    return "\n".join(lines)
