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
