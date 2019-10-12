import os
from flask import Flask, session, render_template, request, url_for, redirect, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_socketio import SocketIO, emit, join_room, send
from functools import wraps  # for security purpose
from encryption import *

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

@app.route("/index")
def index():
    if request.method == "GET":
        if 'logged_in' in session:
            return redirect(url_for('home'))
    return render_template("login.html")

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
        return render_template('signup.html')
    username = request.form.get("username")
    email = request.form.get("email")
    # Email validation
    check_email = db.execute("SELECT * FROM user_signup_data WHERE email:email",
                           {"email": email).fetchall()
    if check_email:
        flash('Email Already exist.')
        return redirect(request.url)
    # password validation                        
    if request.form.get("password") == request.form.get("c_password"):
        # encrypting password once the user signs up.
        password = psw_hasher.hexdigest(request.form.get("password"))
    else:
        flash('Password does not match')
        return redirect(request.url)
    db.execute("INSERT INTO user_signup_data(username,email,password) VALUES(:username,:email,:password)",
               {"username": username, "email": email, "password": password})
    # print("New user: \'%s\' with password \'%s\' inserted into database" % (username, password))
    db.commit()
    db.close()
    return render_template('login.html')

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
        user_exists = db.execute("SELECT username from user_signup_data WHERE username=:username",
                                 {"username": username}).fetchall()
        if len(user_exists) == 0:
            flash('Account does not exist')
            return redirect(url_for('index'))
        query = db.execute("SELECT * FROM user_signup_data WHERE username=:username AND password=:password",
                           {"username": username, "password": password}).fetchall()
        """Lists all channels."""
        channels = db.execute("SELECT * FROM user_channel").fetchall()
        for q in query:
            if q.username == username and q.password == password:
                """Using session here to keep all users sessions separate from each other"""
                session['logged_in'] = True
                session['username'] = q.username
                session['user_id'] = q.id
                return redirect(url_for('home'))
        flash("Invalid password")
    elif request.method == "GET":
        if 'logged_in' in session:
            redirect(url_for('home'))
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route("/home", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        # In idle database loses its connection and should has been refreshed
        setup_database()
        channels = db.execute("SELECT * FROM user_channel").fetchall()
        return render_template("chatroom.html", user_id=session['user_id'], user_name=session['username'],
                               channels=channels)
    else:
        if request.method == "GET":
            if 'logged_in' in session:
                """Need to have some variables to pass"""
                return redirect(url_for('channels'))
            flash('Need to login')
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
    # In idle database loses its connection and should has been refreshed
    setup_database()
    db.execute("INSERT INTO user_channel(channel,description,u_id) VALUES(:channel,:description,:u_id)",
               {"channel": channel, "description": description, "u_id": u_id})
    db.commit()
    db.close()
    return redirect(url_for('channels'))

@app.route("/channels")
@login_required
def channels():
    """Lists all channels."""
    global channels
    # In idle database loses its connection and should has been refreshed
    setup_database()
    channels = db.execute("SELECT * FROM user_channel").fetchall()
    flack = "Flack"
    channel_decription = "This room is flack official public room"
    return render_template("chatroom.html", flack=flack, user_id=session['user_id'], user_name=session['username'],
                           channels=channels, channel_decription=channel_decription)

@app.route("/channels/<int:channel_id>")
@login_required
def channel(channel_id):
    # In idle database loses its connection and should has been refreshed
    setup_database()
    # Make sure channel exists.
    channel = db.execute("SELECT * FROM user_channel WHERE id = :id", {"id": channel_id}).fetchone()
    if channel is None:
        return "No such channel."
    # I'm using ''.join here because query return a tuple
    channel_name = ''.join(db.execute("SELECT channel FROM user_channel WHERE id = :id", {"id": channel_id}).fetchone())
    channel_decription = ''.join(
        db.execute("SELECT description FROM user_channel WHERE id = :id", {"id": channel_id}).fetchone())
    channels = channels = db.execute("SELECT * FROM user_channel").fetchall()
    return render_template("chatroom.html", user_id=session['user_id'], user_name=session['username'],
                           channel_name=channel_name, channels=channels, channel_decription=channel_decription)

@socketio.on("entry message")
def message(data):
    message = data['message']
    name = data['name']
    room = data['rooma']
    import time
    message_time = int(round(time.time() * 1000))
    join_room(room)
    emit("announce message", {"message": message, "name": name, "time":  message_time}, room=room, broadcast=True)

@socketio.on("submit message")
def message(data):
    message = data['message']
    name = data['name']
    room = data['rooma']
    import time
    message_time = int(round(time.time() * 1000))
    join_room(room)
    emit("announce message", {"message": message, "name": name, "time": message_time}, room=room, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
