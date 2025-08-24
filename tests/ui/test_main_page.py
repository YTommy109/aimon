"""メインページのテスト。"""

from pathlib import Path

from pytest_mock import MockerFixture

from app.ui import main_page


class TestMainPage:
    """メインページのテストクラス。"""

    def test_メインページが正しく描画される(self, mocker: MockerFixture) -> None:
        """メインページが正しく描画されることをテストする。"""
        # Arrange
        mock_st = mocker.patch.object(main_page, 'st')
        mock_setup_logging = mocker.patch.object(main_page, 'setup_logging')
        mock_get_config = mocker.patch.object(main_page, 'get_config')
        mock_config = mocker.MagicMock()
        mock_config.data_dir_path = Path('/test/data')
        mock_get_config.return_value = mock_config
        mock_logger = mocker.MagicMock()
        mocker.patch('app.ui.main_page.logging.getLogger', return_value=mock_logger)
        mocker.patch('app.ui.main_page.JsonProjectRepository')

        # Act
        main_page.render_main_page()

        # Assert
        mock_st.title.assert_called_once_with('AI Project Manager')
        mock_setup_logging.assert_called()
        mock_logger.info.assert_called_once_with('Data directory: /test/data')
