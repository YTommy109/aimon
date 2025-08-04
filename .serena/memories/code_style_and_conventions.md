# AI-MAN プロジェクトのコードスタイルと規約

## Python コーディング規約

### 基本設定
- **Python バージョン**: 3.12+
- **行長**: 100文字（ruff設定）
- **インデント**: スペース4個

### 型注釈
- 全ての関数・メソッドに型注釈を付ける
- `# type: ignore` コメントは禁止（TID252ルール）
- Pydanticを使用したデータ検証

### 命名規則
- **クラス名**: PascalCase（例: `ProjectService`）
- **関数・メソッド名**: snake_case（例: `create_project`）
- **変数名**: snake_case（例: `project_id`）
- **定数名**: UPPER_SNAKE_CASE（例: `DEFAULT_TIMEOUT`）

### ドキュメント
- Google スタイルの docstring を使用
- テストコードは docstring 不要
- 関数名で内容が自明な場合は冗長な docstring は書かない

### テスト規約
- **ユニットテスト**: AAA パターン（Arrange, Act, Assert）のコメントを使用
- **E2Eテスト**: Gherkin記法（Given, When, Then）のコメントを使用
- **テスト関数名**: 日本語で内容を明確に（例: `test_プロジェクトが存在しない場合にメッセージが表示される`）
- **セレクタ優先順位**: `get_by_role()` > `get_by_text()` > `get_by_label()` > `locator()`

### アーキテクチャパターン
- **レイヤー分離**: View → Service → Domain → Infrastructure
- **依存性注入**: リポジトリパターンを使用
- **非同期処理**: asyncio を使用した非同期処理
- **エラーハンドリング**: カスタム例外クラスを使用

### 静的解析ルール（ruff）
- **E**: pycodestyle エラー
- **F**: pyflakes（構文エラー、未使用import等）
- **W**: pycodestyle 警告
- **ANN**: flake8-annotations（型注釈チェック）
- **I**: isort（import文の並び順）
- **UP**: pyupgrade（Python新機能への更新推奨）
- **PT**: flake8-pytest-style
- **C90**: mccabe complexity（循環的複雑度）
- **C4**: flake8-comprehensions
- **TID**: flake8-tidy-imports（type: ignore禁止TID252も含む）
- **SIM**: flake8-simplify
- **RET**: flake8-return
- **ARG**: flake8-unused-arguments
- **PIE**: flake8-pie
- **PL**: pylint
- **RUF**: ruff-specific rules
- **B**: flake8-bugbear
- **A**: flake8-builtins
- **COM**: flake8-commas
- **ISC**: flake8-implicit-str-concat
- **T20**: flake8-print
- **N**: pep8-naming
- **S**: bandit（セキュリティ）
- **FBT**: flake8-boolean-trap
- **ERA**: eradicate（コメントアウトコード検出）
- **DTZ**: flake8-datetimez
- **PD**: pandas-vet
- **PLR**: pylint refactor
- **TID252**: type: ignore禁止

### ファイル構成
- **テストファイル**: `test_*.py`
- **テストディレクトリ**: `tests/`（ユニット・インテグレーション）、`tests_e2e/`（E2E）
- **アプリケーション**: `app/` ディレクトリ配下
- **設定ファイル**: `pyproject.toml`（プロジェクト設定）、`justfile`（タスク定義）