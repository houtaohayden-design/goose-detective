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

def test_xunfei_accumulates_ws_results():
    engine = CloudSTTEngine(provider="xunfei", api_key="key", app_id="app", api_secret="secret")
    audio = np.zeros(16000, dtype=np.float32)
    fake_ws = MagicMock()
    frames = [
        '{"code":0,"data":{"status":1,"result":{"ws":[{"cw":[{"w":"我"}]}]}}}',
        '{"code":0,"data":{"status":2,"result":{"ws":[{"cw":[{"w":"在发电室"}]}]}}}',
    ]
    fake_ws.recv.side_effect = frames
    with patch("transcription.cloud_engine.websocket.create_connection", return_value=fake_ws):
        result = engine.transcribe(audio)
    assert result.text == "我在发电室"


def test_xunfei_error_code_returns_empty():
    engine = CloudSTTEngine(provider="xunfei", api_key="key", app_id="app", api_secret="secret")
    audio = np.zeros(16000, dtype=np.float32)
    fake_ws = MagicMock()
    fake_ws.recv.side_effect = ['{"code":10043,"message":"auth error"}']
    with patch("transcription.cloud_engine.websocket.create_connection", return_value=fake_ws):
        result = engine.transcribe(audio)
    assert result.text == ""
