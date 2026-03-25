.PHONY: install install-ui test demo report streamlit precompute clean

install:
	pip install -e ".[dev]"

install-ui:
	pip install -e ".[dev,ui]"

test:
	pytest tests/unit tests/integration -v --tb=short

test-unit:
	pytest tests/unit -v --tb=short

demo:
	python -m src.demo attack --live

report:
	python -m src.demo report

streamlit:
	streamlit run src/streamlit_app/app.py

precompute:
	python -m src.evaluation.precompute

clean:
	rm -rf data/results/*.png data/results/*.pdf data/results/*.json data/results/*.md
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
