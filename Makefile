PYTHON ?= python3

.PHONY: lint test build scan-self validate install-local

lint:
	$(PYTHON) -m ruff check .

test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

build:
	$(PYTHON) -m build

scan-self:
	$(PYTHON) scripts/scan_repo.py . | $(PYTHON) -m json.tool > /dev/null

validate: lint test build scan-self

install-local:
	$(PYTHON) -m pip install --force-reinstall .
