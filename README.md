# AI-MAN: AI Multi-Agent Network

## 概要

AI-MAN (AI Multi-Agent Network) は、指定されたファイル群に対して、あらかじめ定義されたAIツールを非同期で実行し、その進捗状況を管理するためのWebアプリケーションです。

Streamlit製のUIを通じて、ユーザーは以下の操作を行うことができます。

- 実行したいAIツールと対象のファイルパスから「プロジェクト」を作成する。
- 作成したプロジェクトの実行を指示する。
- 実行中のプロジェクトのステータスをリアルタイムで確認する。

バックグラウンドでは、各プロジェクトが独立したプロセスとして実行されるため、複数のタスクを並行して処理することが可能です。

## 技術スタック

- **言語**: Python 3.12
- **パッケージ管理**: uv
- **Webフレームワーク**: Streamlit
- **タスクランナー**: just
- **テスト**: pytest, pytest-cov
- **静的解析・フォーマット**: ruff
- **その他**: Pydantic (データ検証)

## 開発環境のセットアップ

1. **リポジトリのクローン**:

    ```bash
    git clone <repository_url>
    cd aiman
    ```

2. **direnvの設定**:
    このプロジェクトでは、`direnv` を使って環境変数を管理します。`.envrc.template` をコピーして `.envrc` を作成してください。

    ```bash
    cp .envrc.template .envrc
    ```

    `.envrc` を開き、`GEMINI_API_KEY`にご自身のAPIキーを設定してください。

    `.envrc` ファイルがシェルのカレントディレクトリにある場合、`direnv` はその内容をロードします。
    初めてロードする際には、`direnv allow` を実行して内容の実行を許可する必要があります。

    ```bash
    direnv allow
    ```

    これにより、`uv`による仮想環境のセットアップと、プロジェクトの編集可能モードでのインストールが自動的に実行されます。

## 実行方法

各種コマンドは `just` を使って実行します。

- **アプリケーションの起動**:

  ```bash
  just run
  ```

  `http://localhost:8501` にアクセスしてください。

- **テストの実行**:

  ```bash
  just test
  ```

- **テストカバレッジの計測**:

  ```bash
  just coverage
  ```

- **LinterとFormatterの実行**:

  ```bash
  just lint
  just format
  ```
