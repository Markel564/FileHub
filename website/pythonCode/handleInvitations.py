from ..models import User
from github import Github, Auth
import github
import yaml
from flask import session
import requests
from .getToken import get_token
from github import GithubException

def handle_invitation(repoName, owner, action):

    token = get_token()

    if not token:
        return 1

    try:

        g = Github(token)
        user = g.get_user()


        invitations = user.get_invitations()

        for invitation in invitations:
            
            if invitation.repository.name == repoName and invitation.inviter.login == owner:
                id = invitation.id
        

        url = f"https://api.github.com/user/repository_invitations/{id}"

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        if action == "accept":
            response = requests.patch(url, headers=headers)
        else: # decline
            response = requests.delete(url, headers=headers)
        

        if response.status_code == 204:
            return 0
        else:
            return 2

        
    except GithubException as e:
        return 3

    except Exception as e:
        return 4