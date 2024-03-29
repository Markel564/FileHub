from github import Github
from ..models import User, Repository, File, Folder
from .. import db
import github
import yaml
from flask import session
import os
from datetime import datetime



def delete_file(repo, path, name):

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
    
        # deletion will always involve deleting the file from the db
        # moreover, if the repository is cloned, it will involve changing the file.deleted property to True
        # so that it can be later deleted from the file system when the user commits the changes

        file = File.query.filter_by(path=path, name=name).first()

        if not file:
            return 4

        # the file could not be submitted to github yet as the user has not committed the changes
        # then, we will only delete the file from the database (and the file system if the repository is cloned)

        
        # if the file was added for the first time, we can delete it from the database
        # as if not, it will stay there, and will be recognized as a deleted file when the user commits the changes
        # when it does not in fact exist in the file system

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

        while folder_path != repoDB.name:
                
                # open all the folders that have that folder_path as their path
                folder = Folder.query.filter_by(path=folder_path, repository_name=repoDB.name).first()
    
                folder.lastUpdated = datetime.now()
                
                # remove until the last slash
                folder_path = folder_path[:folder_path.rfind("/")]
        
        # since the file is in the file system, we have to delete it
        if os.path.exists(file.FileSystemPath):
            os.remove(file.FileSystemPath)
        db.session.commit()
        return 0

        
    except Exception:
        return 6
    pass 

def delete_folder(repo, path, name):

    pass