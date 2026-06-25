import sys
from pathlib import Path
import click
from course_cli.init import init_course_structure
from course_cli.validate import validate_course_structure
from course_cli.report import generate_report
from course_cli.xapi import load_env, generate_xapi_statement, send_xapi_statement

# Загрузка переменных окружения
load_env()


@click.group()
def main():
    """Course CLI - инструмент структурирования курса."""
    pass

@main.command()
@click.argument('title')
@click.option('--dir', '-d', 'target_dir', default='.', type=click.Path(), help='Папка для создания курса')
def init(title, target_dir):
    """Инициализация структуры нового курса."""
    click.echo(f"Создание курса: '{title}'...")
    
    # Вызов бизнес-логики
    result = init_course_structure(title, target_dir)
    
    # Оформление результата
    if result.get('is_success'):
        click.secho(result['message'], fg='green')
        # Отправка события xAPI
        try:
            stmt = generate_xapi_statement(
                verb_id='http://activitystrea.ms/schema/1.0/initialize',
                verb_display='инициализировал',
                course_title=title,
                course_path=target_dir,
                success=True
            )
            send_xapi_statement(stmt)
        except Exception as e:
            click.echo(f"Предупреждение: не удалось залогировать xAPI событие: {e}", err=True)
    else:
        click.secho("❌ Произошла ошибка при создании курса", fg='red')

@main.command()
@click.argument('course_dir', default='.')
def validate(course_dir):
    """Проверка структуры и метаданных курса."""
    click.echo(f"Запуск проверок для директории: {course_dir}...")
    report = validate_course_structure(course_dir)

    if report['is_valid']:
        click.echo("✅ Курс валиден!")
        
        # Получаем название курса из course.yaml
        yaml_path = Path(course_dir) / 'course.yaml'
        course_title = Path(course_dir).resolve().name
        if yaml_path.exists():
            import yaml
            try:
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'title' in data:
                        course_title = data['title']
            except Exception:
                pass
                
        # Отправка события xAPI
        try:
            stmt = generate_xapi_statement(
                verb_id='http://activitystrea.ms/schema/1.0/validate',
                verb_display='проверил',
                course_title=course_title,
                course_path=course_dir,
                success=True
            )
            send_xapi_statement(stmt)
        except Exception as e:
            click.echo(f"Предупреждение: не удалось залогировать xAPI событие: {e}", err=True)
    else:
        click.echo("❌ Найдены ошибки:")
        for err in report['errors']:
            click.echo(f"  - {err}")
        sys.exit(1)

@main.command()
@click.argument('course_dir', default='.')
def report(course_dir):
    """Генерация отчета и отправка xAPI событий."""
    click.echo(f"Формирование отчета для директории: {course_dir}...")
    
    # Вызов бизнес-логики
    try:
        report_data = generate_report(course_dir)
    except Exception as e:
        click.secho(f"❌ Произошла ошибка при анализе курса: {e}", fg='red')
        sys.exit(1)
        
    # Вывод результатов
    click.echo(f"\n📊 Отчет по курсу: '{report_data['course_title']}'")
    click.echo(f"--------------------------------------------------")
    
    # Статус валидации
    if report_data['is_valid']:
        click.secho("✅ Структура курса: Валидна", fg='green')
    else:
        click.secho("❌ Структура курса: Найдены ошибки", fg='red')
        for err in report_data['validation_errors']:
            click.echo(f"  - {err}")
            
    # Статистика файлов
    click.echo(f"\n📁 Файловая структура:")
    click.echo(f"  - Папок найдено: {report_data['files_stats']['total_directories']}")
    click.echo(f"  - Всего файлов: {report_data['files_stats']['total_files']}")
    click.echo(f"  - Из них Markdown-файлов: {report_data['files_stats']['total_markdown_files']}")
    
    # Покрытие результатов обучения
    o_stats = report_data['outcomes_stats']
    click.echo(f"\n🎯 Покрытие результатов обучения ({o_stats['coverage_percentage']}%):")
    if o_stats['total_outcomes'] == 0:
        click.secho("  - Список результатов в course.yaml пуст или отсутствует", fg='yellow')
    else:
        click.echo(f"  - Всего результатов: {o_stats['total_outcomes']}")
        click.echo(f"  - Охвачено: {len(o_stats['covered_outcomes'])}")
        for o in o_stats['covered_outcomes']:
            click.secho(f"    [+] {o}", fg='green')
        click.echo(f"  - Не охвачено: {len(o_stats['uncovered_outcomes'])}")
        for o in o_stats['uncovered_outcomes']:
            click.secho(f"    [-] {o}", fg='red')
            
    # Отправка события xAPI
    try:
        extensions = {
            'https://example.edu/xapi/extensions/total-files': report_data['files_stats']['total_files'],
            'https://example.edu/xapi/extensions/total-markdown-files': report_data['files_stats']['total_markdown_files'],
            'https://example.edu/xapi/extensions/total-directories': report_data['files_stats']['total_directories'],
            'https://example.edu/xapi/extensions/total-outcomes': o_stats['total_outcomes'],
            'https://example.edu/xapi/extensions/covered-outcomes': o_stats['covered_outcomes'],
            'https://example.edu/xapi/extensions/uncovered-outcomes': o_stats['uncovered_outcomes'],
            'https://example.edu/xapi/extensions/coverage-percentage': o_stats['coverage_percentage'],
            'https://example.edu/xapi/extensions/is-valid': report_data['is_valid'],
        }
        stmt = generate_xapi_statement(
            verb_id='http://activitystrea.ms/schema/1.0/progress',
            verb_display='сформировал отчет',
            course_title=report_data['course_title'],
            course_path=course_dir,
            success=report_data['is_valid'],
            extensions=extensions
        )
        send_xapi_statement(stmt)
    except Exception as e:
        click.echo(f"Предупреждение: не удалось залогировать xAPI событие: {e}", err=True)