import json
import re
from dataclasses import dataclass, field
from typing import Optional
from openai import OpenAI
from analysis.prompts import SYSTEM_PROMPT, build_analysis_prompt


def _strip_json_fences(raw: str) -> str:
    """Remove markdown code fences (```json ... ```) that models often add."""
    raw = raw.strip()
    # Match ```json ... ``` or ``` ... ```
    fence = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```$", raw, re.DOTALL)
    if fence:
        return fence.group(1).strip()
    return raw


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
    # Anthropic provides an OpenAI-compatible layer at /v1/ (use /v1/chat/completions)
    "Claude":     {"base_url": "https://api.anthropic.com/v1",         "model": "claude-opus-4-8"},
    "Gemini":     {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "model": "gemini-2.0-flash"},
    "通义千问":   {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-plus"},
    "Kimi":       {"base_url": "https://api.moonshot.cn/v1",           "model": "moonshot-v1-8k"},
    # Baidu Qianfan v2 OpenAI-compatible endpoint (not the legacy wenxinworkshop path)
    "文心一言":   {"base_url": "https://qianfan.baidubce.com/v2",      "model": "ernie-4.0-8k"},
}


class AnalysisRouter:
    def __init__(self, base_url: str, api_key: str, model: str, timeout: int = 30):
        self._client = OpenAI(base_url=base_url, api_key=api_key, timeout=timeout)
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
        if not raw:
            return []
        try:
            data = json.loads(_strip_json_fences(raw))
        except (json.JSONDecodeError, ValueError):
            return []
        if not isinstance(data, list):
            return []
        results = []
        for item in data:
            if not isinstance(item, dict) or "player" not in item:
                continue
            results.append(AnalysisResult(
                player=item["player"],
                suspicion_score=item.get("suspicion_score", 0),
                contradictions=item.get("contradictions", []),
                summary=item.get("summary", ""),
            ))
        return results

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
        result = (resp.choices[0].message.content or "").strip()
        # Treat short responses starting with 无 (无/无。/无矛盾) as "no contradiction"
        if not result or result.startswith("无"):
            return None
        return result
