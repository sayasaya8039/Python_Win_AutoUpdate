"""Python AutoUpdate - メインエントリーポイント"""

import sys

from PyQt6.QtWidgets import QApplication

from gui import MainWindow


def main() -> int:
    """アプリケーションのエントリーポイント"""
    app = QApplication(sys.argv)
    app.setApplicationName("Python AutoUpdate")
    app.setApplicationVersion("1.0.0")

    # ハイDPIサポート
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
