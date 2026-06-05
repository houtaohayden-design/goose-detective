# tests/test_overlay.py
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

pytest.importorskip("PyQt6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication
from config import Config


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


def make_overlay(config):
    # Patch heavy engines so no model loads / no audio devices needed
    with patch("ui.overlay.WhisperEngine"), \
         patch("ui.overlay.AudioCapture"), \
         patch("ui.overlay.DiarizationEngine"):
        from ui.overlay import OverlayWindow
        return OverlayWindow(config)


def test_router_none_when_no_api_key(app, config):
    overlay = make_overlay(config)
    assert overlay._router is None


def test_router_built_when_api_key_present(app, config):
    config.set("ai_api_key", "test-key")
    with patch("ui.overlay.AnalysisRouter") as mock_router:
        overlay = make_overlay(config)
        assert overlay._router is not None
        mock_router.assert_called_once()


def test_router_rejects_non_https_base_url(app, config):
    config.set("ai_api_key", "test-key")
    config.set("ai_base_url", "http://localhost:8000/v1")
    overlay = make_overlay(config)
    assert overlay._router is None


def test_initial_mode_is_idle(app, config):
    overlay = make_overlay(config)
    assert overlay._mode == "idle"


def test_meeting_mode_ignored_while_recording(app, config):
    overlay = make_overlay(config)
    overlay._mode = "recording"
    overlay._toggle_meeting()
    # Should remain recording, not switch to meeting
    assert overlay._mode == "recording"


def test_build_cloud_engine_when_configured(app, config):
    config.set("stt_engine", "cloud")
    with patch("ui.overlay.AudioCapture"), \
         patch("ui.overlay.DiarizationEngine"), \
         patch("ui.overlay.CloudSTTEngine") as mock_cloud:
        from ui.overlay import OverlayWindow
        overlay = OverlayWindow(config)
        mock_cloud.assert_called_once()


def test_capture_uses_buffer_setting(app, config):
    config.set("audio_buffer_seconds", 15)
    with patch("ui.overlay.AudioCapture") as mock_capture, \
         patch("ui.overlay.DiarizationEngine"), \
         patch("ui.overlay.WhisperEngine"):
        from ui.overlay import OverlayWindow
        OverlayWindow(config)
        mock_capture.assert_called_with(max_buffer_chunks=30)


def test_worker_has_error_signal(app, config):
    from ui.overlay import RecordWorker
    import threading
    worker = RecordWorker(MagicMock(), MagicMock(), MagicMock(), None, [], threading.Lock())
    assert hasattr(worker, "error")


def test_reassign_updates_records(app, config):
    overlay = make_overlay(config)
    segment = MagicMock()
    segment.speaker_id = "SPEAKER_01"
    overlay._records = [
        {"speaker_id": "SPEAKER_01", "segment_id": 1, "player": "玩家1", "text": "a"},
        {"speaker_id": "SPEAKER_02", "segment_id": 2, "player": "玩家2", "text": "b"},
    ]
    overlay._on_segment_reassigned(segment, "玩家5")
    assert overlay._records[0]["player"] == "玩家5"
    assert overlay._records[1]["player"] == "玩家2"


def test_process_once_raises_on_transcribe_failure(app, config):
    from ui.overlay import RecordWorker
    import threading
    import numpy as np
    from dataclasses import dataclass
    capture = MagicMock()
    capture.sample_rate = 16000
    capture.get_audio.return_value = np.zeros(16000, dtype="float32")

    @dataclass
    class Seg:
        start: float
        end: float
        text: str = ""
        player_label: str = "玩家1"

    diarization = MagicMock()
    diarization.process.return_value = [Seg(start=0.0, end=1.0)]
    transcription = MagicMock()
    transcription.transcribe.side_effect = RuntimeError("boom")
    worker = RecordWorker(capture, transcription, diarization, None, [], threading.Lock())
    with pytest.raises(RuntimeError):
        worker._process_once()


def test_process_once_transcribes_per_segment(app, config):
    from ui.overlay import RecordWorker
    import threading, numpy as np
    from dataclasses import dataclass
    from typing import Optional

    @dataclass
    class Seg:
        start: float
        end: float
        speaker_id: str = "S0"
        text: str = ""
        player_label: Optional[str] = "玩家1"

    capture = MagicMock()
    capture.sample_rate = 16000
    capture.get_audio.side_effect = lambda route: np.ones(16000, dtype="float32")

    diar = MagicMock()
    diar.process.side_effect = [
        [Seg(start=0.0, end=0.5, player_label="玩家1"),
         Seg(start=0.5, end=1.0, player_label="玩家2")],
        [],  # MIC route
    ]

    transcription = MagicMock()
    transcription.transcribe.side_effect = [
        MagicMock(text="第一个人说话"),
        MagicMock(text="第二个人说话"),
    ]

    records = []
    worker = RecordWorker(capture, transcription, diar, None, records, threading.Lock())
    emitted = []
    worker.new_segment.connect(lambda s: emitted.append(s))
    worker._process_once()

    texts = [s.text for s in emitted if s.text]
    assert "第一个人说话" in texts
    assert "第二个人说话" in texts
