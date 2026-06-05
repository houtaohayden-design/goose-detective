from enum import Enum
from collections import deque
import numpy as np
import sounddevice as sd
from typing import Optional, Callable
import threading


class AudioRoute(Enum):
    SYSTEM = "system"
    MIC = "mic"


class AudioCapture:
    CHUNK_DURATION = 0.5  # seconds per chunk fed to transcription

    def __init__(self, sample_rate: int = 16000, max_buffer_chunks: int = 60):
        self.sample_rate = sample_rate
        self.max_buffer_chunks = max(1, max_buffer_chunks)
        self.is_recording = False
        self._mic_buffer: deque = deque(maxlen=self.max_buffer_chunks)
        self._system_buffer: deque = deque(maxlen=self.max_buffer_chunks)
        self._mic_lock = threading.Lock()
        self._system_lock = threading.Lock()
        self._mic_stream: Optional[sd.InputStream] = None
        self._system_stream: Optional[sd.InputStream] = None
        self._on_chunk: Optional[Callable] = None  # callback(route, audio_np)

    def set_chunk_callback(self, cb: Callable):
        """Register callback invoked with (AudioRoute, np.ndarray) per chunk."""
        self._on_chunk = cb

    def start(self, mic_device: Optional[int] = None, system_device: Optional[int] = None):
        if self.is_recording:
            return
        with self._mic_lock:
            self._mic_buffer.clear()
        with self._system_lock:
            self._system_buffer.clear()
        self.is_recording = True
        blocksize = int(self.sample_rate * self.CHUNK_DURATION)
        try:
            self._mic_stream = sd.InputStream(
                device=mic_device,
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=blocksize,
                callback=self._mic_callback,
            )
            self._system_stream = sd.InputStream(
                device=system_device,
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=blocksize,
                callback=self._system_callback,
            )
            self._mic_stream.start()
            self._system_stream.start()
        except Exception:
            self.stop()
            raise

    def stop(self):
        self.is_recording = False
        if self._mic_stream:
            self._mic_stream.stop()
            self._mic_stream.close()
            self._mic_stream = None
        if self._system_stream:
            self._system_stream.stop()
            self._system_stream.close()
            self._system_stream = None

    def get_audio(self, route: AudioRoute) -> np.ndarray:
        """Drain buffer and return concatenated audio. Thread-safe drain."""
        buf = self._mic_buffer if route == AudioRoute.MIC else self._system_buffer
        lock = self._mic_lock if route == AudioRoute.MIC else self._system_lock
        chunks = []
        with lock:
            while buf:
                chunks.append(buf.popleft())
        if not chunks:
            return np.array([], dtype=np.float32)
        return np.concatenate(chunks)

    def _mic_callback(self, indata, frames, time, status):
        flat = indata.flatten().copy()
        with self._mic_lock:
            self._mic_buffer.append(flat)
        if self._on_chunk:
            self._on_chunk(AudioRoute.MIC, flat)

    def _system_callback(self, indata, frames, time, status):
        flat = indata.flatten().copy()
        with self._system_lock:
            self._system_buffer.append(flat)
        if self._on_chunk:
            self._on_chunk(AudioRoute.SYSTEM, flat)

    @staticmethod
    def list_devices() -> list:
        """Return list of available audio devices."""
        devices = sd.query_devices()
        return [
            {"index": i, "name": d["name"], "inputs": d["max_input_channels"]}
            for i, d in enumerate(devices)
            if d["max_input_channels"] > 0
        ]
