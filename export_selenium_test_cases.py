import os
import ast
from openpyxl import Workbook

SELENIUM_DIR = "tests/selenium"
OUTPUT_FILE = "Selenium_Test_Cases.xlsx"

def extract_test_cases(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)
    
    test_cases = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            docstring = ast.get_docstring(node) or ""
            test_cases.append({
                "file": os.path.relpath(file_path, SELENIUM_DIR),
                "test_name": node.name,
                "description": docstring.strip()
            })
    return test_cases

def main():
    wb = Workbook()
    ws = wb.active
    ws.title = "Selenium Tests"
    ws.append(["Test File", "Test Function", "Description"])

    for root, _, files in os.walk(SELENIUM_DIR):
        for fname in files:
            if fname.endswith(".py") and not fname.startswith("conftest"):
                full_path = os.path.join(root, fname)
                test_cases = extract_test_cases(full_path)
                for tc in test_cases:
                    ws.append([tc["file"], tc["test_name"], tc["description"]])

    wb.save(OUTPUT_FILE)
    print(f"[✓] Exported Selenium test cases to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
