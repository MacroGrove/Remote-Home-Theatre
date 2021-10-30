"""
INSTALLING REQUIRED PACKAGES
Run the following two commands to install all required packages.
python -m pip install --upgrade pip
python -m pip install --upgrade flask-login
"""

###############################################################################
# Imports
###############################################################################

import os
from flask import Flask, render_template, url_for, redirect
from flask import request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, login_user, logout_user, LoginManager, UserMixin
from hasher import Hasher
from forms import LoginForm, RegisterForm
from datetime import date

###############################################################################
# Basic Configuration
###############################################################################

# Determine the absolute path of our database file
scriptdir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(scriptdir, 'theatre.sqlite3')

# Set-up hasher
scriptdir = os.path.dirname(__file__)
pepfile = os.path.join(scriptdir, "pepper.bin")

with open(pepfile, 'rb') as fin:
    pepper_key = fin.read()

pwd_hasher = Hasher(pepper_key)

# Getting the database object handle from the app

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbpath}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SEND_FILE_MAX_AGE'] = 0
app.config['SECRET_KEY'] = 'bellbottomedbabybutterbellybuttonsimpletonbub'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(email):
    user = User.query.get(email)
    return user

###############################################################################
# Database Setup
###############################################################################

# Create a database model for users
class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Unicode, primary_key=True)
    email = db.Column(db.Unicode, unique=True, nullable=False)
    username = db.Column(db.Unicode, nullable=False)
    password_hash = db.Column(db.LargeBinary)
    verified = db.Column(db.Boolean, nullable=False)
    rooms = db.relationship('Room', backref='owner')
    messages = db.relationship('Message', backref='owner')

    def __str__(self):
        return f"User(username={self.username}, email={self.email})"
    def __repr__(self):
        return f"User({self.email})"

    # make a write-only password property that just updates the stored hash
    @property
    def password(self):
        raise AttributeError("Password is a write-only attribute")
    @password.setter
    def password(self, pwd):
        self.password_hash = pwd_hasher.hash(pwd)
    
    def verify_password(self,pwd):
        return pwd_hasher.check(pwd, self.password_hash)
    
    def is_active():
        return True

    def get_id(self):
        return self.email
    
    def is_authenticated():
        return True

# Create a database model for rooms
class Room(db.Model):
    __tablename__ = 'Rooms'
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Unicode, unique=True, nullable=False)
    title = db.Column(db.Unicode, nullable=False)

    def __str__(self):
        return f"Room(id={self.id}, name={self.name})"
    def __repr__(self): 
        return f"Room({self.id})"

# Create a database model for messages
class Message(db.Model):
    __tablename__ = "Messages"
    users = db.Column(db.Unicode, db.ForeignKey('Users.id'))
    rooms = db.Column(db.Integer, db.ForeignKey('Rooms.id'))
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.Unicode, nullable=False)

# Create a database model for email verification codes
class VerificationCodes(db.Model):
    pass

# Refresh the database to reflect these models
db.drop_all()
db.create_all()

###############################################################################
# Route Handlers
###############################################################################

@app.get('/')
@app.get('/home/')
def index():
    return render_template('home.j2') #You can access current_user here

@app.route('/register/', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if request.method == 'GET':  
        return render_template('register.j2',form=form)

    user = User.query.filter_by(email=form.email.data).first()
    if form.validate() and user is None:
        #...
        user = User(password=form.password.data, email=form.email.data, username=form.username.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    elif user is not None:
        flash("It looks like you already have an account. Please log in.")
        return redirect(url_for('login'))
    else:
        flash("There's a problem with what you've entered...")
        for field, error in form.errors.items():
            flash(f"{field} - {error}")
        return render_template('register.j2', form=form)

@app.route('/login/', methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':  
        return render_template('login.j2', form=form)
    
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('index')
            return redirect(next)
        else:
            flash("Your login info was incorrect.")
            return render_template('login.j2', form=form)
    else:
        for field, error in form.errors.items():
            flash("There's a problem with what you've entered...")
            flash(f"{field} - {error}")
        return render_template('login.j2', form=form)


@app.get('/logout/')
@login_required
def logout():
    logout_user()
    # Maybe flash a message???
    return redirect(url_for('index'))
   
@app.route('/lobby/')
@login_required
def lobby():
    #User can be accessed by current_user in templates
    return render_template('lobby.j2')

@app.route('/room/')
@login_required
def room():
    #User can be accessed by current_user in templates

    #Initialize the room???
    room_id = request.args.get('rid')
    room = Room()
    return render_template('room.j2', room=room)