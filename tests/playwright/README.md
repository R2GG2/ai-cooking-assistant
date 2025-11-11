# Playwright Test Framework - AI Cooking Assistant

## Overview

This is a professional-grade Playwright test automation framework for the AI Cooking Assistant application. The framework demonstrates **best practices in test automation architecture**, including Page Object Model (POM) design, comprehensive test coverage, and maintainable test code.

## Framework Architecture

### Page Object Model (POM)

The framework follows the Page Object Model design pattern, which provides:
- **Separation of concerns**: Test logic separated from page interactions
- **Reusability**: Page objects can be used across multiple tests
- **Maintainability**: UI changes only require updates in one place
- **Readability**: Tests read like user stories

```
tests/playwright/
├── pages/
│   ├── base_page.py              # Base class with common functionality
│   └── cooking_assistant_page.py  # Page object for AI Cooking Assistant
├── conftest.py                    # Pytest fixtures and test configuration
├── test_functional_scenarios.py   # Functional and feature tests
├── test_ui_interactions.py        # UI element and interaction tests
└── README.md                      # This file
```

### Test Categories

#### 1. Functional Tests (`test_functional_scenarios.py`)
- **Basic Functionality**: Page loading, recipe suggestions, equipment queries
- **Allergy & Dietary Concerns**: Allergy detection, vegetarian/vegan, gluten-free
- **Edge Cases**: Empty pantry, vague questions, multiple constraints
- **Response Quality**: Instruction completeness, response length validation

#### 2. UI Interaction Tests (`test_ui_interactions.py`)
- **UI Elements**: Input fields, buttons, response areas
- **Form Validation**: Empty submissions, special characters
- **Responsiveness**: Response times, consecutive queries
- **Accessibility**: Page titles, labels, ARIA attributes
- **Visual Regression**: Screenshot capture for baseline comparison

## Setup Instructions

### Prerequisites
- Python 3.9+
- Virtual environment (recommended)
- Playwright browsers installed

### Installation

1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers** (if not already installed):
   ```bash
   playwright install chromium
   ```

4. **Start the application** (in a separate terminal):
   ```bash
   python app.py  # or your application start command
   ```
   The application should be running at `http://127.0.0.1:5000`

## Running Tests

### Run All Tests
```bash
pytest tests/playwright/ -v
```

### Run Specific Test File
```bash
pytest tests/playwright/test_functional_scenarios.py -v
```

### Run Specific Test Class
```bash
pytest tests/playwright/test_functional_scenarios.py::TestBasicFunctionality -v
```

### Run Specific Test
```bash
pytest tests/playwright/test_functional_scenarios.py::TestBasicFunctionality::test_page_loads_successfully -v
```

### Run Tests in Headless Mode
Edit `conftest.py` and change:
```python
browser = playwright_instance.chromium.launch(headless=True)
```

### Run with HTML Report
```bash
pytest tests/playwright/ --html=test-results/report.html --self-contained-html
```

### Run Tests with Markers
```bash
# Run only slow tests
pytest tests/playwright/ -m slow -v

# Run only visual tests
pytest tests/playwright/ -m visual -v

# Skip slow tests
pytest tests/playwright/ -m "not slow" -v
```

## Test Configuration

### Playwright Browser Options
Located in `conftest.py`:
- **Headless mode**: Run without opening browser window
- **Slow motion**: Slow down operations for debugging (currently 500ms)
- **Video recording**: Capture video of test execution
- **Viewport size**: Default 1280x720

### Timeouts
- **Default selector timeout**: 10 seconds
- **AI response timeout**: 15-30 seconds (configurable per test)
- **Page load timeout**: Default Playwright timeout

## Test Data Strategy

Tests use **inline test data** for simplicity and readability:
- Ingredient combinations
- Dietary restrictions
- Allergy information
- Edge case scenarios

For production frameworks, consider:
- External data files (JSON, CSV)
- Data-driven testing with pytest.mark.parametrize
- Faker library for generated test data

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Install dependencies
  run: |
    pip install -r requirements.txt
    playwright install chromium

- name: Run Playwright tests
  run: pytest tests/playwright/ --html=report.html
```

### Key CI/CD Considerations
- Set `headless=True` for CI environments
- Use Docker containers for consistent environment
- Save test artifacts (screenshots, videos, reports)
- Implement retry logic for flaky tests

## Extending the Framework

### Adding New Page Objects
1. Create new file in `tests/playwright/pages/`
2. Inherit from `BasePage`
3. Define locators as class constants
4. Implement page-specific methods

### Adding New Tests
1. Import the appropriate page object
2. Use `cooking_assistant_page` fixture for automatic setup
3. Follow AAA pattern (Arrange, Act, Assert)
4. Add descriptive docstrings
5. Use appropriate pytest markers

### Custom Fixtures
Add new fixtures in `conftest.py`:
```python
@pytest.fixture
def test_data():
    return {"ingredient": "chicken", "equipment": "oven"}
```

## Best Practices Demonstrated

✅ **Page Object Model** - Separation of test logic and UI interactions
✅ **DRY Principle** - Reusable page objects and fixtures
✅ **Clear Test Names** - Self-documenting test methods
✅ **Comprehensive Coverage** - Happy path, edge cases, negative scenarios
✅ **Maintainable Structure** - Organized by feature and concern
✅ **Assertions with Context** - Meaningful error messages
✅ **Test Independence** - Each test can run standalone
✅ **Pytest Markers** - Categorize and filter tests
✅ **Screenshot Capture** - Visual regression testing foundation
✅ **Performance Testing** - Response time validation

## Troubleshooting

### Tests Fail with "Element not found"
- Verify application is running at `http://127.0.0.1:5000`
- Check if locators match current UI
- Increase timeout values if AI is slow

### Tests Timeout Waiting for AI Response
- AI responses can be slow; increase timeout in individual tests
- Check network connectivity and API keys
- Verify application logs for errors

### Browser Doesn't Launch
- Run `playwright install chromium`
- Check Playwright version: `playwright --version`
- Try different browser: `firefox` or `webkit`

## Metrics & Reporting

### Coverage Areas
- ✅ Core functionality (ingredient queries, recipe suggestions)
- ✅ Dietary restrictions (allergies, vegetarian, gluten-free)
- ✅ Edge cases (empty input, special characters, vague queries)
- ✅ UI interactions (form validation, buttons, response display)
- ✅ Performance (response times, consecutive queries)
- ✅ Accessibility (basic ARIA and semantic HTML checks)

### Test Execution Time
- Fast tests: < 5 seconds
- Standard tests: 5-15 seconds
- Slow tests (marked with `@pytest.mark.slow`): 15-30 seconds

## Framework Statistics

- **Total Test Files**: 2
- **Total Test Cases**: 20+
- **Page Objects**: 2 (Base + CookingAssistant)
- **Test Categories**: Functional, UI, Accessibility, Performance
- **Lines of Code**: ~600 (including documentation)

## Contact & Portfolio

**Framework Author**: Ginka - Senior QA Engineer
**Experience**: 12+ years in QA and test automation
**Specialties**: Test framework architecture, Playwright, Selenium, API testing

This framework demonstrates enterprise-level test automation practices suitable for startup and scale-up environments.

---

**Last Updated**: November 2025
**Playwright Version**: 1.54.0
**Python Version**: 3.9+
