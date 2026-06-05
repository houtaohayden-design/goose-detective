# config.py
import json
import os
import sys
import tempfile
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
                try:
                    self._data = json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"Warning: config file {self._path} is corrupt ({e}); using defaults.", file=sys.stderr)
                    self._data = {}

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
        dir_ = self._path.parent
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=dir_, delete=False, suffix=".tmp"
        ) as tmp:
            json.dump(self._data, tmp, ensure_ascii=False, indent=2)
            tmp_path = tmp.name
        os.replace(tmp_path, self._path)
