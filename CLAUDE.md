# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python logging utility that simplifies logging configuration across modules and threads. The core principle is to configure the root logger once at the application entry point, then use standard `logging.info()`, `logging.debug()`, etc. throughout the codebase - no need to pass logger instances around.

## Development Commands

### Running Tests
```bash
# Run specific test
poetry run pytest tests/test_logger.py::test_setup_logger_basic -v

# Run all tests with coverage
poetry run pytest

# Run all tests (configured with coverage by default)
poetry run pytest -v --cov=logger --cov-report=term-missing
```

### Code Quality
```bash
# Type checking
poetry run mypy .

# Pre-commit hooks (runs black, isort, mypy, bandit, autoflake, flake8)
pre-commit run --all-files

# Individual linters
poetry run black .
poetry run isort .
poetry run flake8
```

## Architecture

### Core Module: `logger/logger.py`
- `setup_logger()`: Main function that configures logging with sensible defaults
  - Configures both console (with colors via colorlog) and file logging (with rotation)
  - Logs are organized by script/app name in `~/python-log/` (or `$PY_LOG_PATH`)
  - File logs rotate hourly with 1MB max size and 5 backups
- `remove_all_loggers()`: Cleans all existing handlers to prevent duplicate logs
- Key design: Configure root logger once, use everywhere without passing instances

### Configuration
- Black line length: 222 characters
- MyPy: Relaxed settings (many checks disabled)
- Pre-commit: Runs black, isort, mypy, bandit, autoflake, flake8
- Test coverage: Configured to report missing lines

### Testing
- Tests use mocking to avoid file system operations
- Special handling for testing environment via `TESTING` env variable
- Coverage target: logger module
