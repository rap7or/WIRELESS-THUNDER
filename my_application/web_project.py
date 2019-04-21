#!/bin/python

import os
import urllib.request

from flask import Flask, render_template, flash, request, redirect, make_response, url_for
from flask_login import LoginManager
from werkzeug.utils import secure_filename
from secrets import token_urlsafe
from my_application.models import db
from my_application.models.users import User
from my_application.models.videos import Video
from datetime import datetime, timedelta
from .config import DevelopmentConfig

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = {'mp4', 'flv'}
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')

app = Flask(__name__)
app.config.from_object(DevelopmentConfig())
login_manager = LoginManager()
with app.app_context():
    db.init_app(app)
    db.create_all()
    db.session.commit()
login_manager.init_app(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR


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
        if user is not None:
            if user.failure_timeout > datetime.now():
                flash("You are locked out")
                return redirect("/login")
            if user.check_password(password):
                cookie = update_session(user)
                user.failure_timeout = datetime.now()
                user.failure = 0
                db.session.add(user)
                db.session.commit()
                resp = make_response(redirect('/'))
                resp.set_cookie('session_cookie', cookie)
                resp.set_cookie('user', "{}".format(user.id))
                return resp
            else:
                user.failure += 1
                if user.failure > 5:
                    user.failure = 0
                    user.failure_timeout = datetime.now() + timedelta(seconds=120)
                db.session.add(user)
                db.session.commit()
        flash('Incorrect username or password')

    return render_template("login.html")


@app.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        user = authenticate_session()
        if user is not None:
            if request.query_string:
                search_string = request.query_string
                search_string = str(search_string).rsplit('=')[1].replace('\'', '')
                try:
                    videos = Video.query.filter(Video.video_title.ilike("%{}%".format(search_string)))
                except Exception as e:
                    print(e)
                    with db.engine.connect() as con:
                        rs = con.execute('ALTER TABLE video ADD FULLTEXT(video_title);')
                        print(rs)
                    videos = Video.query.filter(Video.video_title.ilike("%{}%".format(search_string))).all()
            else:
                videos = Video.query.all()
            return render_template('home.html', videos=videos)
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


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        user = authenticate_session()
        if user is not None:
            if 'file' not in request.files:
                flash('No file uploaded')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No file selected')
                return redirect(request.url)
            if file and allowed_filetype(file.filename):
                filename = secure_filename(file.filename)
                title = filename.rsplit('.', 1)[0]
                unique_name = unique_filename(filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
                video_obj = Video(user, title, unique_name)
                db.session.add(video_obj)
                db.session.commit()
                flash('File successfully uploaded')
                return redirect('/')

    elif request.method == 'GET':
        user = authenticate_session()
        if user is not None:
            return render_template('upload.html')

    return redirect("/login")


@app.route('/download', methods=['POST', 'GET'])
def download_file():
    if request.method == 'POST':
        user = authenticate_session()
        if user is not None:
            if 'filename' not in request.form:
                flash('No filename')
                return redirect(request.url)
            filename = request.form['filename']
            if filename == '':
                flash('No filename')
                return redirect(request.url)
            if 'url' not in request.form:
                flash('No URL')
                return redirect(request.url)
            url = request.form['url']
            if 'url' == '':
                flash('No URL')
                return redirect(request.url)
            if not allowed_filetype(filename):
                flash('This was not an allowed filetype. Make sure the filename ends with .mp4 or another supported filetype.')
                return redirect('/')
            filename = secure_filename(filename)
            title = filename.rsplit('.', 1)[0]
            unique_name = unique_filename(filename)
            try:
                full_path = os.path.join(BASE_DIR, 'static', 'uploads', unique_name)
                urllib.request.urlretrieve(url, filename=full_path)
            except Exception as e:
                print(e)
                return redirect('/')

            video_obj = Video(user, title, unique_name)
            db.session.add(video_obj)
            db.session.commit()
            flash('File successfully uploaded')
            return redirect('/')

    elif request.method == 'GET':
        user = authenticate_session()
        if user is not None:
            return render_template('transfer_from_external_server.html')
    return redirect("/login")


@app.route('/playback/<video>', methods=['GET', 'POST'])
def playback(video):
    user = authenticate_session()
    if user is not None:
        video_obj = Video.query.filter(Video.id == video).first()
        if video_obj is None:
            flash("Video not found!")
            return redirect('/')
        if request.method == 'POST':
            if video_obj.user_id == int(request.cookies['user']):
                db.session.delete(video_obj)
                db.session.commit()
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], video_obj.video_loc))
                flash("Video successfully deleted")
                return redirect('/')
            else:
                flash("You do not have permissions to delete this video!")
                return render_template('playback.html', video=video_obj, user=int(request.cookies['user']))
        elif request.method == 'GET':
            return render_template('playback.html', video=video_obj, user=int(request.cookies['user']))
    return redirect("/login")


def allowed_filetype(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def unique_filename(filename):
    filename_array = '.' in filename and filename.rsplit('.', 1)
    time = str(datetime.now().timestamp()).rsplit('.', 1)[0]
    return filename_array[0] + '-' + time + '.' + filename_array[1]


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
