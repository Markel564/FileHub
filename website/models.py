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
    githubG = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=True, unique=True)
    avatarUrl = db.Column(db.String(255), nullable=False, unique=False)
    
    repositories = db.relationship('Repository', backref='owner', lazy=True)

class Repository(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    path = db.Column(db.String(255), nullable=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    isCloned = db.Column(db.Boolean, default=False)
    lastUpdated = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())

    repository_files = db.relationship('File', backref='belongs_repository', lazy=True)
    repository_folders = db.relationship('Folder', backref='belongs_repository', lazy=True)  
    
    # comits, branches, pulls??
    # files, folders

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sha = db.Column(db.String(40), nullable=False, unique=False)
    repository_name = db.Column(db.String(100), db.ForeignKey('repository.name'), nullable=False)
    lastUpdated = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    fatherFolder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True) # folder where the folder is located

    folder_files = db.relationship('File', backref='belonging_folder', lazy=True) # files in the folder
    subfolders = db.relationship('Folder', backref='parent_folder', lazy=True, remote_side=id) # subfolders of the folder

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # not unique as we can have the same file name in different repositories
    path = db.Column(db.String(255), nullable=True)
    sha = db.Column(db.String(40), nullable=False, unique=False)
    lastUpdated = db.Column(db.DateTime(timezone=True), default=func.now())
    repository_name = db.Column(db.String(100), db.ForeignKey('repository.name'), nullable=False)

    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True) # folder where the file is located 

    



