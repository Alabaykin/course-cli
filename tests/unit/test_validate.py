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


def test_metadata_missing_outcomes(tmp_path: Path) -> None:
    """
    Test validate_course_metadata when course.yaml misses 'outcomes', is empty or not a list.
    """
    yaml_file = tmp_path / 'course.yaml'
    
    # outcomes is completely missing
    yaml_file.write_text("title: My Course\n", encoding='utf-8')
    report = validate_course_metadata(tmp_path)
    assert not report['is_valid']
    assert "Отсутствует или пуст список учебных результатов: 'outcomes'" in report['errors']
    
    # outcomes is not a list (e.g. a string)
    yaml_file.write_text("title: My Course\noutcomes: not-a-list\n", encoding='utf-8')
    report = validate_course_metadata(tmp_path)
    assert not report['is_valid']
    assert "Отсутствует или пуст список учебных результатов: 'outcomes'" in report['errors']
    
    # outcomes is an empty list
    yaml_file.write_text("title: My Course\noutcomes: []\n", encoding='utf-8')
    report = validate_course_metadata(tmp_path)
    assert not report['is_valid']
    assert "Отсутствует или пуст список учебных результатов: 'outcomes'" in report['errors']


def test_metadata_valid(tmp_path: Path) -> None:
    """
    Test validate_course_metadata with valid course.yaml file.
    """
    yaml_file = tmp_path / 'course.yaml'
    yaml_file.write_text("title: My Course\noutcomes:\n- Outcome 1\n- Outcome 2\n", encoding='utf-8')
    
    report = validate_course_metadata(tmp_path)
    assert report['is_valid']
    assert len(report['errors']) == 0


def test_find_broken_links_no_markdown(tmp_path: Path) -> None:
    """
    Test find_broken_links when no markdown files exist in the course directory.
    """
    from course_cli.validate import find_broken_links
    errors = find_broken_links(tmp_path)
    assert len(errors) == 0






