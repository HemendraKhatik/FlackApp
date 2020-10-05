import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(128))


class Channels(db.Model):
    __tablename__ = "channels"
    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text())
    u_id = db.Column(db.Integer())