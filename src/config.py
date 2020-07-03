from sqlalchemy import true, false
import os

DEBUG = true

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')

SQLALCHEMY_TRACK_MODIFICATIONS = false

SECRET_KEY = 'secretkey'
