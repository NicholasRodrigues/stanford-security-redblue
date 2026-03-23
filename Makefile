.PHONY: install test demo report clean

install:
	pip install -e ".[dev]"

test:
	pytest tests/unit tests/integration -v --tb=short

test-unit:
	pytest tests/unit -v --tb=short

demo:
	python -m src.demo attack --live

report:
	python -m src.demo report

clean:
	rm -rf data/results/*.png data/results/*.pdf data/results/*.json data/results/*.md
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
