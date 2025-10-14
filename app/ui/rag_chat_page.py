"""RAGチャットページのUIを管理するモジュール。"""

import asyncio
import logging
import pickle
import re
from contextlib import suppress
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr
from rank_bm25 import BM25Okapi

from app.config import config
from app.models.project import Project
from app.repositories.project_repository import JsonProjectRepository
from app.services.project_service import ProjectService
from app.types import LLMProviderName
from app.utils.llm_client import LLMClient

# 日本標準時のタイムゾーン
JST = ZoneInfo('Asia/Tokyo')

logger = logging.getLogger('aiman')


class RAGChatPage:
    """RAGチャットページのUIを管理するクラス。"""

    # 日本語トークンの最大長（これ以上は分割）
    MAX_JAPANESE_TOKEN_LENGTH = 10
    # 日本語トークンの分割ステップ
    JAPANESE_TOKEN_SPLIT_STEP = 2

    def __init__(self, project_service: ProjectService, project_repo: JsonProjectRepository):
        """RAGチャットページを初期化する。

        Args:
            project_service: プロジェクトサービス。
            project_repo: プロジェクトリポジトリ。
        """
        self.project_service = project_service
        self.project_repo = project_repo
        self._initialize_session_state()

    def _initialize_session_state(self) -> None:
        """セッション状態を初期化する。"""
        if 'selected_project_id' not in st.session_state:
            st.session_state.selected_project_id = None
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        if 'rag_logs' not in st.session_state:
            st.session_state.rag_logs = []

    def render(self) -> None:
        """RAGチャットページをレンダリングする。"""
        st.title('RAG チャット')

        # プロジェクト選択
        selected_project = self._render_project_selection()

        if selected_project:
            # インデックス作成日時表示と再構築ボタン
            self._render_index_status(selected_project)

            # チャット対話欄と入力欄（画面の上2/3）
            with st.container():
                self._render_chat_area(selected_project)

            # ログ出力欄（画面の下1/3）
            with st.container():
                self._render_log_area()
        else:
            st.info('プロジェクトを選択してください。')

    def _render_project_selection(self) -> Project | None:
        """プロジェクト選択UIをレンダリングする。

        Returns:
            選択されたプロジェクト、未選択の場合はNone。
        """
        projects = self.project_repo.find_all()

        if not projects:
            st.warning('プロジェクトが存在しません。')
            return None

        return self._select_project_from_list(projects)

    def _select_project_from_list(self, projects: list[Project]) -> Project | None:
        """プロジェクトリストから選択する。

        Args:
            projects: プロジェクトリスト。

        Returns:
            選択されたプロジェクト、未選択の場合はNone。
        """
        # プロジェクト選択用の辞書を作成
        project_options = {p.name: p for p in projects}
        project_names = list(project_options.keys())

        # デフォルト選択を設定
        default_index = self._get_default_project_index(project_options)

        selected_name = st.selectbox(
            'プロジェクトを選択', project_names, index=default_index, key='project_selector'
        )

        if selected_name:
            selected_project = project_options[selected_name]
            st.session_state.selected_project_id = selected_project.id
            return selected_project

        return None

    def _get_default_project_index(self, project_options: dict[str, Project]) -> int:
        """デフォルトプロジェクトのインデックスを取得する。

        Args:
            project_options: プロジェクト選択肢の辞書。

        Returns:
            デフォルトインデックス。
        """
        default_index = 0
        if st.session_state.selected_project_id:
            for i, (_name, project) in enumerate(project_options.items()):
                if project.id == st.session_state.selected_project_id:
                    default_index = i
                    break
        return default_index

    def _render_index_status(self, project: Project) -> None:
        """インデックス作成日時を表示し、再構築ボタンを配置する。

        Args:
            project: 対象プロジェクト。
        """
        col1, col2 = st.columns([3, 1])

        with col1:
            if project.index_finished_at:
                st.success(
                    f'インデックス作成完了: '
                    f'{project.index_finished_at.strftime("%Y-%m-%d %H:%M:%S")}'
                )
            else:
                st.warning('インデックス未作成')

        with col2:
            if st.button('インデックス再構築', key='rebuild_indexes'):
                self._rebuild_indexes(project)

    def _rebuild_indexes(self, project: Project) -> None:
        """インデックスを再構築する。

        Args:
            project: 対象プロジェクト。
        """
        try:
            self._start_rebuild_process()
            updated_project, message = self.project_service.rebuild_project_indexes(project.id)
            self._handle_rebuild_result(updated_project, message)
        except Exception as e:
            self._handle_rebuild_error(e)

    def _start_rebuild_process(self) -> None:
        """インデックス再構築プロセスを開始する。"""
        st.session_state.rag_logs = []
        self._add_log('インデックス再構築を開始します...')

    def _handle_rebuild_result(self, updated_project: Project | None, message: str) -> None:
        """インデックス再構築結果を処理する。

        Args:
            updated_project: 更新されたプロジェクト。
            message: メッセージ。
        """
        if updated_project:
            self._add_log(f'インデックス再構築完了: {message}')
            st.success(message)
            st.rerun()
        else:
            self._add_log(f'インデックス再構築失敗: {message}')
            st.error(message)

    def _handle_rebuild_error(self, error: Exception) -> None:
        """インデックス再構築エラーを処理する。

        Args:
            error: エラー。
        """
        logger.error(f'インデックス再構築エラー: {error}')
        self._add_log(f'インデックス再構築エラー: {error!s}')
        st.error(f'インデックス再構築エラー: {error!s}')

    def _render_chat_area(self, project: Project) -> None:
        """チャット対話欄と入力欄をレンダリングする。

        Args:
            project: 対象プロジェクト。
        """
        # チャット履歴表示
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_messages:
                with st.chat_message(message['role']):
                    st.write(message['content'])

        # チャット入力
        if prompt := st.chat_input('メッセージを入力してください'):
            # ユーザーメッセージを追加
            st.session_state.chat_messages.append({'role': 'user', 'content': prompt})

            # チャット履歴を再表示
            with chat_container:
                for message in st.session_state.chat_messages:
                    with st.chat_message(message['role']):
                        st.write(message['content'])

            # RAG処理を実行
            self._process_rag_query(project, prompt)

    def _render_log_area(self) -> None:
        """ログ出力欄をレンダリングする。"""
        st.subheader('ログ')
        if 'rag_log_placeholder' not in st.session_state:
            st.session_state.rag_log_placeholder = st.empty()
        log_text = '\n'.join(st.session_state.rag_logs)
        st.session_state.rag_log_placeholder.code(log_text or '')

    # 装飾のないテキストログのみを扱うため、個別表示関数は不要

    def _process_rag_query(self, project: Project, query: str) -> None:
        """RAGクエリを処理する。

        Args:
            project: 対象プロジェクト。
            query: ユーザークエリ。
        """
        try:
            # ログをクリア
            st.session_state.rag_logs = []

            # RAG処理を実行
            response = self._execute_rag_pipeline(project, query)

            # レスポンスをチャット履歴に追加
            st.session_state.chat_messages.append({'role': 'assistant', 'content': response})
            st.rerun()

        except Exception as e:
            logger.error(f'RAG処理エラー: {e}')
            self._add_log(f'RAG処理エラー: {e!s}')
            st.session_state.chat_messages.append(
                {'role': 'assistant', 'content': 'エラーが発生しました。'}
            )

    def _execute_rag_pipeline(self, project: Project, query: str) -> str:
        """RAGパイプラインを実行する。

        Args:
            project: 対象プロジェクト。
            query: ユーザークエリ。

        Returns:
            LLMからの応答。
        """
        # セマンティックサーチ
        self._add_log('セマンティックサーチを実行中...')
        semantic_results = self._perform_semantic_search(project, query)

        # キーワードサーチ
        self._add_log('キーワードサーチを実行中...')
        keyword_results = self._perform_keyword_search(project, query)

        # 結果を統合・重複排除
        self._add_log('検索結果を統合中...')
        combined_context = self._combine_search_results(semantic_results, keyword_results)

        # 件数・参考文書ログ
        self._log_search_counts(len(semantic_results), len(keyword_results), len(combined_context))
        self._log_references(combined_context)

        # LLM問い合わせ
        self._add_log('LLM問い合わせを実行中...')
        return self._call_llm_with_context(query, combined_context)

    def _perform_semantic_search(self, project: Project, query: str) -> list[dict[str, Any]]:
        """セマンティックサーチを実行する。

        Args:
            project: 対象プロジェクト。
            query: 検索クエリ。

        Returns:
            検索結果のリスト。
        """
        results: list[dict[str, Any]] = []
        try:
            # インデックスディレクトリの確認
            source_dir = Path(project.source)
            index_dir = source_dir / 'vector_db'

            if not index_dir.exists():
                logger.warning(f'セマンティックインデックスが存在しません: {index_dir}')
            else:
                # 埋め込みモデルの取得
                embeddings = self._get_embeddings_model()
                if embeddings is not None:
                    # FAISSインデックスの読み込みと検索
                    results = self._search_faiss_index(index_dir, embeddings, query)
        except Exception as e:
            logger.error(f'セマンティックサーチエラー: {e}')
        return results

    def _log_search_counts(self, sem_n: int, kw_n: int, merged_n: int) -> None:
        """検索件数のサマリログを出力する。"""
        self._add_log(f'検索件数: セマンティック={sem_n} キーワード={kw_n} 統合後={merged_n}')

    def _log_references(self, combined_context: list[dict[str, Any]]) -> None:
        """参考文書のログを出力する。"""
        if not combined_context:
            self._add_log('参考文書: 見つかりませんでした')
            return
        for doc in combined_context:
            path = doc.get('path', '')
            score = float(doc.get('score', 0.0))
            preview = doc.get('content', '')[:200]
            self._add_log(f'参考文書: {path} [score={score:.3f}]\n{preview}...')

    def _get_embeddings_model(self) -> OpenAIEmbeddings | GoogleGenerativeAIEmbeddings | None:
        """埋め込みモデルを取得する。

        Returns:
            埋め込みモデル、取得できない場合はNone。
        """
        provider = LLMProviderName(config.llm_provider)
        match provider:
            case LLMProviderName.OPENAI:
                return OpenAIEmbeddings(
                    model=config.openai_embedding_model,
                    api_key=SecretStr(config.openai_api_key) if config.openai_api_key else None,
                )
            case LLMProviderName.GEMINI:
                return GoogleGenerativeAIEmbeddings(
                    model=config.gemini_embedding_model,
                    google_api_key=SecretStr(config.gemini_api_key)
                    if config.gemini_api_key
                    else None,
                )

    def _search_faiss_index(
        self,
        index_dir: Path,
        embeddings: OpenAIEmbeddings | GoogleGenerativeAIEmbeddings,
        query: str,
    ) -> list[dict[str, Any]]:
        """FAISSインデックスで検索を実行する。

        Args:
            index_dir: インデックスディレクトリ。
            embeddings: 埋め込みモデル。
            query: 検索クエリ。

        Returns:
            検索結果のリスト。
        """
        # FAISSインデックスの読み込み
        vectorstore = FAISS.load_local(
            str(index_dir), embeddings, allow_dangerous_deserialization=True
        )

        # 類似検索の実行
        docs = vectorstore.similarity_search(query, k=5)

        # 結果を辞書形式に変換
        results = []
        for doc in docs:
            results.append(
                {
                    'path': doc.metadata.get('path', ''),
                    'content': doc.page_content,
                    'score': 1.0,  # FAISSはスコアを返さないため固定値
                }
            )

        return results

    def _perform_keyword_search(self, project: Project, query: str) -> list[dict[str, Any]]:
        """キーワードサーチを実行する。

        Args:
            project: 対象プロジェクト。
            query: 検索クエリ。

        Returns:
            検索結果のリスト。
        """
        results: list[dict[str, Any]] = []
        try:
            # インデックスディレクトリの確認
            source_dir = Path(project.source)
            index_dir = source_dir / 'keyword_db'

            if not index_dir.exists():
                logger.warning(f'キーワードインデックスが存在しません: {index_dir}')
            else:
                # BM25インデックスの読み込み
                bm25, metadata = self._load_bm25_index(index_dir)
                if bm25 and metadata:
                    # クエリのトークン化と検索実行
                    results = self._search_bm25_index(bm25, metadata, query)
        except Exception as e:
            logger.error(f'キーワードサーチエラー: {e}')
        return results

    def _load_bm25_index(
        self, index_dir: Path
    ) -> tuple[BM25Okapi | None, list[dict[str, Any]] | None]:
        """BM25インデックスを読み込む。

        Args:
            index_dir: インデックスディレクトリ。

        Returns:
            (BM25インデックス, メタデータ)のタプル。
        """
        index_path = index_dir / 'bm25_index.pkl'
        metadata_path = index_dir / 'metadata.pkl'

        if not index_path.exists() or not metadata_path.exists():
            logger.warning(f'BM25インデックスファイルが存在しません: {index_dir}')
            return None, None

        bm25 = self._safe_load_pickle(index_path)
        metadata = self._safe_load_pickle(metadata_path)
        return bm25, metadata

    def _safe_load_pickle(self, path: Path) -> BM25Okapi | list[dict[str, Any]] | None:
        """pickleを安全に読み込む(失敗時はNone)。

        Args:
            path: 読み込むファイルパス。

        Returns:
            読み込んだオブジェクト。失敗時はNone。
        """
        try:
            with open(path, 'rb') as f:
                return pickle.load(f)  # noqa: S301
        except Exception as e:
            logger.error(f'pickle読込エラー: {path} ({e})')
            return None

    def _search_bm25_index(
        self, bm25: BM25Okapi, metadata: list[dict[str, Any]], query: str
    ) -> list[dict[str, Any]]:
        """BM25インデックスで検索を実行する。

        Args:
            bm25: BM25インデックス。
            metadata: メタデータ。
            query: 検索クエリ。

        Returns:
            検索結果のリスト。
        """
        # クエリのトークン化
        query_tokens = self._tokenize_text(query)

        if not query_tokens:
            return []

        # BM25検索の実行
        scores = bm25.get_scores(query_tokens)

        # スコア順にソート
        scored_docs = list(zip(scores, metadata, strict=False))
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        # 上位5件を取得
        results = []
        for score, doc_meta in scored_docs[:5]:
            if score > 0:  # スコアが0より大きいもののみ
                results.append(
                    {
                        'path': doc_meta['path'],
                        'content': doc_meta['content'],
                        'score': float(score),
                    }
                )

        return results

    def _tokenize_text(self, text: str) -> list[str]:
        """テキストをトークン化する。日本語対応の改善実装。

        Args:
            text: トークン化するテキスト。

        Returns:
            トークンのリスト。
        """
        tokens = []

        # 英数字のトークンを抽出
        tokens.extend(self._extract_alphanumeric_tokens(text))

        # 日本語のトークンを抽出
        tokens.extend(self._extract_japanese_tokens(text))

        # 短すぎるトークンや空白のみのトークンを除去
        return [token for token in tokens if len(token) > 1 and token.strip()]

    def _extract_alphanumeric_tokens(self, text: str) -> list[str]:
        """英数字のトークンを抽出する。"""
        tokens = []
        for match in re.finditer(r'[a-zA-Z0-9]+', text):
            tokens.append(match.group().lower())
        return tokens

    def _extract_japanese_tokens(self, text: str) -> list[str]:
        """日本語のトークンを抽出する。"""
        tokens = []
        for match in re.finditer(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+', text):
            token = match.group()
            if len(token) > self.MAX_JAPANESE_TOKEN_LENGTH:
                tokens.extend(self._split_long_japanese_token(token))
            else:
                tokens.append(token)
        return tokens

    def _split_long_japanese_token(self, token: str) -> list[str]:
        """長い日本語トークンを分割する。"""
        split_tokens = []
        for i in range(0, len(token), self.JAPANESE_TOKEN_SPLIT_STEP):
            if i + self.JAPANESE_TOKEN_SPLIT_STEP <= len(token):
                split_tokens.append(token[i : i + self.JAPANESE_TOKEN_SPLIT_STEP])
            else:
                split_tokens.append(token[i:])
        return split_tokens

    def _combine_search_results(
        self, semantic_results: list[dict[str, Any]], keyword_results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """検索結果を統合・重複排除する。

        Args:
            semantic_results: セマンティックサーチ結果。
            keyword_results: キーワードサーチ結果。

        Returns:
            統合された検索結果。
        """
        # 重複排除のためのセット
        seen_paths: set[str] = set()
        combined_results: list[dict[str, Any]] = []

        # セマンティックサーチ結果を優先的に追加
        self._add_semantic_results(semantic_results, seen_paths, combined_results)

        # キーワードサーチ結果を追加（重複を除く）
        self._add_keyword_results(keyword_results, seen_paths, combined_results)

        # スコア順にソート（セマンティックサーチのスコアは固定値1.0）
        combined_results.sort(key=lambda x: x['score'], reverse=True)

        # 最大10件に制限
        return combined_results[:10]

    def _add_semantic_results(
        self,
        semantic_results: list[dict[str, Any]],
        seen_paths: set[str],
        combined_results: list[dict[str, Any]],
    ) -> None:
        """セマンティックサーチ結果を追加する。

        Args:
            semantic_results: セマンティックサーチ結果。
            seen_paths: 既に見たパスのセット。
            combined_results: 統合結果リスト。
        """
        for result in semantic_results:
            path = result['path']
            if path not in seen_paths:
                combined_results.append(result)
                seen_paths.add(path)

    def _add_keyword_results(
        self,
        keyword_results: list[dict[str, Any]],
        seen_paths: set[str],
        combined_results: list[dict[str, Any]],
    ) -> None:
        """キーワードサーチ結果を追加する。

        Args:
            keyword_results: キーワードサーチ結果。
            seen_paths: 既に見たパスのセット。
            combined_results: 統合結果リスト。
        """
        for result in keyword_results:
            path = result['path']
            if path not in seen_paths:
                combined_results.append(result)
                seen_paths.add(path)

    def _call_llm_with_context(self, query: str, context: list[dict[str, Any]]) -> str:
        """コンテキスト付きでLLMを呼び出す。

        Args:
            query: ユーザークエリ。
            context: 検索結果コンテキスト。

        Returns:
            LLMからの応答。
        """
        try:
            # コンテキストをプロンプトに組み込む
            context_text = self._format_context_for_prompt(context)
            prompt = self._create_rag_prompt(query, context_text)

            # LLMクライアントの初期化
            llm_client = LLMClient(LLMProviderName(config.llm_provider))

            # 非同期LLM呼び出し
            return self._await_llm(llm_client, prompt)

        except Exception as e:
            logger.error(f'LLM呼び出しエラー: {e}')
            return f'LLM呼び出しエラー: {e!s}'

    def _await_llm(self, llm_client: LLMClient, prompt: str) -> str:
        """イベントループの有無に応じて非同期LLM呼び出しを行う。"""
        loop = None
        with suppress(RuntimeError):
            loop = asyncio.get_running_loop()
        if loop is not None and loop.is_running():
            result = asyncio.run(llm_client.generate_text(prompt))
        elif loop is not None:
            result = loop.run_until_complete(llm_client.generate_text(prompt))
        else:
            result = asyncio.run(llm_client.generate_text(prompt))
        return result

    def _format_context_for_prompt(self, context: list[dict[str, Any]]) -> str:
        """コンテキストをプロンプト用にフォーマットする。

        Args:
            context: 検索結果コンテキスト。

        Returns:
            フォーマットされたコンテキストテキスト。
        """
        if not context:
            return '参考文書が見つかりませんでした。'

        context_parts = []
        for i, doc in enumerate(context, 1):
            context_parts.append(
                f'【参考文書{i}】\nファイル: {doc["path"]}\n内容: {doc["content"]}\n'
            )

        return '\n'.join(context_parts)

    def _create_rag_prompt(self, query: str, context: str) -> str:
        """RAG用のプロンプトを作成する。

        Args:
            query: ユーザークエリ。
            context: 参考文書コンテキスト。

        Returns:
            作成されたプロンプト。
        """
        return f"""以下の参考文書を基に、ユーザーの質問に回答してください。

{context}

質問: {query}

回答:"""

    def _add_log(self, message: str) -> None:
        """テキストログを追記する。"""
        st.session_state.rag_logs.append(message)
        # 逐次反映
        if 'rag_log_placeholder' in st.session_state:
            log_text = '\n'.join(st.session_state.rag_logs)
            st.session_state.rag_log_placeholder.code(log_text or '')


def render_rag_chat_page(
    project_service: ProjectService, project_repo: JsonProjectRepository
) -> None:
    """RAGチャットページをレンダリングする。

    Args:
        project_service: プロジェクトサービス。
        project_repo: プロジェクトリポジトリ。
    """
    page = RAGChatPage(project_service, project_repo)
    page.render()
