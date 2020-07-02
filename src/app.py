from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))  # absolute path of tthe app

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ini db
db = SQLAlchemy(app)
# Init marshmallow
ma = Marshmallow(app)  # library for object conversion to python native types


# Product Clas/Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)  # two products can't have the same name
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self, name, description, price, qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty


# Product Schema
class ProductSchema(ma.Schema):
    class Meta:  # The fields we're allowed to show
        fields = ('id', 'name', 'description', 'price', 'qty')


# Init Schema
product_schema = ProductSchema()
procuts_schema = ProductSchema(many=True)  # Signaling we're dealing with multiple objects

# Create a Product

# Note: postman -> post -> headers: key Content-Type value  key application/json
# body -> raww
'''
{
    "name": "product1",
    "description": "this is product1",
    "price": 3.75,
    "qty": 6
}
'''


@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    new_product = Product(name, description, price, qty)

    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product)


@app.route('/product', methods=['GET'])
def get_products():
    all_products = Product.query.all()
    result = procuts_schema.dump(all_products)
    return jsonify(result)


# Get a single product
@app.route('/product/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product)


# Update a product
@app.route('/product/<int:id>', methods=['PUt'])
def update_product(id):
    product = Product.query.get(id)
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    # Update the product
    product.name = name
    product.description = description
    product.price = price
    product.qty = qty

    # no add since the product already exists
    db.session.commit()

    return product_schema.jsonify(product)


# Update Product
@app.route('/product/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()

    return product_schema.jsonify(product)


@app.route('/', methods=['GET'])
def index():
    return jsonify({'msg': 'Hello World'})


if __name__ == '__main__':
    app.run(debug=True)

# from app import db
# db.creae_all()
