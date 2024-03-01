from ..models import User, Repository, File, Folder
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session
from datetime import datetime
import os

def add_file(repo, file_name, file_path):
    
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return False
    
    try:
        g = github.Github(user.githubG)
        user = g.get_user()
        repo = user.get_repo(repo)
        # read the file content

        with open("./uploads/"+file_name, 'rb') as file:
            content = file.read()
        
        if file_path == "/": # if the file is in the root
            route = file_name
        else:
            route = file_path + file_name
           
        repo.create_file(route, "Uploaded file", content)

        # remove the file from the server
        os.remove("./uploads/"+file_name)
        
        # add the file to the database
        repo = Repository.query.filter_by(name=repo.name).first()

        if file_path[0] != "/":
            file_path = "/" + file_path

        path = str(repo.name + file_path + file_name)
        folder_path = str(repo.name + file_path)
        
        file = File(name=file_name, path = path, repository_name=repo.name, 
        lastUpdated=datetime.now(), modified = True ,folderPath = folder_path)
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


        db.session.commit()

        # if the repo is cloned, we have to add the file to the file system

        if repo.isCloned:
            repo = Repository.query.filter_by(name=repo.name).first()
 
            print (f"We are looking for {repo.FileSystemPath}/{path}")
            with open(repo.FileSystemPath + path, "wb") as file:
                file.write(content)
            
            file.close()
        return True
        
    except github.GithubException as e:
        print (e)
        return False