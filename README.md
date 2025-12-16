# Python AutoUpdate

Windows用Python自動アップデートツール

## 機能

- インストール済みPythonバージョンの検出
- Python公式サイトから最新バージョン情報を取得
- 新しいバージョンが利用可能な場合に通知
- ワンクリックでダウンロード・インストール
- **定時自動チェック機能** - 毎日指定時刻に自動でバージョンチェック
- **自動インストール機能** - 新バージョンを自動でダウンロード・インストール
- **システムトレイ常駐** - バックグラウンドで動作

## 使い方

1. `Python_AutoUpdate.exe` を起動
2. 自動的にバージョンチェックが実行されます
3. 新しいバージョンがある場合、「アップデート」ボタンが有効になります
4. 「アップデート」をクリックしてインストール

### オプション設定

「オプション設定」ボタンから以下の設定が可能:

- **定時チェック**: 毎日指定時刻に自動でバージョンチェック
- **自動インストール**: 新バージョン検出時に自動でインストール
- **トレイ最小化**: 閉じるボタンでトレイに最小化
- **最小化起動**: 起動時にトレイに最小化
- **自動起動**: Windows起動時に自動起動

## 技術仕様

- **言語**: Python 3.10+
- **GUI**: PyQt6
- **ビルド**: PyInstaller

## 開発環境でのセットアップ

```bash
# 依存関係のインストール
pip install -r requirements.txt

# 実行
python run.py

# ビルド
pyinstaller --onefile --noconsole --name Python_AutoUpdate --distpath "./Python_AutoUpdate" --paths "src" run.py
```

## プロジェクト構造

```
Python_Win_AutoUpdate/
├── src/
│   ├── __init__.py              # バージョン情報
│   ├── version_checker.py       # バージョンチェック機能
│   ├── downloader.py            # ダウンロード機能
│   ├── installer.py             # インストール機能
│   ├── settings_manager.py      # 設定管理
│   ├── scheduler.py             # スケジューラー
│   └── gui/
│       ├── main_window_standalone.py  # メインウィンドウ
│       └── options_dialog.py          # オプション設定画面
├── run.py                       # エントリーポイント
├── requirements.txt             # 依存関係
├── pyproject.toml              # プロジェクト設定
└── Python_AutoUpdate/          # ビルド出力
    └── Python_AutoUpdate.exe
```

## ライセンス

MIT License

## バージョン

v1.1.0
