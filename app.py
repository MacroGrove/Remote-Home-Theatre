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
from flask.sessions import NullSession
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, login_user, logout_user, LoginManager, UserMixin, current_user
from hasher import Hasher
from forms import InputVidForm, LoginForm, RegisterForm, InputVidForm, ResetPasswordForm, RoomForm, ResetPasswordRequestForm
from datetime import date
import yagmail
import jwt
import time


###############################################################################
# Basic Configuration
###############################################################################

# Determine the absolute path of our database file
scriptdir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(scriptdir, "theatre.sqlite3")

# Set-up hasher
scriptdir = os.path.dirname(__file__)
pepfile = os.path.join(scriptdir, "pepper.bin")

with open(pepfile, 'rb') as fin:
    pepper_key = fin.read()

pwd_hasher = Hasher(pepper_key)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE'] = 0
app.config['SECRET_KEY'] = 'bellbottomedbabybutterbellybuttonsimpletonbub'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbpath}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Getting the database object handle from the app
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Set up email
yag = yagmail.SMTP("noreply.remotehometheatre@gmail.com")

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
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode, unique=True, nullable=False)
    username = db.Column(db.Unicode, nullable=False)
    password_hash = db.Column(db.LargeBinary)
    is_verified = db.Column(db.Boolean, nullable=False)
    rooms = db.relationship('Room', backref='owner')
    messages = db.relationship('Message', backref='owner')

    def __str__(self):
        return f"{self.username}"

    # make a write-only password property that just updates the stored hash
    @property
    def password(self):
        raise AttributeError("Password is a write-only attribute")
    @password.setter
    def password(self, pwd):
        self.password_hash = pwd_hasher.hash(pwd)
    
    def verify_password(self,pwd):
        return pwd_hasher.check(pwd, self.password_hash)

    def new_pwd_reset_token(self,expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': expires_in + time.time()},app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def send_pwd_reset_email(user):
        token = user.new_pwd_reset_token()
        yag.send(
            to=user.email,
            subject="Reset Password",
            contents=f"""Hi,{user.email}!\n\nTo reset your password click on the link below:
            \n\n{url_for('get_reset_password', token=token, _external=True)}. Best, The RHT Team"""
        )
    

# Create a database model for rooms
class Room(db.Model):
    __tablename__ = 'Rooms'
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Unicode, unique=True, nullable=False)
    title = db.Column(db.Unicode, nullable=False)
    description = db.Column(db.Unicode)

    def __str__(self):
        return f"Room {self.id} - {self.name})"
    def __repr__(self): 
        return f"Room({self.id})"

# Create a database model for messages
class Message(db.Model):
    __tablename__ = 'Messages'
    user = db.Column(db.Unicode, db.ForeignKey('Users.id'))
    room = db.Column(db.Integer, db.ForeignKey('Rooms.id'))
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.Unicode, nullable=False)

    def __str__(self):
        return f"{self.message}"

# Create a database model for email verification codes
class VerificationCodes(db.Model):
    __tablename__ = 'Codes'
    user = db.Column(db.Integer, db.ForeignKey('Users.id'))
    code = db.Column(db.Unicode, primary_key=True)

# Create a database model for room video queues
class Queue(db.Model):
    __tablename__ = 'Queues'
    room = db.Column(db.Integer, db.ForeignKey('Rooms.id'))
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Unicode, nullable=False)

# Refresh the database to reflect these models
db.drop_all()
db.create_all()

###############################################################################
# Route Handlers
###############################################################################

@app.route('/')
@app.route('/home/', methods=['GET','POST'])
def index():
    form = RoomForm()
    
    if request.method == 'GET':  
        return render_template('home.html', form=form) #You can access current_user here
   
    if form.validate():
        return redirect(f'/room/?roomid={form.room.data}')
    else:
        flash("That room does not exist")
        for field, error in form.errors.items():
            flash(f"{field} - {error}")
        return render_template('home.html', form=form)

# ACCOUNT ACCESS ROUTES

