import sys
import click
from course_cli.init import init_course_structure
from course_cli.validate import validate_course_structure


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
    else:
        click.echo("❌ Найдены ошибки:")
        for err in report['errors']:
            click.echo(f"  - {err}")
        sys.exit(1)

@main.command()
def report():
    """Генерация отчета и отправка xAPI событий."""
    click.echo("Формирование отчета...")
    # Эту часть будет делать Puslore