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
    avatar_url = db.Column(db.String(255), nullable = False, unique=False) 
    repositories = db.relationship('Repository', backref='owner', lazy=True)


class Repository(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    path = db.Column(db.String(255), nullable=True, unique=True)
    isCloned = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    files = db.relationship('File', backref='repository', lazy=True)
    folders = db.relationship('Folder', backref='repository', lazy=True)
    # comits, branches, pulls??
    # files, folders

class Folder(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    repository_name = db.Column(db.String(100), db.ForeignKey('repository.name'), nullable=False)
    repository = db.relationship('Repository', backref='folders', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='folders', lazy=True)
    files = db.relationship('File', backref='folder', lazy=True)
    last_updated = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    folder_father = db.Column(db.String(100), db.ForeignKey('folder.name'), nullable=True)
    folders = db.relationship('Folder', backref='folder', lazy=True)



class File(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    # path = db.Column(db.String(255), nullable=False)
    repository_name = db.Column(db.String(100), db.ForeignKey('repository.name'), nullable=False)
    repository = db.relationship('Repository', backref='files', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='files', lazy=True)
    folder_name = db.Column(db.String(100), db.ForeignKey('folder.name'), nullable=True)
    folder = db.relationship('Folder', backref='files', lazy=True)
    last_updated = db.Column(db.DateTime(timezone=True), default=func.now())



