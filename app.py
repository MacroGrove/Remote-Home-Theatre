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
from flask import jsonify
from flask.sessions import NullSession
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, login_user, logout_user, LoginManager, UserMixin, current_user
from wtforms.fields.core import Label
from hasher import Hasher
from forms import LoginForm, RegisterForm, VideoForm, ResetPasswordForm, RoomForm, NewRoomForm, ResetPasswordRequestForm
from datetime import datetime
import yagmail
import jwt
import time
import rstr


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
    
    def generate_confimration_token(self, expires_in=600):
        return jwt.encode({'confirm' : self.id , 'exp' : expires_in + time.time()},app.config['SECRET_KEY'],algorithm='HS256')
    
    @staticmethod
    def verify_confirmation_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])['confirm']
        except:
            return
        return User.query.get(id)

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
            contents=f"""Hi, {user.email}!
            \n\nTo reset your password click on the link below:
            \n\n{url_for('get_reset_password', token=token, _external=True)}
            \n\n Best, The RHT Team"""
        )

    @staticmethod
    def delete_user(id):
        User.query.filter_by(id=id).delete()
        db.session.commit()

# Create a database model for rooms
class Room(db.Model):
    __tablename__ = 'Rooms'
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Unicode, unique=True, nullable=False)
    title = db.Column(db.Unicode, nullable=False)
    description = db.Column(db.Unicode)
    url = db.Column(db.Unicode)

    def to_json(self):
        return {
            "user_id": self.user_id,
            "id": self.id,
            "code": self.code,
            "title": self.title,
            "description": self.description,
            "url": self.url
        }

# Create a database model for messages
class Message(db.Model):
    __tablename__ = 'Messages'
    user = db.Column(db.Unicode, db.ForeignKey('Users.id'))
    room = db.Column(db.Integer, db.ForeignKey('Rooms.id'))
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.Unicode, nullable=False)

    def to_json(self):
        return {
            "user": self.user,
            "room": self.room,
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message
        }

# Create a database model for room video queues
class Queue(db.Model):
    __tablename__ = 'Queues'
    room = db.Column(db.Integer, db.ForeignKey('Rooms.id'))
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Unicode, nullable=False)

    def to_json(self):
        return {
            "room": self.room,
            "id": self.id,
            "url": self.url
        }


# Refresh the database to reflect these models
db.drop_all()
db.create_all()

###############################################################################
# Route Handlers
###############################################################################

@app.route('/', methods=['GET','POST'])
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
@app.route('/login/<token>', methods=['GET','POST'])
@app.route('/login/', methods=['GET','POST'])
def login(token=None):

    form = LoginForm()

    if request.method == 'GET':  
        return render_template('login.html', form=form)
    
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            if not current_user.is_verified:
                u = User.verify_confirmation_token(token)
                if u is None:
                    flash('Token is invalid or has expired. Try again.')
                    logout_user()
                    User.delete_user(user.id)
                    return redirect(url_for('register'))
                else:
                    u.is_verified = True
                    db.session.commit()
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('lobby')
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
        token = user.generate_confimration_token()
        yag.send(
            to=form.email.data,
            subject="Welcome!",
            contents=f"""Hi, {form.username.data}!
            \n\nWelcome to Remote Home Theatre. Confirm your account by following the link below:
            \n\n{url_for('login', token=token, _external=True)}
            \n\nBest,
            \n\nThe RHT Team""", 
        ) #Make this message nicer.
        flash('Welcome! Check your email for a link to confirm your account.')
        return redirect(url_for('index'))

    elif user is not None:
        flash("This email is already associated with an account. Please choose another or log in.")
        return redirect(url_for('login'))

    else:
        flash("There's a problem with what you've entered...")
        for field, error in form.errors.items():
            flash(f"{field} - {error}")
        return render_template('join.html', form=form)

# LOBBY ROUTE

