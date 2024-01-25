"""
This module contains a function that deletes a repository from the 
database and to the user's github account

Bare in mind it is only done after the user has confirmed the deletion
"""

from ..models import User, Repository
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session

def delete_repo():
    """
    input: none
    output: True if repo has been deleted from the database and Github account, False if not
    """

    # obtain the user from the database
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return False

    try:
        # authenticate the user
        g = github.Github(user.g)
        user = g.get_user()

        # get the repo to be deleted previously saved in the session
        repo_name = session.get('repo_to_remove')
        # search for the repo in the database
        repo = Repository.query.filter_by(name=repo_name).first()
        # if the repository is not in the database, return False
        if repo is None:
            return False

        # delete the repo from the user's github account
        repo = user.get_repo(repo_name)
        repo.delete()

        # delete the repo from the database
        repo = Repository.query.filter_by(name=repo_name).first()
        db.session.delete(repo)
        db.session.commit()

        # remove the repo to be deleted from the session
        session['repo_to_remove'] = None
        
        return True
    except github.GithubException as e:
        return False
