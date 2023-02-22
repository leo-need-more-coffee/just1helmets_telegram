import logging
import sqlite3
import json
import logging
import secrets
import random
from hashlib import sha256, md5

db_name = "data.db"


class ProductList:
    def __init__(self, products):
        self.products = products

    def __getitem__(self, i):
        return self.products[i]

    def __len__(self):
        return len(self.products)


class Product:
    def __init__(self, id:int, name:str=None, description:str=None, image:str=None, price:int=None, categories:int=0, sizes:list = []):
        self.id:int = id
        self.name:str = name
        self.description:str = description
        self.image:str = image
        self.price:int = price
        self.categories:int = categories
        self.sizes:list = sizes

    def save(self):
        conn = sqlite3.connect(db_name)
        conn.execute("UPDATE products SET id = ?, name = ?, description = ?, image = ?, price = ?, categories = ?, sizes = ? WHERE id == ?",
            [self.id, self.name, self.description, self.image, self.price, self.categories, json.dumps(self.sizes)])
        conn.commit()
        conn.close()

    def delete(self):
        conn = sqlite3.connect(db_name)
        conn.execute("DELETE FROM products\
                WHERE id == ?", [self.id])
        conn.commit()
        conn.close()

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image": self.image,
            "price": self.price,
            "categories": self.categories,
            "sizes": self.sizes,
        }

    def add(name:str=None, description:str=None, image:str=None, price:int=None, categories:int=0, sizes:list = []):
        items = Product.all()
        id = max([el.id for el in items]) + 1 if len(items) > 0 else 0

        conn = sqlite3.connect(db_name)
        conn.execute("INSERT INTO products (id, name, description, image, price, categories, sizes) \
            VALUES (?, ?, ?, ?, ?, ?, ?)", (id, name, description, image, price, categories, json.dumps(sizes)))
        conn.commit()
        conn.close()
        return Product(id, name, description, image, price, categories, sizes)

    def get(id):
        conn = sqlite3.connect(db_name)
        cursor = conn.execute("SELECT id, name, description, image, price, categories, sizes FROM products WHERE id==?", [id])
        rows = cursor.fetchall()
        if len(rows) == 0:
            return None
        id, name, description, image, price, categories, sizes = rows[0]
        row = Product(id, name, description, image, price, categories, json.loads(sizes))
        conn.close()
        return row

    def get_by_category(category_id) -> ProductList:
        conn = sqlite3.connect(db_name)
        cursor = conn.execute("SELECT id, name, description, image, price, categories, sizes FROM products WHERE categories == ?", [category_id])
        a = cursor.fetchall()
        rows = []
        for el in a:
            id, name, description, image, price, categories, sizes = el
            rows.append(Product(id, name, description, image, price, categories, json.loads(sizes)))
        conn.close()
        return ProductList(rows)


    def all() -> ProductList:
        conn = sqlite3.connect(db_name)
        cursor = conn.execute("SELECT id, name, description, image, price, categories, sizes FROM products")
        a = cursor.fetchall()
        rows = []
        for el in a:
            id, name, description, image, price, categories, sizes = el
            rows.append(Product(id, name, description, image, price, categories, json.loads(sizes)))
        conn.close()
        return ProductList(rows)


class CategoryList:
    def __init__(self, categories):
        self.categories = categories

    def __getitem__(self, i):
        return self.categories[i]

    def __len__(self):
        return len(self.categories)


class Category:
    def __init__(self, id:int, name:str=None):
        self.id:int = id
        self.name:str = name

        
    def save(self):
        conn = sqlite3.connect(db_name)
        conn.execute("UPDATE categories SET id = ?, name = ? WHERE id == ?",
            [self.id, self.name])
        conn.commit()
        conn.close()

    def delete(self):
        conn = sqlite3.connect(db_name)
        conn.execute("DELETE FROM categories\
                WHERE id == ?", [self.id])
        conn.commit()
        conn.close()

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
        }

    def add(id:int, name:str=None):
        conn = sqlite3.connect(db_name)
        conn.execute("INSERT INTO categories (id, name) \
            VALUES (?, ?)", (id, name))
        conn.commit()
        conn.close()
        return Category(id, name)

    def get(id):
        conn = sqlite3.connect(db_name)
        cursor = conn.execute("SELECT id, name FROM categories WHERE id==?", [id])
        rows = cursor.fetchall()
        if len(rows) == 0:
            return None
        id, name = rows[0]
        row = Product(id, name)    
        conn.close()
        return row

    def all() -> CategoryList:
        conn = sqlite3.connect(db_name)
        cursor = conn.execute("SELECT id, name FROM categories")
        a = cursor.fetchall()
        rows = []
        for el in a:
            id, name = el
            rows.append(Category(id, name))
        conn.close()
        return CategoryList(rows)


