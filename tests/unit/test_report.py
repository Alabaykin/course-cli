import pytest
from pathlib import Path
from course_cli.report import generate_report

def test_generate_report_valid_course(tmp_path: Path):
    """
    Проверяет успешную генерацию отчета: правильный подсчет файлов 
    и корректный анализ покрытия результатов обучения (outcomes).
    """
    # Подготовка валидной структуры
    yaml_path = tmp_path / 'course.yaml'
    yaml_path.write_text("title: Report Course\noutcomes:\n  - Learn Python\n  - Master Git", encoding='utf-8')
    
    (tmp_path / 'modules').mkdir()
    md_path = tmp_path / 'modules' / 'lesson1.md'
    md_path.write_text("In this lesson we will learn python today.", encoding='utf-8')
    
    # Выполнение
    report = generate_report(tmp_path)
    
    # Проверка статистики файлов
    assert report['course_title'] == 'Report Course'
    assert report['files_stats']['total_markdown_files'] == 1
    assert report['files_stats']['total_directories'] == 1
    
    # Проверка статистики результатов
    assert report['outcomes_stats']['total_outcomes'] == 2
    assert 'Learn Python' in report['outcomes_stats']['covered_outcomes']
    assert 'Master Git' in report['outcomes_stats']['uncovered_outcomes']
    assert report['outcomes_stats']['coverage_percentage'] == 50.0
