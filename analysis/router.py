import json
from dataclasses import dataclass, field
from typing import Optional
from openai import OpenAI
from analysis.prompts import SYSTEM_PROMPT, build_analysis_prompt


@dataclass
class AnalysisResult:
    player: str
    suspicion_score: int
    contradictions: list = field(default_factory=list)
    summary: str = ""


# Built-in presets
PRESETS = {
    "DeepSeek":   {"base_url": "https://api.deepseek.com/v1",          "model": "deepseek-chat"},
    "OpenAI":     {"base_url": "https://api.openai.com/v1",            "model": "gpt-4o"},
    "Claude":     {"base_url": "https://api.anthropic.com/v1",         "model": "claude-opus-4-8"},
    "Gemini":     {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "model": "gemini-2.0-flash"},
    "通义千问":   {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-plus"},
    "Kimi":       {"base_url": "https://api.moonshot.cn/v1",           "model": "moonshot-v1-8k"},
    "文心一言":   {"base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat", "model": "ernie-speed-128k"},
}


class AnalysisRouter:
    def __init__(self, base_url: str, api_key: str, model: str):
        self._client = OpenAI(base_url=base_url, api_key=api_key)
        self._model = model

    @classmethod
    def from_preset(cls, preset_name: str, api_key: str) -> "AnalysisRouter":
        preset = PRESETS[preset_name]
        return cls(base_url=preset["base_url"], api_key=api_key, model=preset["model"])

    def analyze(self, records: list) -> list:
        """Deep analysis of full session records, returns suspicion assessment per player."""
        prompt = build_analysis_prompt(records)
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        raw = resp.choices[0].message.content
        data = json.loads(raw)
        return [
            AnalysisResult(
                player=item["player"],
                suspicion_score=item["suspicion_score"],
                contradictions=item.get("contradictions", []),
                summary=item.get("summary", ""),
            )
            for item in data
        ]

    def quick_check(self, new_text: str, player: str, history: list) -> Optional[str]:
        """Quick check of a single utterance. Returns contradiction description or None."""
        if not history:
            return None
        history_text = "\n".join(f"{r['player']}: {r['text']}" for r in history[-10:])
        prompt = (
            f"玩家历史发言：\n{history_text}\n\n"
            f"{player}刚说：「{new_text}」\n\n"
            "若存在明显逻辑矛盾，用一句话描述矛盾（不超过30字）；若无矛盾，只回复「无」。"
        )
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=60,
        )
        result = resp.choices[0].message.content.strip()
        return None if result == "无" else result
