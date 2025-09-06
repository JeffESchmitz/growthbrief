.PHONY: install test cov lint fmt

install:
	python -m pip install -U pip
	pip install -r requirements.txt

test:
	pytest -q

cov:
	pytest --cov=src/growthbrief --cov-report=term-missing

lint:
	python -m pyflakes src || true

fmt:
	python -m autopep8 -r -i src tests || true
