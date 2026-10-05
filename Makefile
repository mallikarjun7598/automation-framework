# Makefile — convenience targets for the automation framework.
# Run `make help` to see everything.

PY := .venv/bin/python
PIP := .venv/bin/pip
PYTHON312 := /opt/homebrew/bin/python3.12

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Create the virtualenv and install all dependencies + browser
	$(PYTHON312) -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PY) -m playwright install chromium

.PHONY: app
app: ## Run the storefront app locally on http://127.0.0.1:5001
	$(PY) -m app.server

.PHONY: lint
lint: ## Run ruff static analysis
	$(PY) -m ruff check app tests

.PHONY: fmt
fmt: ## Auto-fix lint issues where possible
	$(PY) -m ruff check --fix app tests

.PHONY: test-web
test-web: ## Run web tests (Playwright); auto-starts the app
	$(PY) -m pytest tests/web -m web --browser chromium \
		--html=reports/web-report.html --self-contained-html

.PHONY: test-mobile
test-mobile: ## Run mobile tests (skips unless Appium server + device present)
	$(PY) -m pytest tests/mobile -m mobile \
		--html=reports/mobile-report.html --self-contained-html

.PHONY: test-mobile-real
test-mobile-real: ## Run mobile tests for real (requires Appium + device/emulator)
	$(PY) -m pytest tests/mobile -m mobile --appium \
		--html=reports/mobile-report.html --self-contained-html

.PHONY: test
test: ## Run the entire suite (web + mobile) with a combined report
	$(PY) -m pytest --browser chromium \
		--html=reports/report.html --self-contained-html

.PHONY: ci
ci: ## Run the full local CI pipeline mock-up
	./ci/run-ci.sh

.PHONY: clean
clean: ## Remove caches and generated reports
	rm -rf .pytest_cache **/__pycache__ reports/*.html
