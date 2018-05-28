from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import sqlalchemy, datetime
from flask_login import UserMixin

from app import app

db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(11))
    birth_date = db.Column(db.DATE, nullable=False)
    gender = db.Column(db.String(6), nullable=False)
    longitude = db.Column(db.FLOAT, nullable=False)
    latitude = db.Column(db.FLOAT, nullable=False)
    profpic = db.Column(db.LargeBinary)
    bookshelf_user = db.relationship('Bookshelf', uselist=False, backref='user_bookshelf')
    borrow_bookshelfs = db.relationship('BorrowsAssociation', backref='user_borrow')
    wishlists_bookshelf = db.relationship('Wishlist', backref='user_wishlist')
    user_interest = db.relationship('InterestAssociation', backref='user_interest')

    def __init__(self, username='', password='', first_name='', last_name='', contact_number='', birth_date='', gender='',
                 longitude='', latitude='', profpic=''):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.contact_number = contact_number
        self.birth_date = birth_date
        self.gender = gender
        self.longitude = longitude
        self.latitude = latitude
        self.profpic = profpic


class Token(db.Model):
    __tablename__ = 'token'
    id = db.Column(db.Integer, db.ForeignKey('user.id'))
    token = db.Column(db.String(125),primary_key=True)
    TTL =db.Column(db.DateTime)

    def __init__(self, id ='', token ='', TTL = ''):
        self.id = id
        self.token = token
        self.TTL = TTL


class Bookshelf(db.Model):
    __tablename__ = 'bookshelf'
    bookshelf_id = db.Column(db.Integer, primary_key=True)
    bookshef_owner = db.Column(db.String, db.ForeignKey('user.username'))
    owner = db.relationship('User', backref='bookshelf_owner')
    booksContain = db.relationship('ContainsAssociation', backref=db.backref('bookshelf_contains'))
    borrow_users = db.relationship('BorrowsAssociation', backref='bookshelfBooks')
    wishlist_users = db.relation('Wishlist', backref='bookshelfwish')
    purchase = db.relationship('PurchaseAssociation', backref='books_purchase')

    def __init__(self, bookshelf_id='', bookshef_owner=''):
        self.bookshelf_id = bookshelf_id
        self.bookshef_owner = bookshef_owner

#add rating and time

class Books(db.Model):
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.TEXT, nullable=False)
    description = db.Column(db.VARCHAR)
    edition = db.Column(db.Integer, nullable=True)
    year_published = db.Column(db.String(500), nullable=True)
    isbn = db.Column(db.String(20), nullable=False, unique=True)
    types = db.Column(db.String(20), nullable=True)
    book_cover = db.Column(db.TEXT)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.publisher_id'))
    bookshelfBooks = db.relationship('ContainsAssociation', backref='books_contains')
    categoryBooks = db.relationship('CategoryAssociation', backref='books_category')
    booksAuthor = db.relationship('WrittenByAssociation', backref='books_author')
    publisher = db.relationship('Publisher', backref='bookPublish')
    booksInGenre = db.relationship('HasGenreAssociation', backref='books_genre')

    borrowcount = db.Column(db.Integer, default=0)

    def __init__(self, title='', description='', edition='', year_published='', isbn='', types='', publisher_id='', book_cover=''):
        self.title = title
        self.description = description
        self.edition = edition
        self.year_published = year_published
        self.isbn = isbn
        self.types = types
        self.publisher_id = publisher_id
        self.book_cover = book_cover


class ContainsAssociation(db.Model):
    __tablename__ = 'contains'
    contains_id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    availability = db.Column(db.String(3))
    methods= db.Column(db.String(50))
    price = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.datetime.today)
    shelf_id = db.Column(db.Integer, db.ForeignKey('bookshelf.bookshelf_id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    rateBooks = db.relationship('BookRateAssociation', backref='books_rateBooks')
    commentBooks = db.relationship('BookCommentAssociation', backref='books_commentBooks')
    bookshelfcontain = db.relationship('Bookshelf', backref='containingbooks')
    containsbooks = db.relationship('Books', backref='booksBookshelf')

    def __init__(self, shelf_id='', book_id='', quantity='', availability='', methods='', price=''):
        self.shelf_id = shelf_id
        self.book_id = book_id
        self.quantity = quantity
        self.methods = methods
        self.price = price
        self.availability = availability

class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String)
    books = db.relationship('CategoryAssociation', backref='books_cat')

    def __init__(self, category_name=''):
        self.category_name = category_name

class CategoryAssociation(db.Model):
    __tablename__ = 'category_association'
    category_book_id = db.Column(db.Integer)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), primary_key=True)
    book = db.relationship('Books', backref='categorybook')
    category = db.relationship('Category', backref='category_ass')

    def __init__(self, book_id='', category_id=''):
        self.book_id = book_id
        self.category_id = category_id

