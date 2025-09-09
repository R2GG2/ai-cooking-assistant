import pytest
from inventory import Inventory

def test_add_items(qa_inventory):
    qa_inventory.add_item("Test case suite", "QA Automation", 5)
    qa_inventory.add_item("Bug report", "Documentation", 1)
    items = [item["name"] for item in qa_inventory.items]
    assert "Test case suite" in items
    assert "Bug report" in items

def test_edit_item_quantity(qa_inventory):
    qa_inventory.add_item("Test case suite", "QA Automation", 5)
    qa_inventory.edit_item("Test case suite", 10)
    item = next(i for i in qa_inventory.items if i["name"] == "Test case suite")
    assert item["quantity"] == 10

def test_save_to_file(tmp_path):
    inv = Inventory()
    inv.add_item("Temporary item", "Temp", 1)
    file_path = tmp_path / "temp_inventory.json"
    inv.save_to_file(file_path)
    assert file_path.exists()
