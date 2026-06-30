import os
import yaml
from pathlib import Path
from unittest.mock import patch, call
import pytest
from course_cli.init import init_course_structure

@pytest.mark.parametrize("title, expected_title", [
    ("Python Basics", "Python Basics"),
    ("Advanced C++ (2026)", "Advanced C++ (2026)"),
    ("12345", "12345"),
])
def test_init_creates_directories_and_templates(tmp_path: Path, title: str, expected_title: str) -> None:
    """
    Проверяет создание всех необходимых директорий и заполнение шаблонов файлов.
    Соответствует принципу атомарности и кластеризации входных данных.
    """
    result = init_course_structure(title, tmp_path)
    
    assert result['is_success'] is True
    
    # 1. Проверка структуры директорий
    assert (tmp_path / 'modules' / 'module_1').is_dir()
    assert (tmp_path / 'lessons').is_dir()
    assert (tmp_path / 'assessments').is_dir()
    assert (tmp_path / '.githooks').is_dir()
    
    # 2. Проверка контентных шаблонов
    lesson_path = tmp_path / 'modules' / 'module_1' / 'lesson_1.md'
    assert lesson_path.is_file()
    assert expected_title in lesson_path.read_text(encoding='utf-8')
    
    task_path = tmp_path / 'assessments' / 'task_1.md'
    assert task_path.is_file()
    assert "Практическое задание 1" in task_path.read_text(encoding='utf-8')
    
    index_path = tmp_path / 'index.md'
    assert index_path.is_file()
    assert f"# {expected_title}" in index_path.read_text(encoding='utf-8')
    
    # 3. Проверка pre-commit хука
    hook_path = tmp_path / '.githooks' / 'pre-commit'
    assert hook_path.is_file()
    assert "course-cli validate" in hook_path.read_text(encoding='utf-8')
    assert os.access(hook_path, os.X_OK)

def test_init_generates_valid_course_yaml(tmp_path: Path) -> None:
    """
    Проверяет, что генерируется валидный YAML файл со всеми требуемыми ключами.
    """
    title = "YAML Test Course"
    init_course_structure(title, tmp_path)
    
    yaml_path = tmp_path / 'course.yaml'
    assert yaml_path.is_file()
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        
    assert data['title'] == title
    assert 'description' in data
    assert 'outcomes' in data
    assert 'competencies' in data
    assert 'skills' in data

@patch('course_cli.init.subprocess.run')
def test_init_git_integration_success(mock_run, tmp_path: Path) -> None:
    """
    Проверяет Happy Path: вызов системных git команд при отсутствии репозитория.
    Использует мокирование для избежания запуска реального git процесса.
    """
    init_course_structure("Git Test", tmp_path)
    
    expected_calls = [
        call(['git', 'init'], cwd=str(tmp_path), check=True, capture_output=True),
        call(['git', 'config', 'core.hooksPath', '.githooks'], cwd=str(tmp_path), check=True, capture_output=True)
    ]
    mock_run.assert_has_calls(expected_calls, any_order=True)

