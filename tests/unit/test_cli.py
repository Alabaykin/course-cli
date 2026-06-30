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

@patch('course_cli.cli.init_course_structure')
@patch('course_cli.cli.generate_xapi_statement')
@patch('course_cli.cli.send_xapi_statement')
def test_cli_init_interactive_fallback(mock_send, mock_gen, mock_init, runner):
    """
    Проверка кластера эквивалентности: команда init без аргументов вызывает интерактивный ввод.
    Имитирует ввод пользователя через аргумент input.
    """
    mock_init.return_value = {'is_success': True, 'message': 'Success init'}
    
    # Имитируем ввод строки "Interactive Course" и нажатие Enter
    result = runner.invoke(main, ['init'], input='Interactive Course\n')
    
    assert result.exit_code == 0
    assert "Введите название курса" in result.output
    assert "Создание курса: 'Interactive Course'..." in result.output
    mock_init.assert_called_once_with('Interactive Course', '.')

@patch('course_cli.cli.generate_report')
@patch('course_cli.cli.send_xapi_statement')
def test_cli_report_privacy_gate_decline(mock_send, mock_report, runner):
    """
    Проверка шлюза приватности (Privacy Gate): команда report с отказом от отправки в LRS.
    Убеждаемся, что при вводе 'n' (No) функция сетевой отправки НЕ вызывается (Error path/Opt-out).
    """
    mock_report.return_value = {
        'course_title': 'Privacy Course',
        'is_valid': True,
        'validation_errors': [],
        'files_stats': {'total_markdown_files': 1, 'total_files': 1, 'total_directories': 1},
        'outcomes_stats': {'total_outcomes': 1, 'covered_outcomes': [], 'uncovered_outcomes': [], 'coverage_percentage': 0.0}
    }
    
    # Имитируем отказ пользователя (n)
    result = runner.invoke(main, ['report'], input='n\n')
    
    assert result.exit_code == 0
    assert 'Отправить результаты в LRS?' in result.output
    assert 'Отправка в LRS отменена пользователем.' in result.output
    
    # Гарантируем, что данные не утекли
    mock_send.assert_not_called()

@patch('course_cli.cli.validate_course_structure')
@patch('course_cli.cli.generate_xapi_statement')
@patch('course_cli.cli.send_xapi_statement')
def test_cli_validate_success(mock_send, mock_gen, mock_val, runner):
    """Проверка Happy Path: команда validate при успешной валидации."""
    mock_val.return_value = {'is_valid': True, 'errors': []}
    
    result = runner.invoke(main, ['validate'])
    
    assert result.exit_code == 0
    assert "Курс валиден!" in result.output
    mock_gen.assert_called_once()
    mock_send.assert_called_once()

@patch('course_cli.cli.validate_course_structure')
@patch('course_cli.cli.send_xapi_statement')
def test_cli_validate_failure(mock_send, mock_val, runner):
    """Проверка Error Path: команда validate при наличии ошибок."""
    mock_val.return_value = {'is_valid': False, 'errors': ['Ошибка 1', 'Ошибка 2']}
    
    result = runner.invoke(main, ['validate'])
    
    assert result.exit_code == 1
    assert "Найдены ошибки:" in result.output
    assert "Ошибка 1" in result.output
    assert "Ошибка 2" in result.output
    mock_send.assert_not_called()

@patch('course_cli.cli.generate_report')
@patch('course_cli.cli.generate_xapi_statement')
@patch('course_cli.cli.send_xapi_statement')
def test_cli_report_privacy_gate_accept(mock_send, mock_gen, mock_report, runner):
    """Проверка Happy Path: команда report с согласием на отправку в LRS."""
    mock_report.return_value = {
        'course_title': 'Privacy Course',
        'is_valid': True,
        'validation_errors': [],
        'files_stats': {'total_markdown_files': 1, 'total_files': 1, 'total_directories': 1},
        'outcomes_stats': {'total_outcomes': 1, 'covered_outcomes': [], 'uncovered_outcomes': [], 'coverage_percentage': 0.0}
    }
    
    # Имитируем согласие пользователя (y)
    result = runner.invoke(main, ['report'], input='y\n')
    
    assert result.exit_code == 0
    assert "Результаты успешно отправлены в LRS" in result.output
    mock_gen.assert_called_once()
    mock_send.assert_called_once()

