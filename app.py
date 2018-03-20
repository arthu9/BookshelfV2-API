from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from models import *


app = Flask(__name__)

db = SQLAlchemy(app)


@app.route('/signup', methods=['POST'])
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password, first_name=data['first_name'], last_name=data['last_name'],
                    contact_number=data['contact_number'], birth_date=data['birth_date'], gender=data['sex'] , profpic=data['profpic'])
    db.session.add(new_user)
    db.session.commit

    return jsonify({'messsage' : 'New user created'})


@app.route('/user/<user_id>', methods=['GET'])
def get_users(user_id):
   users = User.query.get().where(id=user_id)
   output = []

   for user in users:
       user_data = {}
       user_data['username'] = user.username
       user_data['password'] = user.password
       user_data['first_name'] = user.first_name
       user_data['last_name'] = user.last_name
       user_data['contact_number'] = user.contact_number
       user_data['birth_date'] = user.birth_date
       user_data['gender'] = user.gender
       output.append(user_data)

   return jsonify({'users': output})

@app.route('/user', methods=['GET'])
def get_all_users():

    # if not current_user.admin:
    #     return jsonify({'message' : 'Cannot perform that function!'})

    users = User.query.all()
    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['username'] = user.name
        user_data['password'] = user.password
        user_data['first_name'] = user.first_name
        user_data['last_name'] = user.last_name
        user_data['contact_number'] = user.contact_number
        user_data['birthdate'] = user.birthdate
        user_data['gender'] = user.gender
        user_data['profpic'] = user.profpic
        # user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users', output})


@app.route('/user/bookshelf/<user_id>', methods=['GET'])
def get_books(user_id):

    return 'resp'



if __name__ == '__main__':
    app.run (debug=True)