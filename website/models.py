"""
This section contains the database models for the application.

- User model: used to store the users information in the database
- Repository model: used to store the repositories information in the database
- Folder model: used to store the folders information in the database
- File model: used to store the files information in the database

"""
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    githubG = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    avatarUrl = db.Column(db.String(255), nullable=False, unique=False)
    
    repositories = db.relationship('Repository', backref='owner', lazy=True)

class Repository(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    FileSystemPath = db.Column(db.String(255), nullable=True, unique=False) # unlile files and folders, this filesystemPath represents the folderit is in, and there can be multiple repositories in the same folder                                                           
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    isCloned = db.Column(db.Boolean, default=False)
    lastUpdated = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    loadedInDB = db.Column(db.Boolean, default=False, nullable=False)

    repository_files = db.relationship('File', backref='belongs_repository', lazy=True, cascade="all, delete-orphan") # files in the repository
    repository_folders = db.relationship('Folder', backref='belongs_repository', lazy=True, cascade="all, delete-orphan")  # folders in the repository
    
 
class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) 
    repository_name = db.Column(db.String(100), db.ForeignKey('repository.name'), nullable=False)
    lastUpdated = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    modified = db.Column(db.Boolean, default=True, nullable=False)
    path = db.Column(db.String(255), nullable=False, unique=True)
    folderPath = db.Column(db.String(255), nullable=False, unique=False) #represents the path of his father folder
    FileSystemPath = db.Column(db.String(255), nullable=True, unique=True) 
    deleted = db.Column(db.Boolean, default = False, nullable=True)
    fatherFolder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True) # folder where the folder is located
    addedFirstTime = db.Column(db.Boolean, default=False, nullable=True)

    folder_files = db.relationship('File', backref='belonging_folder', lazy=True) # files in the folder
    subfolders = db.relationship('Folder', backref='parent_folder', lazy=True, remote_side=id) # subfolders of the folder


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) 
    path = db.Column(db.String(255), nullable=False, unique=True)
    lastUpdated = db.Column(db.DateTime(timezone=True), default=func.now())
    modified = db.Column(db.Boolean, default=True, nullable=False)
    shaHash = db.Column(db.String(64), nullable=True, unique=False)   
    repository_name = db.Column(db.String(100), db.ForeignKey('repository.name'), nullable=False)
    folderPath = db.Column(db.String(255), nullable=False, unique=False) #represents the path of his father folder
    FileSystemPath = db.Column(db.String(255), nullable=True, unique=True)
    addedFirstTime = db.Column(db.Boolean, default=False, nullable=True)
    deleted = db.Column(db.Boolean, default = False, nullable=True)

    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True) # folder where the file is located



    



