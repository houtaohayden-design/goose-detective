# ui/overlay.py
import threading
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QPushButton, QLabel)
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from config import Config
from audio.capture import AudioCapture, AudioRoute
from audio.diarization import DiarizationEngine
from transcription.whisper_engine import WhisperEngine
from transcription.cloud_engine import CloudSTTEngine
from analysis.router import AnalysisRouter
from ui.transcript_panel import TranscriptPanel
from ui.analysis_panel import AnalysisPanel
from ui.settings_dialog import SettingsDialog


class RecordWorker(QThread):
    """Background thread: pull audio from AudioCapture -> transcribe -> diarize -> emit."""
    new_segment = pyqtSignal(object)
    annotation_ready = pyqtSignal(object, str)
    error = pyqtSignal(str)

    def __init__(self, capture, transcription_engine, diarization, router, records, records_lock, parent=None):
        super().__init__(parent)
        self._capture = capture
        self._transcription = transcription_engine
        self._diarization = diarization
        self._router = router
        self._records = records
        self._records_lock = records_lock
        self._running = False

    def run(self):
        self._running = True
        while self._running:
            self.msleep(500)
            try:
                self._process_once()
            except Exception as e:
                self.error.emit(str(e))

    def _process_once(self):
        for route in (AudioRoute.SYSTEM, AudioRoute.MIC):
            audio = self._capture.get_audio(route)
            if len(audio) < 8000:  # < 0.5s, skip
                continue
            result = self._transcription.transcribe(audio)
            if not result.text.strip():
                continue
            segs = self._diarization.process(audio)
            for seg in segs:
                seg.text = result.text
                if route == AudioRoute.MIC:
                    seg.player_label = "我"
                with self._records_lock:
                    self._records.append({"player": seg.player_label,
                                          "time": f"{seg.start:.0f}s",
                                          "text": seg.text})
                    history_snapshot = list(self._records[:-1])
                self.new_segment.emit(seg)
                if self._router:
                    annotation = self._router.quick_check(
                        seg.text, seg.player_label, history_snapshot
                    )
                    if annotation:
                        self.annotation_ready.emit(seg, annotation)

    def stop(self):
        self._running = False
        self.wait()


