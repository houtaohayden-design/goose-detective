import numpy as np
import pytest
from audio.diarization import DiarizationEngine, SpeakerSegment

def test_speaker_segment_dataclass():
    seg = SpeakerSegment(start=0.0, end=1.5, speaker_id="SPEAKER_00", text="hello")
    assert seg.player_label is None  # unassigned
    seg.player_label = "玩家1"
    assert seg.player_label == "玩家1"

def test_reassign_speaker():
    engine = DiarizationEngine.__new__(DiarizationEngine)
    engine._segments = []
    seg = SpeakerSegment(start=0.0, end=1.0, speaker_id="SPEAKER_00", text="test")
    engine._segments.append(seg)
    engine.reassign(seg, "玩家3")
    assert seg.player_label == "玩家3"

def test_get_segments_empty():
    engine = DiarizationEngine.__new__(DiarizationEngine)
    engine._segments = []
    assert engine.get_segments() == []

def test_auto_label_new_speaker():
    engine = DiarizationEngine.__new__(DiarizationEngine)
    engine._segments = []
    engine._speaker_map = {}
    engine._player_counter = 1
    label = engine._auto_label("SPEAKER_00")
    assert label == "玩家1"
    label2 = engine._auto_label("SPEAKER_00")
    assert label2 == "玩家1"  # same speaker reuses label
    label3 = engine._auto_label("SPEAKER_01")
    assert label3 == "玩家2"
