import numpy as np
import requests
import io, soundfile as sf
from transcription.base import TranscriptionEngine, TranscriptionResult

class CloudSTTEngine(TranscriptionEngine):
    """
    Generic cloud STT. Supports xunfei and aliyun providers.
    provider: "xunfei" | "aliyun"
    """

    def __init__(self, provider: str, api_key: str):
        self._provider = provider
        self._api_key = api_key

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> TranscriptionResult:
        wav_bytes = self._to_wav(audio, sample_rate)
        if self._provider == "xunfei":
            return self._xunfei(wav_bytes)
        elif self._provider == "aliyun":
            return self._aliyun(wav_bytes)
        raise ValueError(f"Unknown STT provider: {self._provider}")

    def _to_wav(self, audio: np.ndarray, sr: int) -> bytes:
        buf = io.BytesIO()
        sf.write(buf, audio, sr, format="WAV")
        return buf.getvalue()

    def _xunfei(self, wav_bytes: bytes) -> TranscriptionResult:
        # Xunfei speech recognition REST API (simplified; real impl needs signing)
        url = "https://iat-api.xfyun.cn/v2/iat"
        headers = {"Authorization": f"Bearer {self._api_key}"}
        resp = requests.post(url, headers=headers, data=wav_bytes, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        text = data.get("data", {}).get("result", {}).get("ws", "")
        return TranscriptionResult(text=text)

    def _aliyun(self, wav_bytes: bytes) -> TranscriptionResult:
        raise NotImplementedError("阿里云 STT 待接入")
