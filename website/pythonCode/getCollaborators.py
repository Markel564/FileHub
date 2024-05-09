from ..models import User
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session
import os
from .reformatDate import change_format_date
import requests
from .getToken import get_token


def get_collaborators(repo):

    token = get_token()

    if not token:
        print ("Token not found")
        return 1

    try:
        
        g = github.Github(token)
        user = g.get_user()
        # obtain the owner of the repository
        repositories = user.get_repos()

        for repository in repositories:
            if repository.name == repo:
                owner = repository.owner.login
                break

        # URL for the list of collaborators in the repository
        url = f"https://api.github.com/repos/{owner}/{repo}/collaborators"

        print (url)
        # Headers with the authorization token
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        print (headers)
        # Make the request to the GitHub API
        response = requests.get(url, headers=headers)

        print (response.status_code)
        if response.status_code != 200:
            return 2
            
        collabs = response.json()
        collaborators = []

        for collaborator in collabs:

            permissions = collaborator['permissions']

            isAdmin, isWrite, isRead = permissions.get('admin'), permissions.get('push'), permissions.get('pull')

            if isAdmin:
                permissions = "Admin"
            elif isWrite:
                permissions = "Writer"
            else:
                permissions = "Reader"
            collaborators.append({
                'username': collaborator['login'],
                'avatar': collaborator['avatar_url'],
                'permissions': permissions,
                'type': "active"
            })

        url_invitations = f"https://api.github.com/repos/{owner}/{repo}/invitations"
        response = requests.get(url_invitations, headers=headers)
        invitations = response.json()

        print (response.status_code)
        if response.status_code != 200:
            return collaborators # return the collaborators that were found. It could be that the user does not have permission to see the invitations


        for invitation in invitations:
            collaborators.append({
                'username': invitation['invitee']['login'],
                'avatar': invitation['invitee']['avatar_url'],
                'permissions': "Invited",
                'type': "invited"
            })

        return collaborators

        
    except Exception as e:
        print (e)
        return 3