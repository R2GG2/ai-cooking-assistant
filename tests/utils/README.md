# Test Utilities

Utility scripts for test management and reporting.

## 📋 Scripts

### `export_test_cases.py`

Exports all test cases (Selenium + Unit) to a formatted Excel workbook.

**Usage:**
```bash
python tests/utils/export_test_cases.py
```

**Output:**
- File: `tests/selenium/reports/All_Test_Cases.xlsx`
- Sheets:
  - `Summary` - Total test counts
  - `Selenium Tests` - All Selenium test cases
  - `Unit Tests` - All unit test cases

**Features:**
- Automatically discovers all `test_*.py` files
- Extracts test names, docstrings, and line numbers
- Professional Excel formatting with headers
- Sorted alphabetically by file

**Requirements:**
```bash
pip install openpyxl
```

## 🔧 Adding New Utilities

Place new test-related utility scripts in this directory:

```
tests/utils/
├── export_test_cases.py
├── your_new_utility.py
└── README.md
```

**Guidelines:**
- Use descriptive names
- Include docstrings
- Add usage examples to this README
- Follow project code style

---

**Location:** `/tests/utils/`
**Purpose:** Centralized test utilities
