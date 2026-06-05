# config.py
import json
from pathlib import Path

DEFAULTS = {
    "stt_engine": "whisper",          # "whisper" | "cloud"
    "whisper_model": "medium",        # tiny/base/small/medium/large-v3
    "cloud_stt_provider": "xunfei",
    "cloud_stt_key": "",
    "ai_base_url": "https://api.deepseek.com/v1",
    "ai_api_key": "",
    "ai_model": "deepseek-chat",
    "overlay_opacity": 0.85,
    "overlay_width": 420,
    "max_players": 16,
    "hotkey_record": "ctrl+shift+r",
    "hotkey_meeting": "ctrl+shift+m",
    "hotkey_toggle": "ctrl+shift+h",
}

class Config:
    def __init__(self, path: str = "config.json"):
        self._path = Path(path)
        self._data: dict = {}
        self._load()

    def _load(self):
        if self._path.exists():
            with open(self._path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    self._data = json.loads(content)

    def get(self, key: str, default=None):
        if key in self._data:
            return self._data[key]
        if key in DEFAULTS:
            return DEFAULTS[key]
        return default

    def set(self, key: str, value):
        self._data[key] = value
        self._save()

    def _save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
