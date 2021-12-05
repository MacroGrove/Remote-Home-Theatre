from flask_wtf import FlaskForm
from wtforms.validators import EqualTo, InputRequired, Email, Optional
from wtforms.fields.simple import PasswordField, SubmitField, EmailField, StringField

class LoginForm(FlaskForm):
    email = EmailField("Enter email: ", validators=[InputRequired(), Email()])
    # username = StringField("Enter username: ", validators=[InputRequired()])
    password = PasswordField("Enter password: ", validators=[InputRequired()])
    submit = SubmitField("Log In")

class RegisterForm(FlaskForm):
    username = StringField("Enter username: ", validators=[InputRequired()])
    password = PasswordField("Enter password: ", validators=[InputRequired()])
    confirm_password = PasswordField("Confirm password: ", validators=[InputRequired(), EqualTo('password')])
    email = EmailField("Enter email: ", validators=[InputRequired(), Email()])
    submit = SubmitField("Join")

class VideoForm(FlaskForm):
    video = StringField("Enter video link: ", id="video-field")
    submit = SubmitField("Submit", id="video-button")

class RoomForm(FlaskForm):
    room =  StringField("Room Code", validators=[InputRequired()])
    submit = SubmitField("Enter")

class NewRoomForm(FlaskForm):
    name =  StringField("Room Name", validators=[InputRequired()])
    description = StringField("Description", validators=[Optional()])
    submit = SubmitField("Create")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Enter new password: ", validators=[InputRequired()])
    confirm_password = PasswordField("Confirm password: ", validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField("Submit")

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Request Password Reset')