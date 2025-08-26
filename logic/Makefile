# Makefile for ai-cooking-assistant
# Usage: make test-ui / test-all / test-playwright

PYTEST=pytest
REPORT_DIR=reports
TS=$(shell date +"%Y%m%d-%H%M%S")

# Default target
all: test-all

# Run only Selenium UI tests
test-ui:
	BASE_URL=http://127.0.0.1:5000 \
	$(PYTEST) selenium_tests/ \
	  --html=selenium_tests/reports/selenium_$(TS).html \
	  --self-contained-html

# Run full suite (unit + selenium)
test-all:
	BASE_URL=http://127.0.0.1:5000 \
	$(PYTEST) \
	  --html=$(REPORT_DIR)/test_suite_$(TS).html \
	  --self-contained-html

# Run Playwright tests (optional, when browsers installed)
test-playwright:
	$(PYTEST) -m playwright playwright_tests/ \
	  --html=playwright_tests/reports/playwright_$(TS).html \
	  --self-contained-html
