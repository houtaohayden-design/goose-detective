import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from audio.capture import AudioCapture, AudioRoute

def test_audio_route_enum():
    assert AudioRoute.SYSTEM.value == "system"
    assert AudioRoute.MIC.value == "mic"

def test_capture_init():
    cap = AudioCapture(sample_rate=16000)
    assert cap.sample_rate == 16000
    assert cap.is_recording is False

def test_callback_appends_chunks():
    cap = AudioCapture()
    chunk = np.zeros((1024, 1), dtype=np.float32)
    cap._mic_callback(chunk, None, None, None)
    assert len(cap._mic_buffer) == 1
    assert np.array_equal(cap._mic_buffer[0], chunk.flatten())

def test_get_and_clear_buffer():
    cap = AudioCapture()
    cap._mic_buffer.append(np.array([0.1, 0.2], dtype=np.float32))
    cap._mic_buffer.append(np.array([0.3, 0.4], dtype=np.float32))
    result = cap.get_audio(AudioRoute.MIC)
    assert len(result) == 4
    assert len(cap._mic_buffer) == 0

def test_buffer_drops_old_chunks_at_limit():
    cap = AudioCapture(max_buffer_chunks=2)
    cap._mic_callback(np.array([[1.0]], dtype=np.float32), None, None, None)
    cap._mic_callback(np.array([[2.0]], dtype=np.float32), None, None, None)
    cap._mic_callback(np.array([[3.0]], dtype=np.float32), None, None, None)
    result = cap.get_audio(AudioRoute.MIC)
    assert result.tolist() == [2.0, 3.0]
