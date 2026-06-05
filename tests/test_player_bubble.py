# tests/test_player_bubble.py
import pytest
from dataclasses import dataclass
from typing import Optional

# Skip entirely if PyQt6 or a display is unavailable
pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QApplication
from ui.player_bubble import PlayerBubble

@dataclass
class FakeSegment:
    start: float = 0.0
    end: float = 1.0
    speaker_id: str = "SPEAKER_00"
    text: str = "我在发电室"
    player_label: Optional[str] = "玩家1"

@pytest.fixture(scope="module")
def app():
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    application = QApplication.instance() or QApplication([])
    yield application

def test_bubble_holds_segment(app):
    seg = FakeSegment()
    bubble = PlayerBubble(seg, player_index=0, max_players=16)
    assert bubble.segment is seg

def test_set_annotation_shows_label(app):
    seg = FakeSegment()
    bubble = PlayerBubble(seg, player_index=0)
    bubble.set_annotation("与玩家2矛盾")
    assert bubble._annotation_label.isVisibleTo(bubble)
    assert "与玩家2矛盾" in bubble._annotation_label.text()

def test_set_annotation_empty_hides(app):
    seg = FakeSegment()
    bubble = PlayerBubble(seg, player_index=0)
    bubble.set_annotation("something")
    bubble.set_annotation("")
    assert not bubble._annotation_label.isVisibleTo(bubble)
