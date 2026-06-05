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


def test_worker_has_error_signal(app, config):
    from ui.overlay import RecordWorker
    import threading
    worker = RecordWorker(MagicMock(), MagicMock(), MagicMock(), None, [], threading.Lock())
    assert hasattr(worker, "error")


def test_process_once_raises_on_transcribe_failure(app, config):
    from ui.overlay import RecordWorker
    import threading
    import numpy as np
    capture = MagicMock()
    capture.get_audio.return_value = np.zeros(16000, dtype="float32")
    transcription = MagicMock()
    transcription.transcribe.side_effect = RuntimeError("boom")
    worker = RecordWorker(capture, transcription, MagicMock(), None, [], threading.Lock())
    with pytest.raises(RuntimeError):
        worker._process_once()
