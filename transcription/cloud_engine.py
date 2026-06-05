import base64
import hashlib
import hmac
import json
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from urllib.parse import quote

import numpy as np
import websocket

from transcription.base import TranscriptionEngine, TranscriptionResult


class CloudSTTEngine(TranscriptionEngine):
    """
    Generic cloud STT. Supports xunfei and aliyun providers.
    provider: "xunfei" | "aliyun"

    Xunfei IAT (语音听写) uses a WebSocket API with HMAC-SHA256 signed auth,
    requiring three credentials: app_id, api_key, api_secret.
    """

    _XF_HOST = "iat-api.xfyun.cn"
    _XF_PATH = "/v2/iat"

    def __init__(self, provider: str, api_key: str, app_id: str = "", api_secret: str = ""):
        self._provider = provider
        self._api_key = api_key
        self._app_id = app_id
        self._api_secret = api_secret

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> TranscriptionResult:
        if len(audio) == 0:
            return TranscriptionResult(text="")
        if self._provider == "xunfei":
            return self._xunfei(audio, sample_rate)
        elif self._provider == "aliyun":
            return self._aliyun(audio, sample_rate)
        raise ValueError(f"Unknown STT provider: {self._provider}")

    def _to_pcm16(self, audio: np.ndarray, sr: int) -> bytes:
        """Convert float32 [-1,1] audio to 16kHz mono 16-bit little-endian PCM bytes."""
        audio = np.asarray(audio, dtype=np.float32)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        if sr != 16000:
            # Linear resample to 16kHz.
            n_out = int(round(len(audio) * 16000 / sr))
            if n_out <= 0:
                return b""
            x_old = np.linspace(0.0, 1.0, num=len(audio), endpoint=False)
            x_new = np.linspace(0.0, 1.0, num=n_out, endpoint=False)
            audio = np.interp(x_new, x_old, audio).astype(np.float32)
        audio = np.clip(audio, -1.0, 1.0)
        return (audio * 32767.0).astype("<i2").tobytes()

    def _build_auth_url(self) -> str:
        date = format_datetime(datetime.now(timezone.utc), usegmt=True)
        signature_origin = (
            f"host: {self._XF_HOST}\n"
            f"date: {date}\n"
            f"GET {self._XF_PATH} HTTP/1.1"
        )
        signature_sha = hmac.new(
            self._api_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        signature = base64.b64encode(signature_sha).decode("utf-8")
        authorization_origin = (
            f'api_key="{self._api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature}"'
        )
        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode("utf-8")
        return (
            f"wss://{self._XF_HOST}{self._XF_PATH}"
            f"?authorization={quote(authorization)}"
            f"&date={quote(date)}"
            f"&host={quote(self._XF_HOST)}"
        )

    def _xunfei(self, audio: np.ndarray, sample_rate: int) -> TranscriptionResult:
        try:
            pcm = self._to_pcm16(audio, sample_rate)
            url = self._build_auth_url()
            ws = websocket.create_connection(url, timeout=10)
            try:
                self._xf_send_frames(ws, pcm)
                text = self._xf_recv_loop(ws)
            finally:
                try:
                    ws.close()
                except Exception:
                    pass
            return TranscriptionResult(text=text)
        except Exception as e:
            print(f"[CloudSTTEngine] Xunfei STT failed: {e}", file=sys.stderr)
            return TranscriptionResult(text="")

    def _xf_send_frames(self, ws, pcm: bytes) -> None:
        frame_size = 1280  # ~40ms of 16kHz 16-bit mono PCM
        common = {"app_id": self._app_id}
        business = {
            "language": "zh_cn",
            "domain": "iat",
            "accent": "mandarin",
            "vad_eos": 3000,
        }
        data_fmt = {"format": "audio/L16;rate=16000", "encoding": "raw"}

        if not pcm:
            chunks = [b""]
        else:
            chunks = [pcm[i:i + frame_size] for i in range(0, len(pcm), frame_size)]

        for idx, chunk in enumerate(chunks):
            is_first = idx == 0
            is_last = idx == len(chunks) - 1
            data = dict(data_fmt)
            data["audio"] = base64.b64encode(chunk).decode("utf-8")
            if is_first:
                data["status"] = 0
                frame = {"common": common, "business": business, "data": data}
            elif is_last:
                # last frame sends end-of-stream marker
                frame = {"data": {**data_fmt, "status": 2, "audio": ""}}
            else:
                data["status"] = 1
                frame = {"data": data}
            ws.send(json.dumps(frame))

        # Ensure a terminating status=2 frame is always sent.
        if len(chunks) == 1:
            ws.send(json.dumps({"data": {**data_fmt, "status": 2, "audio": ""}}))

    def _xf_recv_loop(self, ws) -> str:
        parts = []
        while True:
            try:
                raw = ws.recv()
            except Exception:
                break
            if not raw:
                break
            msg = json.loads(raw)
            if msg.get("code", 0) != 0:
                raise RuntimeError(
                    f"Xunfei error code={msg.get('code')} msg={msg.get('message')}"
                )
            data = msg.get("data") or {}
            result = data.get("result") or {}
            for item in result.get("ws", []):
                for cw in item.get("cw", []):
                    parts.append(cw.get("w", ""))
            if data.get("status") == 2:
                break
        return "".join(parts)

    def _aliyun(self, audio: np.ndarray, sample_rate: int) -> TranscriptionResult:
        raise NotImplementedError("阿里云 STT 待接入")
