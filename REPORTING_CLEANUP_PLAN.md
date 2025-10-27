# Reporting Architecture Cleanup Plan

## Current State Analysis

### 📁 Report Directories (5 locations!)

1. **`/reports/`** - Root reports folder
   - `assets/` - CSS/styling files
   - `screenshots/` - Old test screenshots
   - `selenium_failures/` - Empty
   - `selenium_report.html` (Oct 20) - OLD
   - `test_report.html` (Oct 23) - OLD
   - `flask_server.log` - OLD
   - `index.html` - OLD

2. **`/tests/reports/`** - EMPTY (should be deleted)

3. **`/tests/selenium/reports/`** - ✅ Current active folder
   - `final_beautiful_report.html` ← Our new report!
   - `ai_responses.jsonl` - AI response log
   - `flask_server.log` - Current
   - `screenshots/` - Current test screenshots
   - `index.html` - Auto-generated
   - `report_latest.html` - Auto-generated

4. **`/test_results/`** - Old JSON results
   - `test_results.json` (Aug 21) - VERY OLD

5. **`/test_results_json/`** - Recent JSON
   - `test_feedback.json` (Oct 27) - Current

### 📄 Export Scripts (3 files!)

1. **`export_selenium_test_cases.py`** (root)
   - Purpose: Export Selenium tests to Excel
   - Output: `Selenium_Test_Cases.xlsx`

2. **`export_unit_test_cases.py`** (root)
   - Purpose: Export unit tests to Excel
   - Output: `docs/unit_test_cases.xlsx`

3. **`tests/selenium/export_selenium_report.py`**
   - Purpose: Generate HTML from JSON using `logic/report_generator.py`
   - Output: Custom HTML reports
   - Status: Uses old reporting system

---

## 🎯 Unified Architecture Plan

### **Single Reports Location**
```
tests/selenium/reports/
├── final_beautiful_report.html  ← Main HTML report (pytest-html)
├── ai_responses.jsonl            ← AI response log
├── flask_server.log              ← Flask startup log
├── screenshots/                  ← Test screenshots
└── assets/                       ← CSS/styling (moved from root)
```

### **Export Scripts Location**
```
tests/utils/
├── export_test_cases.py          ← Unified Excel export
└── README.md                     ← Documentation
```

---

## 📋 Cleanup Actions

### Phase 1: Consolidate Report Folders

1. ✅ **Keep**: `/tests/selenium/reports/` as the ONLY reports folder

2. **Move assets**:
   ```bash
   mv reports/assets/ tests/selenium/reports/assets/
   ```

3. **Archive old reports** (don't delete in case needed):
   ```bash
   mkdir tests/selenium/reports/archive
   mv reports/*.html tests/selenium/reports/archive/
   ```

4. **Delete**:
   - `/reports/` (after moving assets)
   - `/tests/reports/` (empty)
   - `/test_results/` (old)
   - `/test_results_json/` (if not needed)

### Phase 2: Consolidate Export Scripts

1. **Create unified export script**:
   - Merge `export_selenium_test_cases.py` + `export_unit_test_cases.py`
   - New location: `tests/utils/export_test_cases.py`
   - Single command to export both

2. **Deprecate**:
   - `tests/selenium/export_selenium_report.py` - No longer needed (pytest-html does this)
   - `logic/report_generator.py` - Keep for now, may be useful for custom reports

3. **Delete**:
   - Root `export_selenium_test_cases.py`
   - Root `export_unit_test_cases.py`

### Phase 3: Update References

1. **Update `.gitignore`**:
   ```
   # Reports
   tests/selenium/reports/*.html
   tests/selenium/reports/*.json
   tests/selenium/reports/*.jsonl
   tests/selenium/reports/screenshots/
   !tests/selenium/reports/assets/

   # Old (to be removed)
   /reports/
   /test_results/
   /test_results_json/
   ```

2. **Update documentation**:
   - Add `tests/selenium/reports/README.md`
   - Document how to generate reports
   - Document export scripts

---

## 🎯 Final Structure

```
ai-cooking-assistant/
├── tests/
│   ├── selenium/
│   │   ├── reports/           ← SINGLE reports location
│   │   │   ├── assets/        ← Styling
│   │   │   ├── screenshots/   ← Test screenshots
│   │   │   ├── archive/       ← Old reports
│   │   │   ├── final_beautiful_report.html
│   │   │   ├── ai_responses.jsonl
│   │   │   └── flask_server.log
│   │   ├── conftest.py
│   │   └── report_hooks.py    ← Consolidated reporting
│   ├── unit/
│   └── utils/                 ← NEW
│       ├── export_test_cases.py
│       └── README.md
├── logic/
│   └── report_generator.py    ← Keep for custom reports
└── conftest.py                ← Registers report_hooks

❌ DELETED:
├── reports/                   ← OLD root folder
├── test_results/              ← OLD JSON
├── test_results_json/         ← Duplicate
├── export_selenium_test_cases.py  ← Moved
└── export_unit_test_cases.py      ← Moved
```

---

## ✅ Benefits

1. **Single Source of Truth** - All reports in one place
2. **Clean Root Directory** - No clutter
3. **Clear Organization** - Tests own their reports
4. **Easy Maintenance** - One location to manage
5. **Git-Friendly** - Clear ignore patterns

---

## 🚀 Execution Order

1. Create `tests/utils/` directory
2. Create unified export script
3. Move assets folder
4. Archive old HTML reports
5. Delete old directories
6. Update .gitignore
7. Create documentation
8. Verify all references work
