from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml


LINK_REGEX = re.compile(r'!?\[[^\]]*\]\(([^)]+)\)')


def validate_course_metadata(course_dir: str | Path) -> dict[str, Any]:
    '''
    Validate course metadata from course.yaml.

    Args:
        course_dir (str | Path): Path to the course directory.

    Returns:
        dict[str, Any]: Validation report with keys 'is_valid' and 'errors'.
    '''
    dir_path = Path(course_dir)
    yaml_path = dir_path / 'course.yaml'

    # 1. Проверка существования файла
    if not yaml_path.exists():
        return {
            'is_valid': False,
            'errors': ['Файл course.yaml не найден.'],
        }

    # 2. Чтение и парсинг YAML
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return {
            'is_valid': False,
            'errors': [f'Ошибка парсинга YAML: {e}'],
        }
    except Exception as e:
        return {
            'is_valid': False,
            'errors': [f'Ошибка при чтении файла: {e}'],
        }

    # 3. Валидация полей
    errors: list[str] = []
    if not data:
        return {
            'is_valid': False,
            'errors': ['Файл course.yaml пуст.'],
        }

    if 'title' not in data or not data['title']:
        errors.append("Отсутствует обязательное поле: 'title'")

    if 'outcomes' not in data or not isinstance(data['outcomes'], list) or len(data['outcomes']) == 0:
        errors.append("Отсутствует или пуст список учебных результатов: 'outcomes'")

    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
    }


if __name__ == '__main__':
    # Берем путь из аргументов или используем папку по умолчанию
    target_dir = sys.argv[1] if len(sys.argv) > 1 else './test_courses/invalid_course'

    print(f'Проверка курса в директории: {target_dir}')
    report = validate_course_metadata(target_dir)

    if report['is_valid']:
        print('✅ Курс валиден!')
    else:
        print('❌ Найдены ошибки:')
        for err in report['errors']:
            print(f'  - {err}')
