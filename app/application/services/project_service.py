"""プロジェクト関連のサービス関数群。"""

from app.application.data_manager import DataManager
from app.domain.entities import Project


def _validate_project_input(name: str, source: str, ai_tool: str) -> str | None:
    """プロジェクト入力値の検証を行います。

    Returns:
        エラーメッセージ、問題がない場合はNone。
    """
    if not name or not name.strip():
        return 'プロジェクト名を入力してください。'

    return (
        'ソースディレクトリパスを入力してください。'
        if not source or not source.strip()
        else ('AIツールを選択してください。' if not ai_tool or not ai_tool.strip() else None)
    )


def handle_project_creation(
    name: str,
    source: str,
    ai_tool: str,
    data_manager: DataManager,
) -> tuple[Project | None, str]:
    """プロジェクト作成処理を実行します。

    Args:
        name: プロジェクト名。
        source: ソースディレクトリパス。
        ai_tool: AIツールID。
        data_manager: データマネージャー。

    Returns:
        作成したプロジェクト(失敗時はNone)とメッセージのタプル。
    """
    # 入力値チェック
    validation_error = _validate_project_input(name, source, ai_tool)
    if validation_error:
        return None, validation_error

    # プロジェクト作成
    project = data_manager.create_project(name.strip(), source.strip(), ai_tool)

    return (
        (project, f'プロジェクト「{project.name}」を作成しました。')
        if project
        else (None, 'プロジェクトの作成に失敗しました。')
    )


def handle_project_execution(
    project: Project,
    data_manager: DataManager,
) -> tuple[Project | None, str]:
    """プロジェクト実行処理を実行します。

    Args:
        project: 実行するプロジェクト。
        data_manager: データマネージャー。

    Returns:
        更新後のプロジェクト(失敗時はNone)とメッセージのタプル。
    """
    try:
        # プロジェクトの実行開始
        project.start_processing()

        # データベースに保存
        success = data_manager.update_project(project)
        return (
            (project, f'プロジェクト「{project.name}」の実行を開始しました。')
            if success
            else (None, 'プロジェクトの実行開始に失敗しました。')
        )

    except Exception as e:
        return None, f'プロジェクトの実行開始中にエラーが発生しました: {e!s}'
