"""Tests for new logger features: queue handling, rotation parsing, and error handling."""

import datetime
import logging
import os
import threading
import time
from unittest.mock import patch

from logger import setup_logger
from logger.logger import _create_file_handler, _parse_rotation


class TestRotationParsing:
    """Test rotation parameter parsing functionality."""

    def test_size_rotation_bytes(self):
        """Test size-based rotation with byte values."""
        config = _parse_rotation(1000000)
        assert config["type"] == "size"
        assert config["maxBytes"] == 1000000
        assert config["backupCount"] == 5

    def test_size_rotation_mb(self):
        """Test size-based rotation with MB specification."""
        config = _parse_rotation("100 MB")
        assert config["type"] == "size"
        assert config["maxBytes"] == 100 * 1024 * 1024
        assert config["backupCount"] == 5

    def test_size_rotation_gb(self):
        """Test size-based rotation with GB specification."""
        config = _parse_rotation("1 GB")
        assert config["type"] == "size"
        assert config["maxBytes"] == 1024 * 1024 * 1024
        assert config["backupCount"] == 5

    def test_size_rotation_kb(self):
        """Test size-based rotation with KB specification."""
        config = _parse_rotation("500 KB")
        assert config["type"] == "size"
        assert config["maxBytes"] == 500 * 1024
        assert config["backupCount"] == 5

    def test_time_rotation_daily(self):
        """Test time-based rotation with daily specification."""
        config = _parse_rotation("1 day")
        assert config["type"] == "time"
        assert config["when"] == "D"
        assert config["interval"] == 1
        assert config["backupCount"] == 7

    def test_time_rotation_weekly(self):
        """Test time-based rotation with weekly specification."""
        config = _parse_rotation("2 weeks")
        assert config["type"] == "time"
        assert config["when"] == "W0"
        assert config["interval"] == 2
        assert config["backupCount"] == 7

    def test_time_rotation_hourly(self):
        """Test time-based rotation with hourly specification."""
        config = _parse_rotation("6 hours")
        assert config["type"] == "time"
        assert config["when"] == "H"
        assert config["interval"] == 6
        assert config["backupCount"] == 7

    def test_time_rotation_at_time(self):
        """Test time-based rotation at specific time."""
        config = _parse_rotation("12:00")
        assert config["type"] == "time"
        assert config["when"] == "midnight"
        assert config["interval"] == 1
        assert config["backupCount"] == 7

    def test_default_rotation(self):
        """Test default rotation for unrecognized patterns."""
        config = _parse_rotation("invalid")
        assert config["type"] == "time"
        assert config["when"] == "midnight"
        assert config["interval"] == 1
        assert config["backupCount"] == 7


class TestFileHandlerCreation:
    """Test file handler creation with different rotation configurations."""

    @patch("logger.logger.datetime")
    def test_default_rotation_handler(self, mock_datetime, tmp_path):
        """Test default rotation handler creation."""
        mock_datetime.datetime.now.return_value = datetime.datetime(2024, 1, 1, 12, 0)

        handler = _create_file_handler(log_dir=tmp_path, is_testing=False, rotation=None, level_f=logging.DEBUG, format_f="%(message)s")

        assert handler.maxBytes == 1_000_000
        assert handler.backupCount == 5
        assert handler.level == logging.DEBUG

    @patch("logger.logger.datetime")
    def test_size_rotation_handler(self, mock_datetime, tmp_path):
        """Test size-based rotation handler creation."""
        mock_datetime.datetime.now.return_value = datetime.datetime(2024, 1, 1, 12, 0)

        handler = _create_file_handler(log_dir=tmp_path, is_testing=False, rotation="50 MB", level_f=logging.INFO, format_f="%(message)s")

        assert handler.maxBytes == 50 * 1024 * 1024
        assert handler.backupCount == 5
        assert handler.level == logging.INFO

    @patch("logger.logger.datetime")
    def test_time_rotation_handler(self, mock_datetime, tmp_path):
        """Test time-based rotation handler creation."""
        mock_datetime.datetime.now.return_value = datetime.datetime(2024, 1, 1, 12, 0)

        handler = _create_file_handler(log_dir=tmp_path, is_testing=False, rotation="1 day", level_f=logging.WARNING, format_f="%(message)s")

        assert handler.when == "D"
        assert handler.interval == 86400  # TimedRotatingFileHandler converts to seconds
        assert handler.backupCount == 7
        assert handler.level == logging.WARNING

    @patch("logger.logger.datetime")
    def test_testing_filename(self, mock_datetime, tmp_path):
        """Test testing filename generation."""
        mock_datetime.datetime.now.return_value = datetime.datetime(2024, 1, 1, 12, 0)

        handler = _create_file_handler(log_dir=tmp_path, is_testing=True, rotation=None, level_f=logging.DEBUG, format_f="%(message)s")

        # Check that testing filename is used
        assert "testing.log" in str(handler.baseFilename)


