[private]
@default: help

# show help message
@help:
    echo "Usage: just <recipe>"
    echo ""
    just --list

# アプリケーションの実行
run:
    python -m streamlit run app.py

# テストの実行
test:
    pytest

# カバレッジ計測
coverage:
    pytest --cov=app --cov-report=term-missing

# CIテストの実行
test-ci:
    python -m pytest tests-ci

# linter/formatter
lint:
    ruff format . && ruff check --fix .

typecheck:
    mypy .

sync:
    uv sync --extra dev

sync-prod:
    uv sync

venv:
    uv venv -p 3.12
