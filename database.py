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

# define Model for Banks table
class Bank(db.Model):
    __tablename__ = 'Banks'
    code = db.Column(db.Unicode, primary_key=True)
    name = db.Column(db.Unicode, nullable=False)
    address = db.Column(db.Unicode, nullable=False)
    accounts = db.relationship('Account', backref='bank')
    def __str__(self):
        return f"Bank(name={self.name}, code={self.code})"
    def __repr__(self):
        return f"Bank({self.code})"

# define Model for Customers table
class Customer(db.Model):
    __tablename__ = 'Customers'
    c_number = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False)
    phone = db.Column(db.Unicode, nullable=False)
    email = db.Column(db.Unicode, nullable=False)
    address = db.Column(db.Unicode, nullable=False)
    membership = db.Column(db.Unicode, nullable=True)
    accounts = db.relationship('Account', backref='customer')
    def __str__(self):
        return f"Customer(name={self.name}, id={self.c_number})"
    def __repr__(self):
        return f"Customer({self.c_number})"

# define Model for Accounts table
class Account(db.Model):
    __tablename__ = 'Accounts'
    customer_no = db.Column(db.Integer, db.ForeignKey('Customers.c_number'))
    code = db.Column(db.Unicode, db.ForeignKey('Banks.code'))
    account_no = db.Column(db.Integer, primary_key=True)
    startdate = db.Column(db.Date, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    def __str__(self):
        return f"Customer(customer={self.customer.name}, bank={self.bank.name})"
    def __repr__(self):
        return f"Account({self.account_no})"

# Refresh the database to reflect these models
db.drop_all()
db.create_all()