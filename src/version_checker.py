"""Pythonバージョンチェック機能"""

import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional

import requests
from packaging import version


@dataclass
class PythonVersion:
    """Pythonバージョン情報"""
    major: int
    minor: int
    patch: int

    @property
    def version_string(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __str__(self) -> str:
        return self.version_string

    def to_tuple(self) -> tuple[int, int, int]:
        return (self.major, self.minor, self.patch)


class VersionChecker:
    """Pythonバージョンをチェックするクラス"""

    # Python公式サイトのAPIエンドポイント
    PYTHON_API_URL = "https://www.python.org/api/v2/downloads/release/"
    PYTHON_DOWNLOADS_URL = "https://www.python.org/downloads/"

    def __init__(self) -> None:
        self._latest_version: Optional[PythonVersion] = None
        self._download_url: Optional[str] = None

    def get_installed_version(self) -> Optional[PythonVersion]:
        """
        現在インストールされているPythonのバージョンを取得

        Returns:
            インストールされているPythonのバージョン、なければNone
        """
        try:
            # 現在実行中のPythonバージョンを取得
            major, minor, patch = sys.version_info[:3]
            return PythonVersion(major=major, minor=minor, patch=patch)
        except Exception:
            return None

    def get_installed_versions_from_system(self) -> list[PythonVersion]:
        """
        システムにインストールされている全てのPythonバージョンを取得

        Returns:
            インストールされているPythonバージョンのリスト
        """
        versions: list[PythonVersion] = []

        # py launcherを使用してインストール済みバージョンを取得
        try:
            result = subprocess.run(
                ["py", "--list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # 出力からバージョンを抽出
                # 例: " -V:3.12 *        Python 3.12 (64-bit)"
                pattern = r"-V:(\d+)\.(\d+)"
                for match in re.finditer(pattern, result.stdout):
                    major, minor = int(match.group(1)), int(match.group(2))
                    # パッチバージョンを取得するために詳細情報を取得
                    try:
                        detail_result = subprocess.run(
                            ["py", f"-{major}.{minor}", "-c", "import sys; print(sys.version_info.micro)"],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        patch = int(detail_result.stdout.strip()) if detail_result.returncode == 0 else 0
                    except Exception:
                        patch = 0
                    versions.append(PythonVersion(major=major, minor=minor, patch=patch))
        except FileNotFoundError:
            # py launcherがない場合は現在のPythonのみ
            current = self.get_installed_version()
            if current:
                versions.append(current)
        except Exception:
            pass

        return versions

    def get_latest_version(self) -> Optional[PythonVersion]:
        """
        Python公式サイトから最新の安定版バージョンを取得

        Returns:
            最新のPythonバージョン、取得失敗時はNone
        """
        try:
            # Python.orgのダウンロードページをスクレイピング
            response = requests.get(self.PYTHON_DOWNLOADS_URL, timeout=30)
            response.raise_for_status()

            # 最新バージョンを抽出（例: "Download Python 3.12.1"）
            pattern = r'Download Python (\d+)\.(\d+)\.(\d+)'
            match = re.search(pattern, response.text)

            if match:
                self._latest_version = PythonVersion(
                    major=int(match.group(1)),
                    minor=int(match.group(2)),
                    patch=int(match.group(3))
                )
                return self._latest_version

            return None

        except requests.RequestException:
            return None

    def get_download_url(self, target_version: Optional[PythonVersion] = None) -> Optional[str]:
        """
        指定バージョンのWindowsインストーラーのダウンロードURLを取得

        Args:
            target_version: 取得するバージョン（省略時は最新版）

        Returns:
            ダウンロードURL、取得失敗時はNone
        """
        ver = target_version or self._latest_version
        if not ver:
            ver = self.get_latest_version()

        if not ver:
            return None

        # Windows用64bitインストーラーのURL
        # 例: https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe
        url = f"https://www.python.org/ftp/python/{ver.version_string}/python-{ver.version_string}-amd64.exe"

        # URLが有効か確認
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                self._download_url = url
                return url
        except requests.RequestException:
            pass

        return None

    def is_update_available(self, installed: PythonVersion, latest: PythonVersion) -> bool:
        """
        アップデートが利用可能か判定

        Args:
            installed: インストール済みバージョン
            latest: 最新バージョン

        Returns:
            アップデートが利用可能ならTrue
        """
        installed_ver = version.parse(installed.version_string)
        latest_ver = version.parse(latest.version_string)
        return latest_ver > installed_ver

    def check_for_updates(self) -> tuple[Optional[PythonVersion], Optional[PythonVersion], bool]:
        """
        アップデートをチェック

        Returns:
            (インストール済みバージョン, 最新バージョン, アップデート可能か)
        """
        installed = self.get_installed_version()
        latest = self.get_latest_version()

        if installed and latest:
            update_available = self.is_update_available(installed, latest)
            return (installed, latest, update_available)

        return (installed, latest, False)
