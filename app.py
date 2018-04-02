from flask import Flask, jsonify, request, make_response
# from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
# from flask_httpauth import HTTPBasicAuth
from models import *


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/users', methods=['GET'])
@token_required
def get_all_users(current_user):

    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['username'] = user.username
        user_data['password'] = user.password
        user_data['first_name'] = user.first_name
        user_data['last_name'] = user.last_name
        user_data['contact_number'] = user.contact_number
        user_data['birth_date'] = user.birth_date
        user_data['gender'] = user.gender
        user_data['profpic'] = user.profpic
        output.append(user_data)

    return jsonify({'users': output})

@app.route('/user/info/<id>', methods=['GET'])
@token_required
def get_one_user(id):

    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message':'No user found!'})

    user_data = {}
    user_data['id'] = user.id
    user_data['username'] = user.username
    user_data['password'] = user.password
    user_data['first_name'] = user.first_name
    user_data['last_name'] = user.last_name
    user_data['contact_number'] = user.contact_number
    user_data['birth_date'] = user.birth_date
    user_data['gender'] = user.gender
    user_data['profpic'] = user.profpic

    return jsonify({'user': user_data})

@app.route('/signup', methods=['POST'])
def create_user():

    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(username=data['username'], password=hashed_password, first_name=data['first_name'],last_name=data['last_name'],
                    contact_number=data['contact_number'], birth_date=data['birth_date'], gender = data['gender'], profpic = data['profpic'])

    user = User.query.filter_by(username=data['username']).first()

    if user is None:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'New user created!'})
    else:
        return jsonify({'message': 'Username already created'})


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@app.route('/bookshelf/<int:shelf_id>/search/<string:item>', methods=['GET'])
def search(shelf_id, item):

    item = '%'+item+'%'
    books = ContainsAsscociation.query.join(Books).filter((ContainsAsscociation.shelf_id.like(shelf_id)) & ((Books.title.like(item)) | (
        Books.year_published.like(item)) | (Books.types.like(item)) | Books.edition.like(str(item)) | (Books.isbn.like(item)))).all()

    if books is None:
        return jsonify({'message':'No book found!'})

    output = []

    for book in books:
        user_data = {}
        user_data['shelf_id'] = book.shelf_id
        user_data['book_id'] =book.book_id
        user_data['quantity'] = book.quantity
        user_data['availability'] = book.availability
        output.append(user_data)

    return jsonify({'book': output})

@app.route('/user/<int:id>/bookshelf/', methods=['GET'])
def viewbooks(id):

    books = ContainsAsscociation.query.join(Bookshelf).filter_by(bookshelf_id = id).all()

    if books == []:
        return jsonify({'message': 'No book found!'})

    else:

        output = []
        for book in books:
            user_data = {}
            user_data['shelf_id'] = book.shelf_id
            user_data['book_id'] = book.book_id
            user_data['quantity'] = book.quantity
            user_data['availability'] = book.availability
            output.append(user_data)

        return jsonify({'book': output})


# @app.route('/addbok/<int:id>')
# def addbook(id):


if __name__ == '__main__':
    app.run (debug=True)
