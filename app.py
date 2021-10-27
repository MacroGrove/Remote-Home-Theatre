from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import login_required, login_user, logout_user
from objects import Room, User
from forms import LoginForm, RegisterForm


app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE'] = 0
app.config['SECRET_KEY'] = 'bellbottomedbabybutterbellybuttonsimpletonbub'

@app.get('/')
@app.get('/home/')
def index():
    return render_template('home.j2') #You can access current_user here

@app.route('/register/', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if request.method == 'GET':  
        return render_template('register.j2',form=form)

    if form.validate():
        #...
        return redirect(url_for('login'))
    else:
        for field, error in form.errors.items():
            flash("There's a problem with what you've entered...")
            flash(f"{field} - {error}")
        return render_template('register.j2', form=form)

@app.route('/login/', methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':  
        return render_template('login.j2', form=form)
    
    if form.validate():
        user = User() #should query for specific user
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('index')
            return redirect(next)
        else:
            # flash applicable message here
            return render_template('login.j2', form=form)
    else:
        for field, error in form.errors.items():
            flash("There's a problem with what you've entered...")
            flash(f"{field} - {error}")
        return render_template('login.j2', form=form)


@app.get('/logout/')
# @login_required
def logout():
    logout_user()
    # Maybe flash a message???
    return redirect(url_for('index'))
   
@app.route('/lobby/')
# @login_required
def lobby():
    #User can be accessed by current_user in templates
    return render_template('lobby.j2')

@app.route('/room/')
# @login_required
def room():
    #User can be accessed by current_user in templates

    #Initialize the room???
    room_id = request.args.get('rid')
    room = Room()
    return render_template('room.j2', room=room)