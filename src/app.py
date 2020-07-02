from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))  # absolute path of tthe app

# Configs
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
# Init db
db = SQLAlchemy(app)
# Init marshmallow
ma = Marshmallow(app)  # library for object conversion to python native types

from components import *

if __name__ == '__main__':
    app.run(debug=True)

# from app import db
# db.creae_all()
