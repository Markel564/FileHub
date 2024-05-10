""" 
This module contains a function that adds a collaborator to a repository

"""
from ..models import User
from github import Github, Auth
import github
from flask import session
import requests
from .getToken import get_token


def add_collaborator(repoName: str, collaboratorName: str, isAdmin: bool, isReader: bool, isWriter: bool):
    """ 
    input:
        - repoName (string): name of the repository
        - collaboratorName (string): name of the collaborator
        - isAdmin (bool): True if the collaborator is an admin, False otherwise
        - isReader (bool): True if the collaborator is a reader, False otherwise
        - isWriter (bool): True if the collaborator is a writer, False otherwise

    output: 0 if the collaborator has been added, other number otherwise
    """

    user_id = session.get('user_id') # get the user's id from the session
    userDB = User.query.filter_by(id=user_id).first()

    if not userDB: # if the user is not authenticated, return 1
        return 1
    
    if not isAdmin and not isReader and not isWriter: # no role was selected
        return 2 
    
    # check if the user is already a collaborator
    if collaboratorName == userDB.username:
        return 3 # can't add yourself as a collaborator
    
    # check if there is more than 1 role selected
    roles = [isAdmin, isReader, isWriter]
    if roles.count(True) > 1:
        return 4 

    # set the type of permission of the collaborator
    if isAdmin:
        permission = "admin"
    elif isWriter:
        permission = "push"
    else:
        permission = "pull"

    try:

        token = get_token() # get the user's token

        if not token:
            return 1 # user not in the database

        g = Github(token) # authenticate the user
        user = g.get_user()

        # since the url needs the owner of the repository, we need to find it
        repositories = user.get_repos() # get the repositories of the user
        for repo in repositories: # find the repository
            if repo.name == repoName: 
                owner = repo.owner.login 
                break
                
        url = f"https://api.github.com/repos/{owner}/{repoName}/collaborators/{collaboratorName}"

        headers = { # headers to be sent to the API
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        data = {  # data to be sent to the API
            "permission": permission
        }

        response = requests.put(url, headers=headers, json=data)

        if response.status_code == 204:
            return 5 # collaborator already exists

        elif response.status_code == 201:
            return 0 # collaborator invited

        return 6 # error
    
    except Exception as e: 
        return 7
    