class Author(db.Model):
    __tablename__ = 'author'
    author_id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(50))
    authorBooks = db.relationship('WrittenByAssociation', backref="author_books")

    def __init__(self, author_name=''):
        self.author_name = author_name


class WrittenByAssociation(db.Model):
    __tablename__ = 'writtenBy'
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.author_id'))
    author = db.relationship('Author', backref='author_writtenby')
    books = db.relationship('Books', backref='booksAuthor_writtenby')

    def __init__(self, author_id='', book_id=''):
        self.author_id = author_id
        self.book_id = book_id


class Publisher(db.Model):
    __tablename__ = 'publisher'
    publisher_id = db.Column(db.Integer, primary_key=True)
    publisher_name = db.Column(db.String(50))
    publishBooks = db.relationship('Books', backref='publisher_books')

    def __init__(self, publisher_name=''):
        self.publisher_name = publisher_name


class Genre(db.Model):
    __tablename__ = 'genre'
    id_genre = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String, nullable=False, unique=True)
    genreBooks = db.relationship('HasGenreAssociation', backref='genres_books')
    genreInterest = db.relationship('InterestAssociation', backref='genre_interest')

    def __init__(self, genre_name=''):
        self.genre_name = genre_name

class HasGenreAssociation(db.Model):
    __tablename__ = 'hasGenre'
    genre_book_id = db.Column(db.Integer, primary_key=True)
    genreId = db.Column(db.Integer, db.ForeignKey('genre.id_genre'))
    bookId = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    books = db.relationship('Books', backref='booksGenre')
    genre = db.relationship('Genre', backref='bookHasGenre')

    def __init__(self, bookId='', genreId=''):
        self.bookId = bookId
        self.genreId = genreId

class InterestAssociation(db.Model):
    __tablename__ = 'hasInterest'
    interestId = db.Column(db.Integer, primary_key=True)
    user_Id = db.Column(db.Integer, db.ForeignKey('user.id'))
    genreId = db.Column(db.Integer, db.ForeignKey('genre.id_genre'))
    user = db.relationship('User', backref='Interestuser')
    genre = db.relationship('Genre', backref='Interestgenre')




class PurchaseAssociation(db.Model):
    __tablename__ = 'purchase'
    purchase_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    shelf_id = db.Column(db.Integer, db.ForeignKey('bookshelf.bookshelf_id'))
    price = db.Column(db.Integer)
    user = db.relationship('User', backref='purchaseBook')
    bookshelf = db.relationship('Bookshelf', backref='purchasebook')

    def __init__(self, user_id='', shelf_id='', status='', price='', bookid='', seen='', otherUserReturn='',
                 curUserReturn='', returnDate=''):
        self.user_id = user_id
        self.shelf_id = shelf_id
        self.status = status
        self.price = price

class BorrowsAssociation(db.Model):
    __tablename__ = 'borrows'
    borrowed = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    shelf_id = db.Column(db.Integer, db.ForeignKey('bookshelf.bookshelf_id'))
    date = db.Column(db.DateTime, default=datetime.datetime.today)
    status = db.Column(db.Integer)
    price = db.Column(db.Integer)
    bookid = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    seen = db.Column(db.Integer)
    otherUserReturn = db.Column(db.Integer)
    curUserReturn = db.Column(db.Integer)
    returnDate = db.Column(db.TEXT)
    user = db.relationship('User', backref='borrowBookshelfs')
    bookshelf = db.relationship('Bookshelf', backref='borrowUsers')

    def __init__(self, user_id='', shelf_id='', status='', price='', bookid='', seen='', otherUserReturn='',
                 curUserReturn='', returnDate=''):
        self.user_id = user_id
        self.shelf_id = shelf_id
        self.status = status
        self.price = price
        self.bookid = bookid
        self.seen = seen
        self.otherUserReturn = otherUserReturn
        self.curUserReturn = curUserReturn
        self.returnDate = returnDate


class Wishlist(db.Model):
    __tablename__ = "wishlist"
    wishlist_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    shelf_id = db.Column(db.Integer, db.ForeignKey('bookshelf.bookshelf_id'))
    bookId = db.Column(db.Integer)
    user = db.relationship('User', backref='wishlist_user')
    bookshelf = db.relationship('Bookshelf', backref='bookshelf_wishlist')

    def __init__(self, user_id='', shelf_id='', bookId=''):
        self.user_id = user_id
        self.shelf_id = shelf_id
        self.bookId = bookId


