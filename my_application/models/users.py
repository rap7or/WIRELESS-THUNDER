from flask_login import UserMixin
from datetime import datetime
from bcrypt import hashpw, checkpw, gensalt
from my_application.models import db


class User(UserMixin, db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), index=True, unique=True, nullable=False)
    password = db.Column(db.String(255), index=True, unique=True, nullable=False)
    cookie = db.Column(db.String(255))
    cookie_expiration = db.Column(db.DateTime(), nullable=False, default=datetime.now())

    def is_active(self):
        return True

    def set_password(self, password):
        if type(password) is str:
            password = bytes(password, 'utf-8')
        self.password = hashpw(password, gensalt())

    def check_password(self, password):
        return checkpw(bytes(password, 'utf-8'), bytes(self.password, 'utf-8'))

    def get_id(self):
        return self.username

    def is_authenticated(self):
        if self.cookie_expiration > datetime.now():
            return True
        return False

    def check_valid_cookie(self, session_cookie):
        if session_cookie == self.cookie:
            if self.cookie_expiration > datetime.now():
                return True
        return False

    def is_anonymous(self):
        return False

    def __init__(self, username, password):
        self.username = username
        User.set_password(self, password)

    def __repr__(self):
        return "<User '{}'>".format(self.username)
