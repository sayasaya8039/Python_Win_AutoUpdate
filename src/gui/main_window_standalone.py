"""メインウィンドウ（スタンドアロン実行用）"""

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# スタンドアロン実行用のインポート
from version_checker import VersionChecker, PythonVersion
from downloader import Downloader, DownloadError
from installer import Installer, InstallError

__version__ = "1.0.0"


class CheckVersionThread(QThread):
    """バージョンチェック用スレッド"""
    finished = pyqtSignal(object, object, bool)
    error = pyqtSignal(str)

    def __init__(self, checker: VersionChecker) -> None:
        super().__init__()
        self.checker = checker

    def run(self) -> None:
        try:
            installed, latest, update_available = self.checker.check_for_updates()
            self.finished.emit(installed, latest, update_available)
        except Exception as e:
            self.error.emit(str(e))


class DownloadThread(QThread):
    """ダウンロード用スレッド"""
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, downloader: Downloader, url: str, version: PythonVersion) -> None:
        super().__init__()
        self.downloader = downloader
        self.url = url
        self.version = version

    def run(self) -> None:
        try:
            filepath = self.downloader.download(
                self.url,
                self.version,
                progress_callback=self._on_progress
            )
            self.finished.emit(str(filepath))
        except DownloadError as e:
            self.error.emit(str(e))

    def _on_progress(self, downloaded: int, total: int) -> None:
        self.progress.emit(downloaded, total)


