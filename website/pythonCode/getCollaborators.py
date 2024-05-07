from ..models import User
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session
import os
from .reformatDate import change_format_date
import requests


def get_collaborators(repo):

    user_id = session.get('user_id')
    userDB = User.query.filter_by(id=user_id).first()
    
    if not userDB:
        return 1

    try:
        
        g = github.Github(userDB.githubG)
        user = g.get_user()
        # obtain the owner of the repository
        repositories = user.get_repos()

        for repository in repositories:
            if repository.name == repo:
                owner = repository.owner.login
                break

        # URL for the list of collaborators in the repository
        url = f"https://api.github.com/repos/{owner}/{repo}/collaborators"


        # Headers with the authorization token
        headers = {
            "Authorization": f"token {userDB.githubG}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Make the request to the GitHub API
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return 2
            
        collabs = response.json()
        collaborators = []

        for collaborator in collabs:
            
            print (collaborator['login'])
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

        if response.status_code != 200:
            return 2


        for invitation in invitations:
            collaborators.append({
                'username': invitation['invitee']['login'],
                'avatar': invitation['invitee']['avatar_url'],
                'permissions': "Invited",
                'type': "invited"
            })

        return collaborators

        
    except Exception as e:
        print (f"Error is {e}")
        return 3