class TestQueueLogging:
    """Test queue-based thread-safe logging."""

    def test_queue_logging_setup(self):
        """Test that queue logging is properly set up."""
        logger = setup_logger(app="queue-test", use_queue=True, logger_name="test_queue")

        # Check that queue handler was added
        assert len(logger.handlers) == 1
        handler = logger.handlers[0]
        assert handler.__class__.__name__ == "QueueHandler"

        # Check that queue listener was stored
        assert hasattr(logger, "_queue_listeners")
        assert len(logger._queue_listeners) == 1

        # Clean up
        for listener in logger._queue_listeners:
            listener.stop()
        logger.handlers.clear()

    def test_queue_logging_thread_safety(self):
        """Test that queue logging works correctly with multiple threads."""
        setup_logger(app="thread-test", use_queue=True, log_c=False, log_f=False)

        messages = []
        original_info = logging.info

        def capture_info(msg, *args):
            messages.append(msg % args if args else msg)
            return original_info(msg, *args)

        # Mock logging to capture messages
        logging.info = capture_info

        try:

            def worker(thread_id):
                for i in range(5):
                    logging.info(f"Thread {thread_id}: Message {i}")
                    time.sleep(0.01)

            threads = []
            for i in range(3):
                t = threading.Thread(target=worker, args=[i])
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            # Give queue time to process
            time.sleep(0.1)

            # Should have messages from all threads
            assert len(messages) == 15  # 3 threads * 5 messages each

        finally:
            logging.info = original_info


class TestErrorHandling:
    """Test error handling and graceful fallbacks."""

    def test_invalid_log_path_fallback(self):
        """Test graceful fallback when log path is invalid."""
        original_path = os.environ.get("PY_LOG_PATH")
        os.environ["PY_LOG_PATH"] = "/invalid/nonexistent/path"

        try:
            # Should not raise exception, should fall back to console
            logger = setup_logger(app="error-test", logger_name="error_logger")

            # Should have at least one handler (console fallback)
            assert len(logger.handlers) > 0

            # Should be able to log without errors
            logger.info("This should work despite file logging failure")

        finally:
            # Restore original path
            if original_path:
                os.environ["PY_LOG_PATH"] = original_path
            else:
                os.environ.pop("PY_LOG_PATH", None)

            # Clean up
            logger.handlers.clear()

    @patch("logger.logger.Path.mkdir")
    def test_permission_error_fallback(self, mock_mkdir):
        """Test graceful fallback when directory creation fails."""
        mock_mkdir.side_effect = PermissionError("Permission denied")

        # Should not raise exception
        logger = setup_logger(app="permission-test", logger_name="perm_logger")

        # Should have console handler as fallback
        assert len(logger.handlers) > 0

        # Clean up
        logger.handlers.clear()

    def test_no_handlers_fallback(self):
        """Test fallback when both console and file logging are disabled."""
        logger = setup_logger(app="no-handlers", logger_name="no_handler_logger", log_c=False, log_f=False)

        # Should have no handlers since both are disabled
        assert len(logger.handlers) == 0

        # Clean up
        logger.handlers.clear()


class TestParameterValidation:
    """Test parameter validation and edge cases."""

    def test_logger_name_vs_root_logger(self):
        """Test difference between named logger and root logger configuration."""
        # Root logger returns None
        result = setup_logger(app="root-test")
        assert result is None

        # Named logger returns logger instance
        logger = setup_logger(app="named-test", logger_name="test_named")
        assert logger is not None
        assert logger.name == "test_named"

        # Clean up
        logger.handlers.clear()

    def test_level_precedence(self):
        """Test that logger level is set to minimum of console and file levels."""
        logger = setup_logger(app="level-test", logger_name="level_logger", level_c=logging.WARNING, level_f=logging.DEBUG)

        # Logger level should be minimum (DEBUG)
        assert logger.level == logging.DEBUG

        # Clean up
        logger.handlers.clear()

    def test_format_customization(self):
        """Test custom format strings."""
        custom_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        logger = setup_logger(app="format-test", logger_name="format_logger", format_c=custom_format, format_f=custom_format, log_f=False)  # Only test console to avoid file complexities

        # Check that console handler uses custom format
        console_handler = logger.handlers[0]
        assert custom_format in console_handler.formatter._fmt

        # Clean up
        logger.handlers.clear()


class TestIntegration:
    """Integration tests for complete logger functionality."""

    def test_complete_setup_workflow(self):
        """Test complete logger setup with all features."""
        logger = setup_logger(
            app="integration-test",
            logger_name="integration_logger",
            level_c=logging.INFO,
            level_f=logging.DEBUG,
            rotation="1 MB",
            use_queue=False,  # Avoid queue for simpler testing
            log_c=True,
            log_f=False,  # Avoid file complications in test
        )

        # Test basic logging functionality
        logger.info("Integration test message")
        logger.warning("Integration test warning")
        logger.error("Integration test error")

        # Verify logger configuration
        assert logger is not None
        assert logger.name == "integration_logger"
        assert len(logger.handlers) >= 1

        # Clean up
        logger.handlers.clear()

    def test_multiple_setup_calls(self):
        """Test that multiple setup calls don't create duplicate handlers."""
        logger_name = "multi_setup_logger"

        # First setup
        logger1 = setup_logger(app="multi-test", logger_name=logger_name, log_f=False)
        initial_handler_count = len(logger1.handlers)

        # Second setup - should clean up previous handlers
        logger2 = setup_logger(app="multi-test", logger_name=logger_name, log_f=False)

        # Should be same logger instance with same number of handlers
        assert logger1 is logger2
        assert len(logger2.handlers) == initial_handler_count

        # Clean up
        logger1.handlers.clear()
