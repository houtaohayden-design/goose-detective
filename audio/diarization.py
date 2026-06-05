from dataclasses import dataclass, field
from typing import Optional, Callable
import threading
import numpy as np

@dataclass
class SpeakerSegment:
    start: float
    end: float
    speaker_id: str       # pyannote raw ID e.g. "SPEAKER_00"
    text: str = ""
    player_label: Optional[str] = None   # user-visible label e.g. "玩家1"

class DiarizationEngine:
    """
    Speaker diarization engine.
    pyannote requires a Hugging Face token; first run downloads ~300MB model.
    Falls back to CPU if no GPU available.
    """

    def __init__(self, hf_token: Optional[str] = None, on_new_speaker: Optional[Callable] = None):
        self._segments: list = []
        self._speaker_map: dict = {}  # speaker_id -> player_label
        self._player_counter = 1
        self._on_new_speaker = on_new_speaker   # callback(player_label) notifies UI
        self._pipeline = None
        self.__lock = threading.Lock()
        if hf_token:
            self._load_pipeline(hf_token)

    @property
    def _lock(self) -> threading.Lock:
        try:
            return self.__lock
        except AttributeError:
            self.__lock = threading.Lock()
            return self.__lock

    def _load_pipeline(self, hf_token: str):
        from pyannote.audio import Pipeline
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self._pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=hf_token,
        ).to(torch.device(device))

    def process(self, audio: np.ndarray, sample_rate: int = 16000) -> list:
        """Run speaker diarization on audio chunk, return new SpeakerSegments."""
        with self._lock:
            if self._pipeline is None:
                # No model: return single segment labeled as unknown
                seg = SpeakerSegment(start=0.0, end=len(audio)/sample_rate,
                                      speaker_id="SPEAKER_00")
                seg.player_label = self._auto_label("SPEAKER_00")
                self._segments.append(seg)
                return [seg]

        import torch
        diarization = self._pipeline({"waveform": torch.tensor(audio).unsqueeze(0),
                                       "sample_rate": sample_rate})
        with self._lock:
            new_segs = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                seg = SpeakerSegment(start=turn.start, end=turn.end, speaker_id=speaker)
                seg.player_label = self._auto_label(speaker)
                self._segments.append(seg)
                new_segs.append(seg)
            return new_segs

    def _auto_label(self, speaker_id: str) -> str:
        if speaker_id not in self._speaker_map:
            label = f"玩家{self._player_counter}"
            self._speaker_map[speaker_id] = label
            self._player_counter += 1
            if getattr(self, '_on_new_speaker', None):
                self._on_new_speaker(label)
        return self._speaker_map[speaker_id]

    def reassign(self, segment: SpeakerSegment, new_label: str):
        """User manually re-attributes a speech segment."""
        with self._lock:
            old_speaker_id = segment.speaker_id
            for seg in self._segments:
                if seg.speaker_id == old_speaker_id:
                    seg.player_label = new_label

    def get_segments(self) -> list:
        return list(self._segments)

    def clear(self):
        with self._lock:
            self._segments.clear()
            self._speaker_map.clear()
            self._player_counter = 1