# Rates (book)
class BookRateAssociation(db.Model):
    __tablename__ = 'bookRate'
    rate_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('contains.contains_id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.TEXT, nullable=True)
    user = db.relationship('User', backref='user_booksRate')
    books = db.relationship('ContainsAssociation', backref='bookRate')

    def __init__(self, user_id='', book_id='', rating='', comment=''):
        self.user_id = user_id
        self.book_id = book_id
        self.rating = rating
        self.comment = comment


class BookRateTotal(db.Model):
    __tablename__ = 'bookrateTotal'
    totalrate_id = db.Column(db.Integer, primary_key=True)
    bookRated = db.Column(db.Integer, db.ForeignKey('contains.contains_id'))
    numofRates = db.Column(db.Integer)
    totalRate = db.Column(db.Float, default=0)

    def __init__(self, bookRated='', numofRates='', totalRate=''):
        self.bookRated = bookRated
        self.numofRates = numofRates
        self.totalRate = totalRate


# Rates (user)
class UserRateAssociation(db.Model):
    __tablename__ = 'userRate'
    rate_id = db.Column(db.Integer, primary_key=True)
    user_idRater = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_idRatee = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.TEXT)

    def __init__(self, user_idRater='', user_idRatee='', rating='', comment=''):
        self.user_idRater = user_idRater
        self.user_idRatee = user_idRatee
        self.rating = rating
        self.comment = comment


class UserRateTotal(db.Model):
    __tablename__ = 'userRateTotal'
    numOfRate = db.Column(db.Integer, primary_key=True)
    userRatee = db.Column(db.Integer, db.ForeignKey('user.id'))
    userRater = db.Column(db.Integer, db.ForeignKey('user.id'))
    totalRate = db.Column(db.Float)

    def __init__(self, userRatee='', userRater='', totalRate=''):
        self.userRatee = userRatee
        self.userRater = userRater
        self.totalRate = totalRate


# Comment (Book)--------------------------------
class BookCommentAssociation(db.Model):
    __tablename__ = 'bookComment'
    comment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bookshelf_id = db.Column(db.Integer, db.ForeignKey('contains.contains_id'))
    comment = db.Column(db.TEXT)
    date = db.Column(db.DateTime, default=datetime.datetime.today)
    user = db.relationship('User', backref='user_booksComment')
    books = db.relationship('ContainsAssociation', backref='bookComment')

    def __init__(self, user_id='', bookshelf_id='', comment=''):
        self.user_id = user_id
        self.bookshelf_id = bookshelf_id
        self.comment = comment


# Comment (User)
class UserCommentAssociation(db.Model):
    __tablename__ = 'userComment'
    comment_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.today)
    user_idCommenter = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_idCommentee = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment = db.Column(db.TEXT)

    def __init__(self, user_idCommenter='', user_idCommentee='', comment=''):
        self.user_idCommenter = user_idCommenter
        self.user_idCommentee = user_idCommentee
        self.comment = comment


# class Message(db.Model):
#     __tablename__ = 'message'
#     message_id = db.Column(db.Integer, primary_key=True)
#     messageFrom = db.Column(db.Integer, db.ForeignKey('user.id'))
#     messageTo = db.Column(db.Integer, db.ForeignKey('user.id'))
#     content = db.Column(db.String(100))
#     messaging_message = db.relationship('MessageAssociation', backref='messaging')
#
#     def __init__(self, messageFrom='', messageTo='', content='' ):
#         self.messageFrom = messageFrom
#         self.messageTo = messageTo
#         self.content = content
#
# class MessageAssociation(db.Model):
#     __tablename__ = 'messaging'
#     message_id = db.Column(db.Integer, db.ForeignKey('message.message_id'), primary_key=True)
#     messageFrom = db.Column(db.Integer, db.ForeignKey('user.id'))
#     messageTo = db.Column(db.Integer, db.ForeignKey('user.id'))
#     content = db.Column(db.String(100), db.ForeignKey('message.content'))
#     date = db.Column(db.DATE, nullable=False)
#     user = db.relationship('User', backref='userMessage')
#     messaging = db.relationship('Message', backref='hasMessage')
#
#     def __init__(self, messageFrom='', messageTo='', content='', date='' ):
#         self.messageFrom = messageFrom
#         self.messageTo = messageTo
#         self.content = content
#         self.date = date


class ActLogs(db.Model):
    __tablename__ = 'actlogs'
    logs = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    shelf_id = db.Column(db.Integer, db.ForeignKey('bookshelf.bookshelf_id'))
    date = db.Column(db.DateTime, default=datetime.datetime.today)
    status = db.Column(db.Integer)
    bookid = db.Column(db.Integer, db.ForeignKey('contains.contains_id'))

    def __init__(self, user_id='', shelf_id='', status='', bookid=''):
        self.user_id = user_id
        self.shelf_id = shelf_id
        self.status = status
        self.bookid = bookid


db.create_all()
