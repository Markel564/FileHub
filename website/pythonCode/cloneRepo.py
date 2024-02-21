from .. import db
from ..models import User, Repository
from github import Github, Auth
import github
import os
from flask import session

def clone_repo(repoName, path):

    
    path = rf"{path}"
    print ("Path is: ", path)
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    if not user:
        print ("No user")
        return False

    # revise that the path exists
    if not os.path.exists(path):
        print ("No path")
        return False
    
    # revise it is not a file
    if os.path.isfile(path):
        print ("Is a file")
        return False
    
    
    try:
        g = github.Github(user.githubG)
        user = g.get_user()
        repo = user.get_repo(repoName)
        
        # clone the repository
        repo.clone_into(path)
        
        repoDB = Repository.query.filter_by(name=repoName).first()
        repoDB.cloned = True
        repo.path = path    

        return True

    except github.GithubException as e:
        return False

    except Exception as e:
        return False
