""" 
This module contains a function that adds a file to the 
database when a user uploads a file to the website
"""
from ..models import User, Repository, File, Folder
from .. import db
from flask import session
from datetime import datetime
from .getHash import sign_file
from sqlalchemy.exc import SQLAlchemyError


def add_file(repoName: str, file_name: str, file_path: str):
    """
    input: 
        - repoName (string): name of the repository
        - file_name (string): name of the file
        - file_path (string): path of the file within the repository. Ex repo1/folder1/folder2/file1 will have
        a file_path of /folder1/folder2/
        
    output: 0 if the file has been added to the database, other number otherwise

    This function adds a file to the database. Since the repository is cloned (mandatory), the file is also added to the file system
    """
    
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    
    if not user: # if the user is not authenticated, return 1
        return 1
    
    repo = Repository.query.filter_by(name=repoName).first()

    if repo is None: # if the repository does not exist, return 2
        return 2

    if not repo.isCloned: # if the repository is not cloned, return 3
        return 3


    if file_path[0] != "/": # if the path does not start with a slash, add it
            file_path = "/" + file_path

    path = str(repo.name + file_path + file_name) # create the whole path, adding the file name and the repository name
    folder_path = str(repo.name + file_path) # create the folder path

    try:
    
        with open("./uploads/"+file_name, 'rb') as file: # open the file in the uploads folder
            content = file.read()

            if repo.isCloned: # write the file to the file system if the repo is cloned
                # we create the file in the file system of the repository
                repo = Repository.query.filter_by(name=repo.name).first()

                with open(repo.FileSystemPath + path, "wb") as file: # open the file in the file system
                    file.write(content) # write the content of the file
                file.close()

        
        # add the file to the database
        repo = Repository.query.filter_by(name=repoName).first()

        file = File(name=file_name, path = path, repository_name=repo.name, 
        lastUpdated=datetime.now(), modified = True ,folderPath = folder_path, addedFirstTime = True)


        if path in [f.path for f in repo.repository_files]: # there is a chance the file already exists in the repository
            
            f = File.query.filter_by(path=path).first() 
            if f.deleted: # if the file was previously deleted, we will delete the old file from the database and later add the new one
                db.session.delete(f)
                db.session.commit()
            else:
                return 7 # if the file is already in the repository but not deleted, return an error

        
        db.session.add(file) # add the file to the database

        repo.lastUpdated = datetime.now() # update the last updated date of the repository

        # we also have to update the dates of the folders where the file is located

        folder_path = folder_path[:-1] # remove the last /

        while folder_path != repo.name:

            # open all the folders that have that folder_path as their path
            folder = Folder.query.filter_by(path=folder_path, repository_name=repo.name).first()

            folder.lastUpdated = datetime.now() # set the last updated date of the folder to now
            
            # remove until the last slash
            folder_path = folder_path[:folder_path.rfind("/")]

        # sign the file (add a hash to the file)
        file.FileSystemPath = repo.FileSystemPath + path
  
        file.shaHash = sign_file(file.FileSystemPath)

        if not file.shaHash:
            print("Error signing the file")
            return 4
        db.session.commit() # commit the changes to the database

   
        return 0

    except FileNotFoundError as e:
        print(e)
        return 4
    
    except PermissionError:
        return 5
    
    except SQLAlchemyError as e: 
        return 6
        
    except Exception as e:
        return 8