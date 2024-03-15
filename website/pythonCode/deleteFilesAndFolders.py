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
        
        # deletion will always involve deleting the file in github and from the d
        # and, if the repository is cloned, from the local file system

        g = github.Github(user.githubG)
        user = g.get_user()
        repo = user.get_repo(repo)

        file = File.query.filter_by(path=path, name=name).first()

        if not file:
            return False

        # the file could not be submitted to github yet as the user has not committed the changes
        # then, we will only delete the file from the database (and the file system if the repository is cloned)

        

        # first, we delete the file from the github repository
        if not file.addedFirstTime:
            # remove the repoName + / from the path
            file_path = path[len(repoDB.name) + 1:] 
            file_GB = repo.get_contents(file_path)


            repo.delete_file(file_GB.path, "Deleted file", file_GB.sha)

        # then, we delete the file from the database
        db.session.delete(file)

        # also, the repositories lastUpdated field is updated
        repoDB.lastUpdated = datetime.now()

        # we also have to update the dates of the folders where the file is located

        folder_path = file.folderPath[:-1] # remove the last character
        print (folder_path)

        while folder_path != repoDB.name:
                
                print (f"Folder path: {folder_path}")
                # open all the folders that have that folder_path as their path
                folder = Folder.query.filter_by(path=folder_path, repository_name=repoDB.name).first()
    
                folder.lastUpdated = datetime.now()
                
                # remove until the last slash
                folder_path = folder_path[:folder_path.rfind("/")]
        

        db.session.commit()

        # if the file is cloned, we delete it from the local file system

        if repoDB.isCloned:
            try:
                os.remove(file.FileSystemPath)
            except Exception as e:
                print (e)
                return False
        
        return True

        

    except Exception as e:
        print (e)
        return False
    pass 

def delete_folder(repo, path, name):

    pass