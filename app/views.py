import os
import secrets
from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import urllib
from PIL import Image
from werkzeug.urls import url_parse
from datetime import datetime
from time import gmtime, strftime

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    # picture_path = os.path.join(app.root_path, 'static/image', picture_fn)
    # form_picture.save(picture_path)
    # return picture_fn
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save
    return picture_fn

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        current_user.password = bcrypt.generate_password_hash(form.password.data)
        db.session.commit()
        flash(f'Account updated for {form.username.data}!', category='success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='image/' + current_user.image_file )
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route('/')
def index():
    return render_template('index.html', name='Прикладна математика',
                           title='PNU')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # user = User.query.filter_by(email=form.email.data).first()
        # if user:
        #     flash(f'Акаунт вже існує {form.email.data}!', category='warning')
        #     return redirect(url_for('register'))
        # 2. зберегти дані з БД
        username = form.username.data
        email = form.email.data
        password_hash = bcrypt.generate_password_hash(form.password.data)
        user = User(username=username, email=email, password=password_hash)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', category='success')
        return redirect(url_for('login'))
    return render_template('registration.html', title='Register', form=form)



@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,  form.password.data):
            login_user(user, remember=form.remember.data)
            flash('You have been logged in!', category='success')
            # TO DO next_page
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        flash('Login unsuccessful. Please check username and password', category='warning')
        return redirect(url_for('login'))
    return render_template('login.html', form=form, title='Login')


@app.route('/posts', methods=['GET', 'POST'])
def posts():
    user = {'nickname': 'Miguel'}  # видуманий користувач
    posts = [  # список видуманих постів
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("posts.html",
                           title='Home',
                           user=user,
                           posts=posts)
