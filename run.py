"""起動スクリプト"""

import ctypes
import sys
from pathlib import Path

# srcディレクトリをパスに追加
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# バージョン情報
__version__ = "1.1.0"

from PyQt6.QtWidgets import QApplication, QMessageBox

# 多重起動防止用のミューテックス名
MUTEX_NAME = "PythonAutoUpdate_SingleInstance_Mutex"


def check_single_instance() -> bool:
    """
    多重起動をチェック

    Returns:
        初回起動ならTrue、既に起動中ならFalse
    """
    # Windows APIでミューテックスを作成
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, True, MUTEX_NAME)
    last_error = kernel32.GetLastError()

    # ERROR_ALREADY_EXISTS = 183
    if last_error == 183:
        kernel32.CloseHandle(mutex)
        return False

    # ミューテックスのハンドルをグローバルに保持（プロセス終了まで維持）
    global _mutex_handle
    _mutex_handle = mutex
    return True


def main() -> int:
    """アプリケーションのエントリーポイント"""
    # 多重起動チェック
    if not check_single_instance():
        # 既に起動中の場合はメッセージを表示して終了
        app = QApplication(sys.argv)
        QMessageBox.warning(
            None,
            "Python AutoUpdate",
            "アプリケーションは既に起動しています。\n"
            "システムトレイを確認してください。"
        )
        return 1

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
