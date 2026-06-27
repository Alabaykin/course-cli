from __future__ import annotations

from pathlib import Path
from course_cli.validate import validate_course_metadata


def test_metadata_missing_file(tmp_path: Path) -> None:
    """
    Test validate_course_metadata when course.yaml does not exist.
    """
    report = validate_course_metadata(tmp_path)
    assert not report['is_valid']
    assert 'Файл course.yaml не найден.' in report['errors']


def test_metadata_invalid_yaml(tmp_path: Path) -> None:
    """
    Test validate_course_metadata when course.yaml contains invalid YAML.
    """
    yaml_file = tmp_path / 'course.yaml'
    # Write invalid YAML syntax
    yaml_file.write_text("title: My Course\n  outcomes:\n- nested error: : invalid", encoding='utf-8')
    
    report = validate_course_metadata(tmp_path)
    assert not report['is_valid']
    assert any('Ошибка парсинга YAML' in err for err in report['errors'])


def test_metadata_empty_file(tmp_path: Path) -> None:
    """
    Test validate_course_metadata when course.yaml exists but is empty.
    """
    yaml_file = tmp_path / 'course.yaml'
    yaml_file.write_text("", encoding='utf-8')
    
    report = validate_course_metadata(tmp_path)
    assert not report['is_valid']
    assert 'Файл course.yaml пуст.' in report['errors']


def test_metadata_missing_title(tmp_path: Path) -> None:
    """
    Test validate_course_metadata when course.yaml misses 'title' or it is empty.
    """
    yaml_file = tmp_path / 'course.yaml'
    
    # Outcomes is present, but title is missing
    yaml_file.write_text("outcomes:\n- Outcome 1\n", encoding='utf-8')
    report = validate_course_metadata(tmp_path)
    assert not report['is_valid']
    assert "Отсутствует обязательное поле: 'title'" in report['errors']
    
    # Title is empty string
    yaml_file.write_text("title: ''\noutcomes:\n- Outcome 1\n", encoding='utf-8')
    report = validate_course_metadata(tmp_path)
    assert not report['is_valid']
    assert "Отсутствует обязательное поле: 'title'" in report['errors']