@app.route('/lobby/', methods=['GET', 'POST'])
@login_required
def lobby():
    #User can be accessed by current_user in templates
    form = NewRoomForm()

    if request.method == 'GET':  
        return render_template('lobby.html', form=form) #You can access current_user here
    
    if request.method == 'POST':
        if form.validate():
            #Add room to user's table
            userRooms = Room.query.filter_by(user_id=current_user.id).all()

            if len(userRooms) < 6:
                # generate access code
                code = rstr.xeger(r'^[a-zA-Z0-9]{12,}$')
                one_instance = Room(user_id=current_user.id,  
                    code=code, title=form.name.data, description=form.description.data)
                
                db.session.add(one_instance)
                db.session.commit()
                
                return redirect('/lobby/')
            else: 
                flash("You have too many rooms to add another")
                return render_template('lobby.html', form=form)
        else: 
            flash("You have to name your room and give it a description")
            for field, error in form.errors.items():
                flash(f"{field} - {error}")
            return render_template('lobby.html', form=form)

# ROOM ROUTE

@app.route('/room/',  methods=['GET','POST'])
def room():
    #User can be accessed by current_user in templates

    #Initialize the room???
    room_id = request.args.get('roomid')
    room = Room.query.get(room_id)
    
    # q = Queue.query.filter_by(room_id).first()

    #Form to accept youtube link
    form = VideoForm()

    if request.method == 'GET':  
        if "video" in session:

            video = session['video']
            if 'youtube' in video:
                video = video.replace("watch?v=", "embed/")
            elif 'vimeo' in video:
                video = video.replace("vimeo.com","player.vimeo.com/video")
            else:
                flash('Something went wrong.')
                return redirect(url_for('room'))
            return render_template('room.html', room=room, video=video, form=form)
        else:
            return render_template('room.html', room=room, video="", form=form)

    if form.validate():
        if 'youtube' not in form.video.data and 'vimeo' not in form.video.data:
            flash('The url was invalid.')
            return redirect(url_for('room'))
        session['video'] = form.video.data
        
        one_instance = Queue(url=form.video.data, room=room_id)
        db.session.add(one_instance)
        db.session.commit()

        return redirect(url_for("room"))
    else:
        for field, error in form.errors.items():
            flash(f"{field}: {error}")
        return redirect(url_for("room"))

# RESETING PASSWORD ROUTES

@app.get('/reset_request/')
def get_reset_request():
    # if current_user.is_anonymous:
    #     flash('You never validated your account. Check your email for a link to validate your account or try registering again.')
    #     return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    return render_template('reset_password_request.html',form=form)

@app.post('/reset_request/')
def post_reset_request():
    form = ResetPasswordRequestForm()

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # if not current_user.is_verified:
    #     flash('Your account was never validated. Please sign up again.')
    
    if form.validate_on_submit():
        
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('You do not have an account. Please register.')
            return redirect('register')
        if not user.is_verified:
            flash('Your account was never validated. Please sign up again.')
            return redirect(url_for('register'))
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
            user.password = form.password.data
            db.session.commit()
            flash('Your password has been reset.')
            return redirect(url_for('login'))

        for field, error in form.errors.items():
                flash("There's a problem with what you've entered...")
                flash(f"{field} - {error}")
        return render_template('reset_password.html', form=form)

    return render_template('reset_password.html', form=form)

@app.get("/api/v1/messages/<int:room_id>/")
def get_messages(room_id):
    room = Message.query.get_or_404(room_id)

    messages = sorted(room.messages, key=lambda message: message.timestamp)
    json_messages = []

    for message in messages:
        json_messages.append(message.to_json())
    
    return jsonify({
        'timestamp': datetime.utcnow().isoformat(),
        'message': json_messages
    })

@app.post("/api/v1/messages/<int:room_id>/")
def post_message(room_id):
    message = Message.from_json(request.get_json())
    db.session.add(message)
    db.session.commit()
    return jsonify(message.to_json()), 201