""" 
This module is used to handle the invitations to join a repository.

Basically, it accepts or declines the invitation to join a repository 
which the user has been invited to.
"""

from github import Github
import github
from flask import session
import requests
from .getToken import get_token
from github import GithubException

def handle_invitation(repoName: str, owner:str, action : str):

    """ 
    input:
        - repoName: string with the name of the repository
        - owner: string with the name of the owner of the repository
        - action: string with the action to perform (accept or decline)
    output:
        - 0 if invitation was accepted or declined successfully, other number otherwise
    """
    token = get_token()     # get the token from the session

    if not token:          # if the token is not found, return an error code
        return 1

    try:

        g = Github(token) # authenticate the user
        user = g.get_user()

        # get the invitations from the user
        invitations = user.get_invitations()

        for invitation in invitations: # for each invitation, check if it is the one we are looking for
            
            if invitation.repository.name == repoName and invitation.inviter.login == owner: # by seeing it is the repository we are looking for and the owner is the one we are looking for
                id = invitation.id # save te id of the invitation
        
        #  make request to the GitHub API to accept or decline the invitation
        url = f"https://api.github.com/user/repository_invitations/{id}"

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        if action == "accept": # accept
            response = requests.patch(url, headers=headers)
        else: # decline
            response = requests.delete(url, headers=headers)
        

        if response.status_code == 204: # if the request was successful, return 0
            return 0
        else: # if the request was not successful, return an error code
            return 2

        
    except GithubException: # if an exception occurred, return an error code
        return 3

    except Exception: # if an exception occurred, return an error code
        return 4