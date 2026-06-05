# ui/settings_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                              QWidget, QLabel, QLineEdit, QComboBox, QSlider,
                              QPushButton, QFormLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence
from config import Config
from analysis.router import PRESETS

class HotkeyButton(QPushButton):
    """Click then press a key combo to record a new hotkey."""
    hotkey_changed = pyqtSignal(str)

    def __init__(self, current: str, parent=None):
        super().__init__(current, parent)
        self._recording = False
        self.clicked.connect(self._start_recording)

    def _start_recording(self):
        self._recording = True
        self.setText("按下快捷键...")
        self.setStyleSheet("background: #e08c4a; color: #1a2a3a;")

    def keyPressEvent(self, event):
        if self._recording:
            seq = QKeySequence(event.keyCombination()).toString().lower()
            self.setText(seq)
            self._recording = False
            self.setStyleSheet("")
            self.hotkey_changed.emit(seq)
        else:
            super().keyPressEvent(event)

class SettingsDialog(QDialog):
    settings_saved = pyqtSignal()

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self._config = config
        self.setWindowTitle("⚙ 鹅探长设置")
        self.setMinimumWidth(420)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        tabs.addTab(self._build_audio_tab(), "🎙 音频")
        tabs.addTab(self._build_ai_tab(), "🤖 AI模型")
        tabs.addTab(self._build_ui_tab(), "🎨 界面")
        tabs.addTab(self._build_hotkey_tab(), "⌨ 快捷键")

        layout.addWidget(tabs)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.setProperty("class", "main_btn")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _build_audio_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        self._stt_combo = QComboBox()
        self._stt_combo.addItems(["whisper（本地）", "cloud（云端）"])
        self._stt_combo.setCurrentIndex(0 if self._config.get("stt_engine") == "whisper" else 1)
        form.addRow("转录引擎：", self._stt_combo)

        self._whisper_model = QComboBox()
        self._whisper_model.addItems(["tiny", "base", "small", "medium", "large-v3"])
        self._whisper_model.setCurrentText(self._config.get("whisper_model", "medium"))
        form.addRow("Whisper模型：", self._whisper_model)

        self._cloud_key = QLineEdit(self._config.get("cloud_stt_key", ""))
        self._cloud_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._cloud_key.setPlaceholderText("云端STT API Key")
        form.addRow("云端Key：", self._cloud_key)
        return w

    def _build_ai_tab(self):
        w = QWidget()
        form = QFormLayout(w)

        self._preset_combo = QComboBox()
        self._preset_combo.addItems(["自定义"] + list(PRESETS.keys()))
        form.addRow("预设：", self._preset_combo)
        self._preset_combo.currentTextChanged.connect(self._on_preset_changed)

        self._ai_url = QLineEdit(self._config.get("ai_base_url", ""))
        self._ai_url.setPlaceholderText("https://api.deepseek.com/v1")
        form.addRow("Base URL：", self._ai_url)

        self._ai_key = QLineEdit(self._config.get("ai_api_key", ""))
        self._ai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._ai_key.setPlaceholderText("API Key")
        form.addRow("API Key：", self._ai_key)

        self._ai_model = QLineEdit(self._config.get("ai_model", ""))
        self._ai_model.setPlaceholderText("模型名称，如 deepseek-chat")
        form.addRow("模型：", self._ai_model)
        return w

    def _build_ui_tab(self):
        w = QWidget()
        form = QFormLayout(w)

        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(30, 100)
        self._opacity_slider.setValue(int(self._config.get("overlay_opacity", 0.85) * 100))
        form.addRow("透明度：", self._opacity_slider)

        self._width_slider = QSlider(Qt.Orientation.Horizontal)
        self._width_slider.setRange(300, 700)
        self._width_slider.setValue(self._config.get("overlay_width", 420))
        form.addRow("宽度（px）：", self._width_slider)
        return w

    def _build_hotkey_tab(self):
        w = QWidget()
        form = QFormLayout(w)

        self._hk_record = HotkeyButton(self._config.get("hotkey_record", "ctrl+shift+r"))
        self._hk_meeting = HotkeyButton(self._config.get("hotkey_meeting", "ctrl+shift+m"))
        self._hk_toggle = HotkeyButton(self._config.get("hotkey_toggle", "ctrl+shift+h"))

        form.addRow("全程录制：", self._hk_record)
        form.addRow("会议模式：", self._hk_meeting)
        form.addRow("显示/隐藏：", self._hk_toggle)
        return w

    def _on_preset_changed(self, name: str):
        if name in PRESETS:
            self._ai_url.setText(PRESETS[name]["base_url"])
            self._ai_model.setText(PRESETS[name]["model"])

    def _save(self):
        self._config.set("stt_engine", "whisper" if self._stt_combo.currentIndex() == 0 else "cloud")
        self._config.set("whisper_model", self._whisper_model.currentText())
        self._config.set("cloud_stt_key", self._cloud_key.text())
        self._config.set("ai_base_url", self._ai_url.text())
        self._config.set("ai_api_key", self._ai_key.text())
        self._config.set("ai_model", self._ai_model.text())
        self._config.set("overlay_opacity", self._opacity_slider.value() / 100.0)
        self._config.set("overlay_width", self._width_slider.value())
        self._config.set("hotkey_record", self._hk_record.text())
        self._config.set("hotkey_meeting", self._hk_meeting.text())
        self._config.set("hotkey_toggle", self._hk_toggle.text())
        self.settings_saved.emit()
        self.accept()
