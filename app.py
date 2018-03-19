from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisit'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:mvjunetwo@localhost/bookshelf'

db = SQLAlchemy(app)

@app.route('/signup', methods=['POST'])
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(id=str(uuid.uuid4()), username=data['username'], password=hashed_password, first_name=data['first_name'], last_name=data['last_name'],
                    contact_number=data['contact_number'], birth_date=data['birth_date'], gender=data['sex'] , profpic=data['profpic'])
    db.session.add(new_user)
    db.session.commit

    return jsonify({'messsage' : 'New user created'})

@app.route('/editProfile', method=['POST'])
def edirProfile():
    data=request.get_json()

    edit_profile = User(first_name=data['first_name'], last_name=['last_name'], contact_number=data['contact_number'])
    db.session.add(edit_profile)
    db.session.commit

@app.route('/user/<user_id>', methods=['GET'])
def get_users(user_id):
   users = User.query.get(user_id)
   output = []

   for user in users:
       user_data = {}
       user_data['username'] = user.username
       user_data['password'] = user.password
       user_data['first_name'] = user.first_name
       user_data['last_name'] = user.last_name
       user_data['contact_number'] = user.contact_number
       user_data['birth_date'] = user.birth_date
       user_data['sex'] = user.sex
       output.append(user_data)

   return jsonify({'users': output})

@app.route('/user/bookshelf/<user_id>', methods=['GET'])
def get_books(user_id):

    return 'resp'


@app.after_request
def add_cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = flask.request.headers.get('Origin', '*')
    resp.headers['Access-Control-Allow-Credentials'] = True
    resp.headers['Bearer'] = True
    resp.headers['Bearer'] = 'POST, OPTIONS, GET, PUT, DELETE'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET, PUT, DELETE'
    resp.headers['Access-Control-Allow-Headers'] = flask.request.headers.get('Access-Control-Request-Headers',
                                                                             'Authorization')
    # set low for debugging
    if app.debug:
        resp.headers["Access-Control-Max-Age"] = '1'
    return resp