from flask_wtf import FlaskForm
from wtforms.validators import EqualTo, InputRequired, Email, Optional
from wtforms.fields.simple import FileField, PasswordField, SubmitField, EmailField, StringField

class LoginForm(FlaskForm):
    email = EmailField("Enter Email", validators=[InputRequired(), Email()])
    # username = StringField("Enter username: ", validators=[InputRequired()])
    password = PasswordField("Enter Password", validators=[InputRequired()])
    submit = SubmitField("Log In")

class RegisterForm(FlaskForm):
    username = StringField("Enter Username", validators=[InputRequired()])
    password = PasswordField("Enter Password", validators=[InputRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo('password')])
    email = EmailField("Enter Email", validators=[InputRequired(), Email()])
    submit = SubmitField("Join")

class VideoForm(FlaskForm):
    video = StringField("Enter Video Link", id="video-field")
    submit = SubmitField("Load YouTube Link", id="video-button")

class RoomForm(FlaskForm):
    room =  StringField("Room Code", validators=[InputRequired()])
    submit = SubmitField("Enter")

class NewRoomForm(FlaskForm):
    name =  StringField("Room Name", validators=[InputRequired()])
    description = StringField("Description", validators=[Optional()])
    submit = SubmitField("Create")

class DeleteRoomForm(FlaskForm):
    # code = StringField("Code", validators=[InputRequired()])
    submit = SubmitField(" X ")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Enter New Password", validators=[InputRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField("Submit")

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class VideoUploadForm(FlaskForm):
    video = FileField("Video", validators=[InputRequired()])
    submitVideo = SubmitField("Submit")