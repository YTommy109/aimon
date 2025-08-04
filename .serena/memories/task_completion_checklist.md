# タスク完了時のチェックリスト

## コード編集後の必須作業

### Python ファイル編集後
1. **フォーマットとリント実行**
   ```bash
   ruff format {ファイル名} && ruff check --fix {ファイル名}
   ```

2. **型チェック確認**
   ```bash
   mypy {ファイル名}
   ```

3. **テスト実行**
   ```bash
   just test
   ```

### Markdown ファイル編集後
1. **Markdown リント実行**
   ```bash
   markdownlint-cli2 --fix {ファイル名}
   ```

## コミット前の最終チェック

### 全体的な品質チェック
1. **全ファイルのフォーマットとリント**
   ```bash
   just lint
   ```

2. **テスト実行**
   ```bash
   just test
   ```

3. **カバレッジ確認**
   ```bash
   just coverage
   ```

4. **未使用コード検出**
   ```bash
   just vulture
   ```

### 厳密なチェック（重要機能変更時）
1. **E2Eテスト実行**
   ```bash
   just test-e2e
   ```

2. **全テスト実行**
   ```bash
   just test all
   ```

3. **厳密な全チェック**
   ```bash
   just test-all strict
   ```

## 品質基準
- **Lint エラー**: 0件（必須）
- **型チェックエラー**: 0件（必須）
- **テスト失敗**: 0件（必須）
- **カバレッジ**: 適切な範囲をカバー
- **未使用コード**: 最小限に抑制

## 注意事項
- `pyproject.toml` の変更は事前にユーザーに相談
- `# type: ignore` コメントは使用禁止
- テストコードは適切な日本語名で命名
- E2Eテストでは堅牢なセレクタを使用