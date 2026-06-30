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

@patch('course_cli.cli.init_course_structure')
@patch('course_cli.cli.generate_xapi_statement')
@patch('course_cli.cli.send_xapi_statement')
def test_cli_init_with_arguments(mock_send, mock_gen, mock_init, runner):
    """
    Проверка Happy Path: команда init с явной передачей названия курса.
    Проверяется корректный вызов бизнес-логики и отправки xAPI события без интерактива.
    """
    mock_init.return_value = {'is_success': True, 'message': 'Success init'}
    
    result = runner.invoke(main, ['init', 'Test Course'])
    
    assert result.exit_code == 0
    assert "Создание курса: 'Test Course'..." in result.output
    mock_init.assert_called_once_with('Test Course', '.')
    mock_gen.assert_called_once()
    mock_send.assert_called_once()
