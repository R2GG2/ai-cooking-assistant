from inventory import Inventory

# Step 1: Create a new inventory and add items
qa_inventory = Inventory()

# Try loading existing data from file first
qa_inventory.load_from_file("my_inventory.json")

# Add new items
qa_inventory.add_item("Test case suite", "QA Automation", 5)
qa_inventory.add_item("Bug report", "Documentation", 1)

# List current items
qa_inventory.list_items()

# Edit an item's quantity
qa_inventory.edit_item("Test case suite", 10)


# Save to file
qa_inventory.save_to_file("my_inventory.json")
