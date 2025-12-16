"""Pythonインストール機能"""

import ctypes
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional


class InstallError(Exception):
    """インストールエラー"""
    pass


class Installer:
    """Pythonをインストールするクラス"""

    def __init__(self) -> None:
        self._process: Optional[subprocess.Popen] = None

    @staticmethod
    def is_admin() -> bool:
        """管理者権限で実行されているか確認"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    @staticmethod
    def request_admin_elevation() -> bool:
        """
        管理者権限での再起動を要求

        Returns:
            再起動が成功したらTrue（この関数は戻らない場合あり）
        """
        if Installer.is_admin():
            return True

        try:
            # 現在のスクリプトを管理者権限で再実行
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                " ".join(sys.argv),
                None,
                1  # SW_SHOWNORMAL
            )
            return True
        except Exception:
            return False

    def install(
        self,
        installer_path: Path,
        silent: bool = False,
        add_to_path: bool = True,
        install_for_all_users: bool = False,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        Pythonインストーラーを実行

        Args:
            installer_path: インストーラーファイルのパス
            silent: サイレントインストール（UIなし）
            add_to_path: PATHに追加する
            install_for_all_users: 全ユーザー向けにインストール
            progress_callback: 進捗メッセージのコールバック

        Returns:
            インストール成功ならTrue

        Raises:
            InstallError: インストール失敗時
        """
        if not installer_path.exists():
            raise InstallError(f"インストーラーが見つかりません: {installer_path}")

        # インストールオプションを構築
        args = [str(installer_path)]

        if silent:
            args.append("/quiet")
        else:
            args.append("/passive")  # プログレスバーのみ表示

        # PATHに追加
        if add_to_path:
            args.append("PrependPath=1")

        # 全ユーザー向けインストール（管理者権限が必要）
        if install_for_all_users:
            if not self.is_admin():
                raise InstallError("全ユーザー向けインストールには管理者権限が必要です")
            args.append("InstallAllUsers=1")
        else:
            args.append("InstallAllUsers=0")

        # その他のオプション
        args.extend([
            "Include_test=0",  # テストスイートは不要
            "Include_doc=0",   # ドキュメントは不要
            "Include_launcher=1",  # py launcherをインストール
            "InstallLauncherAllUsers=1",
        ])

        if progress_callback:
            progress_callback("インストーラーを起動しています...")

        try:
            # インストーラーを実行
            self._process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if silent else 0
            )

            if progress_callback:
                progress_callback("インストール中...")

            # 完了を待機
            stdout, stderr = self._process.communicate()

            if self._process.returncode == 0:
                if progress_callback:
                    progress_callback("インストールが完了しました")
                return True
            else:
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "不明なエラー"
                raise InstallError(f"インストールに失敗しました (code: {self._process.returncode}): {error_msg}")

        except subprocess.SubprocessError as e:
            raise InstallError(f"インストーラーの実行に失敗しました: {e}") from e

    def cancel(self) -> None:
        """インストールをキャンセル"""
        if self._process:
            try:
                self._process.terminate()
            except Exception:
                pass

    @staticmethod
    def run_installer_elevated(installer_path: Path) -> bool:
        """
        管理者権限でインストーラーを実行

        Args:
            installer_path: インストーラーファイルのパス

        Returns:
            実行が開始されたらTrue
        """
        try:
            # ShellExecuteを使用して管理者権限で実行
            result = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                str(installer_path),
                "/passive PrependPath=1 Include_launcher=1",
                None,
                1  # SW_SHOWNORMAL
            )
            # 32より大きい値は成功
            return result > 32
        except Exception:
            return False
