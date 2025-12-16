"""Pythonインストーラーダウンロード機能"""

import hashlib
import os
import tempfile
from pathlib import Path
from typing import Callable, Optional

import requests

try:
    from .version_checker import PythonVersion
except ImportError:
    from version_checker import PythonVersion


class DownloadError(Exception):
    """ダウンロードエラー"""
    pass


class Downloader:
    """Pythonインストーラーをダウンロードするクラス"""

    # チャンクサイズ（1MB）
    CHUNK_SIZE = 1024 * 1024

    def __init__(self) -> None:
        self._download_path: Optional[Path] = None
        self._is_cancelled = False

    @property
    def download_path(self) -> Optional[Path]:
        """ダウンロードしたファイルのパス"""
        return self._download_path

    def cancel(self) -> None:
        """ダウンロードをキャンセル"""
        self._is_cancelled = True

    def download(
        self,
        url: str,
        version: PythonVersion,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        save_dir: Optional[Path] = None
    ) -> Path:
        """
        Pythonインストーラーをダウンロード

        Args:
            url: ダウンロードURL
            version: ダウンロードするPythonバージョン
            progress_callback: 進捗コールバック (downloaded_bytes, total_bytes)
            save_dir: 保存先ディレクトリ（省略時はtempディレクトリ）

        Returns:
            ダウンロードしたファイルのパス

        Raises:
            DownloadError: ダウンロード失敗時
        """
        self._is_cancelled = False

        # 保存先ディレクトリを設定
        if save_dir is None:
            save_dir = Path(tempfile.gettempdir())
        else:
            save_dir.mkdir(parents=True, exist_ok=True)

        filename = f"python-{version.version_string}-amd64.exe"
        filepath = save_dir / filename

        try:
            # ストリーミングダウンロード
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            # 合計サイズを取得
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                    if self._is_cancelled:
                        # キャンセルされた場合、途中ファイルを削除
                        f.close()
                        if filepath.exists():
                            filepath.unlink()
                        raise DownloadError("ダウンロードがキャンセルされました")

                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        if progress_callback:
                            progress_callback(downloaded_size, total_size)

            self._download_path = filepath
            return filepath

        except requests.RequestException as e:
            raise DownloadError(f"ダウンロードに失敗しました: {e}") from e

    def verify_download(self, filepath: Path, expected_hash: Optional[str] = None) -> bool:
        """
        ダウンロードしたファイルを検証

        Args:
            filepath: 検証するファイルのパス
            expected_hash: 期待されるSHA256ハッシュ（省略時はサイズのみ確認）

        Returns:
            検証成功ならTrue
        """
        if not filepath.exists():
            return False

        # ファイルサイズが0より大きいことを確認
        if filepath.stat().st_size == 0:
            return False

        # ハッシュが指定されている場合は検証
        if expected_hash:
            sha256 = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest().lower() == expected_hash.lower()

        return True

    def cleanup(self) -> None:
        """ダウンロードしたファイルを削除"""
        if self._download_path and self._download_path.exists():
            try:
                self._download_path.unlink()
            except OSError:
                pass
            self._download_path = None
