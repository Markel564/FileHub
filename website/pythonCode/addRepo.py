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


def add_repo(project_name, project_description, readme, isPrivate=False):
    """
    input: 
        - project_name (string): name of the project
        - project_description (string): description of the project
        - readme (boolean): True if the user wants to create a readme file, False if not
        - isPrivate (boolean): True if the user wants to create a private repo, False if not (default is False)
        
    output: True if repo has been added to the database, False if not

    This function adds the repo to github account and database
    """

    # obtain the user's id from the session
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    # if the user is not in the database, return False
    if not user:
        return False

    try:

        # authenticate the user
        g = github.Github(user.g)
        user = g.get_user()

        # create the repository (with project name, description and private/public)
        repo = user.create_repo(project_name, description=project_description, private=isPrivate)
        

        # add the repo to the database
        new_repo = Repository(name=project_name, user_id=user_id)
        db.session.add(new_repo)
        db.session.commit()

        # create the readme file with default text
        if readme:
            repo.create_file("README.md", "Initial commit", "New Repository Created!", branch="main")
        
        g.close()
        return True
    
    except github.GithubException as e:
        return False
