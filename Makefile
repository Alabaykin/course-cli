VENV = venv
VENV_BIN = $(VENV)/bin
PYTHON_SYS = python3
PYTHON = $(VENV_BIN)/python
PIP = $(VENV_BIN)/pip

.PHONY: help setup test demo clean run-cli

.DEFAULT_GOAL := help

help:
	@echo "Доступные команды Course CLI:"
	@echo "  setup    Подготовить виртуальное окружение и установить CLI-утилиту"
	@echo "  run-cli  Запустить Course CLI (вывод справки)"
	@echo "  test     Запустить тесты (pytest)"
	@echo "  demo     Создать временный курс для проверки работы команды init"
	@echo "  clean    Очистить кэши, виртуальное окружение и временные файлы"

$(VENV):
	$(PYTHON_SYS) -m venv $(VENV)

setup: $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e .
test: setup
	$(PYTHON) -m pytest tests/

demo: setup
	@echo "Создаем тестовый курс во временной папке..."
	@rm -rf temp_demo
	@mkdir -p temp_demo
	@cd temp_demo && ../$(VENV_BIN)/course-cli init "Demo Course"
	@echo "Демонстрационный курс создан в папке temp_demo/"

clean:
	rm -rf $(VENV) .pytest_cache temp_demo *.egg-info course_cli.egg-info src/course_cli.egg-info


run-cli: setup
	$(VENV_BIN)/course-cli --help