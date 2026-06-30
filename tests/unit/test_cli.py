import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from course_cli.cli import main

@pytest.fixture
def runner():
    """Фикстура для изолированного запуска команд CLI."""
    return CliRunner()

def test_cli_help(runner):
    """
    Проверка Happy Path: вызов утилиты без аргументов корректно выводит справочную информацию.
    """
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'Course CLI' in result.output
    assert 'init' in result.output
    assert 'validate' in result.output
    assert 'report' in result.output
