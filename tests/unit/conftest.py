import pytest
from inventory import Inventory

@pytest.fixture
def qa_inventory():
    inv = Inventory()
    inv.load_from_file("my_inventory.json")
    return inv
