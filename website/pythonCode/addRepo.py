"""
This module contains a function that adds a repository to the 
database and to the user's github account

"""
from ..models import User, Repository
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from .getToken import get_token




def add_repo(project_name, project_description, isPrivate=False):
    """
    input: 
        - project_name (string): name of the project/repository
        - project_description (string): description of the project
        - isPrivate (boolean): True if the user wants to create a private repo, False if not (default is False)
        
    output: 

    This function adds the repo to github account and database
    """

    # obtain the user's token
    token = get_token()

    if not token:
        return False

    # check if there are other repos with the same name
    repo = Repository.query.filter_by(name=project_name).first()

    if repo is not None:
        return 2

    try:

        # authenticate the user
        g = github.Github(token)
        user = g.get_user()

        # create the repository (with project name, description and private/public)
        repo = user.create_repo(project_name, description=project_description, private=isPrivate)
        

        # add the repo to the database
        new_repo = Repository(name=project_name, lastUpdated=datetime.now())
        db.session.add(new_repo)
        db.session.commit()

        # create the readme file with default text
        repo.create_file("DescriptiveFile.txt", "Initial file!", "New Project Created!", branch="main")
        
        g.close()
        return 0
    
    except github.GithubException:
        return 3

    except SQLAlchemyError:
        return 4
    
    except:
        return 5
