run:
	python src/main.py

lint:
	isort src && flake8 src
