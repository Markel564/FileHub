""" 
This module contains a function that checks the file system for modifications,
deletions or additions of files and folders
"""

import os
from ..models import Folder, File, Repository
from .getHash import sign_file
from .. import db
from datetime import datetime
from .cloneRepo import windows_to_unix_path
from flask import session
from sqlalchemy.exc import SQLAlchemyError
from .getToken import get_token



def check_file_system(repo: str):
    """ 
    input: 
        - repo (string): name of the repository
    
    output: 0 if the file system has been checked correctly, other number otherwise

    This function checks the file system for modifications, deletions or additions of files and folders,
    and updates the database accordingly
    """

    token = get_token() # obtain the token

    if not token: # if the token does not exist, return 1
        return 1

    repo = Repository.query.filter_by(name=repo).first() # obtain the repository

    if not repo: # if no repository is found, return 2
        return 2 
    
    if not repo.isCloned: # if the repository is not cloned, return 3
        return 3
    
    try:
        # we have to check for new files in the file system that the user has entered manually
        # and add them to the database
        # this includes files deleted, added or modified

        # see all the files in the repository 
        for root, dirs, files in os.walk(str(repo.FileSystemPath)+repo.name+"/"):
            
            if not root.startswith(repo.FileSystemPath+repo.name+"/.git"): # omit those files that are in the .git folder

                for file in files:
                    print (file)
                    if file.startswith('~$'): # if the file is a temporary file, we wont check it
                        continue
                    
                    #  obtain the paths
                    # full_file_path is the path of the file in the file system
                    full_file_path = os.path.join(root, file) 
                    # relative_file_path is the path of the file relative to the repository
                    relative_file_path = os.path.relpath(full_file_path, str(repo.FileSystemPath) + repo.name + "/")

                    # relative_file_path_with_repo is the path of the file relative to the repository with the repository name
                    relative_file_path_with_repo = os.path.join(repo.name, relative_file_path) 

                    fileDB = File.query.filter_by(path=relative_file_path_with_repo).first()  # check if the file is in the database
                    
                    # ADDING NEW FILES TO THE DATABASE
                    if not fileDB: # if file not in database, that means the user has added a new file manually

                        # we add the file to the database
                        folderPath = relative_file_path_with_repo.rsplit("/",1)[0] + "/" # the folder path of the file
                        FileSystemPath = windows_to_unix_path(full_file_path, directory=False) # convert the path to unix format
                        hash_of_file = sign_file(FileSystemPath) # and sign the file

                        if not hash_of_file: # if the file cannot be hashed, it means it was not found
                            return 4
                        
                        # create the file with the attributes
                        file = File(name=file, path=relative_file_path_with_repo, repository_name=repo.name, 
                        lastUpdated=datetime.now(), modified=True, folderPath=folderPath, FileSystemPath=FileSystemPath, 
                        shaHash=hash_of_file, addedFirstTime=True)
                        db.session.add(file)

                        # we have to update the date of the folder where the file is located and the repository
                        father_dir = folderPath

                        update_dates(father_dir, repo.name)
    
            
                db.session.commit() # commit the changes to the database
        
        # second, we have to check for modifications in the files that are already in the database
        for file_repo in repo.repository_files: # check all the repository files
            file = File.query.filter_by(path=file_repo.path).first()
            hash_of_file = sign_file(file.FileSystemPath)   # see the hash of the file in the file system


            if file.deleted: # if the file has been deleted, it will not be checked for modifications
                continue

            # DELETING FILES FROM THE DATABASE
            elif not hash_of_file: # if the file is not found, it has been deleted from the fs, so we have to delete it from the database

                if file.addedFirstTime: # not in GitHub
                    db.session.delete(file) # delete the file from the database
                else:
                    file.deleted = True # set the property deleted to True
                    file.modified = False
                    file.addedFirstTime = False

                # we have to update the date of the folder where the file is located and the repository
                father_dir = file.folderPath
                update_dates(father_dir, repo.name) # update the dates of the folders were the file is located
                db.session.commit()
            
            # MODIFICATIONS IN FILES
            # if the hashes are different, there is a modification in the file
            # and so, we have to update the database (NOT GITHUB YET, this is done when user commits changes)
            
            if hash_of_file != file.shaHash:
                file.modified = True # set the property modified to True
                file.shaHash = hash_of_file # update the hash of the file
                file.lastUpdated = datetime.now() # update the last updated date of the file
                # update the date of the folder where the file is located and the repository
                father_dir = file.folderPath
                
                update_dates(father_dir, repo.name)

            
            db.session.commit()


        # finally, we have to check for renamed folders and deleted folders, as well as added folders

        for folder in Folder.query.filter_by(repository_name=repo.name).all():

            # check if the folder's path exists in the file system

            
            if not os.path.exists(folder.FileSystemPath):

                # if the folder is no longer in the file system, it means we must eliminate it from the database
                # regardless of whether it is renamed or deleted completely, we will delete it by putting
                # the attribute deleted to True, and later when the user commits the changes, we will delete it from the database
                if folder.addedFirstTime:
                    db.session.delete(folder)
                else:
                    folder.deleted = True
                    folder.modified = False
                    folder.addedFirstTime = False
                # we will put these files as deleted as well

                # we have to update the date of the folder where the folder is located and the repository
                father_dir = folder.folderPath
                update_dates(father_dir, repo.name)
                db.session.commit()

        db.session.commit()

        return 0

    except SQLAlchemyError:
        return 5

    except Exception:
        return 6


def update_dates(father_dir, repo_name):
    """ 
    This function updates the dates of the folders where the file is located and the repository
    input:
        - father_dir (string): path of the folder where the file is located
        - repo_name (string): name of the repository
    output: None

    """
    repo = Repository.query.filter_by(name=repo_name).first()  
    
    while father_dir != repo.name + "/": # while we have not reached the repository
        folder = Folder.query.filter_by(path=father_dir[:-1], repository_name=repo.name).first() # find the folder in the database

        if not folder:  # there is a chance that the user created the directory manually, so we have to add it to the database
            FileSystemPath = windows_to_unix_path(str(repo.FileSystemPath) + father_dir, True)
            folder = Folder(path=father_dir[:-1], repository_name=repo.name, lastUpdated=datetime.now(),
                            name=father_dir.rsplit("/",2)[1], modified=True,
                            folderPath=father_dir.rsplit("/",2)[0] + "/",
                            FileSystemPath=FileSystemPath, addedFirstTime=True)
            db.session.add(folder)
        
        else:
            folder.lastUpdated = datetime.now() # just update the date of the folder to now and put it as modified
            folder.modified = True
            father_dir = father_dir.rsplit("/",2)[0] + "/" # go to its father directory
    
    repo.lastUpdated = datetime.now() # update the last updated date of the repository
    db.session.commit() 
