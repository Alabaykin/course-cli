VENV = venv
VENV_BIN = $(VENV)/bin
PYTHON_SYS = python3
PYTHON = $(VENV_BIN)/python
PIP = $(VENV_BIN)/pip

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

