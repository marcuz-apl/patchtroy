"""Tests for Patchtroy CLI."""

from unittest.mock import MagicMock, patch

from patchtroy.cli import main
from patchtroy.models import ScrapeResult


def test_cli_help(capsys):
    ret = main([])
    assert ret == 1


def test_cli_single_url():
    fake_result = ScrapeResult(
        url="https://example.com",
        title="Test Page",
        markdown="This is test markdown.",
        success=True,
    )
    with patch("patchtroy.cli.Patchtroy") as mock_cls:
        mock_instance = MagicMock()
        mock_instance.scrape.return_value = fake_result
        mock_cls.return_value = mock_instance

        ret = main(["https://example.com", "--screenshot", "out.png", "--pdf", "out.pdf"])
        assert ret == 0
        mock_cls.assert_called_once()
        # Verify config created had screenshot and pdf enabled
        config_arg = mock_cls.call_args[0][0]
        assert config_arg.screenshot is True
        assert config_arg.pdf is True
        assert config_arg.screenshot_path == "out.png"
        assert config_arg.pdf_path == "out.pdf"


def test_cli_batch_urls():
    fake_result = ScrapeResult(
        url="https://example.com",
        title="Test Page",
        markdown="Markdown content",
        success=True,
    )
    with patch("patchtroy.cli.Patchtroy") as mock_cls:
        mock_instance = MagicMock()
        mock_instance.scrape_many.return_value = [fake_result, fake_result]
        mock_cls.return_value = mock_instance

        ret = main(["https://example.com/1", "https://example.com/2", "-c", "4"])
        assert ret == 0
        config_arg = mock_cls.call_args[0][0]
        assert config_arg.max_concurrency == 4
        mock_instance.scrape_many.assert_called_once_with(["https://example.com/1", "https://example.com/2"])


def test_cli_serve():
    with patch("patchtroy.server.run_server") as mock_run:
        ret = main(["serve", "--port", "9000", "--host", "127.0.0.1"])
        assert ret == 0
        mock_run.assert_called_once_with(host="127.0.0.1", port=9000)
