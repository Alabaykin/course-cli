from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from course_cli.validate import validate_course_structure


def generate_report(course_dir: str | Path) -> dict[str, Any]:
    '''
    Generate a summary report for the course, including validation status,
    file statistics, and learning outcomes coverage.

    Args:
        course_dir (str | Path): Path to the course directory.

    Returns:
        dict[str, Any]: Course report statistics and status.
    '''
    dir_path = Path(course_dir).resolve()

    # 1. Валидация структуры курса
    validation_report = validate_course_structure(dir_path)

    # 2. Подсчет файлов и папок с исключением служебных/игнорируемых каталогов
    ignored_dirs = {'.git', '.venv', 'venv', '__pycache__', 'node_modules', 'temp_demo'}

    def is_ignored(p: Path) -> bool:
        try:
            rel = p.relative_to(dir_path)
        except ValueError:
            return True
        for part in rel.parts:
            if part.startswith('.') and part != '.':
                return True
            if part in ignored_dirs:
                return True
        return False

    all_paths = [p for p in dir_path.rglob('*') if not is_ignored(p)]
    
    total_dirs = sum(1 for p in all_paths if p.is_dir())
    total_files = sum(1 for p in all_paths if p.is_file())
    md_files = [p for p in all_paths if p.is_file() and p.suffix.lower() == '.md']

    # 3. Чтение метаданных курса из course.yaml
    course_title = dir_path.name
    outcomes: list[str] = []
    
    yaml_path = dir_path / 'course.yaml'
    if yaml_path.exists() and yaml_path.is_file():
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data:
                    if 'title' in data and data['title']:
                        course_title = data['title']
                    if 'outcomes' in data and isinstance(data['outcomes'], list):
                        outcomes = [str(o).strip() for o in data['outcomes'] if o]
        except Exception:
            pass

    # 4. Проверка охвата учебных результатов (outcomes) в Markdown-файлах
    covered_outcomes: list[str] = []
    uncovered_outcomes: list[str] = []
    
    if outcomes:
        # Читаем содержимое всех Markdown-файлов один раз для оптимизации
        md_contents: list[str] = []
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    md_contents.append(f.read().lower())
            except Exception:
                pass
        
        # Проверяем вхождение каждого учебного результата
        for outcome in outcomes:
            outcome_lower = outcome.lower()
            is_covered = False
            for content in md_contents:
                if outcome_lower in content:
                    is_covered = True
                    break
            
            if is_covered:
                covered_outcomes.append(outcome)
            else:
                uncovered_outcomes.append(outcome)

    total_outcomes = len(outcomes)
    coverage_percentage = 0.0
    if total_outcomes > 0:
        coverage_percentage = (len(covered_outcomes) / total_outcomes) * 100.0

    return {
        'course_title': course_title,
        'is_valid': validation_report['is_valid'],
        'validation_errors': validation_report['errors'],
        'files_stats': {
            'total_markdown_files': len(md_files),
            'total_files': total_files,
            'total_directories': total_dirs,
        },
        'outcomes_stats': {
            'total_outcomes': total_outcomes,
            'covered_outcomes': covered_outcomes,
            'uncovered_outcomes': uncovered_outcomes,
            'coverage_percentage': round(coverage_percentage, 2),
        }
    }
