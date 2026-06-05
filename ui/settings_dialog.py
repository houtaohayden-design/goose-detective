# ui/settings_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                              QWidget, QLineEdit, QComboBox, QSlider,
                              QPushButton, QFormLayout, QCheckBox, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence
from config import Config
from audio.capture import AudioCapture
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
        tabs.addTab(self._build_advanced_tab(), "🛠 高级")
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

        self._mic_device = QComboBox()
        self._system_device = QComboBox()
        self._populate_audio_devices()
        form.addRow("麦克风设备：", self._mic_device)
        form.addRow("系统音频设备：", self._system_device)

        self._cloud_key = QLineEdit(self._config.get("cloud_stt_key", ""))
        self._cloud_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._cloud_key.setPlaceholderText("讯飞 APIKey")
        form.addRow("讯飞 APIKey：", self._cloud_key)

        self._cloud_app_id = QLineEdit(self._config.get("cloud_stt_app_id", ""))
        self._cloud_app_id.setPlaceholderText("讯飞 APPID")
        form.addRow("讯飞 APPID：", self._cloud_app_id)

        self._cloud_api_secret = QLineEdit(self._config.get("cloud_stt_api_secret", ""))
        self._cloud_api_secret.setEchoMode(QLineEdit.EchoMode.Password)
        self._cloud_api_secret.setPlaceholderText("讯飞 APISecret")
        form.addRow("讯飞 APISecret：", self._cloud_api_secret)

        self._hf_token = QLineEdit(self._config.get("hf_token", ""))
        self._hf_token.setEchoMode(QLineEdit.EchoMode.Password)
        self._hf_token.setPlaceholderText("Hugging Face Token（说话人分离）")
        form.addRow("HF Token：", self._hf_token)
        return w

    def _populate_audio_devices(self):
        def add_items(combo: QComboBox, selected):
            combo.addItem("系统默认", None)
            for device in devices:
                combo.addItem(f"{device['index']} - {device['name']}", device["index"])
            if selected is not None:
                for idx in range(combo.count()):
                    if combo.itemData(idx) == selected:
                        combo.setCurrentIndex(idx)
                        break

        try:
            devices = AudioCapture.list_devices()
        except Exception:
            devices = []
        add_items(self._mic_device, self._config.get("mic_device"))
        add_items(self._system_device, self._config.get("system_device"))

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

        self._ai_timeout = QSpinBox()
        self._ai_timeout.setRange(5, 120)
        self._ai_timeout.setSuffix(" 秒")
        self._ai_timeout.setValue(int(self._config.get("ai_timeout", 30)))
        form.addRow("请求超时：", self._ai_timeout)
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

    def _build_advanced_tab(self):
        w = QWidget()
        form = QFormLayout(w)

        self._enable_quick_check = QCheckBox("开启实时矛盾快检")
        self._enable_quick_check.setChecked(bool(self._config.get("enable_quick_check", True)))
        form.addRow("实时分析：", self._enable_quick_check)

        self._history_limit = QSpinBox()
        self._history_limit.setRange(1, 50)
        self._history_limit.setValue(int(self._config.get("quick_check_history_limit", 10)))
        form.addRow("快检历史条数：", self._history_limit)

        self._buffer_seconds = QSpinBox()
        self._buffer_seconds.setRange(5, 300)
        self._buffer_seconds.setSuffix(" 秒")
        self._buffer_seconds.setValue(int(self._config.get("audio_buffer_seconds", 30)))
        form.addRow("音频缓存上限：", self._buffer_seconds)
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
        self._config.update_many({
            "stt_engine": "whisper" if self._stt_combo.currentIndex() == 0 else "cloud",
            "whisper_model": self._whisper_model.currentText(),
            "mic_device": self._mic_device.currentData(),
            "system_device": self._system_device.currentData(),
            "cloud_stt_key": self._cloud_key.text(),
            "cloud_stt_app_id": self._cloud_app_id.text(),
            "cloud_stt_api_secret": self._cloud_api_secret.text(),
            "hf_token": self._hf_token.text(),
            "ai_base_url": self._ai_url.text().strip(),
            "ai_api_key": self._ai_key.text(),
            "ai_model": self._ai_model.text().strip(),
            "ai_timeout": self._ai_timeout.value(),
            "enable_quick_check": self._enable_quick_check.isChecked(),
            "quick_check_history_limit": self._history_limit.value(),
            "audio_buffer_seconds": self._buffer_seconds.value(),
            "overlay_opacity": self._opacity_slider.value() / 100.0,
            "overlay_width": self._width_slider.value(),
            "hotkey_record": self._hk_record.text(),
            "hotkey_meeting": self._hk_meeting.text(),
            "hotkey_toggle": self._hk_toggle.text(),
        })
        self.settings_saved.emit()
        self.accept()
