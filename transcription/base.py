from dataclasses import dataclass
from typing import Optional
from abc import ABC, abstractmethod
import numpy as np

@dataclass
class TranscriptionResult:
    text: str
    language: str = "zh"
    duration: float = 0.0
    confidence: Optional[float] = None

class TranscriptionEngine(ABC):
    @abstractmethod
    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> TranscriptionResult:
        pass
