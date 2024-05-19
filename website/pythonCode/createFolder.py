""" 
This module contains the function that creates a folder in the repository and in the file system of the repository.

"""
from ..models import Repository, Folder
from .. import db
from flask import session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import os
from .getToken import get_token


def create_folder(repoName: str,folder_name: str, path: str):
    """ 
    input:
        - repoName: name of the repository
        - folder_name: name of the folder
        - path: path of the folder
    output:
        - 0 if successful, other integer otherwise
    This function creates a folder in the repository and in the file system of the repository.
    """

    token = get_token() # obtain the token

    if not token: # if the token does not exist, return error
        return 1
    
    repo = Repository.query.filter_by(name=repoName).first() # filter the repository

    if repo is None: # if there is not repository, return error
        return 2
    
    if not repo.isCloned: # if the repository is not cloned, return error
        return 3
    
    folder = Folder.query.filter_by(path=path, repository_name=repo.name).first() # filter the folder

    if folder is not None: # if the folder already exists, return error
        return 4

    # for folder path, we select the part of the path that is not the folder name itself
    # for example, if the path is "repo/folder1/folder2/", the folder path is "repo/folder1/"
    folderPath = path[:-len(folder_name)] 

    try:
          
        folder = Folder(name=folder_name, repository_name=repo.name,  path = path, lastUpdated = datetime.now(), modified = True,
        folderPath=folderPath, FileSystemPath=repo.FileSystemPath + path, addedFirstTime=True) # create the folder

        repo.lastUpdated = datetime.now() # update the last updated date of the repository

        # we also have to update the dates of the folders where the folder is located
        while folderPath != repo.name+"/":
            # open all the folders that have that folder_path as their path
            fatherFolder = Folder.query.filter_by(path=folderPath[:-1], repository_name=repo.name).first()

            fatherFolder.lastUpdated = datetime.now() # update the last updated date of the folder
            fatherFolder.modified = True # set the folder as modified

            folderPath = folderPath.rsplit("/",2)[0] + "/" # update the folder path
        
        db.session.add(folder) # add the folder to the session
        db.session.commit() # commit the changes

        # moreover, we have to create the folder in the file system of the repository
        path_to_folder = repo.FileSystemPath + path # this is the path to the folder in the file system

        os.makedirs(path_to_folder, exist_ok=True) # create the folder


        # check it exists
        if not os.path.exists(path_to_folder):
            return 5 # error creating the folder in the file system

        return 0

    except SQLAlchemyError:
        return 6

    except Exception:
        return 7



    

