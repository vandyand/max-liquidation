class Item:
    def __init__(self, name, price, url):
        self.name = name
        self.price = price
        self.url = url

    def __repr__(self):
        return f"Item(name={self.name}, price={self.price}, url={self.url})"


class Listing:
    def __init__(self, title, url):
        self.title = title
        self.url = url
        self.items = []  # List of items associated with this listing

    def add_item(self, item):
        self.items.append(item)

    def __repr__(self):
        return f"Listing(title={self.title}, url={self.url}, items={self.items})"

