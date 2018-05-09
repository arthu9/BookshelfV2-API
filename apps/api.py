from apps import *
from models import *

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/users', methods=['GET'])
def get_all_user_accounts():
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


@app.route('/user/info', methods=['GET'])
@token_required
def get_one_user(current_user):
    # if not current_user.admin:

    #     return jsonify({'message' : 'Cannot perform that function!'})

    user = User.query.filter_by(id=current_user).first()

    if not user:
        return jsonify({'message': 'No user found!'})

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

    return jsonify({'information': user_data})


@app.route('/signup', methods=['POST'])
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(username=data['username'], password=hashed_password, first_name=data['first_name'],
                    last_name=data['last_name'],
                    contact_number=data['contact_number'], birth_date=data['birth_date'], gender=data['gender'],
                    profpic=data['profpic'])

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


@app.route('/user/bookshelf/search', methods=['GET', 'POST'])
@token_required
def searchbookshelf(current_user):
    data = request.get_json()

    item = '%' + data['item'] + '%'

    books = Bookshelf.query.filter_by(bookshef_owner=current_user).first()
    shelf_id = books.bookshelf_id

    books = Books.query.join(ContainsAsscociation).filter(
        (cast(shelf_id, sqlalchemy.String).like(item)) & ((Books.title.like(item)) | (
            Books.year_published.like(item)) | (Books.types.like(item)) | cast(Books.edition, sqlalchemy.String).like(
            item) | (Books.isbn.like(item)))).all()

    if books is None:
        return jsonify({'message': 'No book found!'})

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
    books = Bookshelf.query.filter_by(bookshef_owner=current_user).first()
    shelf_id = books.bookshelf_id

    contains = ContainsAsscociation.query.filter_by(shelf_id=shelf_id).first()
    shelf_id = contains.shelf_id

    Book = Books.query.join(ContainsAsscociation).filter_by(shelf_id=shelf_id).all()

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
        book = Books(title = data['title'],edition = data['edition'], year_published = data['year'], isbn =data['isbn'], types =data['types'], publisher_id= publisher_id)
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
    books = ContainsAsscociation.query.join(Bookshelf).filter_by(bookshef_owner=current_user).all()

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


# @app.route('/category/<string:category>/', methods=['GET'])
# def category(category):
#
#     books = Books.query.join(Category).filter(Category.categories == category).filter(Books.book_id == Category.book_id).all()
#     # filter_by(firstname.like(search_var1),lastname.like(search_var2))
#     #
#     # q = (db.session.query(Category, Books)
#     #      .join(Books)
#     #      .join(Category)
#     #      .filter(Category.categories == category)
#     #      .filter(Books.book_id == Category.book_id)
#     #      .all())
#
#     output = []
#
#     for book in books:
#         user_data = {}
#         user_data['title'] = book.title
#         user_data['description'] = book.description
#         user_data['edition'] = book.edition
#         user_data['year'] = book.year_published
#         user_data['isbn'] = book.isbn
#         user_data['types'] = book.types
#         user_data['publisher_id'] = book.publisher_id
#         output.append(user_data)


    # return jsonify({'book': output})

@app.route('/user/wishlist', methods=['POST'])
@token_required
def wishlist(current_user):

    data = request.get_json()

    book = Books.query.filter((Books.title == data['title']) & (Books.edition == data['edition']) & (Books.year_published == data['year']) & (
                    Books.isbn == data['isbn'])).first()
    if book is None:
        newPublisher = Publisher(publisher_name=data['publisher_name'])
        db.session.add(newPublisher)
        db.session.commit()

    return jsonify({'message':'wishlist added'})



# COMMENT (BOOK)
@app.route('/comment-book',methods=['GET','POST'])
@token_required
def commentbook(current_user):
    data = request.get_json()

    comment = BookCommentAssociation(user_id=int(current_user.id), book_id=int(data['bookid']),comment=data['comment'])
    db.session.add(comment)
    db.session.commit()

    return jsonify({'message': 'comment posted!'})

# {"bookid":"1","comment":"any comment here"}


# COMMENT (USER)
@app.route('/comment-user/<int:user_idCommentee>', methods=['GET','POST'])
@token_required
def commentuser(current_user, user_idCommentee):
    data = request.get_json()
    # get_id = User.query.filter_by(id=data['id']).first()
    # get_id = User.query.filter_by(User.book_id == book_id).first()

    new_comment = UserCommentAssociation(user_idCommenter=int(current_user.id), user_idCommentee=user_idCommentee, comment=data['comment'])
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({'message': 'comment posted!'})


# @app.route('/addbok/<int:id>')
# def addbook(id):
