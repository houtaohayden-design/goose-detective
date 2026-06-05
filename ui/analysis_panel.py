# ui/analysis_panel.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QProgressBar,
                              QScrollArea, QFrame)
from PyQt6.QtCore import Qt, pyqtSlot
from ui.theme import SUSPICION_HIGH, SUSPICION_MED, SUSPICION_LOW, player_color

class PlayerSuspicionRow(QFrame):
    def __init__(self, result, color: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(2)

        header = QLabel(f"{result.player}  {result.suspicion_score}%")
        header.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: bold;")
        layout.addWidget(header)

        bar = QProgressBar()
        bar.setValue(result.suspicion_score)
        bar.setTextVisible(False)
        bar.setFixedHeight(8)
        chunk_color = (SUSPICION_HIGH if result.suspicion_score >= 70
                       else SUSPICION_MED if result.suspicion_score >= 40
                       else SUSPICION_LOW)
        bar.setStyleSheet(
            f"QProgressBar {{ background: #2a3a4a; border-radius: 4px; }}"
            f"QProgressBar::chunk {{ background: {chunk_color}; border-radius: 4px; }}"
        )
        layout.addWidget(bar)

        if result.summary:
            summary = QLabel(result.summary)
            summary.setWordWrap(True)
            summary.setStyleSheet("color: #8a9aaa; font-size: 11px;")
            layout.addWidget(summary)

        for c in result.contradictions:
            clabel = QLabel(f"⚠ {c}")
            clabel.setWordWrap(True)
            clabel.setStyleSheet("color: #e08c4a; font-size: 11px;")
            layout.addWidget(clabel)

        self.setStyleSheet(f"QFrame {{ border-left: 3px solid {color}; "
                           f"background: #0f1e2e; border-radius: 0 6px 6px 0; margin: 2px; }}")

class AnalysisPanel(QWidget):
    """Right-side suspicion analysis panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._player_color_map: dict = {}
        self._color_counter = 0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("🔍 嫌疑分析")
        header.setStyleSheet("color: #f5c842; font-size: 13px; font-weight: bold; padding: 6px;")
        layout.addWidget(header)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._container_layout.setSpacing(4)

        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll)

        self._placeholder = QLabel("会议结束后\n点击「分析」\n查看嫌疑排名")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet("color: #3a4a5a; font-size: 12px;")
        self._container_layout.addWidget(self._placeholder)

    def _color_for(self, player: str) -> str:
        if player not in self._player_color_map:
            self._player_color_map[player] = player_color(self._color_counter)
            self._color_counter += 1
        return self._player_color_map[player]

    @pyqtSlot(list)
    def update_results(self, results: list):
        """results: list[AnalysisResult], will be sorted by suspicion descending."""
        # Clear all existing rows
        while self._container_layout.count():
            item = self._container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        sorted_results = sorted(results, key=lambda r: r.suspicion_score, reverse=True)
        for result in sorted_results:
            color = self._color_for(result.player)
            row = PlayerSuspicionRow(result, color)
            self._container_layout.addWidget(row)

        self._container_layout.addStretch()
