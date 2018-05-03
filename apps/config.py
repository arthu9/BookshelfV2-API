import os

DEBUG = True
SQLALCHEMY_DATABASE_URI = os.environ.get('postgresql://kklbdslihbqqjv:ce5ac71de896ae63497f3c07ef2db38675d5d60fd68a79ae4e63aba4a53f43ff@ec2-54-204-39-46.compute-1.amazonaws.com:5432/de58rgv778eq73')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'thisisthesecretkey'
