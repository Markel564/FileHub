"""
This module contains a function that clones a repository to
the user's filesystem, as well as a series of auxiliary
functions

"""

from .. import db
from ..models import User, Repository
from github import Github, Auth
import github
import os
from flask import session
from git import Repo
from .getHash import sign_file
from sqlalchemy.exc import SQLAlchemyError
import requests
from .getToken import get_token


def clone_repo(repoName: str, path: str):
    """ 
    input:
        - repoName: name of the repository
        - path: path where the repository will be cloned
    
    Clones the remote repository from github into a local one
    """

    token = get_token() # obtain the token

    if not token: # return error if it does not exist (user is not authenticated)
        return 1

    repo = Repository.query.filter_by(name=repoName).first() # filter the repository

    if not repo: # if the repository does not exist in the database, then return an error
        return 2
    
    if repo.isCloned: # if the repository is already cloned, return error
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
        g = github.Github(token)
        user = g.get_user()

        # obtain the owner
        repositories = user.get_repos()

        for repo in repositories: # obtain the owner of the repository for the url
            if repo.name == repoName:
                owner = repo.owner.login
                break

        url = f"https://api.github.com/repos/{owner}/{repoName}"

        headers = { 
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        response = requests.get(url, headers=headers) # make request
        
        if response.status_code != 200: # if response is not correct, return error
            return 7

        repo = response.json()

        clone_url = repo['clone_url'] # obtain the clone url given by the response 
                                    # which is the url needed for permissions to clone the repository
        # clone the repository
        Repo.clone_from(clone_url, path + repoName) # + repoName so the folder has the name of the repository

        
        # update the database adding the path and the cloned status
        repoDB = Repository.query.filter_by(name=repoName).first()

        repoDB.isCloned = True # set clone to true
        repoDB.FileSystemPath = path  # and store the fileSystemPath of the repo in the DB

        if not add_hashes(repoName, path): # create the hashes for all the file within the repo
            return 4 # an error is produced if there is something wrong with a file

    
        db.session.commit() # commit changes

        return 0


    except github.GithubException as e:
        return 7

    except Exception as e:
        return 8


def add_hashes(repoName: str, path: str):
    """ 
    input:
        - repoName: name of repository
        - path: path within the filesystem of repository
    output:
        - true if hashes added to all files, else false
    
    adds a hash value to all the files within the repository, and also adds  to DB
    the location in the fs of all files and folders
    """

    repo = Repository.query.filter_by(name=repoName).first() # obtain the repository
    # get its files and folders
    files = repo.repository_files
    folders = repo.repository_folders
    
    if not files or not folders: # if there are no files or folders, return True
        return True
    
    for file in files: # for every file
            
        real_path = path + file.path # obtain the path of it in the fs(the repo's path + its path within the repo)
        # assign the path to the file
        file.FileSystemPath = real_path
        # assign the hash to the file
        file.shaHash = sign_file(real_path)
            
        if not file.shaHash: # the file was not found
            return False
        
        file.modified = False # the file is not modified anymore
        
    for folder in folders:
        # assign the folder its fileSystem path
        real_path = path + folder.path 
        folder.FileSystemPath = real_path


    # commit the files
    db.session.commit()
    return True




def windows_to_unix_path(windows_path: str, directory=False):
    """ 
    input: 
        - windows_path: path were the repository in windows format
        - directory: indicates if the path is is a directory or not
    output:
        a path within the file system in unix format
    
    Converts a windows path to a unix path. If the given path is 
    in unix format, the return will not modify nothing
    """
    # check if there are any / in the path 
    if windows_path.count('/') != 0: # if there are, it is already in unix format
        return windows_path

    # Convert backslashes to forward slashes
    unix_path = windows_path.replace('\\', '/')
    
    # Check if the path starts with a drive letter
    if len(unix_path) > 1 and unix_path[1] == ':':
        drive_letter = unix_path[0].lower() # get the drive letter
        path_without_drive = unix_path[2:] # remove the drive letter and :
        unix_path = '/mnt/' + drive_letter + path_without_drive # add /mnt/ to it

    if directory: # if the path is a directory
        if unix_path[-1] != "/": #if it does not end with /, add it so it is a folder path
            return unix_path + "/"
    return unix_path


def doesPathExist(path: str):
    """ 
    input:
        - path: a path in unix format
    output: true if the path exists within the user's local mathine, false if not
    """
    isExist = os.path.exists(path) # check if it exists
    
    if not isExist: # return false if it does not
        return False
    return True


def permissions(path: str):
    """ 
    input: 
        - path: a path in unix format
    output:
        - True if the user has read, write and execute permissions, false if not
    
    Checks if the user has permissions for that path
    """
    if not os.access(path, os.R_OK): # read permissions
        return False
    if not os.access(path, os.W_OK): # write permissions
        return False
    if not os.access(path, os.X_OK): # execute permissions
        return False
    return True

def isDirectory(path: str):
    """ 
    input:
        - path: path in unix format
    output: 
        - True if it is a directory, False if not
    Checks if were the user wants to clone the repository is a directory path or not
    """
    if not os.path.isdir(path): # if it is not, return False
        return False
    return True