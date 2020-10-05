import os
import re

from flask import Flask, session, render_template, request, url_for, redirect, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_socketio import SocketIO, emit, join_room, send
from functools import wraps  # for security purpose

from models.channel import ChannelDAO, Channel
from models.exceptions import WordSizeException
from models.user import UserDAO, User
from util.encryption import *
from util.form_validation import UserFieldValidation


"""Start of flask app initialization"""

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

user_dao = UserDAO(db)
channel_dao = ChannelDAO(db)



def setup_database():
    global engine
    global db
    if engine == None:
        engine = create_engine(os.getenv("DATABASE_URL"))
    if db == None:
        db = scoped_session(sessionmaker(bind=engine))


setup_database()

# Instantiating encryption util
psw_hasher = HashTable('md5')
msg_hasher = HashTable('sha1')

"""Route Definitions"""

@app.route("/index")
def index():
    if request.method == "GET":
        if 'logged_in' in session:
            return redirect(url_for('home'))
    return render_template("login.html")

@app.route("/about")
def about():
    return render_template("about.html")

#This is your base route
@app.route("/")
def welcome():
    if request.method == "GET":
        if 'logged_in' in session:
            return redirect(url_for('home'))
    return render_template("login.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    # In idle database loses its connection and should has been refreshed
    setup_database()
    if request.method == "GET":
        return render_template('signup.html', error_visibility='none')
    username = request.form.get("username")

    email = request.form.get("email")
    email_error_msg = form_check_email(email)
    if email_error_msg != '':
        flash(email_error_msg, 'error')
        return render_template('signup.html', error_visibility='block', error_msg=email_error_msg)

    if request.form.get("password") == request.form.get("c_password"):
        # checking password strength 
        password_strength = form_password_strength(request.form.get("password"))
        if password_strength == "weak password":
            flash(password_strength, 'error')
            return redirect(request.url)
        if password_strength == "medium password":
            flash(password_strength, 'error')
            return redirect(request.url)
        # The password encryption is satisfied once the user signs up in the right way so that user_dao.saveUser
        # is responsible for encryption. Double encryption is tricky and must be avoided.
        password = request.form.get("password")
    else:
        error_msg = 'Password does not match'
        flash(error_msg, 'error')
        return render_template('signup.html', error_visibility='block')
    user = User(username=username, email=email, password=password)
    # The password will be encrypted here and double encryption must be avoided!
    user_dao.saveUser(user, encryptPassword=True)
    return render_template('login.html')


def form_check_email(email):
    error_msg = ''
    user = user_dao.findUserByEmail(email)
    if user:
        error_msg += 'Email already exists!'
    else:
        match = re.search(r'[\w.-]+@[\w.-]+.\w+', email)
        if match is None:
            error_msg += 'Email not valid!'
    return error_msg

def form_password_strength(password):
    valid_count = 0
    if len(password) >= 8:
        valid_count += 1
    if re.search(r'[A-Z]+', password):
        valid_count += 1
    if re.search(r'[a-z]+', password):
        valid_count += 1
    if re.search(r'[$-/:-?{-~!"^_`\[\]]+', password):
        valid_count += 1
    if valid_count == 4:
        return "strong password"
    elif valid_count == 3:
        return "medium password"
    return "weak password"


@app.route("/login", methods=["POST", "GET"])
def login():
    # In idle database loses its connection and should has been refreshed
    setup_database()
    # This route will only accept the POST request
    if request.method == "POST":
        username = request.form.get("username")
        # For now, the plain text is gonna be encrypted easily; the better way is considering encryption
        # from the begining overall sessions, requests, even Ajax requests, etc.
        password = psw_hasher.hexdigest(request.form.get("password"))
        user = None
        """To ensure that user can log in with either of username and password"""
        try:
            if UserFieldValidation().validateEmail(username):
                user = user_dao.findUserByEmail(username)
            else:
                user = user_dao.findUserByUsername(username)
        except WordSizeException as e:
            user = user_dao.findUserByUsername(username)
        if user is None:
            flash('Account does not exist')
            return redirect(url_for('index'))
        elif password == user.password:
            """Using session here to keep all users sessions separate from each other"""
            session['logged_in'] = True
            session['username'] = user.username
            session['user_id'] = user.id
            return redirect(url_for('home'))
        flash("Invalid password")
    elif request.method == "GET":
        """:session still can have ``logged_in`` with the value that is not necessarily True,
         e.g., False, '' as an empty string, etc., so that checking session to contain a key is not enough!"""
        if 'logged_in' in session :
            redirect(url_for('home'))
    return redirect(url_for('index'))


@app.route("/logout")
def logout():
    if 'logged_in' in session:
        session.pop('logged_in', None)
        session.clear()
    return redirect(url_for('index'))


@app.route("/home", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        # In idle database loses its connection and should has been refreshed
        setup_database()
        channels = channel_dao.findall()
        return render_template(
            "chatroom.html", user_id=session['user_id'], user_name=session['username'], channels=channels
        )
    else:
        if request.method == "GET":
            if 'logged_in' in session:
                """Needs to have some variables to pass"""
                return redirect(url_for('channels'))
            flash('Login is required')
            return redirect(url_for('index'))


"""Securing direct get methods"""

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('you need to login first')
            return redirect(url_for('index'))

    return wrap


@app.route("/channel_creation", methods=["POST"])
@login_required
def channel_creation():
    channel = request.form.get("channel")
    description = request.form.get("description")
    u_id = request.form.get("u_id")
    channel_dao.saveChannel(Channel(channel=channel, description=description, u_id=u_id))
    return redirect(url_for('channels'))


@app.route("/channels")
@login_required
def channels():
    """Lists all channels."""
    channels = channel_dao.findall()
    flack = "Flack"
    channel_decription = "This room is flack official public room"
    return render_template("chatroom.html", flack=flack, user_id=session['user_id'], user_name=session['username'],
                           channels=channels, channel_decription=channel_decription)

@app.route("/channels/public")
def public():
    """Lists all channels."""
    channels = channel_dao.findall()
    flack = "Flack"
    channel_decription = "This room is flack official public room"
    return render_template("chatroom.html", flack=flack, user_id="guest_id", user_name="guest",
                           channels=channels, channel_decription=channel_decription)

@app.route("/channels/<int:channel_id>")
# @login_required
def channel(channel_id):
    # In idle database loses its connection and should has been refreshed
    setup_database()
    # Make sure channel exists.
    channel = channel_dao.findChannelByChannelID(channel_id)
    if channel is None:
        return "No such channel."
    channel_name = channel.channel
    channel_decription = channel.description
    channels = channel_dao.findall()
    # if user is not logged in  set it's id and username to guest
    try:
        user_id = session['user_id']
        user_name = session['username']
    except:
        user_id = "guest"
        user_name = "guest"
    return render_template("chatroom.html", user_id=user_id, user_name=user_name,
                           channel_name=channel_name, channels=channels, channel_decription=channel_decription)

@socketio.on("entry message")
def message(data):
    message = data['message']
    name = data['name']
    room = data['rooma']
    time = data['time']
    join_room(room)
    emit("announce message", {"message": message, "name": name, "time": time}, room=room, broadcast=True)


@socketio.on("submit message")
def message(data):
    message = data['message']
    name = data['name']
    room = data['rooma']
    time = data['time']
    join_room(room)
    emit("announce message", {"message": message, "name": name, "time": time}, room=room, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
