import json  # We'll need this later for file saving

class Inventory:
    def __init__(self):
        self.items = []

    def add_item(self, name, category, quantity):
        self.items.append({
            "name": name,
            "category": category,
            "quantity": quantity
        })

    def remove_item(self, name):
        self.items = [item for item in self.items if item["name"] != name]

    def list_items(self):
        for item in self.items:
            print(f"{item['name']} ({item['category']}): {item['quantity']}")

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.items, file)
        print(f"Inventory saved to '{filename}'.")

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                self.items = json.load(file)
            print(f"Inventory loaded from '{filename}'.")
        except:
            print(f"Couldn't load file '{filename}'. Starting with an empty inventory.")

    def edit_item(self, name, new_quantity):
        for item in self.items:
            if item["name"] == name:
                item["quantity"] = new_quantity
                print(f"Updated '{name}' quantity to {new_quantity}.")
                return
        print(f"Item '{name}' not found. Nothing updated.")
