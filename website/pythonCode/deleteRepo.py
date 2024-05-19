"""
This module contains a function that deletes a repository from the 
database and to the user's github account

Bare in mind it is only done after the user has confirmed the deletion
"""

from ..models import Repository
from .. import db
from github import Github
import github
from flask import session
from sqlalchemy.exc import SQLAlchemyError
import shutil
from .getToken import get_token



def delete_repo():
    """
    input: none
    output: True if repo has been deleted from the database and Github account, False if not
    """
    # authenticate the user
    token = get_token()

    if not token:
        session['repo_to_remove'] = None
        return 1
    # get the repo to be deleted previously saved in the session
    repo_name = session.get('repo_to_remove')

    repo = Repository.query.filter_by(name=repo_name).first()
    # if the repository is not in the database, return an error
    if not repo:
        session['repo_to_remove'] = None
        return 2
    

    try:

        g = github.Github(token)
        user = g.get_user()
        
        repositories = user.get_repos()

        for repo in repositories: # get the owner of the repo
            if repo.name == repo_name:
                owner = repo.owner.login
                break
        
        if owner != user.login: # if the owner is not the same, user cannot delete the repo
            session['repo_to_remove'] = None # remove the repo to be deleted from the session
            return 5

        # if the owner is the same, delete the repo from the user's github account
        repo = user.get_repo(repo_name)
        repo.delete()

        # delete the repo from the database
        repo = Repository.query.filter_by(name=repo_name).first()

        if repo.isCloned: # if the repo is cloned, delete the folder from the file system

            try:
                shutil.rmtree(f"{repo.FileSystemPath}/{repo_name}")
            except:
                return 6
        
        repo_folders = repo.repository_folders # get the associated folders of the db
        repo_files = repo.repository_files # and the associated files of the db

        for folder in repo_folders: # delete the associated folders of the db
            db.session.delete(folder)
        
        for file in repo_files: # delete the associated files of the db
            db.session.delete(file)

        db.session.delete(repo) # delete the repo from the db

        # remove the repo to be deleted from the session
        session['repo_to_remove'] = None
        db.session.commit()

        g.close()
        return 0
    
    except github.GithubException:
        return 3
    
    except SQLAlchemyError:
        return 4
    
    except Exception:
        return 7
