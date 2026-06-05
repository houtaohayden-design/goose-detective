# ui/player_bubble.py
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout,
                              QLabel, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.theme import player_color

class PlayerBubble(QFrame):
    """Single speech bubble. Right-click to reassign to a different player."""

    reassign_requested = pyqtSignal(object, str)  # (segment, new_label)

    def __init__(self, segment, player_index: int, max_players: int = 16, parent=None):
        super().__init__(parent)
        self.segment = segment
        self._max_players = max_players
        self._setup_ui(player_index)

    def _setup_ui(self, player_index: int):
        self.setObjectName("bubble_frame")
        color = player_color(player_index)
        self.setStyleSheet(f"QFrame#bubble_frame {{ background-color: {color}22; "
                           f"border-left: 3px solid {color}; border-radius: 8px; "
                           f"margin: 2px 6px; padding: 4px 8px; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        # Player name + time
        header = QHBoxLayout()
        name_label = QLabel(self.segment.player_label or "未知")
        name_label.setProperty("class", "bubble_player")
        name_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11px;")
        time_str = f"{self.segment.start:.0f}s"
        time_label = QLabel(time_str)
        time_label.setStyleSheet("color: #6a7a8a; font-size: 10px;")
        header.addWidget(name_label)
        header.addStretch()
        header.addWidget(time_label)
        layout.addLayout(header)

        # Speech content
        text_label = QLabel(self.segment.text or "（转录中...）")
        text_label.setWordWrap(True)
        text_label.setStyleSheet("color: #f0e6cc; font-size: 13px;")
        layout.addWidget(text_label)

        # Analysis annotation (updated later)
        self._annotation_label = QLabel("")
        self._annotation_label.setWordWrap(True)
        self._annotation_label.setStyleSheet("color: #e08c4a; font-size: 11px;")
        self._annotation_label.hide()
        layout.addWidget(self._annotation_label)

    def set_annotation(self, text: str):
        if text:
            self._annotation_label.setText(f"⚠ {text}")
            self._annotation_label.show()
        else:
            self._annotation_label.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self._show_reassign_menu(event.globalPosition().toPoint())
        super().mousePressEvent(event)

    def _show_reassign_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background: #1a2a3a; color: #f0e6cc; border: 1px solid #f5c842; }"
                           "QMenu::item:selected { background: #2a3a4a; }")
        title = menu.addAction("重新归属给：")
        title.setEnabled(False)
        for i in range(1, self._max_players + 1):
            label = f"玩家{i}"
            action = menu.addAction(label)
            action.triggered.connect(lambda _, l=label: self.reassign_requested.emit(self.segment, l))
        menu.exec(pos)
