#!/bin/python

from flask import Flask, render_template, request, redirect, Blueprint, make_response
from flask_login import LoginManager
from secrets import token_urlsafe
from my_application.models.users import User, db
from datetime import datetime, timedelta
from .config import DevelopmentConfig


app = Flask(__name__)
app.config.from_object(DevelopmentConfig())
login_manager = LoginManager()
with app.app_context():
    db.init_app(app)
    db.create_all()
    db.session.commit()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        user = authenticate_session()
        if user is not None:
            return redirect("/")
        return render_template("login.html")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter(User.username == username).first()
        print(type(user))
        if user is not None:
            print(user)
            if user.check_password(password):
                cookie = update_session(user)
                resp = make_response(render_template('home.html'))
                resp.set_cookie('session_cookie', cookie)
                resp.set_cookie('user', "{}".format(user.id))
                return resp

    return render_template("login.html")


@app.route('/')
def home():
    if request.method == 'GET':
        user = authenticate_session()
        if user is not None:
            return render_template('home.html')
        return redirect('/login')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        user = authenticate_session()
        if user is not None:
            destroy_session(user)
        return redirect("/login")
    if request.method == 'GET':
        user = authenticate_session()
        if user is not None:
            return render_template("logout.html")
    return redirect("/login")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        u = User(username, password)
        db.session.add(u)
        db.session.commit()
        return redirect("/login")
    if request.method == 'GET':
        return render_template("register.html")


def update_session(user):
    cookie = token_urlsafe(32)
    user.cookie = cookie
    user.cookie_expiration = datetime.now() + timedelta(hours=1)
    db.session.add(user)
    db.session.commit()
    return cookie


def destroy_session(user):
    user.cookie = None
    user.cookie_expiration = datetime.now()
    db.session.add(user)
    db.session.commit()


def authenticate_session():
    if 'user' in request.cookies:
        user_id = request.cookies['user']
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            if user:
                if 'session_cookie' in request.cookies and user.cookie == request.cookies['session_cookie']:
                    if user.cookie_expiration > datetime.now():
                        return user
    return None


if __name__ == "__main__":
    app.run()
