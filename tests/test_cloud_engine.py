# tests/test_cloud_engine.py
import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from transcription.cloud_engine import CloudSTTEngine
from transcription.base import TranscriptionResult

def test_unknown_provider_raises():
    engine = CloudSTTEngine(provider="unknown", api_key="key")
    audio = np.zeros(16000, dtype=np.float32)
    with pytest.raises(ValueError, match="Unknown STT provider"):
        engine.transcribe(audio)

def test_empty_audio_returns_empty():
    engine = CloudSTTEngine(provider="xunfei", api_key="key")
    result = engine.transcribe(np.array([], dtype=np.float32))
    assert result.text == ""

def test_aliyun_raises_not_implemented():
    engine = CloudSTTEngine(provider="aliyun", api_key="key")
    audio = np.zeros(16000, dtype=np.float32)
    with pytest.raises(NotImplementedError):
        engine.transcribe(audio)

def test_xunfei_extracts_text_from_ws_list():
    engine = CloudSTTEngine(provider="xunfei", api_key="key")
    audio = np.zeros(16000, dtype=np.float32)
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": {
            "result": {
                "ws": [
                    {"cw": [{"w": "我"}, {"w": "在"}]},
                    {"cw": [{"w": "发电室"}]},
                ]
            }
        }
    }
    with patch("transcription.cloud_engine.requests.post", return_value=mock_response):
        result = engine.transcribe(audio)
    assert result.text == "我在发电室"
