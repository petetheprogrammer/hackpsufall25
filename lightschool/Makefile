.PHONY: setup run collect

setup:
	python -m venv venv
	. venv/bin/activate && pip install -r pyproject.toml

run:
	python manage.py runserver 0.0.0.0:8000

collect:
	python manage.py collectstatic --noinput