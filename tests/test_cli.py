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


def test_cli_single_url_csv(tmp_path):
    csv_file = tmp_path / "result.csv"
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

        ret = main(["https://example.com", "-f", "csv", "-o", str(csv_file)])
        assert ret == 0
        assert csv_file.exists()
        content = csv_file.read_text(encoding="utf-8")
        assert "url,success,status_code,title" in content
        assert "https://example.com,True,200,Test Page" in content


def test_cli_csv_auto_detect(tmp_path):
    csv_file = tmp_path / "autodetect.csv"
    fake_result = ScrapeResult(
        url="https://example.com/auto",
        title="Auto CSV",
        markdown="Auto CSV Content",
        success=True,
    )
    with patch("patchtroy.cli.Patchtroy") as mock_cls:
        mock_instance = MagicMock()
        mock_instance.scrape.return_value = fake_result
        mock_cls.return_value = mock_instance

        ret = main(["https://example.com/auto", "-o", str(csv_file)])
        assert ret == 0
        assert csv_file.exists()
        content = csv_file.read_text(encoding="utf-8")
        assert "https://example.com/auto,True,200,Auto CSV" in content


def test_cli_batch_csv(tmp_path):
    csv_file = tmp_path / "batch.csv"
    r1 = ScrapeResult(url="https://a.com", title="A", markdown="Doc A", success=True)
    r2 = ScrapeResult(url="https://b.com", title="B", markdown="Doc B", success=False, error="Timeout")

    with patch("patchtroy.cli.Patchtroy") as mock_cls:
        mock_instance = MagicMock()
        mock_instance.scrape_many.return_value = [r1, r2]
        mock_cls.return_value = mock_instance

        ret = main(["https://a.com", "https://b.com", "-f", "csv", "-o", str(csv_file)])
        assert ret == 0
        assert csv_file.exists()
        lines = csv_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 3  # Header + 2 data rows
        assert "https://a.com" in lines[1]
        assert "https://b.com" in lines[2]
        assert "Timeout" in lines[2]


def test_scrape_result_to_csv():
    res = ScrapeResult(
        url="https://example.com/test",
        title="Sample",
        markdown="# Heading\nParagraph",
        metadata={"author": "Marcus", "date": "2026-09-03"},
        success=True,
    )
    csv_text = res.to_csv()
    assert "url,success,status_code,title,author,date" in csv_text
    assert "https://example.com/test" in csv_text
    assert "Marcus" in csv_text
    assert "2026-09-03" in csv_text

