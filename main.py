# main.py
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont
from config import Config

def load_styles(app: QApplication):
    qss_path = Path(__file__).parent / "ui" / "styles.qss"
    if qss_path.exists():
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("鹅探长")

    # Try to load Nunito font if bundled
    font_path = Path(__file__).parent / "assets" / "fonts" / "Nunito-Regular.ttf"
    if font_path.exists():
        QFontDatabase.addApplicationFont(str(font_path))
    app.setFont(QFont("Nunito", 12))

    load_styles(app)

    config = Config(str(Path(__file__).parent / "config.json"))

    from ui.overlay import OverlayWindow
    window = OverlayWindow(config)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
