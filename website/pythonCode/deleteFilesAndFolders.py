from github import Github
from ..models import User, Repository, File, Folder
from .. import db
import github
import yaml
from flask import session
import os
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import shutil



def delete_file(repo, path, name):

    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    print (f"Dentro de delete_file")

    print (f"Arguments: {repo}, {path}, {name}")
    print (f"Types: {type(repo)}, {type(path)}, {type(name)}")
    if not user:
        return 1
    
    repoDB = Repository.query.filter_by(name=repo).first()

    if not repoDB:
        return 2
    
    if not repoDB.isCloned:
        return 3

    try:
    
        # deletion will always involve deleting the file from the db
        # moreover, if the repository is cloned, it will involve changing the file.deleted property to True
        # so that it can be later deleted from the file system when the user commits the changes

        file = File.query.filter_by(path=path, name=name).first()

        print (f"File: {file}")
        if not file:
            return 4

        # the file could not be submitted to github yet as the user has not committed the changes
        # then, we will only delete the file from the database (and the file system if the repository is cloned)

        
        # if the file was added for the first time, we can delete it from the database
        # as if not, it will stay there, and will be recognized as a deleted file when the user commits the changes
        # when it does not in fact exist in the file system

        print (f"File added for the first time: {file.addedFirstTime}")
        if file.addedFirstTime:
            db.session.delete(file)
            db.session.commit()

            # since the file is in the file system, we have to delete it
            if os.path.exists(file.FileSystemPath):
                os.remove(file.FileSystemPath)

            return 0

        # if the repository is cloned (which it has to be), we make it so that the file is deleted in the db (so that the user then
        # commits the deletion). It will be deleted from the database when the user commits the message
        if file.deleted: # if the file is already deleted, the user will not be able to delete it again
            return 5
        file.deleted = True

        # also, the repositories lastUpdated field is updated
        repoDB.lastUpdated = datetime.now()

        # we also have to update the dates of the folders where the file is located

        folder_path = file.folderPath[:-1] # remove the last character

        print (f"Folder path: {folder_path}")
        while folder_path != repoDB.name:
                
                # open all the folders that have that folder_path as their path
                folder = Folder.query.filter_by(path=folder_path, repository_name=repoDB.name).first()
    
                folder.lastUpdated = datetime.now()
                
                # remove until the last slash
                folder_path = folder_path[:folder_path.rfind("/")]
        
        print (f"Time to remove the file from the database")
        print (f"File path: {file.FileSystemPath}")
        # since the file is in the file system, we have to delete it
        if os.path.exists(file.FileSystemPath):
            os.remove(file.FileSystemPath)
        db.session.commit()

        print (f"File deleted from the database")
        return 0

        
    except Exception as e:
        print (e)
        return 6


def delete_folder(repo, path, name):

    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return 1
    
    repoDB = Repository.query.filter_by(name=repo).first()

    if not repoDB:
        return 2
    
    if not repoDB.isCloned:
        return 3
    

    try:

        # Similar to delete_file, we will set the folder.deleted property to True
        # so that it can be later deleted from the file system when the user commits the changes
        # if the folder is not in the file system, it will be deleted from there as well


        folder = Folder.query.filter_by(path=path, name=name).first()

        if not folder:
            return 4
        

        # if the folder was added for the first time (it is not in GitHub), we can delete it from the database 
        if folder.addedFirstTime:
            print ("Folder added for the first time")
            db.session.delete(folder)
            db.session.commit()

            # since the folder is in the file system, we have to delete it
            if os.path.exists(folder.FileSystemPath):
                shutil.rmtree(folder.FileSystemPath)

            return 0

        if folder.deleted:
            return 5

        folder.deleted = True # set the folder as deleted

        # update the dates

        repoDB.lastUpdated = datetime.now()

        # we also have to update the dates of the folders where the folder is located

        folder_path = folder.folderPath[:-1] # remove the last character

        while folder_path != repoDB.name:
                    
                # open all the folders that have that folder_path as their path
                folder = Folder.query.filter_by(path=folder_path, repository_name=repoDB.name).first()
        
                folder.lastUpdated = datetime.now()
                    
                # remove until the last slash
                folder_path = folder_path[:folder_path.rfind("/")]

        # moreover, we will put as deleted all the files and folders that are inside the folder

        subfolders = Folder.query.filter_by(folderPath=folder.path+"/").all()
        files = File.query.filter_by(folderPath=folder.path+"/").all()


        for f in files:
            f.deleted = True

        print ("Path of the folder: ", folder.path)

        for f in subfolders:
            print (f.name)
            print (f.folderPath, f.path)

        while subfolders:
            
            print (subfolders[0].name)
            files = File.query.filter_by(folderPath=subfolders[0].path+"/").all()

            for f in files:
                f.deleted = True
            folders = Folder.query.filter_by(folderPath=subfolders[0].path+"/").all()

            if folders:
                subfolders.append(folders)

            subfolders.pop(0)


        db.session.commit()    
        # delete from file system
        if os.path.exists(folder.FileSystemPath):
            shutil.rmtree(folder.FileSystemPath)
        
        return 0

    except Exception as e:
        print (e)
        return 6
