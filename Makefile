# Makefile for wave-visualizer development

.PHONY: install install-dev setup-dev format lint type-check security all-checks test test-cov test-fast pre-commit pre-commit-install clean build docs dev-check ci-check quick release-check build-demo build-demo-deps test-demo

# Installation targets
install:
	pip install -e .

install-dev: 
	pip install -e ".[dev,test,image-export]"

setup-dev: install-dev pre-commit-install
	@echo "Development environment setup complete!"

# Code quality targets
format:
	black wave_visualizer tests example_visualizations
	isort wave_visualizer tests example_visualizations

lint:
	flake8 wave_visualizer tests
	pydocstyle wave_visualizer

type-check:
	mypy wave_visualizer

security:
	bandit -r wave_visualizer -f json -o bandit-report.json
	bandit -r wave_visualizer

all-checks: format lint type-check security
	@echo "All quality checks passed!"

# Test targets
test:
	pytest

test-cov:
	pytest --cov=wave_visualizer --cov-report=html --cov-report=term-missing

test-fast:
	pytest -m "not slow"

# Pre-commit targets
pre-commit:
	pre-commit run --all-files

pre-commit-install:
	pre-commit install

# Build targets
clean:
	rm -rf build/ dist/ *.egg-info/ __pycache__/
	rm -rf wave_visualizer_demo_dist/ wave_visualizer_demo_package/
	rm -f wave_visualizer_demo.exe wave_visualizer_demo
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:
	python -m build

# Demo executable targets
build-demo-deps:
	pip install pyinstaller>=5.13.0
	@echo "Demo build dependencies installed"

build-demo: build-demo-deps clean
	python build_executable.py
	@echo "Demo executable built successfully!"
	@echo "Package location: wave_visualizer_demo_package/"

test-demo:
	@echo "Testing demo executable..."
	@if [ -f "wave_visualizer_demo_package/wave_visualizer_demo.exe" ]; then \
		echo "Windows executable found"; \
	elif [ -f "wave_visualizer_demo_package/wave_visualizer_demo" ]; then \
		echo "Unix executable found"; \
		echo "Making executable..."; \
		chmod +x wave_visualizer_demo_package/wave_visualizer_demo; \
	else \
		echo "No executable found. Run 'make build-demo' first."; \
		exit 1; \
	fi
	@echo "Demo executable is ready for testing"

# Documentation
docs:
	@echo "Documentation available in:"
	@echo "  - README.md (Quick start)"
	@echo "  - documentation.txt (Comprehensive reference)"

# Development workflow targets
dev-check: format lint type-check test-fast
	@echo "Development checks completed!"

ci-check: all-checks test
	@echo "CI checks completed!"

quick: format test-fast
	@echo "Quick development check completed!"

release-check: all-checks test build build-demo
	@echo "Release checks completed!"
	@echo "Ready for distribution!" 