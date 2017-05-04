venv_dir=local/venv
python3=python3.5

check: $(venv_dir)/packages-installed
	$(venv_dir)/bin/pytest -v --tb=native $(pytest_args) tests

$(venv_dir)/packages-installed: Makefile requirements-tests.txt setup.py
	test -d $(venv_dir) || $(python3) -m venv $(venv_dir)
	$(venv_dir)/bin/pip install -U pip
	$(venv_dir)/bin/pip install -r requirements-tests.txt
	$(venv_dir)/bin/pip install -e .
	touch $@
