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
# just test     -> pytest --testmon (変更の影響範囲のみテスト)
# just test ut  -> ユニットテスト (変更の影響範囲のみ)
# just test ci  -> CIテスト (変更の影響範囲のみ)
# just test all -> 全件テスト
test suite='':
    #!/usr/bin/env zsh
    set -euo pipefail

    case '{{suite}}' in
        '')
            echo "Running affected tests only..."
            pytest --testmon
            ;;
        'ut')
            echo "Running affected unit tests (excluding CI tests)..."
            pytest --testmon -m "not ci" tests
            ;;
        'ci')
            echo "Running affected CI tests..."
            pytest --testmon -m "ci" tests/ci
            ;;
        'all')
            echo "Running all tests..."
            pytest
            ;;
        *)
            echo "Unknown test suite: '{{suite}}'. Available: 'ut', 'ci', 'all'"
            exit 1
            ;;
    esac

# E2Eテストの実行
# just test-e2e [headed|debug|smoke|core|ui|performance|accessibility]
test-e2e mode='':
    #!/usr/bin/env zsh
    set -euo pipefail

    PYTEST_CMD="pytest tests_e2e --base-url {{BASE_URL}}"

    case '{{mode}}' in
        '')
            # 全テスト実行
            ;;
        'headed')
            PYTEST_CMD="$PYTEST_CMD --headed"
            ;;
        'debug')
            PYTEST_CMD="$PYTEST_CMD --headed --slowmo 1000"
            ;;
        'smoke')
            PYTEST_CMD="$PYTEST_CMD -k 'test_ページ全体の基本レイアウトが正しく表示される'"
            ;;
        'core')
            PYTEST_CMD="$PYTEST_CMD -k 'test_プロジェクト作成フォーム or test_プロジェクト詳細モーダル'"
            ;;
        'ui')
            PYTEST_CMD="$PYTEST_CMD -k 'test_デスクトップレイアウト or test_モバイルレイアウト'"
            ;;
        'performance')
            PYTEST_CMD="$PYTEST_CMD -k 'test_ページの読み込み時間 or test_自動更新機能のパフォーマンス'"
            ;;
        'accessibility')
            PYTEST_CMD="$PYTEST_CMD -k 'test_キーボードナビゲーション or test_ARIAラベル or test_カラーコントラスト'"
            ;;
        'single-browser')
            PYTEST_CMD="pytest tests_e2e --base-url {{BASE_URL}} --browser chromium"
            ;;
        *)
            echo "Unknown test-e2e mode: '{{mode}}'"
            echo "Available: 'headed', 'debug', 'smoke', 'core', 'ui', 'performance', 'accessibility', 'single-browser'"
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
    just test all
    
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

@watch:
    fswatch -o app tests | xargs -n1 -I{} just test
