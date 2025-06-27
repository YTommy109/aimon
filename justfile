[private]
@default: help

# 変数定義
TEST_PORT := "8502"
BASE_URL := "http://localhost:" + TEST_PORT

# show help message
@help:
    echo "Usage: just <recipe>"
    echo ""
    just --list

# アプリケーションの実行
# just run      -> 開発環境で実行（デフォルトポート）
# just run test -> テスト環境で実行（ポート{{TEST_PORT}}）
start env='':
    #!/usr/bin/env zsh
    set -euo pipefail
    
    case '{{env}}' in
        '')
            echo "Running in development mode..."
            streamlit run app.py
            ;;
        'test')
            echo "Running in test mode (port {{TEST_PORT}})..."
            streamlit run app.py --server.port {{TEST_PORT}} -- --app-env test
            ;;
        *)
            echo "Unknown run environment: '{{env}}'. Available: 'test'"
            exit 1
            ;;
    esac

# 統合テストランナー
# just test     -> pytest (ユニットテストとCIテスト)
# just test ut  -> ユニットテスト
# just test ci  -> CIテスト
# just test e2e -> E2Eテスト
test suite='':
    #!/usr/bin/env zsh
    set -euo pipefail

    case '{{suite}}' in
        '')
            echo "Running unit and CI tests..."
            pytest
            ;;
        'ut')
            echo "Running unit tests (excluding CI tests)..."
            pytest -m "not ci" tests
            ;;
        'ci')
            echo "Running CI tests..."
            pytest -m "ci" tests/ci
            ;;
        *)
            echo "Unknown test suite: '{{suite}}'. Available: 'ut', 'ci'"
            exit 1
            ;;
    esac

# E2Eテストの実行
# just test-e2e [headed|debug]
test-e2e mode='':
    #!/usr/bin/env zsh
    set -euo pipefail

    PYTEST_CMD="pytest tests-e2e --base-url {{BASE_URL}}"

    case '{{mode}}' in
        '')
            # No extra args
            ;;
        'headed')
            PYTEST_CMD="$PYTEST_CMD --headed"
            ;;
        'debug')
            PYTEST_CMD="$PYTEST_CMD --headed --slowmo 1000"
            ;;
        *)
            echo "Unknown test-e2e mode: '{{mode}}'. Available: 'headed', 'debug'"
            exit 1
            ;;
    esac

    eval $PYTEST_CMD

# カバレッジ計測
coverage:
    pytest --cov=app --cov-report=term-missing

# linter/formatter
lint:
    ruff format . && ruff check --fix .

# 型チェック
mypy:
    mypy .

# 'prod'が指定された場合は本番環境の、それ以外は開発環境の依存関係を同期する
sync mode='dev':
    #!/usr/bin/env zsh
    set -euo pipefail

    if [[ '{{mode}}' == 'prod' ]]; then
        echo "Syncing production dependencies..."
        uv sync
    else
        echo "Syncing development dependencies..."
        uv sync --extra dev
    fi

# 仮想環境の作成
venv:
    uv venv -p 3.12

# すべてのチェックとテストを実行
# just test-all        -> lint, mypy, test (e2eテストは省略)
# just test-all strict -> lint, mypy, test, test-e2e (e2eテストも実行)
test-all mode='':
    #!/usr/bin/env zsh
    set -euo pipefail
    
    echo "Running lint..."
    just lint
    echo "Running mypy..."
    just mypy
    echo "Running tests..."
    just test
    
    case '{{mode}}' in
        '')
            echo "Skipping e2e tests (use 'just test-all strict' to include e2e tests)"
            ;;
        'strict')
            echo "Running e2e tests..."
            just test-e2e
            ;;
        *)
            echo "Unknown test-all mode: '{{mode}}'. Available: 'strict'"
            exit 1
            ;;
    esac
