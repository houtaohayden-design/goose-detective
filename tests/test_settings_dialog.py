# tests/test_settings_dialog.py
import os
import tempfile
import pytest

pytest.importorskip("PyQt6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication
from config import Config
from ui.settings_dialog import SettingsDialog, HotkeyButton

@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])

@pytest.fixture
def config():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    cfg = Config(path)
    yield cfg
    os.unlink(path)

def test_dialog_loads_config_values(app, config):
    config.set("ai_model", "my-model")
    dlg = SettingsDialog(config)
    assert dlg._ai_model.text() == "my-model"

def test_save_persists_values(app, config):
    dlg = SettingsDialog(config)
    dlg._ai_key.setText("secret-key")
    dlg._whisper_model.setCurrentText("large-v3")
    dlg._save()
    assert config.get("ai_api_key") == "secret-key"
    assert config.get("whisper_model") == "large-v3"

def test_preset_changed_fills_url_and_model(app, config):
    dlg = SettingsDialog(config)
    dlg._on_preset_changed("DeepSeek")
    assert "deepseek" in dlg._ai_url.text().lower()
    assert dlg._ai_model.text() == "deepseek-chat"

def test_opacity_slider_saved_as_fraction(app, config):
    dlg = SettingsDialog(config)
    dlg._opacity_slider.setValue(70)
    dlg._save()
    assert config.get("overlay_opacity") == 0.70

def test_hotkey_button_initial_text(app):
    btn = HotkeyButton("ctrl+shift+r")
    assert btn.text() == "ctrl+shift+r"
