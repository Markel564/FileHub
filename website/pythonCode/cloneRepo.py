from .. import db
from ..models import User, Repository
from github import Github, Auth
import github
import os
from flask import session
from git import Repo
from .getHash import sign_file, sign_folder



def clone_repo(repoName, path):

    
    path = rf"{path}"

    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    if not user:

        return False

    # convert the path to unix in case it is windows
    path = windows_to_unix_path(path)
    

    # revise that the path exists
    if not doesPathExist(path):
        print ("Path does not exist")
        return False
    
    # revise that the path has the right permissions
    if not permissions(path):
        print ("Path does not have the right permissions")
        return False
    
    
    # check that the path is a directory
    if not isDirectory(path):
        print ("Path is not a directory")
        return False

    
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
            return False

  
        db.session.commit()


        return True

    except github.GithubException as e:
        print ("Exception is", e)
        return False

    except Exception as e:
        print (e)
        return False


def add_hashes(repoName, path):



    repo = Repository.query.filter_by(name=repoName).first()
    files = repo.repository_files
    folders = repo.repository_folders
    
    if not files or not folders:
        return True
    
    try:
        for file in files:
            
            real_path = path + file.path
            # assign the path to the file
            file.FileSystemPath = real_path
            # assign the hash to the file
            file.shaHash = sign_file(real_path)

        
        for folder in folders:
            
            real_path = path + folder.path
            # assign the path to the folder
            folder.FileSystemPath = real_path
            # assign the hash to the folder
            folder.shaHash = sign_folder(real_path)


        
        db.session.commit()
    
    except Exception as e:
        print (e)
        return False

    return True


def add_shas_to_db(repoName, path):

    # obtain the hashes of the files and folders in the repository (re)
    # maybe modify the 'path' of files and folders to put the unix path

    # list all the files and folders in the repository database associated with this repository
    repo = Repository.query.filter_by(name=repoName).first()
    files = repo.repository_files
    folders = repo.repository_folders




def windows_to_unix_path(windows_path):
    # Convert backslashes to forward slashes
    unix_path = windows_path.replace('\\', '/')
    
    # Check if the path starts with a drive letter
    if len(unix_path) > 1 and unix_path[1] == ':':
        drive_letter = unix_path[0].lower()
        path_without_drive = unix_path[2:]
        unix_path = '/mnt/' + drive_letter + path_without_drive

    if unix_path[-1] == "/":
        return unix_path
    return unix_path + "/"


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