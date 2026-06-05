# tests/test_config.py
import json, os, tempfile, pytest
from config import Config

def test_default_config():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        cfg = Config(path)
        assert cfg.get("stt_engine") == "whisper"
        assert cfg.get("whisper_model") == "medium"
        assert cfg.get("overlay_opacity") == 0.85
        assert cfg.get("max_players") == 16
    finally:
        os.unlink(path)

def test_set_and_persist():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        cfg = Config(path)
        cfg.set("api_key", "test-key-123")
        cfg2 = Config(path)
        assert cfg2.get("api_key") == "test-key-123"
    finally:
        os.unlink(path)

def test_get_missing_returns_default():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        cfg = Config(path)
        assert cfg.get("nonexistent", "fallback") == "fallback"
    finally:
        os.unlink(path)
