from ..models import User
from .. import db
from github import Github, Auth
import github
import yaml
from flask import session
import requests
from .getToken import get_token



def eliminate_collaborator(repo, collaborator):

    token = get_token()

    if not token:
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
        
        if owner == collaborator:
            return 2

        url = f"https://api.github.com/repos/{owner}/{repo}/collaborators/{collaborator}"

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        response = requests.delete(url, headers=headers)

        if response.status_code != 204:
            return 2
        
        return 0
        
    except Exception as e:
        
        return 3


