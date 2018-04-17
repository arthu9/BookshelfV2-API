from flask import Flask, jsonify, request, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from flask_httpauth import HTTPBasicAuth
from models import *
from sqlalchemy import cast


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
            current = User.query.filter_by(id=data['id']).first()
            current_user = current.id
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

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
        user_data['longitude'] = user.longitude
        user_data['latitude'] = user.latitude
        user_data['profpic'] = user.profpic
        output.append(user_data)

    return jsonify({'users': output})


@app.route('/user/info', methods=['GET'])
@token_required
def get_one_user(current_user):

    user = User.query.filter_by(id=current_user).first()

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
    user_data['longitude'] = user.longitude
    user_data['latitude'] = user.latitude
    user_data['profpic'] = user.profpic

    return jsonify({'information': user_data})


@app.route('/signup', methods=['POST'])
def create_user():

    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(username=data['username'], password=hashed_password, first_name=data['first_name'],last_name=data['last_name'],contact_number=data['contact_number'], birth_date=data['birth_date'], gender = data['gender'], longitude=data['longitude'], latitude=data['latitude'])

    user = User.query.filter_by(username=data['username']).first()

    if user is None:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'New user created!'})
    else:
        return jsonify({'message': 'Username already created'})


@app.route('/login', methods=['GET', 'POST'])
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

  
@app.route('/search', methods=['GET', 'POST'])
def search():

    data = request.get_json()
    item = '%' + data['item'] + '%'

    books = Books.query.filter(((Books.title.like(item)) | (Books.year_published.like(item)) | (Books.types.like(item)) | cast(Books.edition, sqlalchemy.String).like(str(item)) | (Books.isbn.like(item)))).all()

    if books is None:
        return jsonify({'message':'No book found!'})

    output = []

    for book in books:
        user_data = {}
        user_data['title'] = book.title
        user_data['description'] = book.description
        user_data['year_published'] = book.year_published
        user_data['isbn'] = book.isbn
        user_data['types'] = book.types
        user_data['publisher_id'] = book.publisher_id
        output.append(user_data)

    return jsonify({'book': output})



@app.route('/user/bookshelf/search', methods=['GET','POST'])
@token_required
def searchbookshelf(current_user):

    data = request.get_json()

    item = '%'+data['item']+'%'

    books = Bookshelf.query.filter_by(bookshef_owner = current_user).first()
    shelf_id = books.bookshelf_id

    books = ContainsAsscociation.query.join(Books).filter((cast(shelf_id, sqlalchemy.String).like(item)) & ((Books.title.like(item)) | (
        Books.year_published.like(item)) | (Books.types.like(item)) | cast(Books.edition, sqlalchemy.String).like(item) | (Books.isbn.like(item)))).all()

    if books is None:
        return jsonify({'message':'No book found!'})

    output = []

    for book in books:
        user_data = {}
        user_data['title'] = book.title
        user_data['description'] = book.description
        user_data['year_published'] = book.year_published
        user_data['isbn'] = book.isbn
        user_data['types'] = book.types
        user_data['publisher_id'] = book.publisher_id
        output.append(user_data)

    return jsonify({'book': output})

@app.route('/user/bookshelf', methods=['GET'])
@token_required
def viewbook(current_user):

    books = Bookshelf.query.filter_by(bookshef_owner = current_user).first()
    shelf_id = books.bookshelf_id

    contains = ContainsAsscociation.query.filter_by(shelf_id = shelf_id).first()
    shelf_id = contains.shelf_id

    Book = Books.query.join(ContainsAsscociation).filter_by(shelf_id = shelf_id).all()

    # q = (db.session.query(Books, Bookshelf, ContainsAsscociation, Author)
    #      .filter(Bookshelf.bookshef_owner == id)
    #      .filter(ContainsAsscociation.shelf_id == Bookshelf.bookshelf_id)
    #      .filter(Books.book_id == ContainsAsscociation.book_id)
    #      .filter(Author.author_id == Books.publisher_id)
    #      .all())

    output = []

    for book in Book:
        user_data = {}
        user_data['title'] = book.title
        user_data['description'] = book.description
        user_data['edition'] = book.edition
        user_data['year'] = book.year_published
        user_data['isbn'] = book.isbn
        user_data['types'] = book.types
        user_data['publisher_id'] = book.publisher_id
        output.append(user_data)


    return jsonify({'book': output})


#COMMENT (BOOK)
@app.route('/comment-book/<int:current_user>/<int:book_id>', methods=['GET', 'POST'])
# @app.route('/comment-book', methods=['POST'])
def commentbook(current_user, book_id):

    data = request.get_json()

    comment = BookCommentAssociation(comment=data['comment'])

    # rateOld = BookRateAssociation.query.filter((BookRateAssociation.user_id == current_user.id) & (BookRateAssociation.book_id == book_id)).first()

    new_comment = BookCommentAssociation.query.filter((BookCommentAssociation.user_id == current_user.id) & (BookCommentAssociation.book_id == book_id)).first()

    if new_comment is not None:
        db.session.add(comment)
        db.session.commit()
        return jsonify({'message': 'comment posted!'})
    else:
        return jsonify({'message': 'cant post comment :(', 'book_id': book_id})



