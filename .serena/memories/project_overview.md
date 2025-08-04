# AI-MAN プロジェクト概要

## プロジェクトの目的
AI-MAN (AI Multi-Agent Network) は、指定されたファイル群に対して、あらかじめ定義されたAIツールを非同期で実行し、その進捗状況を管理するためのWebアプリケーションです。

Streamlit製のUIを通じて、ユーザーは以下の操作を行うことができます：
- 実行したいAIツールと対象のファイルパスから「プロジェクト」を作成する
- 作成したプロジェクトの実行を指示する
- 実行中のプロジェクトのステータスをリアルタイムで確認する

バックグラウンドでは、各プロジェクトが独立したプロセスとして実行されるため、複数のタスクを並行して処理することが可能です。

## 技術スタック
- **言語**: Python 3.12
- **パッケージ管理**: uv
- **Webフレームワーク**: Streamlit
- **タスクランナー**: just
- **テスト**: pytest, pytest-cov, pytest-playwright
- **静的解析・フォーマット**: ruff
- **型チェック**: mypy
- **その他**: Pydantic (データ検証), Playwright (E2Eテスト)

## アーキテクチャ
- **View Layer**: Streamlit UI
- **Service Layer**: ビジネスロジック (ProjectService, AIToolService)
- **Domain Layer**: ドメインモデルとリポジトリインターフェース
- **Infrastructure Layer**: 外部システム連携とデータ永続化

## プロジェクト構造
```
aiman/
├── app/                    # メインアプリケーション
│   ├── models/            # ドメインモデル
│   ├── repositories/      # データアクセス層
│   ├── services/          # ビジネスロジック
│   ├── ui/               # Streamlit UIコンポーネント
│   └── utils/            # ユーティリティ
├── tests/                 # ユニットテスト・インテグレーションテスト
├── tests_e2e/            # E2Eテスト
├── pages/                # Streamlitページ
└── docs/                 # ドキュメント
```