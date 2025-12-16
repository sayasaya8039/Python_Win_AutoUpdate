"""起動スクリプト"""

import sys
from pathlib import Path

# srcディレクトリをパスに追加
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# バージョン情報
__version__ = "1.0.0"

from PyQt6.QtWidgets import QApplication
from version_checker import VersionChecker, PythonVersion
from downloader import Downloader, DownloadError
from installer import Installer, InstallError


def main() -> int:
    """アプリケーションのエントリーポイント"""
    # GUI のインポートは実行時に
    from gui.main_window_standalone import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("Python AutoUpdate")
    app.setApplicationVersion(__version__)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
