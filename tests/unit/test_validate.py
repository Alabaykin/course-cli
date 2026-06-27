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


def test_find_broken_links_valid_links(tmp_path: Path) -> None:
    """
    Test find_broken_links when links are valid (exist, external, anchor-only, or empty).
    """
    from course_cli.validate import find_broken_links
    
    # Create target files
    (tmp_path / 'lesson1.md').write_text("Lesson content", encoding='utf-8')
    (tmp_path / 'img').mkdir()
    (tmp_path / 'img' / 'pic.png').write_text("", encoding='utf-8')
    
    # Create indexing markdown with valid links
    index_md = tmp_path / 'index.md'
    index_md.write_text(
        "Link to [Lesson 1](lesson1.md)\n"
        "Link to [Pic](img/pic.png)\n"
        "Link to [External](https://google.com)\n"
        "Link to [Anchor](#anchor-link)\n"
        "Link to [Empty]()\n",
        encoding='utf-8'
    )
    
    errors = find_broken_links(tmp_path)
    assert len(errors) == 0


def test_find_broken_links_with_broken(tmp_path: Path) -> None:
    """
    Test find_broken_links when broken relative links are present.
    """
    from course_cli.validate import find_broken_links
    
    # Create indexing markdown with broken links
    index_md = tmp_path / 'index.md'
    index_md.write_text(
        "Link to [Missing Lesson](lessons/missing.md)\n"
        "Link to [Absolute Missing Root](/missing_root.png)\n",
        encoding='utf-8'
    )
    
    errors = find_broken_links(tmp_path)
    assert len(errors) == 2
    assert any('lessons/missing.md' in err or 'lessons\\missing.md' in err for err in errors)
    assert any('missing_root.png' in err for err in errors)


def test_find_broken_links_read_error(tmp_path: Path, mocker) -> None:
    """
    Test find_broken_links handles exceptions when opening markdown files.
    """
    from course_cli.validate import find_broken_links
    
    md_file = tmp_path / 'broken.md'
    md_file.write_text("Some text", encoding='utf-8')
    
    # Mock open to raise PermissionError when opening broken.md
    original_open = open
    def mock_open(file, *args, **kwargs):
        if Path(file).name == 'broken.md':
            raise PermissionError("Permission denied")
        return original_open(file, *args, **kwargs)
        
    mocker.patch('builtins.open', mock_open)
    
    errors = find_broken_links(tmp_path)
    assert len(errors) == 1
    assert 'Ошибка при анализе файла broken.md' in errors[0]









