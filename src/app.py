from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Init app
app = Flask(__name__)


# Configs
app.config.from_pyfile('config.py')

# Init db
db = SQLAlchemy(app)
# Init marshmallow
ma = Marshmallow(app)  # library for object conversion to python native types

from components import *

if __name__ == '__main__':
    app.run(debug=True)

# from app import db
# db.creae_all()
