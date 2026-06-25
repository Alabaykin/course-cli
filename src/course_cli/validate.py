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


def find_broken_links(course_dir: str | Path) -> list[str]:
    '''
    Find broken relative links in all markdown files in the course directory.

    Args:
        course_dir (str | Path): Path to the course directory.

    Returns:
        list[str]: A list of error messages for broken links.
    '''
    dir_path = Path(course_dir)
    errors: list[str] = []

    # Находим все Markdown-файлы рекурсивно
    md_files = list(dir_path.rglob('*.md'))

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    for link in LINK_REGEX.findall(line):
                        # Отсекаем query-параметры и хэш-фрагменты
                        clean_link = link.split('#')[0].split('?')[0].strip()

                        # Игнорируем внешние ссылки
                        if any(clean_link.lower().startswith(proto) for proto in ('http://', 'https://', 'mailto:', 'ftp://', 'tel:')):
                            continue

                        # Игнорируем ссылки, которые ссылаются только на якорь или пусты
                        if link.strip().startswith('#') or not clean_link:
                            continue

                        # Определяем полный путь к целевому файлу
                        if clean_link.startswith('/') or clean_link.startswith('\\'):
                            # Относительно корня курса
                            target_path = dir_path / clean_link.lstrip('/\\')
                        else:
                            # Относительно текущего файла
                            target_path = (md_file.parent / clean_link).resolve()

                        # Проверяем существование файла/папки
                        if not target_path.exists():
                            # Вычисляем относительный путь для красивого вывода
                            try:
                                rel_md = md_file.relative_to(dir_path)
                            except ValueError:
                                rel_md = md_file

                            try:
                                rel_target = target_path.relative_to(dir_path) if target_path.is_relative_to(dir_path) else target_path
                            except ValueError:
                                rel_target = target_path

                            errors.append(
                                f'Битая ссылка в {rel_md}:{line_num}: "{link}" (файл не найден: {rel_target})'
                            )
        except Exception as e:
            try:
                rel_md = md_file.relative_to(dir_path)
            except ValueError:
                rel_md = md_file
            errors.append(f'Ошибка при анализе файла {rel_md}: {e}')

    return errors


def validate_course_structure(course_dir: str | Path) -> dict[str, Any]:
    '''
    Validate course structure including metadata (course.yaml), existence of index.md,
    and correctness of relative markdown links.

    Args:
        course_dir (str | Path): Path to the course directory.

    Returns:
        dict[str, Any]: Validation report with keys 'is_valid' and 'errors'.
    '''
    dir_path = Path(course_dir)
    errors: list[str] = []

    # 1. Валидация метаданных (course.yaml)
    metadata_report = validate_course_metadata(dir_path)
    if not metadata_report['is_valid']:
        errors.extend(metadata_report['errors'])

    # 2. Проверка наличия корневого файла index.md
    index_path = dir_path / 'index.md'
    if not index_path.exists():
        errors.append("Отсутствует корневой файл 'index.md'")
    elif not index_path.is_file():
        errors.append("Путь 'index.md' существует, но не является файлом")

    # 3. Поиск битых ссылок в Markdown-файлах
    if dir_path.exists() and dir_path.is_dir():
        broken_links_errors = find_broken_links(dir_path)
        errors.extend(broken_links_errors)

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