class MainWindow(QMainWindow):
    """メインウィンドウ"""

    def __init__(self) -> None:
        super().__init__()
        self.checker = VersionChecker()
        self.downloader = Downloader()
        self.installer = Installer()

        self._installed_version: Optional[PythonVersion] = None
        self._latest_version: Optional[PythonVersion] = None
        self._download_url: Optional[str] = None
        self._check_thread: Optional[CheckVersionThread] = None
        self._download_thread: Optional[DownloadThread] = None

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self) -> None:
        """UIをセットアップ"""
        self.setWindowTitle(f"Python AutoUpdate v{__version__}")
        self.setFixedSize(500, 400)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )

        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # タイトル
        title_label = QLabel("Python AutoUpdate")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # バージョン情報エリア
        version_widget = QWidget()
        version_widget.setObjectName("versionWidget")
        version_layout = QVBoxLayout(version_widget)
        version_layout.setContentsMargins(20, 20, 20, 20)
        version_layout.setSpacing(15)

        # インストール済みバージョン
        installed_layout = QHBoxLayout()
        installed_title = QLabel("インストール済み:")
        installed_title.setObjectName("versionTitle")
        self.installed_label = QLabel("確認中...")
        self.installed_label.setObjectName("versionValue")
        installed_layout.addWidget(installed_title)
        installed_layout.addStretch()
        installed_layout.addWidget(self.installed_label)
        version_layout.addLayout(installed_layout)

        # 最新バージョン
        latest_layout = QHBoxLayout()
        latest_title = QLabel("最新バージョン:")
        latest_title.setObjectName("versionTitle")
        self.latest_label = QLabel("確認中...")
        self.latest_label.setObjectName("versionValue")
        latest_layout.addWidget(latest_title)
        latest_layout.addStretch()
        latest_layout.addWidget(self.latest_label)
        version_layout.addLayout(latest_layout)

        layout.addWidget(version_widget)

        # ステータス表示
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)

        # ボタンエリア
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.check_button = QPushButton("更新を確認")
        self.check_button.setObjectName("primaryButton")
        self.check_button.clicked.connect(self._check_for_updates)
        button_layout.addWidget(self.check_button)

        self.update_button = QPushButton("アップデート")
        self.update_button.setObjectName("successButton")
        self.update_button.setEnabled(False)
        self.update_button.clicked.connect(self._start_update)
        button_layout.addWidget(self.update_button)

        layout.addLayout(button_layout)
        layout.addStretch()

        # フッター（バージョン表示）
        footer_label = QLabel(f"v{__version__}")
        footer_label.setObjectName("footerLabel")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(footer_label)

    def _apply_styles(self) -> None:
        """スタイルを適用"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0F172A;
            }
            QWidget {
                background-color: transparent;
                color: #E0F2FE;
                font-family: "Segoe UI", "Yu Gothic UI", sans-serif;
            }
            #titleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #7DD3FC;
                padding: 10px;
            }
            #versionWidget {
                background-color: #1E293B;
                border-radius: 12px;
            }
            #versionTitle {
                font-size: 14px;
                color: #94A3B8;
            }
            #versionValue {
                font-size: 16px;
                font-weight: bold;
                color: #E0F2FE;
            }
            #statusLabel {
                font-size: 14px;
                color: #94A3B8;
                min-height: 40px;
            }
            #progressBar {
                background-color: #1E293B;
                border: none;
                border-radius: 8px;
                height: 20px;
                text-align: center;
            }
            #progressBar::chunk {
                background-color: #38BDF8;
                border-radius: 8px;
            }
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
            }
            #primaryButton {
                background-color: #38BDF8;
                color: #0F172A;
            }
            #primaryButton:hover {
                background-color: #7DD3FC;
            }
            #primaryButton:disabled {
                background-color: #475569;
                color: #94A3B8;
            }
            #successButton {
                background-color: #34D399;
                color: #0F172A;
            }
            #successButton:hover {
                background-color: #A7F3D0;
            }
            #successButton:disabled {
                background-color: #475569;
                color: #94A3B8;
            }
            #footerLabel {
                font-size: 11px;
                color: #64748B;
            }
            QMessageBox {
                background-color: #1E293B;
            }
            QMessageBox QLabel {
                color: #E0F2FE;
            }
            QMessageBox QPushButton {
                background-color: #38BDF8;
                color: #0F172A;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
            }
        """)

    def showEvent(self, event) -> None:
        """ウィンドウ表示時に自動でバージョンチェック"""
        super().showEvent(event)
        self._check_for_updates()

    def _check_for_updates(self) -> None:
        """バージョンチェックを開始"""
        self.check_button.setEnabled(False)
        self.update_button.setEnabled(False)
        self.status_label.setText("バージョンを確認しています...")
        self.installed_label.setText("確認中...")
        self.latest_label.setText("確認中...")

        self._check_thread = CheckVersionThread(self.checker)
        self._check_thread.finished.connect(self._on_check_finished)
        self._check_thread.error.connect(self._on_check_error)
        self._check_thread.start()

    def _on_check_finished(
        self,
        installed: Optional[PythonVersion],
        latest: Optional[PythonVersion],
        update_available: bool
    ) -> None:
        """バージョンチェック完了時"""
        self.check_button.setEnabled(True)
        self._installed_version = installed
        self._latest_version = latest

        if installed:
            self.installed_label.setText(f"Python {installed.version_string}")
        else:
            self.installed_label.setText("インストールされていません")

        if latest:
            self.latest_label.setText(f"Python {latest.version_string}")
            self._download_url = self.checker.get_download_url(latest)
        else:
            self.latest_label.setText("取得失敗")

        if update_available and self._download_url:
            self.status_label.setText("新しいバージョンが利用可能です！")
            self.status_label.setStyleSheet("color: #34D399;")
            self.update_button.setEnabled(True)
        elif installed and latest:
            self.status_label.setText("最新バージョンを使用しています")
            self.status_label.setStyleSheet("color: #94A3B8;")
        else:
            self.status_label.setText("バージョン情報を取得できませんでした")
            self.status_label.setStyleSheet("color: #F87171;")

    def _on_check_error(self, error: str) -> None:
        """バージョンチェックエラー時"""
        self.check_button.setEnabled(True)
        self.status_label.setText(f"エラー: {error}")
        self.status_label.setStyleSheet("color: #F87171;")
        self.installed_label.setText("不明")
        self.latest_label.setText("取得失敗")

    def _start_update(self) -> None:
        """アップデートを開始"""
        if not self._latest_version or not self._download_url:
            return

        reply = QMessageBox.question(
            self,
            "確認",
            f"Python {self._latest_version.version_string} をダウンロードしてインストールしますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self._start_download()

    def _start_download(self) -> None:
        """ダウンロードを開始"""
        self.check_button.setEnabled(False)
        self.update_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("ダウンロード中...")
        self.status_label.setStyleSheet("color: #94A3B8;")

        self._download_thread = DownloadThread(
            self.downloader,
            self._download_url,
            self._latest_version
        )
        self._download_thread.progress.connect(self._on_download_progress)
        self._download_thread.finished.connect(self._on_download_finished)
        self._download_thread.error.connect(self._on_download_error)
        self._download_thread.start()

    def _on_download_progress(self, downloaded: int, total: int) -> None:
        """ダウンロード進捗更新"""
        if total > 0:
            percent = int((downloaded / total) * 100)
            self.progress_bar.setValue(percent)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total / (1024 * 1024)
            self.status_label.setText(f"ダウンロード中... {mb_downloaded:.1f} / {mb_total:.1f} MB")

    def _on_download_finished(self, filepath: str) -> None:
        """ダウンロード完了時"""
        self.progress_bar.setValue(100)
        self.status_label.setText("ダウンロード完了。インストーラーを起動します...")

        installer_path = Path(filepath)

        try:
            if self.installer.run_installer_elevated(installer_path):
                self.status_label.setText("インストーラーが起動しました")
                self.status_label.setStyleSheet("color: #34D399;")

                QMessageBox.information(
                    self,
                    "インストール",
                    "Pythonインストーラーが起動しました。\n"
                    "インストール完了後、このツールを再起動して確認してください。"
                )
            else:
                self.status_label.setText("インストーラーの起動に失敗しました")
                self.status_label.setStyleSheet("color: #F87171;")
        except Exception as e:
            self.status_label.setText(f"エラー: {e}")
            self.status_label.setStyleSheet("color: #F87171;")

        self.check_button.setEnabled(True)
        self.progress_bar.setVisible(False)

    def _on_download_error(self, error: str) -> None:
        """ダウンロードエラー時"""
        self.check_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"ダウンロードエラー: {error}")
        self.status_label.setStyleSheet("color: #F87171;")

    def closeEvent(self, event) -> None:
        """ウィンドウを閉じる時"""
        if self._check_thread and self._check_thread.isRunning():
            self._check_thread.quit()
            self._check_thread.wait()

        if self._download_thread and self._download_thread.isRunning():
            self.downloader.cancel()
            self._download_thread.quit()
            self._download_thread.wait()

        super().closeEvent(event)
