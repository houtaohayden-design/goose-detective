import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from transcription.whisper_engine import WhisperEngine
from transcription.base import TranscriptionResult

def test_result_dataclass():
    r = TranscriptionResult(text="hello", language="zh", duration=1.5)
    assert r.text == "hello"
    assert r.confidence is None

def test_whisper_engine_init():
    with patch("transcription.whisper_engine.WhisperModel") as mock_model:
        engine = WhisperEngine(model_size="tiny")
        mock_model.assert_called_once_with("tiny", device="auto", compute_type="auto")

def test_transcribe_returns_result():
    with patch("transcription.whisper_engine.WhisperModel") as mock_cls:
        mock_model = MagicMock()
        mock_cls.return_value = mock_model
        seg = MagicMock()
        seg.text = " 我在发电室"
        seg.avg_logprob = -0.3
        mock_model.transcribe.return_value = ([seg], MagicMock(language="zh", duration=2.0))

        engine = WhisperEngine(model_size="tiny")
        audio = np.zeros(16000, dtype=np.float32)
        result = engine.transcribe(audio)

        assert result.text == "我在发电室"
        assert result.language == "zh"

def test_transcribe_empty_audio_returns_empty():
    with patch("transcription.whisper_engine.WhisperModel"):
        engine = WhisperEngine.__new__(WhisperEngine)
        engine._model = None
        result = engine.transcribe(np.array([], dtype=np.float32))
        assert result.text == ""
