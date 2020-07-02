from app import app, db, ma
from models import User, Product, ProductSchema
from flask import request, jsonify, make_response
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

## Users

# Note: add x-access-token and the token in the header of the request
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# Return all users
@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):  # argument mandated by the decorator
    if not current_user.admin:
        return jsonify({'message': 'The user has no permission to perform this taks'})

    users = User.query.all()
    output = []

    for user in users:
        user_data = {'public_id': user.public_id,
                     'name': user.name,
                     'password': user.password,
                     'admin': user.admin}
        output.append(user_data)

    return jsonify({'Users': output})


# Return a single user given it's id
@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'The user has no permission to perform this taks'})

    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found'})

    user_data = {'public_id': user.public_id,
                 'name': user.name,
                 'password': user.password,
                 'admin': user.admin}

    return jsonify({'user': user_data})


# Creates a user
# Note: Postman -> raw_text: json
@app.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    if not current_user.admin:
        return jsonify({'message': 'The user has no permission to perform this taks'})

    name = request.json['name']
    password = request.json['password']

    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(public_id=str(uuid.uuid4()), name=name, password=hashed_password, admin=False)

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New User created!'})


# Promotes the passed user_id to an admim user
@app.route('/user/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'The user has no permission to perform this taks'})

    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found'})

    user.admin = True
    db.session.commit()

    return jsonify({'message': 'The user has been promoted'})


# Deletes an user
@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'The user has no permission to perform this taks'})

    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'The user has been deleted'})


# Login a user and attribute a json web token
# This is the only route that works with basic http authentication, the rest will use the jwt
# Note: Postman -> GET /login -> auth -> basic auth
@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Empty parameter(s)',
                             401,  # Unauthorized
                             {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(
        name=auth.username).first()  # since the username is unique there's only one element in the list

    if not user:
        return make_response('User does not exist',
                             401,  # Unauthorized
                             {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        # JWT - JSON web token
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},  # The token is valid for 30 minutes
            app.config['SECRET_KEY'])  # key used to encode the token
        return jsonify({'token': token.decode('UTF 8')})
    else:
        return make_response('Wrong password',
                             401,  # Unauthorized
                             {'WWW-Authenticate': 'Basic realm="Login required!"'})





# Init Schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)  # Signaling we're dealing with multiple objects

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
@token_required
def add_product(current_user):
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']
    user_id = current_user.id

    new_product = Product(name, description, price, qty, user_id)

    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product)


@app.route('/product', methods=['GET'])
@token_required
def get_products(current_user):
    if current_user.admin:  # if the user is an admim shows all products
        all_products = Product.query.all()
        result = products_schema.dump(all_products)
        return jsonify(result)
    else:
        user_products = Product.query.filter_by(user_id=current_user.id).all()

        output = []

        for product in user_products:
            product_data = {'name': product.name,
                            'description': product.description,
                            'price': product.price,
                            'qty': product.qty}
            output.append(product_data)

        return jsonify({'products': output})


# Get a single product
@app.route('/product/<int:id>', methods=['GET'])
@token_required
def get_product(current_user, id):
    product = Product.query.get(id)
    if product:
        if current_user.admin:
            return product_schema.jsonify(product)
        else:
            if product.user_id == current_user.id:
                return product_schema.jsonify(product)
            else:
                return jsonify({'message': 'User does not have permission to view this product'})
    else:
        return jsonify({'message': 'The product does not exist'})


# Update a product
@app.route('/product/<int:id>', methods=['PUT'])
@token_required
def update_product(current_user, id):
    product = Product.query.get(id)
    if product:
        print(current_user.id)
        print(product.user_id)
        if current_user.id == product.user_id:
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
        else:
            return jsonify({'message': 'User does not have permission'})
    else:
        return jsonify({'message': 'The product does not exist'})


# Update Product
@app.route('/product/<int:id>', methods=['DELETE'])
@token_required
def delete_product(current_user, id):
    product = Product.query.get(id)
    if product:
        if current_user.id == product.user_id:
            db.session.delete(product)
            db.session.commit()
            return product_schema.jsonify(product)
        else:
            return jsonify({'message': 'User does not have permission'})
    else:
        return jsonify({'message': 'Product does not exist'})


@app.route('/', methods=['GET'])
def index():
    return jsonify({'msg': 'If this shows up then the api is working'})
