import logging
import sqlite3
import json
import logging
import secrets
import random
from hashlib import sha256, md5

db_name = "data.db"


class Item:
    def __init__(self, id:int, user_id:int, product_id:int, size:str=None):
        self.id:int = id
        self.user_id:int = user_id
        self.product_id:int = product_id
        self.size:str = size

    def save(self):
        conn = sqlite3.connect(db_name)
        conn.execute("UPDATE carts SET id = ?, user_id = ?, product_id = ?, size = ? WHERE id == ?",
            [ self.id, self.user_id, self.product_id, self.size,  self.id])
        conn.commit()
        conn.close()

    def delete(self):
        conn = sqlite3.connect(db_name)
        conn.execute("DELETE FROM carts\
                WHERE id == ?", [self.id])
        conn.commit()
        conn.close()

    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "size": self.size,
        }

    def add(user_id:int, product_id:int, size:str=None):
        items = Item.all()
        id = max([el.id for el in items]) + 1 if len(items) > 0 else 0
        
        conn = sqlite3.connect(db_name)
        conn.execute("INSERT INTO carts (id, user_id, product_id, size) \
            VALUES (?, ?, ?, ?)", (id, user_id, product_id, size))
        conn.commit()
        conn.close()
        return Item(id, user_id, product_id, size)

    def get(id):
        conn = sqlite3.connect(db_name)
        cursor = conn.execute("SELECT id, user_id, product_id, size FROM carts WHERE id==?", [id])
        rows = cursor.fetchall()
        if len(rows) == 0:
            return None
        id, user_id, product_id, size = rows[0]
        row = Item(id, user_id, product_id, size)    
        conn.close()
        return row

    def get_by_product_id(user_id, product_id):
        conn = sqlite3.connect(db_name)
        cursor = conn.execute("SELECT id, user_id, product_id, size FROM carts WHERE user_id == ? AND product_id == ?", [user_id, product_id])
        a = cursor.fetchall()
        rows = []
        for el in a:
            id, user_id, product_id, size = el
            rows.append(Item(id, user_id, product_id, size))
        conn.close()
        return rows

    def get_cart(user_id):
        conn = sqlite3.connect(db_name)
        cursor = conn.execute("SELECT id, user_id, product_id, size FROM carts WHERE user_id == ?", [user_id])
        a = cursor.fetchall()
        rows = []
        for el in a:
            id, user_id, product_id, size = el
            rows.append(Item(id, user_id, product_id, size))
        conn.close()
        return rows

    def all():
        conn = sqlite3.connect(db_name)
        cursor = conn.execute("SELECT id, user_id, product_id, size FROM carts")
        a = cursor.fetchall()
        rows = []
        for el in a:
            id, user_id, product_id, size = el
            rows.append(Item(id, user_id, product_id, size))
        conn.close()
        return rows


class Cart:
    def __init__(self, user_id:int, items:list=[]):
        self.user_id:int = user_id
        self.items:list = items
    
    def add_product(self, product_id, size=None):
        item = Item.add(self.user_id, product_id, size)
        self.items = Item.get_cart(self.user_id)
        return self
    
    def json(self):
        return {
            "user_id": self.user_id,
            "items": [el.json() for el in self.items]
        }

    def delete_product(self, product_id):
        items = Item.get_by_product_id(self.user_id, product_id)
        items[-1].delete()
        self.items = Item.get_cart(self.user_id)

        return self
    
    def clear_cart(self):
        items = Item.get_cart(self.user_id)
        for item in items:
            item.delete()
        self.items = Item.get_cart(self.user_id)
        return self

    def get(user_id:int):
        items = Item.get_cart(user_id)
        return Cart(user_id, items)