@app.route('/user/addbook', methods=['POST'])
@token_required
def addbook(current_user):

    data = request.get_json()

    book = Books.query.filter((Books.title == data['title']) & (Books.edition == data['edition']) & (Books.year_published == data['year']) & (Books.isbn == data['isbn'])).first()
    publisher = Publisher.query.filter(Publisher.publisher_name == data['publisher_name']).first()
    author = Author.query.filter(
        (Author.author_first_name == data['author_fname']) & (Author.author_last_name == data['author_lname'])).first()
    if (book is None) or (publisher is None) or (author is None):
        if publisher is None:
            newPublisher = Publisher(publisher_name= data['publisher_name'])
            db.session.add(newPublisher)
            db.session.commit()
            publisher_id = Publisher.query.filter((Publisher.publisher_name == data['publisher_name'])).first()
            if author is None:
                author = Author(data['author_fname'], data['author_lname'])
                db.session.add(author)
                db.session.commit()
            elif author is not None:
                auth_id = Author.query.filter((Author.author_first_name == data['author_fname']) and (Author.author_last_name == data['author_lname'])).first()
        elif publisher is not None:
            publisher_id = Publisher.query.filter((Publisher.publisher_name == data['publisher_name'])).first()
            if author is None:
                authbook = Author(data['author_fname'], data['author_lname'])
                db.session.add(authbook)
                db.session.commit()
            elif author is not None:
                auth_id = Author.query.filter((Author.author_first_name == data['author_fname']) and (
                    Author.author_last_name == data['author_lname'])).first()

        publisher = Publisher.query.filter(Publisher.publisher_name == data['publisher_name']).first()
        publisher_id = publisher.publisher_id
        book = Books(title=data['title'], edition=data['edition'], year_published=data['year'], isbn=data['isbn'], types=data['types'], publisher_id=publisher_id)
        db.session.add(book)
        db.session.commit()

        written = WrittenByAssociation(auth_id.author_id, book.book_id)
        db.session.add(written)
        db.session.commit()

        bookshelf = Bookshelf.query.filter_by(bookshef_owner=current_user).first()
        shelf_id = bookshelf.bookshelf_id

        contain = ContainsAsscociation(shelf_id, book.book_id, 1, 'YES')
        db.session.add(contain)
        db.session.commit()

        return jsonify({'message': 'New book created!'})

    else:

        bookshelf = Bookshelf.query.filter_by(bookshef_owner=current_user).first()
        shelf_id = bookshelf.bookshelf_id

        bookquantity = ContainsAsscociation.query.filter((ContainsAsscociation.shelf_id == shelf_id) & (ContainsAsscociation.book_id == book.book_id)).first()
        if bookquantity is None:
            contain = ContainsAsscociation(shelf_id, book.book_id, 1, 'YES')
            db.session.add(contain)
            db.session.commit()
        else:
            curQuant = bookquantity.quantity
            bookquantity.quantity = int(curQuant + 1)
            db.session.commit()

    return jsonify({'message': 'New book counted!'})

# {"title": "new book","edition": "20", "year": "2018", "isbn": "SEVENTEEN", "types": "HARD" , "publisher_name":"DK", "author_fname": "SEANNE", "author_lname": "CANOY"}


@app.route('/user/bookshelf/availability', methods=['GET'])
@token_required
def viewbooks(current_user):

    books = ContainsAsscociation.query.join(Bookshelf).filter_by(bookshef_owner = current_user).all()

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

@app.route('/category/<string:category>/', methods=['GET'])
def category(category):

    books = Books.query.join(Category).filter(Category.categories == category).filter(Books.book_id == Category.book_id).all()
    # filter_by(firstname.like(search_var1),lastname.like(search_var2))
    #
    # q = (db.session.query(Category, Books)
    #      .join(Books)
    #      .join(Category)
    #      .filter(Category.categories == category)
    #      .filter(Books.book_id == Category.book_id)
    #      .all())

    output = []

    for book in books:
        user_data = {}
        user_data['title'] = book.title
        user_data['description'] = book.description
        user_data['edition'] = book.edition
        user_data['year'] = book.year_published
        user_data['isbn'] = book.isbn
        user_data['types'] = book.types
        user_data['publisher_id'] = book.publisher_id
        output.append(user_data)


    return jsonify({'book': output})


#COMMENT (USER)
# @app.route('/profile/comment-user/', methods=['GET', 'POST'])
@app.route('/profile/comment-user/<int:user_id>', methods=['GET', 'POST'])
def comment(current_user, user_id):

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




# @app.route('/ratings/<int:book_id>', methods=['POST'])
# def ratings(book_id):
#
#     data = request.get_json()
#
#     current_user = User.query.filter_by(id=id).first()
#
#     rate = BookRateAssociation(rating=data['rating'])
#
#     rateOld = BookRateAssociation.query.filter(
#         (BookRateAssociation.user_id == current_user.id) & (BookRateAssociation.book_id == book_id)).first()
#
#     if rateOld is None:
#         rateOld.rating = rate
#         db.session.commit()


# if __name__ == '__main__':
#     app.run(debug=True)
