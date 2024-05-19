""" 
This module contains a function that returns the invitations of a user
using the GitHub API
"""

from github import Github
import github
from .reformatDate import change_format_date
from .getToken import get_token




def get_invitations():
    """ 
    input: none
    output: a list of invitations or an error code if the request was not successful
    This function makes an api request to the GitHub API to obtain the invitations of a user
    """

    token = get_token() # get the token from the session

    if not token:
        return 1 # if the token is not found, return an error code

    try:
        g = Github(token) # authenticate the user
        user = g.get_user()

        invitations = user.get_invitations() # get the invitations of the user

        invites = []
        for invitation in invitations: # for each invitation, append the information to the list
            
            invites.append({
                'inviter': invitation.inviter.login, # the inviter of the invitation
                'repository': invitation.repository.name, # the repository of the invitation
                'date': change_format_date(invitation.created_at), # the date of the invitation
                'avatar': invitation.inviter.avatar_url # the avatar of the inviter
            })

        return invites
    except Exception:
        return 2
