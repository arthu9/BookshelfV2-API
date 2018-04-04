from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from flask_httpauth import HTTPBasicAuth
from models import *
from flask_login import LoginManager, current_user, login_user, login_required, logout_user


auth = HTTPBasicAuth()

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
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/users', methods=['GET'])
def get_all_users():

    # if not current_user.admin:
    #     return jsonify({'message' : 'Cannot perform that function!'})

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

    return jsonify({'users', output})

@app.route('/user/info/<id>', methods=['GET'])
@token_required
def get_one_user(id):
    # if not current_user.admin:

    #     return jsonify({'message' : 'Cannot perform that function!'})

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

    return jsonify({'user' : user_data})

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
        return jsonify({'message': 'username already created'})

# @app.route('/user/<user_id>', methods=['PUT'])
# @token_required
# def promote_user(current_user, public_id):
#
#     # if not current_user.admin:
#     #     return jsonify({'message' : 'Cannot perform that function!'})
#
#     user = User.query.filter_by(public_id=public_id).first()
#
#     if not user:
#         return jsonify({'message' : 'No user found!'})
#
#     user.admin = True
#     db.session.commit()
#
#     return jsonify({'message' : 'The user has been promoted!'})
#
# @app.route('/user/<user_id>', methods=['DELETE'])
# @token_required
# def delete_user(current_user, public_id):
#
#     # if not current_user.admin:
#     #     return jsonify({'message' : 'Cannot perform that function!'})
#
#     user = User.query.filter_by(public_id=public_id).first()
#
#     if not user:
#         return jsonify({'message': 'No user found!'})
#
#     db.session.delete(user)
#     db.session.commit()
#
#     return ({'message' : 'The user has been deleted!'})

#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#
#     if current_user.is_authenticated is True:
#          return jsonify({'status': 'success', 'message': 'current user is authenticated'})
#          # return redirect(url_for('home'))
#
#     elif form.validate_on_submit():
#
#         user = User.query.filter_by(username=form.username.data).first()
#
#         if user:
#             if check_password_hash(user.password, form.password.data):
#                 login_user(user, remember=True)
#                 token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
#                 return jsonify({'status': 'success', 'username': user.username, 'message': 'success','token': token.decode('UTF-8')})
#                 # return redirect(url_for('home'))
#             else:
#                 # flash('Invalid username or password')
#                 return jsonify({'status': 'Could not verify', 'message': 'error'})
#                 # return render_template('login.html', form=form)
#         else:
#             return jsonify({'status': 'Could not verify', 'message': 'error'})
#             # return render_template('login.html', form=form)
#     return jsonify({'status': 'Could not verify', 'message': 'error'})
#     # return render_template('login.html', form=form)


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


#COMMENT (USER)
# @app.route('/profile/commentUser/', methods=['GET', 'POST'])
@app.route('/profile/commentUser/<int:user_id>', methods=['GET', 'POST'])
def comment(user_id):

    if user_id == current_user.id:
        comments = UserCommentAssociation.query.filter((UserCommentAssociation.user_idCommentee == current_user.id))
        x = []
        for c in comments:
            s = User.query.filter_by(id=c.user_idCommenter).first()
            x.append(s.first_name + ' ' + s.last_name)
        return jsonify({'message': 'ok', 'comments': comments, 'name': x,'currrent_user': current_user})
    else:
        user = User.query.filter_by(id=user_id).first()
        otheruserId = user_id
        comments = UserCommentAssociation.query.filter((UserCommentAssociation.user_idCommentee == user_id))
        xs = []
        for c in comments:
            s = User.query.filter_by(id=c.user_idCommenter).first()
            xs.append(s.first_name + ' ' + s.last_name)
        if request.method == 'POST':
            comment = request.form['comment']
            commentOld = UserCommentAssociation.query.filter((UserCommentAssociation.user_idCommentee == otheruserId) & (
                UserCommentAssociation.user_idCommenterter == current_user.id)).first()

            if commentOld is not None:
                commentOld.comment = comment
                db.session.commit()

            else:
                newCommenter = UserCommentAssociation(current_user.id, otheruserId,comment)
                db.session.add(newCommenter)
                db.session.commit()
            return jsonify({'message': 'ok', 'user_id': user_id})
        return jsonify({'message': 'ok', 'user': user, 'comments': comments, 'name': xs, 'currrent_user': current_user})


#COMMENT (BOOK)
# @app.route('/commentBook/', methods=['POST', 'GET'])
@app.route('/commentBook/<int:book_id>', methods=['POST', 'GET'])
def commentbook(book_id):
    data = request.get_json()
    comment = request.form['comment']
    commentOld = BookCommentAssociation.query.filter((BookCommentAssociation.user_id == current_user.id) & (BookCommentAssociation.book_id == book_id)).first()
    if commentOld is not None:
        commentOld.comment = comment
        db.session.commit()

    else:
        newCommenter = BookCommentAssociation(current_user.id, book_id, comment)
        db.session.add(newCommenter)
        db.session.commit()

    # return redirect(url_for('indibook', book_id=book_id, page_num=1))
    return jsonify({'message': 'ok', 'book_id': book_id})




if __name__ == '__main__':
    app.run (debug=True)
