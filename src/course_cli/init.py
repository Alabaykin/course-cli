import yaml
from pathlib import Path
from typing import Any

def init_course_structure(title: str, target_dir: str | Path) -> dict[str, Any]:
    """
    Генерирует базовую структуру курса: папки и файлы-шаблоны.
    """
    base_path = Path(target_dir)

    # Создаем корневые папки
    directories = ['modules', 'lessons']
    for d in directories:
        (base_path / d).mkdir(parents=True, exist_ok=True)

    # Генерируем метаданные для course.yaml
    yaml_path = base_path / 'course.yaml'
    metadata = {
        'title': title,
        'outcomes': [
            "Пример результата 1 (замените на свой)",
            "Пример результата 2 (замените на свой)"
        ],
        'skills': []
    }
    
    # Записываем YAML
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(
            metadata, 
            f, 
            allow_unicode=True, 
            default_flow_style=False, 
            sort_keys=False
        )

    # Создаем стартовый index.md, если его нет
    index_path = base_path / 'index.md'
    if not index_path.exists():
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\nДобро пожаловать в курс! Здесь будет описание.\n")

    return {
        'is_success': True,
        'message': f"Структура курса успешно создана в '{base_path.resolve()}'"
    }