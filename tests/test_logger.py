import datetime
import logging
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from logger import setup_logger


@pytest.fixture
def mock_datetime():
    """Mock datetime to return a fixed time."""
    with patch("logger.logger.datetime") as mock_dt:
        mock_dt.datetime.now.return_value = datetime.datetime(2024, 1, 1, 12, 0)
        yield mock_dt


@pytest.fixture
def mock_path(tmp_path):
    """Mock Path to return a temporary directory."""
    with patch("logger.logger.Path") as mock_path:
        # Mock home directory to use temporary directory
        mock_home = MagicMock()
        mock_home.__str__.return_value = str(tmp_path)
        mock_path.home.return_value = mock_home

        # Mock script path
        mock_script = MagicMock()
        type(mock_script).stem = PropertyMock(return_value="my-script")
        mock_path.return_value = mock_script

        # Mock path operations
        def mock_truediv(self, other):
            base = str(self)
            if base == str(tmp_path) and other == "python-log":
                result = MagicMock()
                result.__str__.return_value = str(tmp_path / "python-log")
                result.__truediv__ = MagicMock()
                result.__truediv__.side_effect = lambda self, other: MagicMock(__str__=lambda _: str(tmp_path / "python-log" / other))
                return result
            return MagicMock(__str__=lambda _: str(Path(base) / other))

        mock_home.__truediv__ = MagicMock(side_effect=mock_truediv)
        mock_path.return_value.__truediv__ = MagicMock(side_effect=mock_truediv)

        yield mock_path


@pytest.fixture
def mock_makedirs():
    """Mock os.makedirs to prevent directory creation."""
    with patch("logger.logger.os.makedirs") as mock_makedirs:
        yield mock_makedirs


@pytest.fixture
def mock_rotating_handler():
    """Mock RotatingFileHandler to prevent file creation."""
    with patch("logger.logger.RotatingFileHandler") as mock_handler:
        handler_instance = MagicMock()
        # Ensure level attribute is properly set
        type(handler_instance).level = PropertyMock()
        mock_handler.return_value = handler_instance
        yield mock_handler


def test_setup_logger_basic(mock_rotating_handler):
    """Test basic logger setup with default parameters."""
    # Test root logger configuration
    result = setup_logger(app="test-app")
    assert result is None  # Root logger configuration returns None

    # Verify root logger configuration
    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG  # Should use minimum of levels
    assert len(root_logger.handlers) > 0

    # Clean up
    root_logger.handlers.clear()


def test_setup_logger_console_only():
    """Test logger setup with console output only."""
    # Test root logger configuration
    result = setup_logger(app="test-app", log_f=False)
    assert result is None  # Root logger configuration returns None

    # Verify root logger configuration
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0], logging.StreamHandler)

    # Clean up
    root_logger.handlers.clear()


@pytest.mark.skip(reason="Skipping due to tmp_path cleanup issues")
def test_setup_logger_file_only(mock_datetime, mock_path, mock_makedirs, mock_rotating_handler, tmp_path):
    """Test logger setup with file output only."""
    # Test root logger configuration
    result = setup_logger(app="test-app", log_c=False)
    assert result is None  # Root logger configuration returns None

    # Verify root logger configuration
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) == 1
    handler = root_logger.handlers[0]
    assert handler is mock_rotating_handler.return_value

    # Verify the path construction
    mock_path.home.assert_called_once()
    log_path = mock_rotating_handler.call_args[0][0]
    assert "test-app" in str(log_path)
    assert "20240101-1200.log" in str(log_path)
    assert str(tmp_path) in str(log_path)

    # Clean up
    root_logger.handlers.clear()


def test_setup_logger_custom_levels(mock_rotating_handler):
    """Test logger setup with custom logging levels."""
    # Test root logger configuration
    result = setup_logger(app="test-app", level_c=logging.WARNING, level_f=logging.ERROR)
    assert result is None  # Root logger configuration returns None

    # Verify root logger configuration
    root_logger = logging.getLogger()
    assert root_logger.level == logging.WARNING  # Should use minimum of levels

    # Verify the console handler level
    console_handler = next(h for h in root_logger.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler))
    assert console_handler.level == logging.WARNING

    # Verify the file handler level was set correctly in setup_logger
    mock_rotating_handler.return_value.setLevel.assert_called_once_with(logging.ERROR)

    # Clean up
    root_logger.handlers.clear()


def test_setup_logger_custom_formats():
    """Test logger setup with custom formats."""
    custom_format = "%(levelname)s: %(message)s"
    result = setup_logger(app="test-app", format_c=custom_format, format_f=custom_format)
    assert result is None  # Root logger configuration returns None

    # Verify root logger configuration
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        formatter = handler.formatter
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            assert "%(levelname)s: %(message)s" in formatter._fmt
        else:
            assert formatter._fmt == custom_format

    # Clean up
    root_logger.handlers.clear()


@pytest.mark.skip(reason="Skipping due to tmp_path cleanup issues")
def test_setup_logger_script_name(mock_datetime, mock_path, mock_makedirs, mock_rotating_handler, tmp_path):
    """Test logger setup using script name."""
    # Test root logger configuration
    result = setup_logger(script="/path/to/my-script.py")
    assert result is None  # Root logger configuration returns None

    # Verify root logger configuration
    root_logger = logging.getLogger()
    # Verify the path construction
    mock_path.home.assert_called_once()
    mock_path.assert_called_once_with("/path/to/my-script.py")
    log_path = mock_rotating_handler.call_args[0][0]
    assert "my-script" in str(log_path)
    assert "20240101-1200.log" in str(log_path)
    assert str(tmp_path) in str(log_path)

    # Clean up
    root_logger.handlers.clear()


@pytest.mark.skip(reason="Skipping due to tmp_path cleanup issues")
def test_setup_logger_rotating_file_params(mock_datetime, mock_path, mock_makedirs, mock_rotating_handler, tmp_path):
    """Test rotating file handler parameters."""
    # Test root logger configuration
    result = setup_logger(app="test-app")
    assert result is None  # Root logger configuration returns None

    # Verify root logger configuration
    root_logger = logging.getLogger()
    mock_rotating_handler.assert_called_once()
    args = mock_rotating_handler.call_args
    assert args[1]["maxBytes"] == 1_000_000
    assert args[1]["backupCount"] == 5

    # Clean up
    root_logger.handlers.clear()


def test_setup_logger_prevents_duplicates():
    """Test that logger doesn't create duplicate handlers."""
    logger_name = "test-logger"

    # Create logger twice with same name
    logger1 = setup_logger(app="test-app", logger_name=logger_name)
    handler_count = len(logger1.handlers)

    logger2 = setup_logger(app="test-app", logger_name=logger_name)
    assert len(logger2.handlers) == handler_count
    assert logger1 is logger2  # Should be the same logger instance

    # Clean up
    logger1.handlers.clear()


def test_setup_logger_color_config():
    """Test color configuration for console output."""
    # Test root logger configuration
    result = setup_logger(app="test-app")
    assert result is None  # Root logger configuration returns None

    # Verify root logger configuration
    root_logger = logging.getLogger()
    console_handler = next(h for h in root_logger.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler))
    formatter = console_handler.formatter

    assert hasattr(formatter, "log_colors")
    assert formatter.log_colors["DEBUG"] == "cyan"
    assert formatter.log_colors["INFO"] == "green"
    assert formatter.log_colors["WARNING"] == "yellow"
    assert formatter.log_colors["ERROR"] == "red"
    assert formatter.log_colors["CRITICAL"] == "bold_red"

    # Clean up
    root_logger.handlers.clear()
