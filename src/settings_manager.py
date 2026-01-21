"""設定管理クラス"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
import os


@dataclass
class AppSettings:
    """アプリケーション設定"""
    # 自動アップデート設定
    auto_update_enabled: bool = False
    scheduled_time: str = "09:00"  # HH:MM形式
    auto_install_enabled: bool = False  # 自動インストールのON/OFF
    include_prerelease: bool = False  # プレリリース版を表示

    # 一般設定
    minimize_to_tray: bool = True
    start_minimized: bool = False
    run_at_startup: bool = False

    # 最後のチェック日時
    last_check_date: str = ""


class SettingsManager:
    """設定を管理するクラス"""

    def __init__(self) -> None:
        # 設定ファイルのパス（ユーザーのAppDataに保存）
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            self._settings_dir = Path(appdata) / "PythonAutoUpdate"
        else:
            self._settings_dir = Path.home() / ".python_autoupdate"

        self._settings_dir.mkdir(parents=True, exist_ok=True)
        self._settings_file = self._settings_dir / "settings.json"
        self._settings: AppSettings = self._load_settings()

    @property
    def settings(self) -> AppSettings:
        """現在の設定を取得"""
        return self._settings

    @property
    def settings_dir(self) -> Path:
        """設定ディレクトリのパス"""
        return self._settings_dir

    def _load_settings(self) -> AppSettings:
        """設定ファイルから読み込み"""
        if self._settings_file.exists():
            try:
                with open(self._settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return AppSettings(**data)
            except (json.JSONDecodeError, TypeError, KeyError):
                # 設定ファイルが壊れている場合はデフォルト値を使用
                return AppSettings()
        return AppSettings()

    def save_settings(self) -> None:
        """設定をファイルに保存"""
        with open(self._settings_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self._settings), f, indent=2, ensure_ascii=False)

    def update_settings(self, **kwargs) -> None:
        """設定を更新して保存"""
        for key, value in kwargs.items():
            if hasattr(self._settings, key):
                setattr(self._settings, key, value)
        self.save_settings()

    def set_auto_update(self, enabled: bool) -> None:
        """自動アップデートの有効/無効を設定"""
        self._settings.auto_update_enabled = enabled
        self.save_settings()

    def set_scheduled_time(self, time_str: str) -> None:
        """定時時刻を設定（HH:MM形式）"""
        self._settings.scheduled_time = time_str
        self.save_settings()

    def set_auto_install(self, enabled: bool) -> None:
        """自動インストールの有効/無効を設定"""
        self._settings.auto_install_enabled = enabled
        self.save_settings()

    def set_include_prerelease(self, enabled: bool) -> None:
        """プレリリース版の表示設定"""
        self._settings.include_prerelease = enabled
        self.save_settings()

    def set_last_check_date(self, date_str: str) -> None:
        """最後のチェック日時を記録"""
        self._settings.last_check_date = date_str
        self.save_settings()

    def setup_startup(self, enable: bool) -> bool:
        """
        Windows起動時に自動起動する設定

        Args:
            enable: 有効にするかどうか

        Returns:
            設定成功ならTrue
        """
        try:
            import winreg

            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "PythonAutoUpdate"

            # 実行ファイルのパスを取得
            import sys
            if getattr(sys, 'frozen', False):
                # PyInstallerでビルドされた場合
                exe_path = sys.executable
            else:
                # 開発環境
                exe_path = f'"{sys.executable}" "{Path(__file__).parent.parent / "run.py"}"'

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
            )

            if enable:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass  # 既に削除されている

            winreg.CloseKey(key)
            self._settings.run_at_startup = enable
            self.save_settings()
            return True

        except Exception:
            return False
