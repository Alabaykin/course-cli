import click
from course_cli.init import init_course_structure
from pathlib import Path

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
def validate():
    """Проверка структуры и метаданных курса."""
    click.echo("Запуск проверок...")
    # Эту часть будет делать Puslore

@main.command()
def report():
    """Генерация отчета и отправка xAPI событий."""
    click.echo("Формирование отчета...")
    # Эту часть будет делать Puslore