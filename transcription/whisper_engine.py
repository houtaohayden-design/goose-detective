import numpy as np
from faster_whisper import WhisperModel
from transcription.base import TranscriptionEngine, TranscriptionResult

class WhisperEngine(TranscriptionEngine):
    def __init__(self, model_size: str = "medium"):
        self._model = WhisperModel(model_size, device="auto", compute_type="auto")

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> TranscriptionResult:
        if len(audio) == 0:
            return TranscriptionResult(text="")
        segments, info = self._model.transcribe(
            audio,
            language="zh",
            beam_size=5,
            vad_filter=True,
        )
        text = "".join(seg.text for seg in segments).strip()
        return TranscriptionResult(
            text=text,
            language=info.language,
            duration=info.duration,
            confidence=None,
        )
