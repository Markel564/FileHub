from ..models import User, Repository, File
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session
from datetime import datetime


def add_file(repo, file_name, path):
    
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return False
    
    try:
        g = github.Github(user.githubG)
        user = g.get_user()
        repo = user.get_repo(repo)

        print ("repo: ", repo)
        
        # read the file content

        with open("./uploads/"+file_name, 'rb') as file:
            content = file.read()
        
        route = path + file_name
        print ("route: ", route)    
        repo.create_file(route, "Uploaded file", content)

        return True
    except github.GithubException as e:
        print (e)
        return False