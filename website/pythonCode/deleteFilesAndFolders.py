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
        return False
    
    try:
        repoDB = Repository.query.filter_by(name=repo).first()

        if not repoDB:
            return False
        
        # deletion will always involve deleting the file from the db
        # moreover, if the repository is cloned, it will involve changing the file.deleted property to True
        # so that it can be later deleted from the file system when the user commits the changes

        file = File.query.filter_by(path=path, name=name).first()

        if not file:
            return False

        # the file could not be submitted to github yet as the user has not committed the changes
        # then, we will only delete the file from the database (and the file system if the repository is cloned)

        
        # if the file was added for the first time, we can delete it from the database
        # as if not, it will stay there, and will be recognized as a deleted file when the user commits the changes
        # when it does not in fact exist in the file system

        if file.addedFirstTime:
            db.session.delete(file)
            db.session.commit()
            return True

        # if the repository is cloned, we make it so that the file is deleted in the db (so that the user then
        # commits the deletion). It will be deleted from the database when the user commits the message
        if repoDB.isCloned:
            file.deleted = True

        # also, the repositories lastUpdated field is updated
        repoDB.lastUpdated = datetime.now()

        # we also have to update the dates of the folders where the file is located

        folder_path = file.folderPath[:-1] # remove the last character

        while folder_path != repoDB.name:
                
                print (f"Folder path: {folder_path}")
                # open all the folders that have that folder_path as their path
                folder = Folder.query.filter_by(path=folder_path, repository_name=repoDB.name).first()
    
                folder.lastUpdated = datetime.now()
                
                # remove until the last slash
                folder_path = folder_path[:folder_path.rfind("/")]
        

        db.session.commit()
        return True

        

    except Exception as e:
        print (e)
        return False
    pass 

def delete_folder(repo, path, name):

    pass