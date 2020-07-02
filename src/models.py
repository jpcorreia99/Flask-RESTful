from app import db, ma

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)


# Product Clas/Model

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)  # two products can't have the same name
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

    def __init__(self, name, description, price, qty, user_id):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty
        self.user_id = user_id


# Product Schema
class ProductSchema(ma.Schema):
    class Meta:  # The fields we're allowed to show
        fields = ('id', 'name', 'description', 'price', 'qty', 'user_id')