""" 
This module contains a function that returns the collaborators of a repository
""" 

from ..models import User
from .. import db
from github import Github, Auth
import github
from flask import session
import os
from .reformatDate import change_format_date
import requests
from .getToken import get_token


def get_collaborators(repo: str):

    """ 
    input:
        - repo: the name of the repository
    output:
        - a list of collaborators in the repository, or an error code if the request was not successful
    This function makes an api request to the GitHub API to obtain the collaborators of a repository
    and returns such list or an error code if the request was not successful

    """

    token = get_token() # get the token from the session

    if not token:
        return 1

    try:
        
        g = github.Github(token)
        user = g.get_user()
        # obtain the owner of the repository
        repositories = user.get_repos()

        # obtain the owner of the repository for the url
        for repository in repositories:
            if repository.name == repo:
                owner = repository.owner.login
                break

        # URL for the list of collaborators in the repository
        url = f"https://api.github.com/repos/{owner}/{repo}/collaborators" # url to get the collaborators

        # Headers with the authorization token
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Make the request to the GitHub API
        response = requests.get(url, headers=headers)

        if response.status_code != 200: # if the request was not successful, return an error code
            return 2
            
        collabs = response.json() # get the collaborators from the response
        collaborators = [] # add the collaborators to a list (only their names, avatars, permissions and type of collaborator)

        for collaborator in collabs:

            permissions = collaborator['permissions'] # get the permissions of the collaborator

            isAdmin, isWrite, isRead = permissions.get('admin'), permissions.get('push'), permissions.get('pull') # check the permissions of the collaborator

            # in reality, permissionas are usually push, pull and admin, but for representation purposes, the permissions are represented as Admin, Writer and Reader
            # since users without experience are not acustomed to those terms
            if isAdmin: 
                permissions = "Admin"
            elif isWrite:
                permissions = "Writer"
            else:
                permissions = "Reader"
            collaborators.append({ # add the collaborator to the list
                'username': collaborator['login'],
                'avatar': collaborator['avatar_url'],
                'permissions': permissions,
                'type': "active" # active collaborator means that it is already a collaborator
            })

        # Now, get the invitations of the repository, as those are also going to be listed

        url_invitations = f"https://api.github.com/repos/{owner}/{repo}/invitations"
        response = requests.get(url_invitations, headers=headers)
        invitations = response.json()

        # if user does not have permission to see the invitations, return the collaborators that were found
        if response.status_code != 200:
            return collaborators # return the collaborators that were found. It could be that the user does not have permission to see the invitations

        # apply same concept as before
        for invitation in invitations:
            collaborators.append({
                'username': invitation['invitee']['login'],
                'avatar': invitation['invitee']['avatar_url'],
                'permissions': "Invited", # it does not have permissions yet
                'type': "invited" # invited collaborator means that the user has been invited to be a collaborator. It is used for representation purposes (front-end)
            })

        return collaborators

        
    except Exception:
        return 3