# ui/transcript_panel.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QLabel)
from PyQt6.QtCore import Qt, pyqtSlot
from ui.player_bubble import PlayerBubble

class TranscriptPanel(QWidget):
    """Left-side live speech record panel."""

    def __init__(self, diarization_engine, max_players: int = 16, parent=None):
        super().__init__(parent)
        self._engine = diarization_engine
        self._max_players = max_players
        self._player_index: dict = {}  # label -> 0-based color index
        self._color_counter = 0
        self._bubbles: list = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("📜 发言记录")
        header.setStyleSheet("color: #f5c842; font-size: 13px; font-weight: bold; padding: 6px;")
        layout.addWidget(header)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._container_layout.setSpacing(2)
        self._container_layout.addStretch()

        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll)

    def _color_index_for(self, label: str) -> int:
        if label not in self._player_index:
            self._player_index[label] = self._color_counter
            self._color_counter += 1
        return self._player_index[label]

    @pyqtSlot(object)
    def add_segment(self, segment):
        """Add a new speech bubble. segment is a SpeakerSegment."""
        label = segment.player_label or "未知"
        index = self._color_index_for(label)

        bubble = PlayerBubble(segment, index, self._max_players)
        bubble.reassign_requested.connect(self._on_reassign)
        self._bubbles.append(bubble)

        # Insert before the trailing stretch
        count = self._container_layout.count()
        self._container_layout.insertWidget(count - 1, bubble)
        self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        )

    def update_annotation(self, segment, annotation: str):
        for bubble in self._bubbles:
            if bubble.segment is segment:
                bubble.set_annotation(annotation)
                break

    def _on_reassign(self, segment, new_label: str):
        self._engine.reassign(segment, new_label)
        # Ensure the new label has a color index assigned
        self._color_index_for(new_label)

    def clear(self):
        for bubble in self._bubbles:
            bubble.deleteLater()
        self._bubbles.clear()
        self._player_index.clear()
        self._color_counter = 0
