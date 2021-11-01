from flask_wtf import FlaskForm
from wtforms.validators import EqualTo, InputRequired, Email
from wtforms.fields.core import StringField
from wtforms.fields.html5 import EmailField
from wtforms.fields.simple import PasswordField, SubmitField
class LoginForm(FlaskForm):
    email = EmailField("Enter email: ", validators=[InputRequired(), Email()])
    # username = StringField("Enter username: ", validators=[InputRequired()])
    password = PasswordField("Enter password: ", validators=[InputRequired()])
    submit = SubmitField("Submit")
class RegisterForm(FlaskForm):
    username = StringField("Enter username: ", validators=[InputRequired()])
    password = PasswordField("Enter password: ", validators=[InputRequired()])
    confirm_password = PasswordField("Confirm password: ", validators=[InputRequired(), EqualTo('password')])
    email = EmailField("Enter email: ", validators=[InputRequired(), Email()])
    submit = SubmitField("Submit")
class InputVidForm(FlaskForm):
    video = StringField("Enter video link: ")
class RoomForm(FlaskForm):
    room =  StringField("", validators=[InputRequired()])
    submit = SubmitField("Submit")