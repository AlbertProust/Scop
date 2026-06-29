VENV_DIR = scop-env
PYTHON = python3
PIP = $(VENV_DIR)/bin/pip
ACTIVATE = . $(VENV_DIR)/bin/activate

.PHONY: setup install activate clean

setup: $(VENV_DIR)
	$(PYTHON) -m venv $(VENV_DIR)
	$(ACTIVATE) && $(PIP) install --upgrade pip
	$(ACTIVATE) && $(PIP) install glfw PyOpenGL numpy

$(VENV_DIR):
	$(PYTHON) -m venv $(VENV_DIR)

install: setup

activate:
	@echo "Run the following command to activate the virtualenv:"
	@echo "    source $(VENV_DIR)/bin/activate"

clean:
	rm -rf $(VENV_DIR)