from ..models import User, Repository, File, Folder
from .. import db
import yaml
from flask import session
from datetime import datetime
import os
from .getHash import sign_file
from sqlalchemy.exc import SQLAlchemyError


def add_file(repoName, file_name, file_path):
    
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return 1
    
    repo = Repository.query.filter_by(name=repoName).first()

    if repo is None:
        return 2

    if not repo.isCloned:
        return 3


    if file_path[0] != "/":
            file_path = "/" + file_path

    path = str(repo.name + file_path + file_name)
    folder_path = str(repo.name + file_path)

    try:
    
        with open("./uploads/"+file_name, 'rb') as file:
            content = file.read()

            if repo.isCloned: # write the file to the file system if the repo is cloned
                # we create the file in the file system of the repository
                repo = Repository.query.filter_by(name=repo.name).first()

                with open(repo.FileSystemPath + path, "wb") as file:
                    file.write(content)
                file.close()

        
        os.remove("./uploads/"+file_name)
        
        # add the file to the database
        repo = Repository.query.filter_by(name=repoName).first()

        
        file = File(name=file_name, path = path, repository_name=repo.name, 
        lastUpdated=datetime.now(), modified = True ,folderPath = folder_path, addedFirstTime = True)


        if path in [f.path for f in repo.repository_files]: # if the file is already in the repository (same place)
            
            f = File.query.filter_by(path=path).first()
            if f.deleted: # if the file was deleted, we will delete the file from the database and add the new one
                db.session.delete(f)
                db.session.commit()
            else:
                return 7 # the file is already in the repository, and in the same location (plus, not deleted)

        
        db.session.add(file)

        repo.lastUpdated = datetime.now() # update the last updated date of the repository

        # we also have to update the dates of the folders where the file is located

        folder_path = folder_path[:-1] # remove the last character

        while folder_path != repo.name:

            # open all the folders that have that folder_path as their path
            folder = Folder.query.filter_by(path=folder_path, repository_name=repo.name).first()

            folder.lastUpdated = datetime.now()
            
            # remove until the last slash
            folder_path = folder_path[:folder_path.rfind("/")]


        # if the repo is cloned, we have to hash the file
        if repo.isCloned:
            file.FileSystemPath = repo.FileSystemPath + path
  
            file.shaHash = sign_file(file.FileSystemPath)

            if not file.shaHash:
                return 4
        db.session.commit()

   
        return 0

    except FileNotFoundError as e:
        print (e)
        return 4
    
    except PermissionError:
        return 5
    
    except SQLAlchemyError as e: 
        print (e)
        return 6
        
    except Exception as e:
        print (e)  
        return 8