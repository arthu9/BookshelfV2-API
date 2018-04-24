from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import *
import models

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:pagararea1096@127.0.0.1:5432/bookshelf'
# engine = sqlalchemy.create_engine('postgresql://postgres:pagararea1096@127.0.0.1:5432/bookshelf')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisthesecretkey'
