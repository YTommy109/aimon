# AI-MAN プロジェクトで使用する主要コマンド

## 開発環境セットアップ
```bash
# 依存関係の同期
uv sync --extra dev

# 仮想環境の作成
just venv
```

## アプリケーション実行
```bash
# 開発環境で実行
just run

# テスト環境で実行
just run test
```

## テスト実行
```bash
# 影響範囲のテストのみ実行（推奨）
just test

# ユニットテストのみ
just test ut

# CIテストのみ
just test ci

# 全テスト実行
just test all

# カバレッジ計測
just coverage
```

## E2Eテスト実行
```bash
# 全E2Eテスト
just test-e2e

# ヘッドレスモード無効（ブラウザ表示）
just test-e2e headed

# デバッグモード
just test-e2e debug
```

## コード品質管理
```bash
# フォーマットとリント
just lint

# フォーマットのみ
just ruff

# 特定ファイルのフォーマット
just ruff path/to/file.py

# 未使用コード検出
just vulture

# 型チェック
just ty

# 全チェック実行
just test-all

# 厳密な全チェック（E2Eテスト含む）
just test-all strict
```

## ドキュメント生成
```bash
# HTMLドキュメント生成
just docs
```

## Markdownファイルのフォーマット
```bash
# 全Markdownファイル
just mdlint

# 特定ファイル
just mdlint path/to/file.md
```

## ファイル監視（開発用）
```bash
# ファイル変更時にテスト実行
just watch
```

## システムコマンド
```bash
# プロジェクト状態確認
jj status --no-pager

# ファイル検索
find . -name "*.py" -type f

# テキスト検索
grep -r "pattern" .

# ディレクトリ構造確認
ls -la
tree .  # または find . -type d
```