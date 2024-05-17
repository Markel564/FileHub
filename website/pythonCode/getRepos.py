"""
This module contains a function that gets all the repos of the user's 
github account and adds them to the database (if they are not already there)

"""

from ..models import User, Repository
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session
from sqlalchemy.exc import SQLAlchemyError
from .cryptography import decrypt_token
from .getToken import get_token
import os

def get_repos():
    """
    input: none
    output: list of strings containing the names of the repositories for
    later displaying them in the home page

    This function gets all the repos belonging to the authenticated user
    and returns a list with the names of the repos. It is used to 
    display the repos in the home page
    """

    try:
        
        # authenticate the user
        token = get_token()

        if not token:
            return False
        g = Github(token)


        user = g.get_user()
        # get the user's repos (do not mistake with the function get_repos() used to get the repos from the database)!
        # This one is from the github api to obtain the repos from the user's account
        repositories = user.get_repos()


        # add the repositories to the db
        for repo in repositories:
            # if one repository from GitHub account is not in the database, add it
            if not Repository.query.filter_by(name=repo.name).first():
                new_repo = Repository(name=repo.name, lastUpdated=repo.updated_at)
                db.session.add(new_repo)
                db.session.commit()
        
        g.close()

        for repo in repositories: # check if the user deleted a repo from the local filesystem
            repo = Repository.query.filter_by(name=repo.name).first()
            
            if repo.isCloned: # check if it exists in the local filesystem

                if not os.path.exists(repo.FileSystemPath+f"/{repo.name}"): # if it does not exist, set isCloned to False

                    repo.isCloned = False
                    db.session.commit()
        
        # finally, delete the repositories that are in the database but not in the user's account
        repo_db = Repository.query.all()

        for repo in repo_db: # check if the user deleted a repo from the github account
            if repo.name not in [repo.name for repo in repositories]:
                db.session.delete(repo)
                db.session.commit()

        repo_names = [repo.name for repo in repositories]
        return repo_names
    
    except github.GithubException as e:
        print ("In get repos", e)
        return False

    except Exception as e:
        print ("In get repos", e)
        return False