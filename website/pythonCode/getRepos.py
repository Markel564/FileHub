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


def get_repos():
    """
    input: none
    output: list of strings containing the names of the repositories for
    later displaying them in the home page

    This function gets all the repos belonging to the authenticated user
    and returns a list with the names of the repos. It is used to 
    display the repos in the home page
    """
    # obtain the user from the database
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()

    try:

        # authenticate the user
        g = Github(user.githubG)


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
        repo_names = [repo.name for repo in repositories]
        return repo_names
    
    except github.GithubException as e:
        print(e)
        return False

    except Exception as e:
        print(e)
        return False