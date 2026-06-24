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

