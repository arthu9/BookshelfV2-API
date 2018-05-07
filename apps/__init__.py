from flask import Flask, Blueprint, request, abort,url_for, jsonify, g, render_template, make_response,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import cast
import os, sqlalchemy, jwt, datetime
from flask_httpauth import HTTPBasicAuth
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_cors import CORS


app = Flask(__name__)

db = SQLAlchemy(app)

CORS(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mvjunetwo@localhost/bookshelf'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['USE_SESSION_FOR_NEXT'] = True
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = 'thisissecret'
app.secret_key = os.urandom(24)

#rttr

from apps import api


#def createDB():
#    engine = sqlalchemy.create_engine('postgresql://postgres:mvjunetwo@localhost') #connects to server
#    conn = engine.connect()
#    conn.execute("commit")
#    conn.execute("create database bookshelf")
#    conn.close()

#def createTables():

# db.create_all()



#createDB()
#createTables()

