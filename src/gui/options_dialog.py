"""オプション設定ダイアログ"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import QTime

try:
    from ..settings_manager import AppSettings, SettingsManager
except ImportError:
    from settings_manager import AppSettings, SettingsManager


class OptionsDialog(QDialog):
    """オプション設定ダイアログ"""

    settings_changed = pyqtSignal()  # 設定が変更された

    def __init__(self, settings_manager: SettingsManager, parent=None) -> None:
        super().__init__(parent)
        self.settings_manager = settings_manager
        self._setup_ui()
        self._apply_styles()
        self._load_current_settings()

    def _setup_ui(self) -> None:
        """UIをセットアップ"""
        self.setWindowTitle("オプション設定")
        self.setFixedSize(450, 480)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowCloseButtonHint
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 自動アップデート設定グループ
        auto_update_group = QGroupBox("自動アップデート設定")
        auto_update_group.setObjectName("settingsGroup")
        auto_layout = QVBoxLayout(auto_update_group)
        auto_layout.setSpacing(15)

        # 自動チェック有効化
        self.auto_check_checkbox = QCheckBox("定時に自動でバージョンチェックする")
        self.auto_check_checkbox.setObjectName("settingsCheckbox")
        self.auto_check_checkbox.stateChanged.connect(self._on_auto_check_changed)
        auto_layout.addWidget(self.auto_check_checkbox)

        # 定時時刻設定
        time_layout = QHBoxLayout()
        time_label = QLabel("チェック時刻:")
        time_label.setObjectName("settingsLabel")
        self.time_edit = QTimeEdit()
        self.time_edit.setObjectName("timeEdit")
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setEnabled(False)
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)
        time_layout.addStretch()
        auto_layout.addLayout(time_layout)

        # 自動インストール有効化
        self.auto_install_checkbox = QCheckBox("新しいバージョンを自動でインストールする")
        self.auto_install_checkbox.setObjectName("settingsCheckbox")
        self.auto_install_checkbox.setEnabled(False)
        auto_layout.addWidget(self.auto_install_checkbox)

        # 注意書き
        warning_label = QLabel("※ 自動インストールは管理者権限が必要です")
        warning_label.setObjectName("warningLabel")
        auto_layout.addWidget(warning_label)

        layout.addWidget(auto_update_group)

        # 一般設定グループ
        general_group = QGroupBox("一般設定")
        general_group.setObjectName("settingsGroup")
        general_layout = QVBoxLayout(general_group)
        general_layout.setSpacing(15)

        # トレイに最小化
        self.minimize_to_tray_checkbox = QCheckBox("閉じるボタンでトレイに最小化")
        self.minimize_to_tray_checkbox.setObjectName("settingsCheckbox")
        general_layout.addWidget(self.minimize_to_tray_checkbox)

        # 最小化状態で起動
        self.start_minimized_checkbox = QCheckBox("最小化状態で起動")
        self.start_minimized_checkbox.setObjectName("settingsCheckbox")
        general_layout.addWidget(self.start_minimized_checkbox)

        # Windows起動時に自動起動
        self.run_at_startup_checkbox = QCheckBox("Windows起動時に自動起動")
        self.run_at_startup_checkbox.setObjectName("settingsCheckbox")
        general_layout.addWidget(self.run_at_startup_checkbox)

        layout.addWidget(general_group)

        layout.addStretch()

        # ボタンエリア
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.setObjectName("secondaryButton")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("保存")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self._save_settings)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def _apply_styles(self) -> None:
        """スタイルを適用"""
        self.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
            }
            QWidget {
                color: #E0F2FE;
                font-family: "Segoe UI", "Yu Gothic UI", sans-serif;
            }
            #settingsGroup {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
            #settingsGroup::title {
                color: #7DD3FC;
                font-weight: bold;
                padding: 0 8px;
            }
            #settingsCheckbox {
                font-size: 13px;
                spacing: 8px;
                min-height: 28px;
                padding: 4px 0px;
            }
            #settingsCheckbox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #475569;
                background-color: #1E293B;
            }
            #settingsCheckbox::indicator:checked {
                background-color: #38BDF8;
                border-color: #38BDF8;
            }
            #settingsCheckbox::indicator:hover {
                border-color: #7DD3FC;
            }
            #settingsLabel {
                font-size: 13px;
                color: #94A3B8;
                min-height: 24px;
            }
            #warningLabel {
                font-size: 11px;
                color: #FBBF24;
                margin-top: 5px;
                min-height: 20px;
            }
            #timeEdit {
                background-color: #1E293B;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 14px;
                color: #E0F2FE;
                min-width: 100px;
                min-height: 28px;
            }
            #timeEdit:disabled {
                color: #64748B;
                background-color: #0F172A;
            }
            QPushButton {
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                border: none;
                min-width: 100px;
            }
            #primaryButton {
                background-color: #38BDF8;
                color: #0F172A;
            }
            #primaryButton:hover {
                background-color: #7DD3FC;
            }
            #secondaryButton {
                background-color: #475569;
                color: #E0F2FE;
            }
            #secondaryButton:hover {
                background-color: #64748B;
            }
        """)

    def _load_current_settings(self) -> None:
        """現在の設定を読み込んでUIに反映"""
        settings = self.settings_manager.settings

        self.auto_check_checkbox.setChecked(settings.auto_update_enabled)
        self.time_edit.setEnabled(settings.auto_update_enabled)
        self.auto_install_checkbox.setEnabled(settings.auto_update_enabled)

        # 時刻を設定
        try:
            hour, minute = map(int, settings.scheduled_time.split(":"))
            self.time_edit.setTime(QTime(hour, minute))
        except (ValueError, AttributeError):
            self.time_edit.setTime(QTime(9, 0))

        self.auto_install_checkbox.setChecked(settings.auto_install_enabled)
        self.minimize_to_tray_checkbox.setChecked(settings.minimize_to_tray)
        self.start_minimized_checkbox.setChecked(settings.start_minimized)
        self.run_at_startup_checkbox.setChecked(settings.run_at_startup)

    def _on_auto_check_changed(self, state: int) -> None:
        """自動チェックのチェック状態が変わった時"""
        enabled = state == Qt.CheckState.Checked.value
        self.time_edit.setEnabled(enabled)
        self.auto_install_checkbox.setEnabled(enabled)
        if not enabled:
            self.auto_install_checkbox.setChecked(False)

    def _save_settings(self) -> None:
        """設定を保存"""
        time_str = self.time_edit.time().toString("HH:mm")

        self.settings_manager.update_settings(
            auto_update_enabled=self.auto_check_checkbox.isChecked(),
            scheduled_time=time_str,
            auto_install_enabled=self.auto_install_checkbox.isChecked(),
            minimize_to_tray=self.minimize_to_tray_checkbox.isChecked(),
            start_minimized=self.start_minimized_checkbox.isChecked(),
        )

        # Windows起動時の自動起動設定
        if self.run_at_startup_checkbox.isChecked() != self.settings_manager.settings.run_at_startup:
            self.settings_manager.setup_startup(self.run_at_startup_checkbox.isChecked())

        self.settings_changed.emit()
        self.accept()
