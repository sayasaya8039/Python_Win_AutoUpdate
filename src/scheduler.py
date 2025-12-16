"""スケジューラー機能"""

from datetime import datetime, time, timedelta
from typing import Callable, Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class UpdateScheduler(QObject):
    """定時アップデートをスケジュールするクラス"""

    # シグナル
    scheduled_check_triggered = pyqtSignal()  # 定時チェックがトリガーされた
    next_check_updated = pyqtSignal(str)  # 次回チェック時刻が更新された

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer_timeout)
        self._scheduled_time: Optional[time] = None
        self._enabled = False
        self._last_check_date: Optional[str] = None

        # 1分ごとに時刻をチェック
        self._check_timer = QTimer(self)
        self._check_timer.timeout.connect(self._check_scheduled_time)
        self._check_timer.setInterval(60 * 1000)  # 60秒

    @property
    def is_enabled(self) -> bool:
        """スケジューラーが有効かどうか"""
        return self._enabled

    @property
    def scheduled_time(self) -> Optional[time]:
        """設定されている定時時刻"""
        return self._scheduled_time

    @property
    def next_check_datetime(self) -> Optional[datetime]:
        """次回チェック日時を取得"""
        if not self._enabled or not self._scheduled_time:
            return None

        now = datetime.now()
        today_scheduled = datetime.combine(now.date(), self._scheduled_time)

        # 今日の定時がまだ来ていない、かつ今日チェックしていない場合
        if now < today_scheduled and self._last_check_date != now.strftime("%Y-%m-%d"):
            return today_scheduled

        # 明日の定時
        return today_scheduled + timedelta(days=1)

    def set_scheduled_time(self, time_str: str) -> None:
        """
        定時時刻を設定

        Args:
            time_str: HH:MM形式の時刻文字列
        """
        try:
            hour, minute = map(int, time_str.split(":"))
            self._scheduled_time = time(hour=hour, minute=minute)
            self._update_next_check_signal()
        except (ValueError, AttributeError):
            self._scheduled_time = time(hour=9, minute=0)

    def set_last_check_date(self, date_str: str) -> None:
        """最後のチェック日を設定"""
        self._last_check_date = date_str

    def start(self) -> None:
        """スケジューラーを開始"""
        self._enabled = True
        self._check_timer.start()
        self._update_next_check_signal()

    def stop(self) -> None:
        """スケジューラーを停止"""
        self._enabled = False
        self._check_timer.stop()
        self._timer.stop()

    def _check_scheduled_time(self) -> None:
        """定時時刻をチェック"""
        if not self._enabled or not self._scheduled_time:
            return

        now = datetime.now()
        current_time = now.time()
        today_str = now.strftime("%Y-%m-%d")

        # 今日既にチェック済みならスキップ
        if self._last_check_date == today_str:
            return

        # 定時時刻を過ぎたかチェック（1分の誤差許容）
        scheduled_minutes = self._scheduled_time.hour * 60 + self._scheduled_time.minute
        current_minutes = current_time.hour * 60 + current_time.minute

        if current_minutes >= scheduled_minutes and current_minutes < scheduled_minutes + 2:
            self._last_check_date = today_str
            self.scheduled_check_triggered.emit()
            self._update_next_check_signal()

    def _on_timer_timeout(self) -> None:
        """タイマータイムアウト時"""
        self.scheduled_check_triggered.emit()

    def _update_next_check_signal(self) -> None:
        """次回チェック時刻のシグナルを発行"""
        next_dt = self.next_check_datetime
        if next_dt:
            self.next_check_updated.emit(next_dt.strftime("%Y-%m-%d %H:%M"))
        else:
            self.next_check_updated.emit("")

    def trigger_now(self) -> None:
        """今すぐチェックをトリガー"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        self._last_check_date = today_str
        self.scheduled_check_triggered.emit()
        self._update_next_check_signal()
