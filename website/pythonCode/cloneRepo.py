from .. import db
from ..models import User, Repository
from github import Github, Auth
import github
import os
from flask import session
from git import Repo
from .getHash import sign_file
from sqlalchemy.exc import SQLAlchemyError



def clone_repo(repoName, path):

    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return 1

    repo = Repository.query.filter_by(name=repoName).first()

    if not repo:
        return 2
    
    if repo.isCloned:
        return 3

    path = rf"{path}"


    # convert the path to unix in case it is windows
    path = windows_to_unix_path(path, directory=True)
    
    # revise that the path exists
    if not doesPathExist(path):
        return 4
    
    # revise that the path has the right permissions
    if not permissions(path):
        return 5
    
    # check that the path is a directory
    if not isDirectory(path):
        return 6

    try:
        g = github.Github(user.githubG)
        user = g.get_user()
        repo = user.get_repo(repoName)
        
        # clone the repository
        Repo.clone_from(repo.clone_url, path + repoName)
        
        # update the database adding the path and the cloned status
        repoDB = Repository.query.filter_by(name=repoName).first()

        repoDB.isCloned = True
        repoDB.FileSystemPath = path  

        if not add_hashes(repoName, path):
            return 4

        db.session.commit()

        return 0


    except github.GithubException:
        return 7

    except Exception:
        return 8


def add_hashes(repoName, path):


    repo = Repository.query.filter_by(name=repoName).first()
    files = repo.repository_files
    folders = repo.repository_folders
    
    if not files or not folders: # if there are no files or folders, return True
        return True
    
    for file in files:
            
        real_path = path + file.path
        # assign the path to the file
        file.FileSystemPath = real_path
        # assign the hash to the file
        file.shaHash = sign_file(real_path)
            
        if not file.shaHash:
            return False
        
    for folder in folders:
            
        real_path = path + folder.path
        # assign the path to the folder
        folder.FileSystemPath = real_path


        
    db.session.commit()
    return True




def windows_to_unix_path(windows_path, directory=False):
    # Convert backslashes to forward slashes

    unix_path = windows_path.replace('\\', '/')
    
    # Check if the path starts with a drive letter
    if len(unix_path) > 1 and unix_path[1] == ':':
        drive_letter = unix_path[0].lower()
        path_without_drive = unix_path[2:]
        unix_path = '/mnt/' + drive_letter + path_without_drive

    if directory:
        if unix_path[-1] != "/":
            return unix_path + "/"
    return unix_path


def doesPathExist(path):
    isExist = os.path.exists(path)  
    
    if not isExist:
        print ("Does not exist")
        return False
    return True


def permissions(path):
    if not os.access(path, os.R_OK):
        print ("Not readable")
        return False
    if not os.access(path, os.W_OK):
        print ("Not writable")
        return False
    if not os.access(path, os.X_OK):
        print ("Not executable")
        return False
    return True

def isDirectory(path):
    if not os.path.isdir(path):
        print ("Not a directory")
        return False
    return True