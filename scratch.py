import jwt
import time
from flask import Flask
from app import User

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE'] = 0
app.config['SECRET_KEY'] = 'bellbottomedbabybutterbellybuttonsimpletonbub'
user = User(id=100)
expires_in = time.time() + 60000
token = jwt.encode({'reset_password': user.id, 'exp': expires_in},app.config['SECRET_KEY'], algorithm='HS256')
print(token)
print(jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password'])