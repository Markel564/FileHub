from ..models import User, Repository, Folder
from .. import db
import yaml
from flask import session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import os


def create_folder(repoName,folder_name, path):

    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return 1
    
    repo = Repository.query.filter_by(name=repoName).first()

    if repo is None:
        return 2
    
    if not repo.isCloned:
        return 3
    
    folder = Folder.query.filter_by(path=path, repository_name=repo.name).first()

    if folder is not None:
        return 4

    # for folder path, we select the part of the path that is not the folder name itself
    folderPath = path[:-len(folder_name)] 

    try:
          
        folder = Folder(name=folder_name, repository_name=repo.name,  path = path, lastUpdated = datetime.now(), modified = True,
        folderPath=folderPath, FileSystemPath=repo.FileSystemPath + path, addedFirstTime=True)

        repo.lastUpdated = datetime.now() # update the last updated date of the repository
        # we also have to update the dates of the folders where the folder is located

        # folderPath = folderPath[:-1] # remove the last character

        while folderPath != repo.name+"/":
            
            # open all the folders that have that folder_path as their path
            fatherFolder = Folder.query.filter_by(path=folderPath[:-1], repository_name=repo.name).first()

            fatherFolder.lastUpdated = datetime.now()
            fatherFolder.modified = True

            folderPath = folderPath.rsplit("/",2)[0] + "/"
        
        db.session.add(folder)
        db.session.commit()

        # moreover, we have to create the folder in the file system of the repository
        path_to_folder = repo.FileSystemPath + path

        os.makedirs(path_to_folder, exist_ok=True)


        # check it exists
        if not os.path.exists(path_to_folder):
            return 5 # error creating the folder in the file system

        return 0

    except SQLAlchemyError as e:
        return 6

    except Exception as e:
        return 7



    

