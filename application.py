import os
from flask import Flask, session, render_template, request, url_for, redirect, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_socketio import SocketIO, emit ,join_room
from functools import wraps # for security purpose

app = Flask(__name__)
DATABASE_URL="postgres://vfobhheluegnpw:0704135dad9d809b773c6ad4555bfdc87cd76999ccb90c8c99a0ec982f3267de@ec2-23-21-130-182.compute-1.amazonaws.com:5432/da71gb54aqbou7"

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

@app.route("/signup",methods=["POST","GET"])
def signup():
	if request.method=="GET":
		return render_template('signup.html')
	username=request.form.get("username")
	email=request.form.get("email")
	if request.form.get("password") == request.form.get("c_password"):
		password=request.form.get("password")
	else:
		flash('Password does not match')
		return redirect(url_for('index'))
	db.execute("INSERT INTO user_signup_data(username,email,password) VALUES(:username,:email,:password)",
	{"username":username,"email":email,"password":password})
	db.commit()
	db.close()
	return render_template('login.html')

@app.route("/login",methods=["POST","GET"])
def login():
	#This route will only accept the POST request
	if request.method == "POST":
		username=request.form.get("username")
		password=request.form.get("password")
		query=db.execute("SELECT * FROM user_signup_data WHERE username=:username AND password=:password",
		{"username":username,"password":password}).fetchall()
		"""Lists all channels."""
		global channels
		channels = db.execute("SELECT * FROM user_channel").fetchall()
		for q in query:
			if q.username==username and q.password==password:
				"""Using session here to keep all users sessions separate from each other"""
				session['logged_in'] = True
				session['username'] = q.username
				# global un
				# un = q.username
				session['user_id'] = q.id
				return redirect(url_for('home'))
	if request.method == "GET":
		if 'logged_in' in session:
			redirect(url_for('home'))
	return redirect(url_for('index'))

@app.route("/logout")
def logout():
	session.pop('logged_in',None)
	return redirect(url_for('index'))

@app.route("/home",methods=["POST","GET"]) 
def home():
	if request.method == "POST":
		global channels
		return render_template("chatroom.html",user_id=session['user_id'],user_name=session['username'],channels=channels)
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

@app.route("/channel_creation",methods=["POST"])
@login_required
def channel_creation():
	channel=request.form.get("channel")
	description=request.form.get("description")
	u_id=request.form.get("u_id")
	db.execute("INSERT INTO user_channel(channel,description,u_id) VALUES(:channel,:description,:u_id)",
	{"channel":channel,"description":description,"u_id":u_id})
	db.commit()
	db.close()			
	return redirect(url_for('channels'))

@app.route("/channels")
@login_required
def channela():
	"""Lists all channels."""
	global channels
	flack="Flack"
	return render_template("chatroom.html",flack=flack,user_id=session['user_id'],user_name=session['username'], channels=channels)

@app.route("/channels/<int:channel_id>")
@login_required
def channel(channel_id):
	"""Lists details about a single channel."""
	# Make sure flight exists.
	channel = db.execute("SELECT * FROM user_channel WHERE id = :id", {"id": channel_id}).fetchone()
	if channel is None:
		return "No such channel."
	# I'm using ''.join here because query return a tuple
	channel_name =''.join(db.execute("SELECT channel FROM user_channel WHERE id = :id", {"id": channel_id}).fetchone())
	channel_decription =''.join(db.execute("SELECT description FROM user_channel WHERE id = :id", {"id": channel_id}).fetchone())
	global channels	
	return render_template("chatroom.html",user_id=session['user_id'],user_name=session['username'], channel_name=channel_name,channels=channels, channel_decription=channel_decription)    

@socketio.on("search room")
def message(data):
	channel = data['room']
	room = db.execute("SELECT * FROM user_channel WHERE channel LIKE :channel",
	{"channel":channel}).fetchall()
	print(room)
	emit("announce room", {"room":room}, broadcast=True)

@socketio.on("submit message")
def message(data):
	message = data['message']
	name = data['name']
	room = data['rooma']
	from datetime import datetime
	now = datetime.now()
	time = now.strftime("%I:%M:%S")
	join_room(room)
	emit("announce message", {"message": message,"name":name,"time":time}, room=room, broadcast=True)

if __name__ == '__main__':
	app.run(DEBUG='True')
