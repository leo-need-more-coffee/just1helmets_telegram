from hashlib import sha256, md5
import secrets
import datetime
from traceback import print_tb
import requests
import shutil
from io import StringIO
import json

from flask import Flask, jsonify, request, redirect
from flask import make_response
from flask import send_file, render_template
import sys, os
import db
from cart import Cart, Item

global app
app = Flask(__name__, static_folder='', template_folder='')


class Cart_route:
    @app.route("/users/<int:user_id>/cart/", methods=["GET"])
    def get_cart(user_id):
        cart = Cart.get(user_id)
        return make_response(jsonify({'cart': cart.json()}), 200)

    @app.route("/users/<int:user_id>/cart/products/<int:product_id>", methods=["POST"])
    def add_product(user_id, product_id):
        cart = Cart.get(user_id)
        cart.add_product(product_id)
        return make_response(jsonify({'response': 'ok'}), 200)

    @app.route("/users/<int:user_id>/cart/products/<int:product_id>/size/<string:size>", methods=["POST"])
    def add_product_with_size(user_id, product_id, size):
        cart = Cart.get(user_id)
        cart.add_product(product_id, size)
        return make_response(jsonify({'response': 'ok'}), 200)

    @app.route("/items/<int:item_id>/size/<string:size>", methods=["PUT"])
    def change_item_size(item_id, size):
        item = Item.get(item_id)
        item.size = size
        item.save()
        return make_response(jsonify({'response': 'ok'}), 200)
    

    @app.route("/items/<int:item_id>", methods=["GET"])
    def get_item(item_id):
        item = Item.get(item_id)
        return make_response(jsonify({'item': item.json()}), 200)

    @app.route("/items/<int:item_id>", methods=["DELETE"])
    def change_size(item_id):
        item = Item.get(item_id)
        item.delete()
        return make_response(jsonify({'response': 'ok'}), 200)

    @app.route("/users/<int:user_id>/cart/products/<int:product_id>", methods=["DELETE"])
    def delete_product(user_id, product_id):
        cart = Cart.get(user_id)
        cart.delete_product(product_id)
        return make_response(jsonify({'response': 'ok'}), 200)

    @app.route("/users/<int:user_id>/cart/", methods=["DELETE"])
    def clear_cart(user_id):
        cart = Cart.get(user_id)
        cart.clear_cart()
        return make_response(jsonify({'response': 'ok'}), 200)


class Product:
    @app.route("/products", methods=["POST"])
    def post_product():
        data = request.json
        print(data)
        Product.add_from_json(data)
        return make_response(jsonify(product.json()), 200)

    @app.route("/products", methods=["PUT"])
    def put_product():
        data = request.json
        print(data)
        product = db.Product.get(data['id'])
        product.edit_from_json(data)
        product.save()
        return make_response(jsonify(product.json()), 200)

    @app.route("/products/<int:id>", methods=["GET"])
    def get_product(id):
        product = db.Product.get(id)
        return make_response(jsonify(product.json()), 200)
    
    @app.route("/products/", methods=["GET"])
    def get_products():
        products = db.Product.all()
        if 'page' in request.args and 'count' in request.args:
            page = int(request.args['page'])
            count = int(request.args['count'])
            products = products[page*count:(page + 1)*count]
        return make_response(jsonify(products.json()), 200)

class Category:
    @app.route("/categories/", methods=["GET"])
    def get_categories():
        item = db.Category.all()
        return make_response(jsonify([el.json() for el in item]), 200)


@app.route("/", methods=["GET"])
def home():
    if 'category' in request.args:
        products = db.Product.get_by_category(request.args['category'])
    else:
        products = db.Product.all()
    return render_template('list.html', products=products, user_id = request.args['user_id'])


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8080", debug = True)
