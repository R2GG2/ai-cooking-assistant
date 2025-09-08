import os
import re
from openpyxl import Workbook

UNIT_TEST_DIR = "tests/unit"
EXPORT_PATH = "docs/unit_test_cases.xlsx"

def extract_test_cases():
    cases = []
    for root, _, files in os.walk(UNIT_TEST_DIR):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    lines = f.readlines()
                    for idx, line in enumerate(lines):
                        if line.strip().startswith("def test_"):
                            name = re.findall(r"def\s+(test_[a-zA-Z0-9_]+)", line)[0]
                            cases.append([file, name, idx + 1])
    return cases

def write_to_excel(cases):
    wb = Workbook()
    ws = wb.active
    ws.title = "Unit Test Cases"
    ws.append(["Filename", "Test Case Name", "Line Number"])

    for case in cases:
        ws.append(case)

    os.makedirs(os.path.dirname(EXPORT_PATH), exist_ok=True)
    wb.save(EXPORT_PATH)
    print(f"Exported {len(cases)} unit test cases to {EXPORT_PATH}")

if __name__ == "__main__":
    test_cases = extract_test_cases()
    write_to_excel(test_cases)
