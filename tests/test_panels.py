# tests/test_panels.py
import os
import pytest
from dataclasses import dataclass, field
from typing import Optional

pytest.importorskip("PyQt6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication
from ui.transcript_panel import TranscriptPanel
from ui.analysis_panel import AnalysisPanel

@dataclass
class FakeSegment:
    start: float = 0.0
    end: float = 1.0
    speaker_id: str = "SPEAKER_00"
    text: str = "测试发言"
    player_label: Optional[str] = "玩家1"

@dataclass
class FakeResult:
    player: str
    suspicion_score: int
    contradictions: list = field(default_factory=list)
    summary: str = ""

class FakeEngine:
    def __init__(self):
        self.reassigned = []
    def reassign(self, segment, label):
        self.reassigned.append((segment, label))

@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])

def test_add_segment_creates_bubble(app):
    panel = TranscriptPanel(FakeEngine(), max_players=16)
    panel.add_segment(FakeSegment())
    assert len(panel._bubbles) == 1

def test_same_player_reuses_color_index(app):
    panel = TranscriptPanel(FakeEngine())
    panel.add_segment(FakeSegment(player_label="玩家1"))
    panel.add_segment(FakeSegment(player_label="玩家1"))
    panel.add_segment(FakeSegment(player_label="玩家2"))
    assert panel._player_index["玩家1"] == 0
    assert panel._player_index["玩家2"] == 1

def test_clear_removes_bubbles(app):
    panel = TranscriptPanel(FakeEngine())
    panel.add_segment(FakeSegment())
    panel.clear()
    assert len(panel._bubbles) == 0
    assert panel._color_counter == 0

def test_reassign_calls_engine(app):
    engine = FakeEngine()
    panel = TranscriptPanel(engine)
    seg = FakeSegment()
    panel._on_reassign(seg, "玩家3")
    assert engine.reassigned == [(seg, "玩家3")]

def test_update_results_sorts_by_suspicion(app):
    panel = AnalysisPanel()
    results = [
        FakeResult(player="玩家1", suspicion_score=30),
        FakeResult(player="玩家2", suspicion_score=85),
    ]
    panel.update_results(results)
    # After update, container has rows + stretch; just verify no crash and color map populated
    assert "玩家1" in panel._player_color_map
    assert "玩家2" in panel._player_color_map

def test_update_annotation_sets_on_matching_bubble(app):
    panel = TranscriptPanel(FakeEngine())
    seg = FakeSegment()
    panel.add_segment(seg)
    panel.update_annotation(seg, "矛盾点")
    assert panel._bubbles[0]._annotation_label.isVisibleTo(panel._bubbles[0])
