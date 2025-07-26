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

    case '{{mode}}' in
        '')
            # 全テスト実行
            pytest tests_e2e --base-url {{BASE_URL}}
            ;;
        'headed')
            # ヘッドレスモード無効（ブラウザ表示）
            pytest tests_e2e --base-url {{BASE_URL}} --headed
            ;;
        'debug')
            # デバッグモード（ブラウザ表示+スローモーション）
            pytest tests_e2e --base-url {{BASE_URL}} --headed --slowmo 1000
            ;;
        *)
            echo "Unknown test-e2e mode: '{{mode}}'"
            echo "Available: 'headed', 'debug'"
            exit 1
            ;;
    esac

# カバレッジ計測
coverage:
    pytest --cov=app --cov-report=term-missing

# ruff
ruff path='':
    #!/usr/bin/env zsh
    set -euo pipefail

    if [[ '{{path}}' == '' ]]; then
        ruff format . && ruff check --fix .
    else
        ruff format {{path}} && ruff check --fix {{path}}
    fi


# linter/formatter
lint:
    ruff format . && ruff check --fix .
    just vulture
    mypy .

# 'prod'が指定された場合は本番環境の、それ以外は開発環境の依存関係を同期する
sync mode='':
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
# just test-all        -> lint, test (e2eテストは省略)
# just test-all strict -> lint, test, test-e2e (e2eテストも実行)
test-all mode='':
    #!/usr/bin/env zsh
    set -euo pipefail
    
    echo "Running lint..."
    just lint
    echo "Running tests..."
    just coverage
    
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

playwright-mcp:
    npx @playwright/mcp

mdlint path='':
    #!/usr/bin/env zsh
    set -euo pipefail

    if [[ '{{path}}' == '' ]]; then
        markdownlint-cli2 --fix .
    else
        markdownlint-cli2 --fix {{path}}
    fi

# 未使用コードの検出
# 参考: https://scrapbox.io/PythonOsaka/Python%E3%81%AE%E9%9D%99%E7%9A%84%E8%A7%A3%E6%9E%90%E3%83%84%E3%83%BC%E3%83%ABVulture%E3%82%92%E4%BD%BF%E3%81%A3%E3%81%A6%E3%81%BF%E3%82%88%E3%81%86
vulture path='':
    #!/usr/bin/env zsh
    set -euo pipefail

    if [[ '{{path}}' == '' ]]; then
        vulture app pages tests tests_e2e
    else
        vulture {{path}}
    fi

# 型チェック
# 参考: https://github.com/astral-sh/ty
ty:
    uvx ty check

# HTMLドキュメント生成
docs:
    pdoc app --html --output-dir docs
