""" 
This module contains a function to eliminate a collaborator from a repository
"""
from github import Github
import github
import requests
from .getToken import get_token



def eliminate_collaborator(repo: str, collaborator: str):
    """ 
    input:
        - repo: the name of the repository
        - collaborator: the collaborator to be eliminated
    output:
        - 0 if the collaborator has been eliminated, another number otherwise
    eliminates a collaborator from a repository
    """

    token = get_token() # get the token from the session

    if not token:
        return 1

    try:
        
        g = github.Github(token)
        user = g.get_user()
        # obtain the owner of the repository
        repositories = user.get_repos()

        for repository in repositories: # obtain the owner of the repository for the url
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

        response = requests.delete(url, headers=headers) # make request to eliminate the collaborator

        if response.status_code != 204: # if the collaborator has not been eliminated
            return 2
        
        return 0
        
    except Exception:
        return 3


