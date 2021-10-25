import os
from datetime import date
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Determine the absolute path of our database file
scriptdir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(scriptdir, 'theatre.sqlite3')

# Configure the Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbpath}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Getting the database object handle from the app
db = SQLAlchemy(app)

# define Model for Users table
class User(db.Model):
    __tablename__ = 'Users'
    email = db.Column(db.Unicode, primary_key=True)
    username = db.Column(db.Unicode, nullable=False)
    password = db.Column(db.Unicode, nullable=False)
    accounts = db.relationship('User', backref='user')
    def __str__(self):
        return f"User(username={self.username}, email={self.email})"
    def __repr__(self):
        return f"User({self.email})"

# define Model for Room table
class Room(db.Model):
    __tablename__ = 'Rooms'
    user = db.Column(db.Unicode, db.ForeignKey('Users.email'))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False)
    users = db.relationship('User', backref='room')
    def __str__(self):
        return f"Room(id={self.id}, name={self.name})"
    def __repr__(self): 
        return f"Room({self.id})"

# define Model for Message table
class Message(db.Model):
    __tablename__ = "Messages"
    user = db.Column(db.Unicode, db.ForeignKey('Users.email'))
    room = db.Column(db.Integer, db.ForeignKey('Rooms.id'))
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Unicode, nullable=False)
    accounts = db.relationship('User', backref='message')
    rooms = db.relationship('Room', backref='message')

# Refresh the database to reflect these models
db.drop_all()
db.create_all()