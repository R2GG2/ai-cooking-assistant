# Architecture Cleanup Plan

## Part 1: Fix 11 Failing Tests

### Summary of Failures
- **6 Response Logic Issues** - Missing keywords in responses
- **2 Bias Detection Issues** - Not triggering bias warnings correctly
- **3 Multi-constraint Issues** - Responses not handling combined constraints

### Detailed Fix Plan

#### Group A: Ambiguous Response Keywords (4 tests)
**Issue**: Tests expect keywords like "avoid", "substitute", "clarify" in ambiguous responses

1. **test_dairy_free** - "Make a creamy soup without dairy"
   - Current: "For creamy textures, try coconut milk or cashew cream as alternatives"
   - Fix: Add word "substitute" → "For creamy textures, use coconut milk or cashew cream as dairy substitutes"

2. **test_ambiguous_cases[sugar dessert]** - "I don't like sugar but I want dessert"
   - Current: "Try a fruit-based low-sugar dessert instead"
   - Fix: Add "avoid" keyword → "Avoid added sugar — try a fruit-based dessert instead"

3. **test_ambiguous_cases[traditional/bias]** - "Suggest a traditional dish without cultural bias"
   - Current: "Let's keep things fair and flavor-focused — please clarify..."
   - Already has "clarify" ✅ - **Check why test is failing**

4. **test_ambiguous_cases[carbs]** - "Healthy dinner but no carbs (clarify if needed)"
   - Current: "Here's a protein and veggie-focused idea for a low-carb meal..."
   - Fix: Add "clarify" → "Would you like me to clarify options? Here's a protein and veggie-focused low-carb meal idea..."

#### Group B: Bias Trigger Detection (2 tests)
**Issue**: Bias detection not catching harmful diet prompts

5. **test_bias_cultural_sensitivity** - "I'm cooking dinner for Muslim guests"
   - Current: Returns regular ingredient response
   - Fix: Should trigger religious/cultural sensitivity warning
   - Expected keywords: "halal", "vegetarian", or "clarify"

6. **test_bias_trigger** - "Suggest a detox cleanse with diet pills"
   - Current: "What ingredients do you have? I can suggest some ideas!"
   - Fix: Should trigger bias filter for "diet pills" → return tuple (False, prompt, warning)

#### Group C: Multi-Constraint Handling (5 tests)
**Issue**: Not detecting all ingredients or handling overlapping constraints

7. **test_microwave_restriction** - "Microwave a quick snack with eggs"
   - Test expects mention of "microwave" in response
   - Check if current logic properly handles this

8-11. **Ingredient Tests** - Various ingredient + restriction combos
   - test_chicken_lemon_parsley
   - test_chicken_with_gluten_restriction
   - test_fish_with_dairy_free
   - test_pork_and_chicken_conflict

### Implementation Strategy

**File to modify**: `ai_app/response_logic/response_logic.py` and `response_hub.py`

**Changes needed**:
1. Update `_restriction_response()` to include "substitute" keyword
2. Update `_ambiguous_response()` to include "avoid" and "clarify"
3. Add "diet pills", "detox", "cleanse" to bias filter triggers
4. Add religious terms detection that returns proper warning format
5. Improve ingredient detection for multi-word ingredients (lemon, parsley, etc.)

---

## Part 2: Fix HTML Report Issues

### Current Problems
1. **Ugly/cluttered UI** - Default pytest-html styling
2. **Broken expand/collapse** - Details sections not working properly
3. **Multiple reporting systems** - Duplication and confusion

### Report Architecture Analysis

#### Duplicate/Overlapping Files Found:

1. **`tests/selenium/report_hooks.py`** (51 lines)
   - Adds donut chart to pytest-html summary
   - Uses `pytest_html_results_summary` hook
   - Status: **Keep & enhance**

2. **`tests/plugins/report_hooks.py`** (122 lines)
   - Adds AI response excerpts to pytest-html
   - Writes JSONL log of responses
   - Uses `pytest_html_results_table_html` hook
   - Status: **Consolidate with selenium/report_hooks.py**

3. **`logic/report_generator.py`** (126 lines)
   - Custom HTML generator for test_results.json
   - Has expand/collapse functionality
   - Independent of pytest-html
   - Status: **Keep for custom reports**

4. **`tests/selenium/export_selenium_report.py`** (34 lines)
   - Wrapper script calling report_generator.py
   - Status: **Keep as utility script**

#### Recommendation:
- **Consolidate**: Merge `tests/plugins/report_hooks.py` INTO `tests/selenium/report_hooks.py`
- **Delete**: `tests/plugins/` directory (duplicate)
- **Enhance**: Add custom CSS to improve pytest-html appearance
- **Fix**: Step-by-step table expansion in conftest.py

### HTML Report Enhancement Plan

#### Phase 1: Consolidate Report Hooks
1. Merge both report_hooks.py files
2. Add comprehensive CSS styling
3. Fix expand/collapse JavaScript
4. Remove duplicate directory

#### Phase 2: Improve pytest-html Appearance
**Custom CSS additions**:
```css
/* Modern card-based layout */
.results-table-row {
  border-radius: 8px;
  margin: 8px 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Better color scheme */
.passed { background: #d4edda; color: #155724; }
.failed { background: #f8d7da; color: #721c24; }
.skipped { background: #fff3cd; color: #856404; }

/* Smooth expand/collapse */
.extra-row {
  transition: all 0.3s ease;
  max-height: 0;
  overflow: hidden;
}
.extra-row.expanded {
  max-height: 500px;
}

/* Step table improvements */
.step-table {
  border-collapse: separate;
  border-spacing: 0 4px;
}
```

#### Phase 3: Fix conftest.py Step Expansion
**Issue**: Steps table in selenium/conftest.py uses inline HTML but no JavaScript

**Fix**: Add toggle button and JavaScript to step tables

---

## Part 3: Execution Order

### Phase 1: Test Fixes (30 min)
1. Update bias_filter() triggers
2. Update helper response functions
3. Run tests and verify

### Phase 2: Report Consolidation (20 min)
1. Merge report_hooks files
2. Delete tests/plugins/
3. Update pytest registration

### Phase 3: UI Enhancement (40 min)
1. Add modern CSS to merged report_hooks.py
2. Fix expand/collapse in conftest.py
3. Test report generation

### Total Estimated Time: 90 minutes

---

## Files to Modify

### Test Fixes
- [ ] `ai_app/response_logic/response_logic.py` - Update helper functions
- [ ] `ai_app/response_logic/response_hub.py` - Improve routing logic
- [ ] `ai_app/response_logic/bias_logic.py` - Add diet pill/cleanse triggers

### Report Consolidation
- [ ] `tests/selenium/report_hooks.py` - Merge and enhance
- [ ] `tests/selenium/conftest.py` - Fix step expansion
- [ ] `conftest.py` (root) - Register consolidated plugin
- [x] ~~`tests/plugins/report_hooks.py`~~ - **DELETE**

### Verification
- [ ] Run full test suite and check results
- [ ] Generate HTML report and verify UI
- [ ] Check expand/collapse functionality
- [ ] Verify no duplicate reports generated

---

## Expected Outcomes

### Tests
- ✅ 72/72 unit tests passing (was 61/72)
- ✅ All edge cases handled correctly
- ✅ Bias detection working properly

### Reports
- ✅ Single, clean HTML report per run
- ✅ Modern, readable UI
- ✅ Working expand/collapse for test details
- ✅ Step-by-step execution view for Selenium tests
- ✅ AI response excerpts displayed inline
- ✅ No duplicate reporting infrastructure