class OverlayWindow(QMainWindow):
    def __init__(self, config: Config):
        super().__init__()
        self._config = config
        self._records = []
        self._records_lock = threading.Lock()
        self._worker = None
        self._mode = "idle"  # idle | recording | meeting

        self._capture = AudioCapture()
        self._diarization = DiarizationEngine(
            on_new_speaker=lambda label: print(f"新玩家检测到: {label}")
        )
        self._transcription = self._build_transcription_engine()
        self._router = self._build_router()

        self._setup_window()
        self._setup_ui()
        self._apply_opacity()
        self._register_hotkeys()

    def _build_transcription_engine(self):
        if self._config.get("stt_engine") == "whisper":
            return WhisperEngine(model_size=self._config.get("whisper_model", "medium"))
        return CloudSTTEngine(
            provider=self._config.get("cloud_stt_provider", "xunfei"),
            api_key=self._config.get("cloud_stt_key", ""),
        )

    def _build_router(self):
        key = self._config.get("ai_api_key", "")
        url = self._config.get("ai_base_url", "")
        model = self._config.get("ai_model", "")
        if not key:
            return None
        return AnalysisRouter(base_url=url, api_key=key, model=model)

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumHeight(400)
        self.resize(self._config.get("overlay_width", 420), 600)

    def _setup_ui(self):
        central = QWidget()
        central.setObjectName("overlay")
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title bar
        titlebar = QWidget()
        titlebar.setObjectName("titlebar")
        titlebar.setFixedHeight(40)
        tb_layout = QHBoxLayout(titlebar)
        tb_layout.setContentsMargins(10, 4, 10, 4)

        logo = QLabel("🪶 鹅探长")
        logo.setObjectName("title_label")
        tb_layout.addWidget(logo)
        tb_layout.addStretch()

        self._record_btn = QPushButton("⏺ 全程")
        self._record_btn.setProperty("class", "main_btn")
        self._record_btn.clicked.connect(self._toggle_recording)
        tb_layout.addWidget(self._record_btn)

        self._meeting_btn = QPushButton("🔔 会议")
        self._meeting_btn.setProperty("class", "main_btn")
        self._meeting_btn.clicked.connect(self._toggle_meeting)
        tb_layout.addWidget(self._meeting_btn)

        self._analyze_btn = QPushButton("🔍")
        self._analyze_btn.setProperty("class", "main_btn")
        self._analyze_btn.clicked.connect(self._run_full_analysis)
        tb_layout.addWidget(self._analyze_btn)

        settings_btn = QPushButton("⚙")
        settings_btn.setProperty("class", "main_btn")
        settings_btn.clicked.connect(self._open_settings)
        tb_layout.addWidget(settings_btn)

        main_layout.addWidget(titlebar)

        # Body: left transcript / right analysis
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self._transcript_panel = TranscriptPanel(self._diarization,
                                                  max_players=self._config.get("max_players", 16))
        self._analysis_panel = AnalysisPanel()

        body_layout.addWidget(self._transcript_panel, 3)
        body_layout.addWidget(self._analysis_panel, 2)
        main_layout.addWidget(body)

        # Drag support
        titlebar.mousePressEvent = self._drag_start
        titlebar.mouseMoveEvent = self._drag_move
        self._drag_pos = QPoint()

    def _apply_opacity(self):
        self.setWindowOpacity(self._config.get("overlay_opacity", 0.85))

    def _register_hotkeys(self):
        self._shortcuts = []
        for key_cfg, handler in [
            ("hotkey_record", self._toggle_recording),
            ("hotkey_meeting", self._toggle_meeting),
            ("hotkey_toggle", self._toggle_visibility),
        ]:
            seq = self._config.get(key_cfg)
            if seq:
                sc = QShortcut(QKeySequence(seq), self)
                sc.activated.connect(handler)
                self._shortcuts.append(sc)

    def _toggle_recording(self):
        if self._mode == "recording":
            self._stop_worker()
            self._mode = "idle"
            self._record_btn.setText("⏺ 全程")
        else:
            if self._mode == "meeting":
                return  # already recording in meeting mode
            self._start_worker()
            self._mode = "recording"
            self._record_btn.setText("⏹ 停止")

    def _toggle_meeting(self):
        if self._mode == "meeting":
            self._stop_worker()
            self._mode = "idle"
            self._meeting_btn.setText("🔔 会议")
            self._run_full_analysis()
        else:
            if self._mode == "recording":
                return
            self._records.clear()
            self._transcript_panel.clear()
            self._start_worker()
            self._mode = "meeting"
            self._meeting_btn.setText("⏹ 结束会议")

    def _start_worker(self):
        if self._worker is not None:
            return
        self._capture.start()
        self._worker = RecordWorker(
            self._capture, self._transcription,
            self._diarization, self._router, self._records, self._records_lock
        )
        self._worker.new_segment.connect(self._transcript_panel.add_segment)
        self._worker.annotation_ready.connect(self._transcript_panel.update_annotation)
        self._worker.error.connect(self._on_worker_error)
        self._worker.start()

    def _on_worker_error(self, msg: str):
        print(f"[RecordWorker error] {msg}")

    def _stop_worker(self):
        if self._worker:
            self._worker.stop()
            self._worker = None
        self._capture.stop()

    def _run_full_analysis(self):
        if not self._router:
            return
        with self._records_lock:
            records_snapshot = list(self._records)
        if not records_snapshot:
            return
        results = self._router.analyze(records_snapshot)
        self._analysis_panel.update_results(results)

    def _open_settings(self):
        dlg = SettingsDialog(self._config, self)
        dlg.settings_saved.connect(self._on_settings_saved)
        dlg.exec()

    def _on_settings_saved(self):
        self._apply_opacity()
        self.resize(self._config.get("overlay_width", 420), self.height())
        was_running = self._worker is not None
        self._transcription = self._build_transcription_engine()
        self._router = self._build_router()
        if was_running:
            self._stop_worker()
            self._start_worker()

    def _toggle_visibility(self):
        self.setVisible(not self.isVisible())

    def _drag_start(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def _drag_move(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def closeEvent(self, event):
        self._stop_worker()
        super().closeEvent(event)
