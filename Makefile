.PHONY: help
help:
	@echo "Available commands:"
	@awk -F ':.*#' '/^[a-zA-Z0-9_-]+:/ { printf "  %-15s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

env:  # Make virtual environment
	python3.10 -m venv .venv

requirements:  # Capture package dependencies
	pip freeze > requirements.txt

install:  # Install packages
	pip install -r requirements.txt

test:  # Run unit tests
	python -m pytest

test-cov:  # Run unit tests and record code coverage
	python -m pytest --cov --cov-report=html:coverage_re --cov-config=./tests/.coveragerc
	echo 'http://localhost:63342/clf_backend/~coverage_re/index.html'

tailwind:  # Run tailwind for development
	python ./manage.py tailwind start

build:  # Run build commands for tailwind and static files
	python ./manage.py tailwind build
	python ./manage.py collectstatic
