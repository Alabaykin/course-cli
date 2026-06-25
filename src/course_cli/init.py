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

    hooks_dir = base_path / '.githooks'
    hooks_dir.mkdir(exist_ok=True)
    
    hook_path = hooks_dir / 'pre-commit'
    hook_script = '''#!/usr/bin/env bash

RED='\\033[0;31m'
GREEN='\\033[0;32m'
NC='\\033[0m' # No Color

echo "Очередь pre-commit: Запуск Course CLI валидации..."

STASH_CREATED=0
if ! git diff --quiet; then
    git stash push -q --keep-index -m "course-cli-pre-commit-stash"
    STASH_CREATED=1
fi

course-cli validate .
RESULT=$?

if [ $STASH_CREATED -eq 1 ]; then
    git stash pop -q
fi

if [ $RESULT -ne 0 ]; then
    echo -e "${RED}❌ Коммит отклонен: Найдены ошибки в структуре курса или course.yaml.${NC}"
    echo -e "${RED}Пожалуйста, исправьте ошибки, добавьте файлы через 'git add' и попробуйте снова.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Валидация успешно пройдена. Коммит разрешен.${NC}"
exit 0
'''
    return {
        'is_success': True,
        'message': f"Структура курса успешно создана в '{base_path.resolve()}'"
    }