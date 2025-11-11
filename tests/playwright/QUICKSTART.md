# Playwright Framework - Quick Start Guide

## 🚀 Run Tests in 3 Steps

### Step 1: Start the Application
```bash
cd /Users/ginka/Documents/ai-cooking-assistant
source venv/bin/activate
python ai_app/app.py
```
Application should be running at: `http://127.0.0.1:5000`

### Step 2: Open New Terminal & Activate Environment
```bash
cd /Users/ginka/Documents/ai-cooking-assistant
source venv/bin/activate
```

### Step 3: Run Tests
```bash
# Run all Playwright tests
pytest tests/playwright/ -v

# Run specific test file
pytest tests/playwright/test_functional_scenarios.py -v

# Run one test class
pytest tests/playwright/test_functional_scenarios.py::TestBasicFunctionality -v
```

## 📊 What You'll See

- Browser will open automatically (Chrome)
- Tests will interact with the cooking assistant
- You'll see real-time test execution
- Results display in terminal with ✓ or ✗

## 🎯 Quick Test Examples

### Run Fast Tests Only (Skip Slow Ones)
```bash
pytest tests/playwright/ -m "not slow" -v
```

### Run With Detailed Output
```bash
pytest tests/playwright/ -v -s
```

### Generate HTML Report
```bash
pytest tests/playwright/ --html=test-results/report.html --self-contained-html
```

## 📁 Framework Structure

```
tests/playwright/
├── pages/                        # Page Object Model
│   ├── base_page.py             # Common functionality
│   └── cooking_assistant_page.py # App-specific actions
├── conftest.py                   # Test configuration & fixtures
├── test_functional_scenarios.py  # 15+ functional tests
├── test_ui_interactions.py       # 8+ UI/UX tests
├── README.md                     # Full documentation
└── QUICKSTART.md                 # This file
```

## ✅ What's Tested

- ✓ Recipe suggestions based on ingredients
- ✓ Allergy detection and warnings
- ✓ Dietary restrictions (vegetarian, vegan, gluten-free)
- ✓ Edge cases (empty input, special characters)
- ✓ UI interactions (forms, buttons, validation)
- ✓ Performance (response times)
- ✓ Accessibility basics

## 🐛 Troubleshooting

**Tests fail immediately?**
- Make sure Flask app is running on port 5000
- Check virtual environment is activated

**Timeout errors?**
- AI responses can be slow; this is expected
- Tests have 15-30 second timeouts built in

**Browser doesn't open?**
- Run: `playwright install chromium`
- Check Playwright version: `playwright --version`

## 📈 Expected Results

- **Total tests**: 20+
- **Execution time**: 3-5 minutes (with AI response delays)
- **Pass rate**: Depends on AI availability and application state

---

**Ready to run?** Execute Step 1 above!
