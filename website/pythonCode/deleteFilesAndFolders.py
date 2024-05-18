""" 
This module contains the functions to delete files and folders from the repository and the file system of the repository.
"""

from github import Github
from ..models import User, Repository, File, Folder
from .. import db
import github
from flask import session
import os
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import shutil
from .getToken import get_token



def delete_file(repo, path, name):
    """ 
    input:
        - repo: name of the repository
        - path: path of the file in DB
        - name: name of the file
    output:
        - 0 if successful, other integer otherwise
    """
    token = get_token() # obtain the token

    if not token: # if the token does not exist, return error
        return 1
    
    repoDB = Repository.query.filter_by(name=repo).first() # filter the repository

    if not repoDB: # if there is not repository, return error
        return 2
    
    if not repoDB.isCloned: # if the repository is not cloned, return error
        return 3

    try:
    
        # deletion will always involve deleting the file from the db
        # moreover, it will involve changing the file.deleted property to True
        # so that it can be later deleted from the file system when the user commits the changes

        file = File.query.filter_by(path=path, name=name).first() # filter the file

        if not file: # if the file does not exist, return error
            return 4
       
        # if the file was added for the first time, we can delete it from the database (it is not in GitHub)
        # as if not, it will stay there, and will be recognized as a deleted file when the user commits the changes
        # when it does not in fact exist in the file system

        if file.addedFirstTime: # if the file was added for the first time (it is not in GitHub), we can delete it from the database
            db.session.delete(file) # delete the file from the database
            db.session.commit() # commit the changes

            # since the file is in the file system, we have to delete it
            if os.path.exists(file.FileSystemPath):
                os.remove(file.FileSystemPath)

            return 0 # return 0 if successful

        # if the repository is cloned (which it has to be), we make it so that the file is deleted in the db (so that the user then
        # commits the deletion). It will be deleted from the database when the user commits the message
        if file.deleted: # if the file is already deleted, the user will not be able to delete it again
            return 5

        # if not, just set the file as deleted
        file.deleted = True
        file.modified = False # the file is not modified anymore
        # also, the repositoryes' lastUpdated field is updated
        repoDB.lastUpdated = datetime.now()

        # we also have to update the dates of the folders where the file is located

        folder_path = file.folderPath[:-1] # remove the last character (/)

        while folder_path != repoDB.name: # while the folder path is not the repository name
                
                # open all the folders that have that folder_path as their path
                folder = Folder.query.filter_by(path=folder_path, repository_name=repoDB.name).first()
    
                folder.lastUpdated = datetime.now() # update the last updated date of the folder
                
                # remove until the last slash
                folder_path = folder_path[:folder_path.rfind("/")]
        

        # since the file is in the file system, we have to delete it
        if os.path.exists(file.FileSystemPath):
            os.remove(file.FileSystemPath)

        db.session.commit() # commit the changes

        return 0

        
    except Exception as e:
        print (e)
        return 6


def delete_folder(repo: str, path: str, name: str):
    """ 
    input:
        - repo: name of the repository
        - path: path of the folder in DB
        - name: name of the folder
    output:
        - 0 if successful, other integer otherwise
    This function is very similar to delete_file, but it deletes a folder instead of a file.
    """

    token = get_token() # obtain the token

    if not token: # if the token does not exist, return error
        return 1
    
    repoDB = Repository.query.filter_by(name=repo).first() # filter the repository

    # same as before, check if the repository exists and is cloned  
    if not repoDB:
        return 2
    
    if not repoDB.isCloned:
        return 3    

    try:

        # Similar to delete_file, we will set the folder.deleted property to True
        # so that it can be later deleted from the file system when the user commits the changes
        # if the folder is in the file system, it will be deleted from there as well

        folder = Folder.query.filter_by(path=path, name=name).first() # filter the folder

        if not folder: # if the folder does not exist, return error
            return 4

        if folder.deleted: # if the folder is already deleted, the user will not be able to delete it again
            return 5

        print (f"Folder to delete {folder.name}")
        repoDB.lastUpdated = datetime.now() # update the last updated date of the repository

        subfolders = Folder.query.filter(Folder.folderPath.like(f"{folder.path}/%")).all() # filter the subfolders
        files = File.query.filter(File.folderPath.like(folder.path + "/%")).all() # filter the files

        print (f"Subfolders {subfolders}")
        print (f"Files {[f.name for f in files]}")
        # since the folder is in the file system, delete it (no need to delete subfolders and files, as they will be deleted when the folder is deleted)
        print (folder.FileSystemPath)
        if os.path.exists(folder.FileSystemPath):
            print ("Folder exists in file system")
            shutil.rmtree(folder.FileSystemPath)
            print ("Deleted folder in file system")
        
        folder_path = folder.folderPath[:-1] # remove the last character

        while folder_path != repoDB.name:    # update the date of previous folders                        
            # open all the folders that have that folder_path as their path
            prior_folder = Folder.query.filter_by(path=folder_path, repository_name=repoDB.name).first()
            prior_folder.lastUpdated = datetime.now() # update the last updated date of the folder
            # remove until the last slash
            folder_path = folder_path[:folder_path.rfind("/")]

        for f in subfolders: 
            db.session.delete(f) # delete the subfolders from the database
            
        # if the folder was added for the first time (it is not in GitHub), we can delete it from the database 
    
        for f in files: 
            if f.addedFirstTime:  # if it is not in github, we can delete it from the database
                db.session.delete(f)
            f.deleted = True # if it is in github, we set it as deleted, and not deleted from the database until the user commits the changes
            f.modified = False
            print (f"file {f.name} is deleted")
        db.session.delete(folder) # delete the folder from the database (it is not in GitHub)
        print (f"DELETE FOLDER {folder.name}")
        db.session.commit()    
         
        return 0

    except Exception as e:
        print (e)
        return 6
