# config.py
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

DEFAULTS = {
    "stt_engine": "whisper",          # "whisper" | "cloud"
    "whisper_model": "medium",        # tiny/base/small/medium/large-v3
    "cloud_stt_provider": "xunfei",
    "cloud_stt_key": "",
    "cloud_stt_app_id": "",
    "cloud_stt_api_secret": "",
    "hf_token": "",
    "mic_device": None,
    "system_device": None,
    "ai_base_url": "https://api.deepseek.com/v1",
    "ai_api_key": "",
    "ai_model": "deepseek-chat",
    "ai_timeout": 30,
    "enable_quick_check": True,
    "quick_check_history_limit": 10,
    "audio_buffer_seconds": 30,
    "overlay_opacity": 0.85,
    "overlay_width": 420,
    "max_players": 16,
    "hotkey_record": "ctrl+shift+r",
    "hotkey_meeting": "ctrl+shift+m",
    "hotkey_toggle": "ctrl+shift+h",
}

def default_config_path() -> Path:
    if sys.platform == "win32":
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return root / "GooseDetective" / "config.json"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "GooseDetective" / "config.json"
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "goose-detective" / "config.json"

class Config:
    def __init__(self, path: Optional[str] = None):
        self._path = Path(path) if path is not None else default_config_path()
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

    def update_many(self, values: dict):
        self._data.update(values)
        self._save()

    def _save(self):
        dir_ = self._path.parent
        dir_.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=dir_, delete=False, suffix=".tmp"
        ) as tmp:
            json.dump(self._data, tmp, ensure_ascii=False, indent=2)
            tmp_path = tmp.name
        os.replace(tmp_path, self._path)
