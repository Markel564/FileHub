"""
This section contains the database models for the application.

- User model: stores the user's GitHub ID, github class, name, email, and repositories
- Repository model: stores the repository's ID, and the user's ID

"""
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    g = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100),nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=True, unique=True) 
    avatar_url = db.Column(db.String(255)) 
    repositories = db.relationship('Repository', backref='owner', lazy=True)


class Repository(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