@app.route('/login/', methods=['GET','POST'])
def login():
    form = LoginForm()

    if request.method == 'GET':  
        return render_template('login.html', form=form)
    
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
            return render_template('login.html', form=form)
    else:
        for field, error in form.errors.items():
            flash("There's a problem with what you've entered...")
            flash(f"{field} - {error}")
        return render_template('login.html', form=form)

@app.get('/logout/')
@login_required
def logout():
    logout_user()
    flash("Sucessfully logged out.")
    return redirect(url_for('index'))

# ACCOUNT REGISTRATION ROUTES

@app.route('/register/', methods=['GET','POST'])
def register():
    form = RegisterForm()
    
    if request.method == 'GET':  
        return render_template('join.html',form=form)

    user = User.query.filter_by(email=form.email.data).first()
    
    if form.validate() and user is None:
        #...
        user = User(password=form.password.data, email=form.email.data, username=form.username.data, is_verified=False)
        db.session.add(user)
        db.session.commit()
        yag.send(
            to=form.email.data,
            subject="Welcome!",
            contents=f"""Hi, {form.username.data}!\nWelcome to Remote Home Theatre.\n\nBest,\n\nThe RHT Team""", 
        ) #Make this message nicer.
        return redirect(url_for('login'))

    elif user is not None:
        flash("This email is already associated with an account. Please choose another or log in.")
        return redirect(url_for('login'))

    else:
        flash("There's a problem with what you've entered...")
        for field, error in form.errors.items():
            flash(f"{field} - {error}")
        return render_template('join.html', form=form)

# LOBBY ROUTE

@app.route('/lobby/')
@login_required
def lobby():
    #User can be accessed by current_user in templates
    return render_template('lobby.html')

# ROOM ROUTE

@app.route('/room/',  methods=['GET','POST'])
@login_required
def room():
    #User can be accessed by current_user in templates

    #Initialize the room???
    room_id = request.args.get('rid')
    room = Room()

    #Form to accept youtube link
    vidForm = InputVidForm()

    if request.method == 'GET':        
        if "video" in session:
            vid = session['video']
            vid = vid.replace("watch?v=", "embed/")
            return render_template('roomWithVid.j2', room=room, vid=vid)
        else:
            return render_template('roomWithoutVid.j2', room=room, vidForm=vidForm)

    if vidForm.validate():
        session['video'] = vidForm.video.data
        return redirect(url_for("room"))
    else:
        for field, error in vidForm.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for("room"))

# RESETING PASSWORD ROUTES

@app.get('/reset_request/')
def get_reset_request():
    form = ResetPasswordRequestForm()
    return render_template('reset_password_request.html',form=form)

@app.post('/reset_request/')
def post_reset_request():
    form = ResetPasswordRequestForm()

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if form.validate_on_submit():
        
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            User.send_pwd_reset_email(user)
        flash('Check your email for password reset instructions. It might take a minute. If, after a few minutes, it still has not arrived, please check your spam folder before trying again.')
        return redirect(url_for('login'))

    for field, error in form.errors.items():
            flash("There's a problem with what you've entered...")
            flash(f"{field} - {error}")
    return render_template('reset_password_request.html', form=form)

@app.route('/reset_password/<token>/', methods=['GET','POST'])
def get_reset_password(token):
    form = ResetPasswordForm()

    if request.method == 'POST':

        if current_user.is_authenticated:
            flash('You are already logged in')
            return redirect(url_for('index'))

        user = User.verify_reset_password(token)
        if user is None:
            flash('Token is invalid or has expired. Try again.')
            return redirect(url_for('index'))

        if form.validate():
            # user.password = form.password.data
            # db.session.add(user)
            # user.set_password(form.password.data)
            user.password = form.password.data
            db.session.commit()
            flash('Your password has been reset.')
            return redirect(url_for('login'))

        for field, error in form.errors.items():
                flash("There's a problem with what you've entered...")
                flash(f"{field} - {error}")
        return render_template('reset_password.html', form=form)

    return render_template('reset_password.html', form=form)






    

    

